from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Literal, TypeAlias, Union, Optional

from edmacro import utils

import numpy as np

if TYPE_CHECKING:
    from edmacro import MacroController


mapButtonDirection: TypeAlias = Union[
    Literal["map_up"], Literal["map_down"], Literal["map_left"], Literal["map_right"]
]


class Action(ABC):

    REQUIRED_ACTIONS: list[str] = []

    def __init__(self, macro_controller: MacroController):
        self.macro_controller = macro_controller
        self._ahk = self.macro_controller.ahk

    @property
    def __export__name__(self):
        """
        Name of the action. This is used to export the action to the macro controller.
        Then you can access the action by mc.actions.<name>
        """
        return self.__class__.__name__

    @abstractmethod
    def execute(self):
        pass

    def on_register(self):
        """
        This method is called when the action is registered in the macro controller.
        This is important because actions may need other actions as dependencies.
        """
        pass

    def restart_char(self):
        """
        Restart the character by pressing `esc`, `r`, and `enter`.
        We are resetting the camera by default.
        """

        self.macro_controller.logger.info("Restarting character")
        self._ahk.key_press("esc")
        time.sleep(0.3)
        self._ahk.key_press("r")
        time.sleep(0.3)
        self._ahk.key_press("enter")
        time.sleep(2)

        if not self.detect_if_in_telerporter():
            if not self.current_map_is_known():
                raise RuntimeError("The player wasnt respawned in the teleporter and we dont know wich map he is. Aborting.")
            self.macro_controller.logger.debug(
                "The player wasnt respawned in the teleporter. Lets open the map and teleport him to same place."
            )
            self.move_to_map(*self.macro_controller.current_map)
        self.reset_camera()

    def reset_camera(self) -> None:
        """
        Drag mouse to the center of the screen to set camera perspective in top-down view.
        Then, spam  `o` to zoom out the camera to the max, and finally type `i` to zoom in a bit.
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


    def open_map(self) -> None:

        has_map_keybind = self.macro_controller.configs.getboolean(
            "PLAYER_STATS", "HAS_MAP_KEYBIND", fallback=False
        )

        # KNOWN ISSUE: The player respawn is set to the nearest spawnpoint in each map
        # if the player is in the beginning of the map, then the respawn will be set to the beginning
        # If the player is in nearest to the teleport, then the respawn will be set to the teleport
        # The major problem occurs when the player between two maps, so the game dont know where to respawn
        # and throws the player to Pet Park.
        # Dont worth fix this, because the player can just buy MAP_KEYBIND and the problem is solved
        # But doesnt worth remove this functionlaity, because there is some actions that dont will have this issue.
        if not has_map_keybind:
            # reset the char
            self.restart_char()
            time.sleep(1)
            self._ahk.key_press("e")
            time.sleep(5)
            self.macro_controller.logger.info("Opened map")
            return
        self._ahk.key_press("g")
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

        bound = 0, 0, *self.macro_controller.user_resolution
        map_left = self.macro_controller.assets["map_left"]
        map_right = self.macro_controller.assets["map_right"]
        map_down = self.macro_controller.assets["map_down"]

        # lets spam map_down until we reach the first map
        needle = map_down
        haystack = utils.screenshot(hwnd=self.macro_controller.roblox_hwnd, region=bound)
        _, pos = utils.locate(needle, haystack, bound=bound)
        for __ in range(10):
            self._ahk.click(pos.left, pos.top)
            time.sleep(0.3)

        # do the same for the other scenarios
        needle = map_left
        haystack = utils.screenshot(hwnd=self.macro_controller.roblox_hwnd, region=bound)
        _, pos = utils.locate(needle, haystack, bound=bound)
        self._ahk.click(pos[0], pos[1])
        time.sleep(0.3)

        # then spam map_down
        needle = map_down
        haystack = utils.screenshot(hwnd=self.macro_controller.roblox_hwnd, region=bound)
        _, pos = utils.locate(needle, haystack, bound=bound)
        for __ in range(10):
            self._ahk.click(pos[0], pos[1])
            time.sleep(0.3)

        # finally for the last scenario
        needle = map_right
        haystack = utils.screenshot(hwnd=self.macro_controller.roblox_hwnd, region=bound)
        _, pos = utils.locate(needle, haystack, bound=bound)
        self._ahk.click(pos[0], pos[1])
        time.sleep(0.3)

        # then spam map_down
        needle = map_down
        haystack = utils.screenshot(hwnd=self.macro_controller.roblox_hwnd, region=bound)
        _, pos = utils.locate(needle, haystack, bound=bound)
        for __ in range(10):
            self._ahk.click(pos[0], pos[1])
            time.sleep(0.3)

        self.macro_controller.current_map = (0, 0)
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
        self.open_map()
        if None in self.macro_controller.current_map:
            self.macro_controller.logger.warning(
                "Warning! Current map is unknown. Brute forced back to map zero"
            )
            self.brute_force_back_to_map_zero()

        bound = utils.Rect(0, 0, *self.macro_controller.user_resolution)
        path = self.resolve_map_path(
            _from=self.macro_controller.current_map,  # type: ignore
            to=(map_index, map_column),
        )
        self.macro_controller.logger.info(
            f"({self.macro_controller.current_map[0]}, {self.macro_controller.current_map[1]}) -> ({map_index}, {map_column}): {path}"
        )
        haystack = utils.screenshot(
            hwnd=self.macro_controller.roblox_hwnd, region=bound
        )  # we only need to take the screenshot once
        for direction, times in path:
            needle = self.macro_controller.assets[direction]
            _, pos = utils.locate(needle, haystack, bound=bound)
            for __ in range(times):
                self._ahk.click(pos.left, pos.top)
                time.sleep(0.3)
                self.macro_controller.current_map = (map_index, map_column)

        self.macro_controller.logger.info(f"Moved to map {map_index} column {map_column}")

        # then press the teleport button
        needle = self.macro_controller.assets["teleport_button"]
        haystack = utils.screenshot(hwnd=self.macro_controller.roblox_hwnd, region=bound)
        _, pos = utils.locate(needle, haystack, bound=bound)
        self._ahk.click(pos.left, pos.top)
        time.sleep(1.5)
        # then reset the char. We need this because the camera perspective changes
        # when we teleport
        self.restart_char()

    def detect_if_in_telerporter(
        self, threshold: float = 0.9, sc: Optional[np.ndarray] = None
    ) -> bool:
        """
        Check if the player is near to the teleporter, by looking for the "press e" button.
        This is particularly useful because some maps doesnt respawn the player in the same place
        """
        if not sc:
            sc = utils.screenshot(
                hwnd=self.macro_controller.roblox_hwnd,
                region=(0, 0, *self.macro_controller.user_resolution),
            )

        needle = self.macro_controller.assets["teleporter_detector"]
        conf, _ = utils.locate(needle, sc)
        return conf > threshold

    def reset_if_needed(self):
        if self.macro_controller.needs_restart_perspective:
            self.reset_camera()
            self.macro_controller.needs_restart_perspective = False
            self.macro_controller.logger.info("Reset camera perspective")
        return None

    def current_map_is_known(self) -> bool:
        return None not in self.macro_controller.current_map
