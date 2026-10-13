"""Run skill-creator's run_eval.py unchanged, on any OS.

Usage: run_eval_compat.py <skill-creator-dir> <run_eval.py arguments...>

run_eval.py waits on select.select() over a subprocess pipe. Windows' select() accepts sockets
only, so every query raises, is recorded as "not triggered", and a skill that fires normally
scores as if it never does — while its negatives still pass. On Windows this swaps in a
PeekNamedPipe-based select(); elsewhere it changes nothing. The patch sits at module top level
because ProcessPoolExecutor's spawned workers re-import this file, not run_eval's caller.

Run it with PYTHONUTF8=1: run_eval.py also reads and writes text without an encoding.
"""
import os
import select
import sys
import time

if len(sys.argv) > 1 and "SKILL_CREATOR_DIR" not in os.environ:
    os.environ["SKILL_CREATOR_DIR"] = sys.argv[1]
if os.environ.get("SKILL_CREATOR_DIR"):
    sys.path.insert(0, os.environ["SKILL_CREATOR_DIR"])

if os.name == "nt":
    import ctypes
    import msvcrt
    from ctypes import wintypes

    _peek = ctypes.windll.kernel32.PeekNamedPipe
    _peek.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p,
                      ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
    _peek.restype = wintypes.BOOL

    def _select(rlist, wlist, xlist, timeout=None):
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            ready = []
            for f in rlist:
                avail = wintypes.DWORD(0)
                # A failed peek means the writer closed the pipe: report it readable so the
                # caller's os.read() returns b"" and sees EOF.
                if not _peek(msvcrt.get_osfhandle(f.fileno()), None, 0, None, ctypes.byref(avail), None) \
                        or avail.value:
                    ready.append(f)
            if ready or (deadline is not None and time.monotonic() >= deadline):
                return ready, [], []
            time.sleep(0.05)

    select.select = _select

if __name__ == "__main__":
    from scripts import run_eval

    sys.argv = ["run_eval.py", *sys.argv[2:]]
    run_eval.main()
