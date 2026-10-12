set -e
apt-get update -qq && apt-get install -y -qq git sox libsox-dev ffmpeg build-essential >/dev/null
cd /tmp
for t in qwen cosy; do
  python -m venv /tmp/venv-$t
  /tmp/venv-$t/bin/pip install -q --upgrade pip
  /tmp/venv-$t/bin/pip install -q "torch==2.7.1+cu118" "torchaudio==2.7.1+cu118" --index-url https://download.pytorch.org/whl/cu118
  if [ $t = cosy ]; then /tmp/venv-$t/bin/pip install -q "setuptools<70" wheel; /tmp/venv-$t/bin/pip install -q --no-build-isolation openai-whisper==20231117; fi
  /tmp/venv-$t/bin/pip install -q -r /voice/pod/requirements-teacher-$t.txt -c /voice/pod/constraints-teacher.txt --extra-index-url https://download.pytorch.org/whl/cu118 && echo "INSTALL OK $t" || echo "INSTALL FAILED $t"
  /tmp/venv-$t/bin/python -c "import torch, torchaudio; print(\"VERSIONS $t\", torch.__version__, torchaudio.__version__)"
done
/tmp/venv-qwen/bin/python -c "import qwen_tts, faster_whisper, huggingface_hub; from qwen_tts import Qwen3TTSModel; print('IMPORT OK qwen', qwen_tts.__file__)"
git clone -q https://github.com/QwenAudio/CosyVoice.git /tmp/cosy && cd /tmp/cosy && git checkout -q 074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc && git submodule update -q --init --recursive
PYTHONPATH=/tmp/cosy:/tmp/cosy/third_party/Matcha-TTS /tmp/venv-cosy/bin/python -c "from cosyvoice.cli.cosyvoice import AutoModel; print('IMPORT OK cosy')"
