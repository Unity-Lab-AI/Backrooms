"""Unity's acoustic model, trained from random weights: phonemes -> log-mel, with explicit knobs.

FastSpeech2-style. A transformer encoder reads the phonemes, three small predictors give every phoneme a
duration, a pitch and an energy, a length regulator stretches the phonemes to frames and a transformer
decoder writes the mel. Durations are learned without any outside aligner: a small alignment encoder
scores every (frame, phoneme) pair, trained by a forward-sum (CTC) loss, and monotonic alignment search
turns that into hard durations (Badlani et al., "One TTS Alignment To Rule Them All").

The knobs are the emotion: at inference the predicted pitch can be shifted, its range widened, given a
contour, and energy and pace scaled per phoneme -- see infer.py PRESETS.
"""
import hashlib
import math
import torch
import torch.nn as nn
import torch.nn.functional as F


def is_heldout(name):
    """2% of clips, by name hash, never trained on by either model: the honest check."""
    return int(hashlib.sha1(name.encode()).hexdigest()[:8], 16) % 50 == 0


def mask_from_lens(lens, n=None):
    n = n or int(lens.max())
    return torch.arange(n, device=lens.device)[None, :] < lens[:, None]   # True = real


class PosEnc(nn.Module):
    def __init__(self, d, n=4000):
        super().__init__()
        pe = torch.zeros(n, d)
        pos = torch.arange(n).float()[:, None]
        div = torch.exp(torch.arange(0, d, 2).float() * (-math.log(10000.0) / d))
        pe[:, 0::2], pe[:, 1::2] = torch.sin(pos * div), torch.cos(pos * div)
        self.register_buffer("pe", pe)

    def forward(self, x):                      # x [B, T, d]
        return x + self.pe[: x.size(1)][None]


class FFTBlock(nn.Module):
    def __init__(self, d, heads=2, k=9, drop=0.1):
        super().__init__()
        self.att = nn.MultiheadAttention(d, heads, dropout=drop, batch_first=True)
        self.n1, self.n2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.ff = nn.Sequential(nn.Conv1d(d, d * 4, k, padding=k // 2), nn.ReLU(), nn.Dropout(drop),
                                nn.Conv1d(d * 4, d, 1))
        self.drop = nn.Dropout(drop)

    def forward(self, x, real):                # real [B, T] True = real
        a, _ = self.att(x, x, x, key_padding_mask=~real)
        x = self.n1(x + self.drop(a)) * real[..., None]
        f = self.ff(x.transpose(1, 2)).transpose(1, 2)
        return self.n2(x + self.drop(f)) * real[..., None]


class Stack(nn.Module):
    def __init__(self, d, n):
        super().__init__()
        self.pos, self.blocks = PosEnc(d), nn.ModuleList(FFTBlock(d) for _ in range(n))

    def forward(self, x, real):
        x = self.pos(x)
        for b in self.blocks:
            x = b(x, real)
        return x


class Predictor(nn.Module):
    """One scalar per position (duration in log frames, normalized pitch or normalized energy)."""

    def __init__(self, d, k=3, drop=0.5):
        super().__init__()
        self.c1, self.c2 = nn.Conv1d(d, d, k, padding=k // 2), nn.Conv1d(d, d, k, padding=k // 2)
        self.n1, self.n2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.drop, self.out = nn.Dropout(drop), nn.Linear(d, 1)

    def forward(self, x, real):
        x = self.drop(self.n1(F.relu(self.c1(x.transpose(1, 2))).transpose(1, 2)))
        x = self.drop(self.n2(F.relu(self.c2(x.transpose(1, 2))).transpose(1, 2)))
        return self.out(x).squeeze(-1) * real


class Aligner(nn.Module):
    """Scores every (mel frame, phoneme) pair: log-prob = -temperature * squared distance."""

    def __init__(self, d, n_mels, c=80, temp=0.0005):
        super().__init__()
        self.k = nn.Sequential(nn.Conv1d(d, d * 2, 3, padding=1), nn.ReLU(), nn.Conv1d(d * 2, c, 1))
        self.q = nn.Sequential(nn.Conv1d(n_mels, n_mels * 2, 3, padding=1), nn.ReLU(),
                               nn.Conv1d(n_mels * 2, n_mels, 1), nn.ReLU(), nn.Conv1d(n_mels, c, 1))
        self.temp = temp

    def forward(self, emb, mel, text_real):    # emb [B,N,d], mel [B,80,T]
        k, q = self.k(emb.transpose(1, 2)), self.q(mel)                     # [B,c,N], [B,c,T]
        dist = (q[:, :, :, None] - k[:, :, None, :]).pow(2).sum(1)          # [B,T,N]
        logp = -self.temp * dist
        logp = logp.masked_fill(~text_real[:, None, :], -1e4)
        return logp                                                          # unnormalized


def forward_sum_loss(logp, text_lens, mel_lens, blank=-1.0):
    """CTC over the phoneme sequence, whole batch in one call: every phoneme must be visited, in order.
    logp [B,T,N] unnormalized with padded phonemes already at -1e4."""
    logp = F.pad(logp.float(), (1, 0), value=blank)                         # blank as column 0
    lp = F.log_softmax(logp, dim=-1).transpose(0, 1)                         # [T,B,N+1]
    n = logp.size(2) - 1
    target = torch.arange(1, n + 1, device=logp.device)[None].expand(logp.size(0), n)
    return F.ctc_loss(lp, target, mel_lens, text_lens, zero_infinity=True)


try:
    import numba
    import numpy as np

    @numba.njit(parallel=True, cache=True)
    def _mas_batch(lp, tl, ml, out):
        """Monotonic alignment search, one item per thread. lp [B,T,N] log-softmaxed, out [B,N] durations."""
        for b in numba.prange(lp.shape[0]):
            t, n = ml[b], tl[b]
            q = np.full((t, n), -1e30, dtype=np.float32)
            q[0, 0] = lp[b, 0, 0]
            for i in range(1, t):
                q[i, 0] = q[i - 1, 0] + lp[b, i, 0]
                for j in range(1, min(i + 1, n)):
                    q[i, j] = max(q[i - 1, j], q[i - 1, j - 1]) + lp[b, i, j]
            j = n - 1
            for i in range(t - 1, -1, -1):
                out[b, j] += 1
                if j > 0 and (j >= i or q[i - 1, j - 1] > q[i - 1, j]):
                    j -= 1
except ImportError:                                                           # the GPU loop below still works
    _mas_batch = None


@torch.no_grad()
def hard_durations(logp, text_lens, mel_lens):
    """Monotonic alignment search for the whole batch -> durations [B,N] (sum = mel length).
    Each frame belongs to exactly one phoneme, phonemes in order, every phoneme at least one frame.
    Compiled parallel CPU search when numba is present (~1000x fewer GPU launches), else a batched GPU loop."""
    if _mas_batch is not None:
        lp = F.log_softmax(logp.float(), dim=-1).cpu().numpy()
        out = np.zeros((logp.size(0), logp.size(2)), dtype=np.int64)
        _mas_batch(lp, text_lens.cpu().numpy().astype(np.int64), mel_lens.cpu().numpy().astype(np.int64), out)
        return torch.from_numpy(out).to(logp.device, non_blocking=True)
    return hard_durations_gpu(logp, text_lens, mel_lens)


@torch.no_grad()
def hard_durations_gpu(logp, text_lens, mel_lens):
    """Monotonic alignment search for the whole batch on the GPU -> durations [B,N] (sum = mel length).
    Each frame belongs to exactly one phoneme, phonemes in order, every phoneme at least one frame."""
    B, T, N = logp.shape
    dev = logp.device
    lp = F.log_softmax(logp.float(), dim=-1)
    neg = torch.tensor(-1e9, device=dev)
    tok = torch.arange(N, device=dev)[None]
    lp = torch.where(tok[:, None, :] < text_lens[:, None, None], lp, neg)
    q = torch.full((B, T, N), -1e9, device=dev)
    q[:, 0, 0] = lp[:, 0, 0]
    for i in range(1, T):
        prev = q[:, i - 1]
        q[:, i, 0] = prev[:, 0] + lp[:, i, 0]
        q[:, i, 1:] = torch.maximum(prev[:, 1:], prev[:, :-1]) + lp[:, i, 1:]
    dur = torch.zeros(B, N, dtype=torch.long, device=dev)
    j = (text_lens - 1).clone()
    rows = torch.arange(B, device=dev)
    for i in range(T - 1, -1, -1):
        active = i < mel_lens                                                # frames past an item's end do nothing
        dur[rows, j] += active.long()
        if i == 0:
            break
        # as many phonemes left as frames left (frame i is 0-based, phoneme j too): must step down every frame
        must = j >= i
        step = active & (j > 0) & (must | (q[rows, i - 1, (j - 1).clamp(min=0)] > q[rows, i - 1, j]))
        j = j - step.long()
    return dur


def token_index(dur, n_frames):
    """For every frame, the phoneme it belongs to. dur [B,N] -> idx [B,n_frames] (clamped), frame mask."""
    ends = dur.cumsum(1)
    frames = torch.arange(n_frames, device=dur.device)[None].expand(dur.size(0), -1)
    idx = torch.searchsorted(ends, frames.contiguous(), right=True)
    real = frames < ends[:, -1:]
    return idx.clamp(max=dur.size(1) - 1), real


def phoneme_average(frame_values, dur, voiced_only=False):
    """Mean of a frame curve inside each phoneme's frames. frame_values [B,T], dur [B,N] -> [B,N]."""
    ends = dur.cumsum(1)
    starts = ends - dur
    csum = F.pad(frame_values.float().cumsum(1), (1, 0))
    if voiced_only:
        ccount = F.pad((frame_values != 0).float().cumsum(1), (1, 0))
    ends_c, starts_c = ends.clamp(max=csum.size(1) - 1), starts.clamp(max=csum.size(1) - 1)
    total = csum.gather(1, ends_c) - csum.gather(1, starts_c)
    count = (ccount.gather(1, ends_c) - ccount.gather(1, starts_c)) if voiced_only else dur.float()
    return torch.where(count > 0, total / count.clamp(min=1), torch.zeros_like(total))


def regulate(x, dur, n_frames=None):
    """Stretch phonemes to frames by gather, whole batch at once. x [B,N,d], dur [B,N] -> [B,T,d], lens [B]."""
    lens = dur.sum(1)
    n_frames = n_frames or int(lens.max())
    idx, real = token_index(dur, n_frames)
    out = x.gather(1, idx[..., None].expand(-1, -1, x.size(2))) * real[..., None]
    return out, lens


class UnityVoice(nn.Module):
    def __init__(self, n_symbols, n_mels=80, d=256, enc=4, dec=4):
        super().__init__()
        self.emb = nn.Embedding(n_symbols, d, padding_idx=0)
        self.encoder, self.decoder = Stack(d, enc), Stack(d, dec)
        self.dur, self.pitch, self.energy = Predictor(d), Predictor(d), Predictor(d)
        self.pitch_emb = nn.Conv1d(1, d, 3, padding=1)
        self.energy_emb = nn.Conv1d(1, d, 3, padding=1)
        self.aligner = Aligner(d, n_mels)
        self.out = nn.Linear(d, n_mels)

    def forward(self, phon, text_lens, mel, mel_lens, f0n, en):
        """Training pass. f0n / en are frame curves already normalized (0 = unvoiced for f0n)."""
        text_real = mask_from_lens(text_lens, phon.size(1))
        emb = self.emb(phon)
        h = self.encoder(emb, text_real)
        with torch.autocast("cuda", enabled=False):                        # distances need fp32
            logp = self.aligner(emb.float(), mel.float(), text_real)
        dur = hard_durations(logp, text_lens, mel_lens)
        p_tgt = phoneme_average(f0n, dur, voiced_only=True)
        e_tgt = phoneme_average(en, dur)
        p_hat, e_hat, d_hat = self.pitch(h, text_real), self.energy(h, text_real), self.dur(h, text_real)
        h = h + self.pitch_emb(p_tgt[:, None]).transpose(1, 2) + self.energy_emb(e_tgt[:, None]).transpose(1, 2)
        frames, lens = regulate(h, dur)
        mel_hat = self.out(self.decoder(frames, mask_from_lens(lens, frames.size(1)))).transpose(1, 2)
        return dict(mel_hat=mel_hat, logp=logp, dur=dur, p_tgt=p_tgt, e_tgt=e_tgt, p_hat=p_hat, e_hat=e_hat,
                    d_hat=d_hat, text_real=text_real)

    @torch.no_grad()
    def infer(self, phon, pitch_fn=None, energy_fn=None, pace_fn=None):
        """phon [1,N]. Each *_fn(values [N], position 0..1 [N]) -> adjusted values: the emotion knobs."""
        real = torch.ones_like(phon, dtype=torch.bool)
        h = self.encoder(self.emb(phon), real)
        p, e = self.pitch(h, real)[0], self.energy(h, real)[0]
        logd = self.dur(h, real)[0]
        pos = torch.linspace(0, 1, phon.size(1), device=phon.device)
        if pitch_fn: p = pitch_fn(p, pos)
        if energy_fn: e = energy_fn(e, pos)
        d = torch.exp(logd) - 1
        if pace_fn: d = pace_fn(d, pos)
        dur = torch.clamp(torch.round(d), min=1).long()[None]
        h = h + self.pitch_emb(p[None, None]).transpose(1, 2) + self.energy_emb(e[None, None]).transpose(1, 2)
        frames, lens = regulate(h, dur)
        return self.out(self.decoder(frames, mask_from_lens(lens))).transpose(1, 2)
