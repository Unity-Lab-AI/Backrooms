#!/usr/bin/env bash
# The stream rig is Windows-only: it drives RimWorldWin64.exe, OBS-Portable, the Windows audio stack and
# Win32 input. This wrapper says so plainly instead of failing somewhere deep inside the scripts.
# On Windows use the matching windows/*.bat launcher.
echo "linux/restart.sh: the Unity stream rig runs on Windows only (RimWorldWin64, OBS-Portable, Win32 input/audio)." >&2
echo "Run windows/restart.bat on the Windows machine instead." >&2
exit 2
