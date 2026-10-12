"""Atomic no-replace publication for owned sibling directories.

Windows rename already refuses an existing target; Linux requires renameat2 with
RENAME_NOREPLACE. Unsupported kernels/filesystems fail rather than weaken safety.
This helper never deletes or cleans up interrupted temporary directories.
"""
import ctypes
import errno
import os
import sys
from pathlib import Path


def publish_directory(source, destination):
    source, destination = Path(source), Path(destination)
    if not source.is_dir() or source.is_symlink() or source.parent.resolve() != destination.parent.resolve():
        raise ValueError("Publication requires an owned directory and sibling destination")
    if sys.platform == "win32":
        os.rename(source, destination)
        return
    if sys.platform != "linux":
        raise OSError(errno.ENOTSUP, "No verified no-replace primitive on this platform")
    libc = ctypes.CDLL(None, use_errno=True)
    try:
        rename = libc.renameat2
    except AttributeError:
        raise OSError(errno.ENOSYS, "renameat2 unavailable; temporary preserved") from None
    rename.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
    rename.restype = ctypes.c_int
    if rename(-100, os.fsencode(source), -100, os.fsencode(destination), 1) != 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), str(destination))
