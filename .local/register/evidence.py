import glob
import hashlib
import io
import json
import os
import subprocess

root = r"C:\Users\gfour\Desktop\Backrooms"
out = os.path.join(root, "docs", "implementation", "evidence", "mod-register-rebuild-2026-09-29")
os.makedirs(out, exist_ok=True)


def sha(path):
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest().upper()


def run(args, target):
    result = subprocess.run(args, cwd=root, capture_output=True, text=True,
                            env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    io.open(os.path.join(out, target), "w", encoding="utf-8").write(
        (result.stdout or "") + (result.stderr or ""))
    return result.returncode


codes = {
    "register-build.txt": run(["python", "tools/research/build-mod-register.py"], "register-build.txt"),
    "register-check.txt": run(["python", "tools/research/check-mod-register.py"], "register-check.txt"),
    "gate0-audit.json": run(["python", "tools/research/audit-gate0.py"], "gate0-audit.json"),
}

workbook = os.path.join(root, "outputs", "rimrooms-async-industries-register-2026-09-27",
                        "Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx")
document = os.path.join(root, "outputs", "rimrooms-async-industries-register-2026-09-27",
                        "Rimrooms_Async_Industries_294_Mod_Integration_Register.html")
assembly = os.path.join(root, "Mod", "Rimrooms - Async Industries", "1.6", "Assemblies",
                        "RimroomsAsyncIndustries.dll")

sources = []
for pattern in ("docs/research/rimworld-server-mod-inventory.csv",
                "docs/research/mod-register-integration-fields-2026-09-29.csv",
                "docs/research/mod-register-overview-2026-09-29.csv",
                "tools/research/build-mod-register.py",
                "tools/research/check-mod-register.py"):
    path = os.path.join(root, pattern.replace("/", os.sep))
    sources.append({"path": pattern, "bytes": os.path.getsize(path), "sha256": sha(path)})

manifest = {
    "note": "Register rebuild checkpoint. No C# source changed and no version was bumped; the "
            "assembly hash below is identical to the one recorded for 0.6.4-dev, which is the "
            "point. Compilation and structural verification establish consistency only; no game, "
            "test or runtime compatibility result is claimed.",
    "modVersion": "0.6.4-dev",
    "assemblySha256": sha(assembly),
    "assemblyUnchangedFrom": "0.6.4-dev (4057EFD15AAB4B1C609732AB18A02F025C9A98A8D951374CE7333A80C9780728)",
    "cleanRebuild": "obj/ and bin/ deleted before the build recorded in build-output.txt",
    "workbook": {
        "path": "outputs/rimrooms-async-industries-register-2026-09-27/"
                "Rimrooms_Async_Industries_294_Mod_Integration_Register.xlsx",
        "bytes": os.path.getsize(workbook),
        "sha256": sha(workbook),
        "deterministic": "two consecutive builds of an unchanged source give this same hash",
        "sheets": ["Overview", "Index", "Mod Register", "Mod Cards"],
        "modRows": 294,
        "registerColumns": 17,
    },
    "htmlRegister": {
        "path": "outputs/rimrooms-async-industries-register-2026-09-27/"
                "Rimrooms_Async_Industries_294_Mod_Integration_Register.html",
        "bytes": os.path.getsize(document),
        "sha256": sha(document),
        "why": "There is no spreadsheet application on this machine and no .xlsx association "
               "at all, so this is the register that actually gets read. Browser only, no "
               "install, no external asset, works offline.",
        "views": ["Overview", "Index", "Full register", "Mod cards"],
        "search": "live across all 17 columns of every row; stance, firmness and family filters",
    },
    "toolExitCodes": codes,
    "sources": sources,
}
io.open(os.path.join(out, "register-manifest.json"), "w", encoding="utf-8").write(
    json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"exitCodes": codes,
                  "htmlSha256": manifest["htmlRegister"]["sha256"],
                  "workbookSha256": manifest["workbook"]["sha256"],
                  "assemblySha256": manifest["assemblySha256"]}, indent=2))
