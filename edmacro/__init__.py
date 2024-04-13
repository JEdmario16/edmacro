from ahk import AHK
from loguru import logger

from edmacro import config

from edmacro import utils as rbx

from PIL import Image

import os

from ahk._sync.engine import CoordModeTargets


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
        self.roblox_hwnd = rbx.get_roblox_window()
        self.win_dimensions = rbx.get_roblox_window_pos(self.roblox_hwnd)
        self.current_map_index: int | None = None
        self.current_map_col: int | None = None

    def __load_assets(self):
        self.assets = {}
        for asset in os.listdir("assets"):
            self.assets[asset] = Image.open(f"assets/{asset}")
        logger.debug(f"Loaded {len(self.assets)} assets.")
