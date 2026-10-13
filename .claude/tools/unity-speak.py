"""Unity's voice: her own trained voice (models/unity-voice), served by models/unity-voice/serve.py on :5123.

    python .claude/tools/unity-speak.py "text to say"          # speak and wait
    python .claude/tools/unity-speak.py --bg "text to say"     # speak, return at once

Delivery comes from UNITY_SPEAK_EMOTION / UNITY_SPEAK_ACT (set by the autopilot from the brain's say/reply_chat call).
There is no fallback voice (owner 2026-10-13: fallbacks are against the laws; Piper is retired): if her voice
server is down or refuses the line, this exits non-zero with the reason on stderr and the caller logs it.
Writes a temp WAV and hands it to OBS's "Unity voice" media source and the stream studio (POST /api/voice).
"""
import os, sys, time, wave, tempfile, subprocess

VOICE_URL = os.environ.get("UNITY_VOICE_TTS_URL", "http://127.0.0.1:5123")


def synth(text, out):
    import json, urllib.request, urllib.error
    body = {"text": text}
    if os.environ.get("UNITY_SPEAK_EMOTION"):
        body["emotion"] = os.environ["UNITY_SPEAK_EMOTION"]
    if os.environ.get("UNITY_SPEAK_ACT"):
        body["speech_act"] = os.environ["UNITY_SPEAK_ACT"]
    req = urllib.request.Request(VOICE_URL + "/say", json.dumps(body).encode(), {"Content-Type": "application/json"})
    try:
        wav = urllib.request.urlopen(req, timeout=60).read()
    except urllib.error.HTTPError as e:
        raise SystemExit("her voice refused the line: %s" % e.read().decode(errors="replace")[:300])
    except OSError as e:
        raise SystemExit("her voice server is not reachable at %s (%s)" % (VOICE_URL, e))
    with open(out, "wb") as f:
        f.write(wav)


LOCK = os.path.join(tempfile.gettempdir(), "unity-voice.lock")


def take_turn(wait=90, stale=120):
    """One line at a time across processes: parallel calls queue here instead of talking over each other."""
    end = time.time() + wait
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode()); os.close(fd)
            return True
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(LOCK) > stale:
                    os.remove(LOCK); continue
            except OSError:
                continue
            if time.time() > end:
                return False
            time.sleep(0.2)


def give_turn():
    try:
        os.remove(LOCK)
    except OSError:
        pass


def main():
    args = sys.argv[1:]
    bg = False
    if args and args[0] == "--bg":
        bg = True; args = args[1:]
    text = " ".join(args).strip()
    if not text:
        return
    if bg:
        subprocess.Popen([sys.executable, os.path.abspath(__file__), text],
                         creationflags=getattr(subprocess, "DETACHED_PROCESS", 0),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    if not take_turn():
        return
    out = os.path.join(tempfile.gettempdir(), "unity-voice-%d-%d.wav" % (os.getpid(), int(time.time() * 1000)))
    try:
        speak(text, out)
    finally:
        give_turn()
        try:
            os.remove(out)
        except OSError:
            pass


def studio_token():
    tok = os.environ.get("STUDIO_TOKEN")
    if tok:
        return tok
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".studio-token"), encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def wav_seconds(path):
    try:
        with wave.open(path, "rb") as w:
            return w.getnframes() / float(w.getframerate() or 1)
    except Exception:
        return 0.0


def speak(text, out):
    synth(text, out)
    # The stream hears the voice through OBS's "Unity voice" media source, which plays this file:
    # OBS decodes it itself (the browser-source audio route crackled to static on stream).
    try:
        import shutil, obsws_python as obs
        live = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".studio-images",
                            "obs-voice-%d-%d.wav" % (int(time.time() * 1000), os.getpid()))
        shutil.copyfile(out, live)
        cl = obs.ReqClient(host="127.0.0.1", port=4455, timeout=5)
        # a NEW path each line: OBS re-opens the media only when the file setting changes
        cl.set_input_settings("Unity voice", {"local_file": live, "is_local_file": True}, True)
    except Exception:
        pass
    # The overlay page plays it too, so the owner hears it locally (desktop audio is muted in OBS).
    try:
        import base64, json, urllib.request
        url = os.environ.get("STUDIO_URL", "http://127.0.0.1:4317") + "/api/voice"
        data = json.dumps({"wav": base64.b64encode(open(out, "rb").read()).decode()}).encode()
        urllib.request.urlopen(urllib.request.Request(url, data=data,
                               headers={"Content-Type": "application/json", "X-Studio-Token": studio_token()}),
                               timeout=10).read()
        # hold the turn while the line plays so the next one does not cut it off
        time.sleep(min(wav_seconds(out), 60))
        return
    except Exception:
        pass
    import winsound
    winsound.PlaySound(out, winsound.SND_FILENAME)


if __name__ == "__main__":
    main()
