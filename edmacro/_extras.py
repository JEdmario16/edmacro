import os
import time
from typing import List, Optional, Tuple

import cv2 as cv
import numpy as np
import pywintypes
import win32api
import win32con

from edmacro import utils


def change_monitor_resolution(width: int, height: int) -> None:
    """
    Change the resolution of the monitor to the specified width and height.
    This function is only used to collect images for testing purposes.

    """

    devmode = pywintypes.DEVMODEType()  # type: ignore

    devmode.PelsWidth = width
    devmode.PelsHeight = height

    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT

    result = win32api.ChangeDisplaySettings(devmode, win32con.CDS_TEST)
    if result == win32con.DISP_CHANGE_BADMODE:
        raise ValueError(
            "Invalid resolution: The specified resolution is not supported by the monitor."
        )
    win32api.ChangeDisplaySettings(devmode, 0)


def collect_screenshots(
    output_folder: str,
    resolutions: list[tuple[int, int]],
    images_prefix: str,
    bound_areas: Optional[List[Tuple[int, int, int, int]]] = None,
    only_game_area: bool = True,
) -> None:
    """
    Collect screenshots of the specified resolutions and save them in the output folder.

    Parameters:
    - output_folder: The folder where the screenshots will be saved.
    - resolutions: A list of tuples with the width and height of the resolution.
    - images_prefix: The prefix of the images.
    - bound_areas: A list of tuples with the bound areas of the screenshots.
    - only_game_area: If True, only the game area will be captured. Otherwise, the entire screen will be captured.

    """
    game_hwnd = utils.get_roblox_window() if only_game_area else None

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for index, resolution in enumerate(resolutions):
        bound_area = (
            bound_areas.pop(0)
            if bound_areas
            else (0, 0, *utils.primary_monitor_working_area())
        )
        change_monitor_resolution(resolution[0], resolution[1])
        time.sleep(4)
        # Take a screenshot
        # Save the screenshot in the output folder
        sc = utils.screenshot(hwnd=game_hwnd, region=bound_area)

        cv.imwrite(
            f"{output_folder}/{images_prefix}_{resolution[0]}x{resolution[1]}.png", sc
        )


def test_needles_in_different_haystacks(
    needle: str,
    haystack_images_folder: str,
    save_result: bool = False,
    verbose: bool = False,
    **kwargs,
) -> float:
    """
    Test the needle image in different haystack images.
    return the mean squared error of the needle in the haystack images.
    """
    images = [
        file_name
        for file_name in os.listdir(haystack_images_folder)
        if file_name.endswith(".png")
    ]
    confidences = []
    for image in images:
        max_conf, pos = utils.locate(
            needle, f"{haystack_images_folder}/{image}", **kwargs
        )
        print(f"{image}: {max_conf} at {pos}") if verbose else None
        confidences.append(max_conf)
        if save_result:
            if not os.path.exists(f"{haystack_images_folder}/results"):
                os.makedirs(f"{haystack_images_folder}/results")
            # Draw a rectangle around the needle in the haystack image
            haystack = cv.imread(f"{haystack_images_folder}/{image}")

            cv.rectangle(
                haystack,
                (pos[0], pos[1]),
                (pos[0] + len(needle), pos[1] + len(needle)),
                (0, 255, 0),
                2,
            )

            cv.imwrite(f"{haystack_images_folder}/results/{image}_result.png", haystack)
    return ((1 - np.asarray(confidences)) ** 2).mean()
