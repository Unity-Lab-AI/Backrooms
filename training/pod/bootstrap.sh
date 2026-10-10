#!/usr/bin/env bash
# The pod's own launch command (set at create time, like the brain project's donor launcher -- no SSH needed).
# Pulls the training files from the repo branch, runs the whole training (run.sh), and serves /workspace/gguf over
# HTTP on 8000 the whole time, so progress (status.txt, run.log) and the finished models download through the
# RunPod proxy: https://<pod-id>-8000.proxy.runpod.net/
set -u
W=/workspace; mkdir -p $W/gguf
BRANCH="${SHELLS_BRANCH:-feature/bug-testing}"
REPO="${SHELLS_REPO:-https://github.com/Unity-Lab-AI/Backrooms.git}"
cd $W
python3 -m http.server 8000 --directory $W/gguf >/dev/null 2>&1 &
status() { echo "$(date -u +%FT%TZ) $*" > $W/gguf/status.txt; }
status "cloning"
git clone -q --depth 1 --filter=blob:none --sparse -b "$BRANCH" "$REPO" $W/repo && (cd $W/repo && git sparse-checkout set training/pod training/data)
mkdir -p $W/data $W/pod
cp $W/repo/training/data/*.jsonl $W/repo/training/data/tools.json $W/data/ 2>/dev/null
cp $W/repo/training/pod/*.sh $W/repo/training/pod/*.py $W/pod/
status "training"
# progress visible from outside: the log is mirrored into the served folder every 30 s
( while true; do tail -c 20000 $W/run.log > $W/gguf/run.log.txt 2>/dev/null; ls $W/state > $W/gguf/state.txt 2>/dev/null; sleep 30; done ) &
if bash $W/pod/run.sh; then status "DONE"; else status "FAILED (see run.log.txt)"; fi
tail -c 20000 $W/run.log > $W/gguf/run.log.txt; ls $W/state > $W/gguf/state.txt
sleep infinity      # keep serving until the pod is deleted
