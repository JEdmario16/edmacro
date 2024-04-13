import time
from typing import List, Optional, Sequence

import cv2 as cv
import numpy as np
import win32con
import win32gui
import win32ui


def get_roblox_window() -> Optional[int]:
    """
    Return the window handle (HWND) of the Roblox window.

    This function searches for the window with the title "Roblox" and returns its window handle (HWND).
    If no such window is found, the function returns None.

    Returns:
        Optional[int]: The window handle (HWND) of the Roblox window, if found, or None if no window is found.

    Example:
        # Get the window handle of the Roblox window
        hwnd = get_roblox_window()
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
    Return the position of the Roblox window in screen coordinates.

    This function retrieves the position of the Roblox window specified by its handle (HWND)
    or, if no handle is provided, it automatically finds the Roblox window. The position is
    returned in the format (left, top, right, bottom), representing the coordinates of the
    top-left and bottom-right corners of the window's bounding box.

    Parameters:
        hwnd (Optional[int]): The window handle (HWND) of the Roblox window for which to retrieve the position.
            If not provided (default None), the function will attempt to find the window automatically.

    Returns:
        tuple[int, int, int, int]: A tuple containing the position of the Roblox window.
            The position is returned in the format (left, top, right, bottom), where:
            - left: The X-coordinate of the left edge of the window.
            - top: The Y-coordinate of the top edge of the window.
            - right: The X-coordinate of the right edge of the window.
            - bottom: The Y-coordinate of the bottom edge of the window.

    Note:
        If no window handle (HWND) is provided and the Roblox window cannot be found automatically,
        the function will return the position (0, 0, 0, 0).

    Example:
        # Get the position of the Roblox window
        window_pos = get_roblox_window_pos()
    """

    if not hwnd:
        hwnd = get_roblox_window()
    if hwnd:
        return win32gui.GetWindowRect(hwnd)
    return 0, 0, 0, 0


def activate_roblox(hwnd: Optional[int] = None) -> bool:
    """
    Activate the Roblox window by bringing it to the front and ensuring it is visible.

    This function activates the Roblox window specified by its handle (HWND) by bringing it to the front
    and ensuring it is visible. If no window handle is provided, the function retrieves the handle using
    the `get_roblox_window` function. Before activating the window, the function minimizes and then maximizes
    it to ensure it becomes active.

    Parameters:
        hwnd (Optional[int]): The window handle (HWND) of the Roblox window to activate.
            If not provided (default None), the function will attempt to retrieve the handle using `get_roblox_window`.

    Returns:
        bool: True if the Roblox window was successfully activated, False otherwise.

    Note:
        This function may fail to activate the window if it is not visible or if the window handle cannot be retrieved.

    Example:
        # Activate the Roblox window
        success = activate_roblox()
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
    Return the coordinates of the center point of the specified window.

    This function calculates the center point of the window specified by its handle (HWND)
    or, if no handle is provided, it calculates the center point of the primary screen.

    Parameters:
        hwnd (Optional[int]): The window handle (HWND) of the window for which to calculate the center point.
            If not provided (default None), the center point of the primary screen will be calculated.

    Returns:
        tuple[int, int]: A tuple containing the X and Y coordinates of the center point of the window.
            The coordinates are returned in the format (x_center, y_center).

    Example:
        # Calculate the center point of a window with handle 'hwnd'
        window_center = get_window_center(hwnd)

    Note:
        If no window handle (HWND) is provided, this function calculates the center point of the primary screen.
    """

    left, top, right, bottom = get_roblox_window_pos(hwnd)
    return (left + right) // 2, (top + bottom) // 2


def screenshot(region: tuple[int, int, int, int], hwnd: int) -> np.ndarray:
    """
    Take a screenshot of a specified region from the given window.

    This function provides a faster alternative to `pyautogui.screenshot` by directly capturing
    the specified region from the window identified by its handle (HWND).

    Parameters:
        region (tuple[int, int, int, int]): A tuple representing the coordinates of the region to capture.
            It should be in the format (x_top, y_top, width, height), where:
            - x_top: The X-coordinate of the top-left corner of the region.
            - y_top: The Y-coordinate of the top-left corner of the region.
            - width: The width of the region.
            - height: The height of the region.
        hwnd (int): The window handle (HWND) of the desired window from which to capture the screenshot.

    Returns:
        np.ndarray: A NumPy array representing the captured screenshot, with shape (height, width, 3).
            The array contains pixel values in the RGB format.

    Note:
        This function uses Windows API calls to capture the screenshot, which may be more efficient
        than `pyautogui.screenshot`, especially for capturing specific regions of a window.

    Example:
        # Capture a region of the window with handle 'hwnd' starting at coordinates (100, 100)
        # with width 200 pixels and height 150 pixels
        screenshot_region = screenshot((100, 100, 200, 150), hwnd)
    """
    x, y, w, h = region

    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0, 0), (w, h), dcObj, (x, y), win32con.SRCCOPY)

    buffer = dataBitMap.GetBitmapBits(True)
    img_np = np.frombuffer(buffer, dtype=int).reshape(h, w)

    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())
    del buffer

    return img_np


def locate(
    needle: str, haystack: str, bound: tuple[int, int, int, int]
) -> tuple[float, Sequence[int]]:
    """
    Locate a image within another image and return the match score and location.
    This function uses the Template Matching method to locate the needle image within the haystack image.
    The match score and location of the best match are returned.
    It is slower than the `locate_fast` function but more accurate.

    Parameters:
        needle (str): The path to the needle image to search for.
        haystack (str): The path to the haystack image in which to search for the needle.
        bound (tuple[int, int, int, int]): A tuple representing the bounding box of the region to search within.
            It should be in the format (x_start, y_start, width, height), where:
            - x_start: The X-coordinate of the top-left corner of the bounding box.
            - y_start: The Y-coordinate of the top-left corner of the bounding box.
            - width: The width of the bounding box.
            - height: The height of the bounding box.

    Returns:
        tuple[float, Sequence[int]]: A tuple containing the match score and location of the best match.
            The match score is a float value indicating the similarity between the needle and the haystack.
            The location is a tuple (x, y) representing the coordinates of the top-left corner of the match.
    """
    needle_img = cv.imread(needle)
    haystack_img = cv.imread(haystack)

    if bound:
        x_start, y_start, width, height = bound
        haystack_img = haystack_img[
            y_start : y_start + height, x_start : x_start + width
        ]

    result = cv.matchTemplate(haystack_img, needle_img, cv.TM_CCOEFF_NORMED)
    _, max_val, __, max_loc = cv.minMaxLoc(result)

    return max_val, max_loc


def locate_from_buffer(
    needle: np.ndarray, haystack: np.ndarray, bound: tuple[int, int, int, int]
) -> tuple[float, Sequence[int]]:
    """
    Locate a image within another image and return the match score and location.
    This function uses the Template Matching method to locate the needle image within the haystack image.
    The match score and location of the best match are returned.
    It is slower than the `locate_fast` function but more accurate.

    Parameters:
        needle (np.ndarray): The needle image to search for, represented as a NumPy array.
        haystack (np.ndarray): The haystack image in which to search for the needle, represented as a NumPy array.
        bound (tuple[int, int, int, int]): A tuple representing the bounding box of the region to search within.
            It should be in the format (x_start, y_start, width, height), where:
            - x_start: The X-coordinate of the top-left corner of the bounding box.
            - y_start: The Y-coordinate of the top-left corner of the bounding box.
            - width: The width of the bounding box.
            - height: The height of the bounding box.

    Returns:
        tuple[float, Sequence[int]]: A tuple containing the match score and location of the best match.
            The match score is a float value indicating the similarity between the needle and the haystack.
            The location is a tuple (x, y) representing the coordinates of the top-left corner of the match.
    """
    needle_img = needle
    haystack_img = haystack

    if bound:
        x_start, y_start, width, height = bound
        haystack_img = haystack_img[
            y_start : y_start + height, x_start : x_start + width
        ]

    result = cv.matchTemplate(haystack_img, needle_img, cv.TM_CCOEFF_NORMED)
    _, max_val, __, max_loc = cv.minMaxLoc(result)

    return max_val, max_loc
