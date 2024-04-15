import os

import cv2
import numpy as np
from ahk import AHK
from ahk._sync.engine import CoordModeTargets
from loguru import logger

from edmacro import config, utils

from edmacro.actions import Action

import importlib
import inspect


class MacroController:
    def __init__(self) -> None:
        self.ahk = AHK()

        # setup ahk
        targets: list[CoordModeTargets] = ["ToolTip", "Pixel", "Mouse"]
        for target in targets:
            self.ahk.set_coord_mode(target=target, relative_to="Window")

        self.ahk.set_send_mode("Event")

        # load config
        self.configs = config.get_config()

        # setup logger
        self.logger = logger
        logger.debug("Config loaded")

        # setup logger
        log_level = self.configs.get("OTHERS", "LOG_LEVEL", fallback="DEBUG")
        logger.add(
            "edmacro.log",
            rotation="1 week",
            retention="1 month",
            level=log_level.upper(),
        )
        logger.info("MacroController initialized")

        self.__load_assets()
        logger.info("Assets loaded")

        # global attributes
        # They are useful for the actions to know the current state of the game

        self.roblox_hwnd = utils.get_roblox_window()

        self.win_dimensions = utils.get_roblox_window_pos(self.roblox_hwnd)
        self.user_resolution = utils.get_user_resolution()

        # State variables
        self.current_map_index: int | None = None
        self.current_map_col: int | None = None
        self.needs_restart_perspective: bool = (
            False  # Used when some action change the perspective to unknown state
        )

    def __load_assets(self) -> None:
        self.assets: dict[str, np.ndarray] = {}
        for asset in os.listdir("assets"):
            self.assets[asset.split(".")[0]] = cv2.imread(
                f"assets/{asset}", cv2.IMREAD_COLOR
            )

        logger.debug(f"Loaded {len(self.assets)} assets.")

    def register_actions(self):
        actions = config.INSTALLED_ACTIONS
        for action in actions:
            module = importlib.import_module(action)
            for name, obj in inspect.getmembers(module):
                if issubclass(obj, Action) and obj != Action:
                    self.logger.debug(f"Registering action {obj}")
                    obj(self)
