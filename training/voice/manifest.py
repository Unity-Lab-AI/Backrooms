"""Hash every input of the voice training run into VOICE_MANIFEST.json; the pod refuses any other inputs.

    python training/voice/manifest.py          # write the manifest and print its digest
    python training/voice/manifest.py --check  # verify the files against the manifest, print the digest

The digest is what the owner approves at launch (VOICE_DIGEST on the pod).
"""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FILES = ["training/voice/" + f for f in ("make_dataset.py", "prep.py", "model.py", "train_acoustic.py", "vocoder.py",
         "train_vocoder.py", "infer.py", "unity-voice.pt", "pod/run_voice.sh")] + ["training/data/brain/train.jsonl"]
PATH = os.path.join(HERE, "VOICE_MANIFEST.json")


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def digest(files):
    return hashlib.sha256("".join("%s  %s\n" % (files[k], k) for k in sorted(files)).encode()).hexdigest()


if "--check" in sys.argv:
    m = json.load(open(PATH))
    bad = [rel for rel, want in m["files"].items() if sha(rel) != want]
    if bad:
        print("MISMATCH:" + ",".join(bad)); sys.exit(1)
    print(digest(m["files"]))
else:
    files = {rel: sha(rel) for rel in FILES}
    with open(PATH, "w", newline="\n") as f:                                # LF, as git stores it
        json.dump({"files": files, "digest": digest(files)}, f, indent=1)
    print(digest(files))
