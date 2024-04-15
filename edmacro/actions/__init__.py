from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Literal, TypeAlias, Union, TYPE_CHECKING

from ahk import AHK

from edmacro import utils

if TYPE_CHECKING:
    from edmacro import MacroController


mapButtonDirection: TypeAlias = Union[
    Literal["map_up"], Literal["map_down"], Literal["map_left"], Literal["map_right"]
]


class Action(ABC):

    def __init__(self, macro_controller: MacroController):
        self.macro_controller = macro_controller
        self._ahk = self.macro_controller.ahk

    @abstractmethod
    def execute(self):
        pass

    def restart_char(self):
        """
        Restart the character by pressing `esc`, `r`, and `enter`.
        We are resetting the camera by default.
        """

        self.macro_controller.logger.info("Restarting character")
        self.macro_controller.do_something_that_not_exists = True
        self._ahk.key_press("esc")
        time.sleep(0.3)
        self._ahk.key_press("r")
        time.sleep(0.3)
        self._ahk.key_press("enter")
        time.sleep(2)

        self.reset_camera()

    def reset_camera(self) -> None:
        """
        Drag mouse to the center of the screen to set camera perspective in top-down view.
        Then, spam  `o` to zoom out the camera to the max, and finally type `i` to zoom in a bit. (Avoids the camera flickering bug)
        """
        x_start, y_start, x_end, y_end = self.macro_controller.win_dimensions
        center = ((x_end - x_start) // 2, (y_end - y_start) // 2)

        self._ahk.mouse_move(*center)
        time.sleep(0.3)
        self._ahk.mouse_drag(
            center[0],
            center[1] + 30,
            from_position=(center[0], center[1] - 100),
            speed=10,
            button="right",
            relative=False,
        )

        self._ahk.key_down("o")
        time.sleep(0.5)
        self._ahk.key_up("o")
        self._ahk.key_press("i")
        time.sleep(0.1)
        self._ahk.key_press("i")

        return None

    # Moving through the maps
    def go_to_map(self, map_index: int, map_column: int) -> None:
        current_map_index = self.macro_controller.current_map_index
        current_map_col = self.macro_controller.current_map_col

        if current_map_index == None or current_map_col == None:
            # Then current map is unknown, so lets force move map to the first one
            pass

    def open_map(self) -> None:
        # reset the char
        self.restart_char()
        time.sleep(1)
        # then press e
        # it works because the player always respwan in teleporter from current map
        self._ahk.key_press("e")
        time.sleep(5)
        self.macro_controller.logger.info("Opened map")

    def zoom_in_camera(self):
        # first, max zoom out
        self._ahk.key_down("o")
        time.sleep(1)
        self._ahk.key_up("o")
        time.sleep(0.3)
        self._ahk.key_down("i")
        time.sleep(0.3)
        self._ahk.key_up("i")
        self.macro_controller.logger.info("Zoomed in camera")
        self.macro_controller.needs_restart_perspective = True

    def brute_force_back_to_map_zero(self):

        self.macro_controller.logger.info("Brute forcing back to map zero")
        assert (
            self.macro_controller.current_map_index is None
        ), "Only use this method when the current map is unknown"

        # open map
        self.open_map()

        # we have two possible scenarios here:
        # first: we are in a map in column 0, then we can spam map_down until we reach the first map
        # second: we are in a map in column 1, then press map_left one time, and then spam map_down until we reach the first map
        # third: we are in a map in column 2, then press map_right two times, and then spam map_down until we reach the first map
        # we can brute force all cenarios, because if we are in a map in column 0, then map_left will do nothing, and the same for map_right
        # and if we are in a map in column 2, then map_right will do nothing, and the same for map_left
        # lets get the map buttons
        bound = 0, 0, *self.macro_controller.user_resolution
        map_left = self.macro_controller.assets["map_left"]
        map_right = self.macro_controller.assets["map_right"]
        map_down = self.macro_controller.assets["map_down"]

        # lets spam map_down until we reach the first map
        needle = map_down
        haystack = utils.screenshot(
            hwnd=self.macro_controller.roblox_hwnd, region=bound
        )
        _, pos = utils.locate_from_buffer(needle, haystack, bound=bound)
        for __ in range(10):
            self._ahk.click(pos[0], pos[1])
            time.sleep(0.3)

        # do the same for the other scenarios
        needle = map_left
        haystack = utils.screenshot(
            hwnd=self.macro_controller.roblox_hwnd, region=bound
        )
        _, pos = utils.locate_from_buffer(needle, haystack, bound=bound)
        self._ahk.click(pos[0], pos[1])
        time.sleep(0.3)

        # then spam map_down
        needle = map_down
        haystack = utils.screenshot(
            hwnd=self.macro_controller.roblox_hwnd, region=bound
        )
        _, pos = utils.locate_from_buffer(needle, haystack, bound=bound)
        for __ in range(10):
            self._ahk.click(pos[0], pos[1])
            time.sleep(0.3)

        # finally for the last scenario
        needle = map_right
        haystack = utils.screenshot(
            hwnd=self.macro_controller.roblox_hwnd, region=bound
        )
        _, pos = utils.locate_from_buffer(needle, haystack, bound=bound)
        self._ahk.click(pos[0], pos[1])
        time.sleep(0.3)

        # then spam map_down
        needle = map_down
        haystack = utils.screenshot(
            hwnd=self.macro_controller.roblox_hwnd, region=bound
        )
        _, pos = utils.locate_from_buffer(needle, haystack, bound=bound)
        for __ in range(10):
            self._ahk.click(pos[0], pos[1])
            time.sleep(0.3)

        self.macro_controller.current_map_col = 0
        self.macro_controller.current_map_index = 0
        self.macro_controller.logger.info("Brute forced back to map zero")

    def resolve_map_path(
        self, _from: tuple[int, int], to: tuple[int, int]
    ) -> list[tuple[mapButtonDirection, int]]:
        """
        Resolve the path from the map _from to the map _to.
        """
        # notice that the order matters, because we need to move first in the vertical direction
        path: list[tuple[mapButtonDirection, int]] = []
        horizontal_dist = to[1] - _from[1]
        vertical_dist = to[0] - _from[0]

        # if we are in column 0, then we need to move in vertical direction first
        if _from[1] == 0:
            if vertical_dist > 0:
                path.extend([("map_up", vertical_dist)])
            elif vertical_dist < 0:
                path.extend([("map_down", abs(vertical_dist))])

            if horizontal_dist > 0:
                path.extend([("map_right", horizontal_dist)])
            elif horizontal_dist < 0:
                path.extend([("map_left", abs(horizontal_dist))])
        # else we need to move in horizontal direction first
        else:
            if horizontal_dist > 0:
                path.extend([("map_right", horizontal_dist)])
            elif horizontal_dist < 0:
                path.extend([("map_left", abs(horizontal_dist))])

            if vertical_dist > 0:
                path.extend([("map_up", vertical_dist)])
            elif vertical_dist < 0:
                path.extend([("map_down", abs(vertical_dist))])
        return path

    def move_to_map(self, map_index: int, map_column: int):
        if self.macro_controller.current_map_index is None:
            self.brute_force_back_to_map_zero()
            self.macro_controller.logger.warning(
                f"Warning! Current map is unknown. Brute forced back to map zero"
            )

        bound = 0, 0, *self.macro_controller.user_resolution
        path = self.resolve_map_path(
            _from=(
                self.macro_controller.current_map_index,
                self.macro_controller.current_map_col,
            ),  # type: ignore # noqa cause we forced the current map to be not None
            to=(map_index, map_column),
        )
        self.macro_controller.logger.info(
            f"({self.macro_controller.current_map_index}, {self.macro_controller.current_map_col}) -> ({map_index}, {map_column}): {path}"
        )
        haystack = utils.screenshot(
            hwnd=self.macro_controller.roblox_hwnd, region=bound
        )  # we only need to take the screenshot once
        for direction, times in path:
            needle = self.macro_controller.assets[direction]
            _, pos = utils.locate_from_buffer(needle, haystack, bound=bound)
            for __ in range(times):
                self._ahk.click(pos[0], pos[1])
                time.sleep(0.3)
                self.macro_controller.current_map_index = map_index
                self.macro_controller.current_map_col = map_column

        self.macro_controller.logger.info(
            f"Moved to map {map_index} column {map_column}"
        )

        # then press the teleport button
        needle = self.macro_controller.assets["teleport_button"]
        haystack = utils.screenshot(
            hwnd=self.macro_controller.roblox_hwnd, region=bound
        )
        _, pos = utils.locate_from_buffer(needle, haystack, bound=bound)
        self._ahk.click(pos[0], pos[1])
        time.sleep(1)
        # then reset the char. We need this because the camera perspective changes
        # when we teleport
        self.restart_char()

    def reset_if_needed(self):
        if self.macro_controller.needs_restart_perspective:
            self.reset_camera()
            self.macro_controller.needs_restart_perspective = False
            self.macro_controller.logger.info("Reset camera perspective")
        return None
