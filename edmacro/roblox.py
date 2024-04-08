import time
from typing import List, Optional

import win32con
import win32gui


def get_roblox_window() -> Optional[int]:
    """
    Returns the window handle of the Roblox window. If no window is found, it will return None.
    """

    def callback(hwnd: int, windows: List[int | None]) -> bool:
        if win32gui.GetWindowText(hwnd) == "Roblox":
            windows.append(hwnd)
        return True

    windows: List[Optional[int]] = []
    win32gui.EnumWindows(callback, windows)
    return windows[0] if windows else None


def get_roblox_window_pos(hwnd: Optional[int] = None) -> tuple[int, int, int, int]:
    """
    Returns the position of the Roblox window in the format (left, top, right, bottom),
    If no window is found, it will return (0, 0, 0, 0).

    :param hwnd: The window handle of the Roblox window. If None, it will be found automatically.
    :return: The position of the Roblox window.
    """
    if not hwnd:
        hwnd = get_roblox_window()
    if hwnd:
        return win32gui.GetWindowRect(hwnd)
    return 0, 0, 0, 0


def activate_roblox(hwnd: Optional[int] = None) -> bool:
    """
    Activates the Roblox window by bringing it to the front. You can pass
    a hwnd to dont call get_roblox_window() every time.

    :param hwnd: The window handle of the Roblox window.
    :return: True if the window was activated, False otherwise.
    """
    # if the window is showing but not active, win32gui.SetForegroundWindow(hwnd) will not work
    # so let's minimize and maximize the window to make it active
    hwnd = hwnd or get_roblox_window()
    if not hwnd:
        return False

    if win32gui.IsWindowVisible(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        time.sleep(0.1)
    # we will take advantage that we are activating the window to maximize it
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    time.sleep(0.1)
    return True


def get_window_center(hwnd: Optional[int] = None) -> tuple[int, int]:
    """
    Returns the center of the window.

    :param hwnd: The window handle of the window.
    :return: The center of the window.
    """
    left, top, right, bottom = get_roblox_window_pos(hwnd)
    return (left + right) // 2, (top + bottom) // 2
