import time
from abc import ABC, abstractmethod

from ahk import AHK

from edmacro import MacroController


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
