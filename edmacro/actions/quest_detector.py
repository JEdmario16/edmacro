import time
from typing import Literal, Tuple, TypeAlias, Union

import cv2
import numpy as np

from edmacro import actions, utils

import re

targetTask: TypeAlias = Union[
    Literal["crab_beard"], Literal["bruh_bounty"], Literal["sailors_request"]
]


class QuestDetector(actions.Action):

    __export__name__ = "quest_detector"

    QUEST_DETECTOR_SPOT_MAP = (7, -1)

    def go_to_detector_spot(self):

        if self.QUEST_DETECTOR_SPOT_MAP != self.macro_controller.current_map:
            self.macro_controller.logger.debug("Going to detector spot's map")
            self.move_to_map(*self.QUEST_DETECTOR_SPOT_MAP)
        else:
            self.macro_controller.logger.debug(
                "Char is in the correct map. Going to detector spot"
            )

        self.reset_if_needed()
        time.sleep(0.3)

        self._ahk.key_down("w")
        time.sleep(1.0)
        self._ahk.key_up("w")
        time.sleep(0.3)
        self._ahk.key_down("d")
        time.sleep(2)
        self._ahk.key_up("d")
        time.sleep(0.3)
        self._ahk.key_down("w")
        time.sleep(2)
        self._ahk.key_up("w")

        self.macro_controller.logger.debug("Arrived at detector spot")

    def zoom_perspective_to_quest_detector(self):
        self._ahk.key_down("i")
        time.sleep(0.5)
        self._ahk.key_up("i")
        self.macro_controller.needs_restart_perspective = True
        self.macro_controller.logger.debug("Zoomed perspective to quest detector")

    def detect_quest_header(
        self, target_task: targetTask
    ) -> tuple[np.ndarray, Tuple[int, int, int, int]]:
        w, h = self.macro_controller.user_resolution

        # These bounds are founded manually, taking screenshots and testing
        # you can se this results in tests/quest_detector_bounds
        x_start = 8 * (w // 10) - 10
        y_start = int(h * 0.2)

        bound_region = utils.Rect(
            x_start,
            y_start,
            w - x_start,
            int(h * 0.75),
        )

        if not self.macro_controller.roblox_hwnd:
            self.macro_controller.roblox_hwnd = utils.get_roblox_window()
            assert (
                self.macro_controller.roblox_hwnd is not None
            ), "Roblox window not found"
        region = utils.screenshot(
            region=bound_region, hwnd=self.macro_controller.roblox_hwnd
        )

        # detect the quest title
        needle = self.macro_controller.assets[target_task + "_header"]

        conf, result_pos = utils.locate(
            needle=needle,
            haystack=region,
            bound=(0, 0, region.shape[0], region.shape[0]),
        )
        self.macro_controller.logger.debug(
            f"Locate {target_task} header with Confidence: {conf}, Result Pos: {result_pos}"
        )

        width, height = needle.shape[1], needle.shape[0]

        # save the region
        cv2.imwrite("quest_header.png", region)
        return (
            region,
            (result_pos[0], result_pos[1], width, height),
        )  # (cutted region, (x, y, width, height))

    def detect_quest(self, target_task: targetTask = "crab_beard") -> str:
        """
        This method will detect the crab beard quest header
        The idea here is detect where is the quest header(or title) in the screen
        and crop the image using the header position as reference to get only the first task.
        Since completed tasks are moved to the end of the list, we can always get the first task
        Note that before detect crab beard, we do another crop to get the quests section only
        This is because the header detection peform image matching, wich could give false positives.
        Finally, sometimes the OCR give us artifacts, so we need to clean the text.
        """

        region, detected_header_pos = self.detect_quest_header(target_task)
        # lets do another crop, with only the first task
        # this crop uses all the width and 25 pixels of height
        y_top = (
            detected_header_pos[1] + detected_header_pos[3] - 5
        )  # start from the bottom of the header. 10 for safety
        width = region.shape[1]

        # the height depends on the screen resolution, but we can use 25 pixels
        height = 15 if self.macro_controller.user_resolution[1] <= 768 else 25

        region = region[
            y_top : y_top + height, 0 : width - 20
        ]  # 20 to remove the scrollbar
        cv2.imwrite("quest_text.png", region)
        # get the text
        text = utils.extract_text_from_image(region, config="--oem 3 --psm 6")

        # clean the text
        text = text.lower().replace("\n", " ")
        self.macro_controller.logger.info(f"Quest text: {text}")

        return text

    def execute(self, target_task: targetTask = "crab_beard") -> str:
        self.macro_controller.logger.info("Starting Quest Detector Action.")
        self.go_to_detector_spot()
        self.zoom_perspective_to_quest_detector()
        quest_text = self.detect_quest(target_task)
        self.macro_controller.logger.info("Quest Detector Action Finished.")

        REGEX_EXPR = r"[^a-zA-Z0-9|\s{1,}]"
        quest_text = re.sub(REGEX_EXPR, "", quest_text)
        return quest_text
