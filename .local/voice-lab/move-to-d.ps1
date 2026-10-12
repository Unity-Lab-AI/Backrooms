# Move the big untracked voice-lab folders to the USB drive (owner: "Move voice lab to D: (Recommended)") and
# leave a directory junction at each old path so every script and tool keeps working unchanged.
$ErrorActionPreference = 'Stop'
$src = 'C:\Users\gfour\Desktop\Backrooms\.local\voice-lab'
$dst = 'D:\voice-lab'
foreach ($name in 'models', 'dataset', 'feats', 'pod-build-artifacts-2026-10-11-v2', 'auditions') {
    $from = Join-Path $src $name; $to = Join-Path $dst $name
    if ((Get-Item $from).LinkType -eq 'Junction') { "skip ${name} (already moved)"; continue }
    robocopy $from $to /E /COPY:DAT /R:2 /W:2 /NP /NFL /NDL /NJH | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed for ${name} ($LASTEXITCODE)" }
    $a = (Get-ChildItem $from -Recurse -File | Measure-Object Length -Sum)
    $b = (Get-ChildItem $to -Recurse -File | Measure-Object Length -Sum)
    if ($a.Count -ne $b.Count -or $a.Sum -ne $b.Sum) { throw "copy check failed for ${name}: $($a.Count)/$($a.Sum) vs $($b.Count)/$($b.Sum)" }
    Remove-Item $from -Recurse -Force
    cmd /c mklink /J "$from" "$to" | Out-Null
    "moved ${name}: $($b.Count) files, $([math]::Round($b.Sum/1GB,2)) GB, junction in place"
}
