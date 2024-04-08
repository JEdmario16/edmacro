from ahk import AHK
from loguru import logger

from edmacro import config

from edmacro import roblox as rbx

from PIL import Image

import os


class MacroController:
    def __init__(self):
        self.ahk = AHK()

        # setup ahk
        targets = ["Pixel", "Mouse", "Menu"]
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

        self.roblox_hwnd = rbx.get_roblox_window()
        self.win_dimensions = rbx.get_roblox_window_pos(self.roblox_hwnd)

        self.__load_assets()
        logger.info("Assets loaded")

    def __load_assets(self):
        self.assets = {}
        for asset in os.listdir("assets"):
            self.assets[asset] = Image.open(f"assets/{asset}")
