"""Best-effort keyboard lock-state detection."""

import sys


VK_CAPITAL = 0x14


def caps_lock_enabled():
    """Return Caps Lock state where the operating system exposes it."""
    if sys.platform != "win32":
        return False

    try:
        import ctypes

        return bool(ctypes.windll.user32.GetKeyState(VK_CAPITAL) & 1)
    except (AttributeError, OSError):
        return False
