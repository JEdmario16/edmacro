from edmacro import MacroController
from edmacro.actions import Action, utils


import time
from datetime import datetime


class ShrineAndShops(Action):

    __export__name__ = "shrine_and_shops"

    SHOPS_MAPS = {
        "prizes_counter": (8, 0),
        "tomes_shrine": (8, 0),
        "hardcore_tomes_shrine": (9, 0),
    }

    SHRINES_AND_SHOPS_COOLDOWNS = {
        "prizes_counter": 60 * 20,
        "tomes_shrine": 60 * 40,
        "hardcore_tomes_shrine": 60 * 40,
    }

    PRIZE_COUNTER_THRESHOLD = 0.9

    def __init__(self, macro_controller: MacroController):
        super().__init__(macro_controller)

        self.last_prize_counter: datetime | None = None
        self.last_tomes_shrine: datetime | None = None
        self.last_hardcore_tomes_shrine: datetime | None = None

    def execute(self):
        self.macro_controller.logger.info("Running shrine and shops")
        self.check_shrine_and_shops()

    def check_shrine_and_shops(self):
        if (
            self.last_prize_counter is None
            or (self.last_prize_counter - datetime.now()).seconds
            > self.SHRINES_AND_SHOPS_COOLDOWNS["prizes_counter"]
        ):
            self.go_to_prizes_counter()
            self.prize_counter_buy_all()

        if (
            self.last_tomes_shrine is None
            or (self.last_tomes_shrine - datetime.now()).seconds
            > self.SHRINES_AND_SHOPS_COOLDOWNS["tomes_shrine"]
        ):
            self.go_to_tomes_shrine()

        if (
            self.last_hardcore_tomes_shrine is None
            or (self.last_hardcore_tomes_shrine - datetime.now()).seconds
            > self.SHRINES_AND_SHOPS_COOLDOWNS["hardcore_tomes_shrine"]
        ):
            self.go_to_hardcore_tomes_shrine()

    def go_to_prizes_counter(self):

        self.macro_controller.logger.debug("Going to prizes counter map")
        self.move_to_map(*self.SHOPS_MAPS["prizes_counter"])
        self._ahk.key_down("a")
        time.sleep(1.5)
        self._ahk.key_up("a")
        self._ahk.key_down("w")
        time.sleep(1)
        self._ahk.key_up("w")

    def prize_counter_buy_all(self):
        bound = utils.Rect(0, 0, *self.macro_controller.user_resolution)
        needle = self.macro_controller.assets["prize_counter_price_location"]
        # first, lets scroll to bottom
        self._ahk.send("{WheelDown}", key_press_duration=0.5)
        time.sleep(1)

        while True:
            sc = utils.screenshot(hwnd=self.macro_controller.roblox_hwnd, region=bound)
            conf, pos = utils.locate(sc, needle, bound=bound)

            if conf <= self.PRIZE_COUNTER_THRESHOLD:
                break

            for _ in range(20):
                self._ahk.click(pos[0], pos[1])
                time.sleep(0.1)
            time.sleep(0.5)

        # after buy all move to left to close the shop dialog
        self._ahk.key_down("a")
        time.sleep(2)
        self._ahk.key_up("a")
        self.macro_controller.logger.info("Bought all prizes")
        self.last_prize_counter = datetime.now()

    def go_to_tomes_shrine(self):

        self.macro_controller.logger.debug("Going to tomes shrine map")
        self.move_to_map(*self.SHOPS_MAPS["tomes_shrine"])

        self._ahk.key_down("a")
        time.sleep(6)
        self._ahk.key_up("a")
        self._ahk.key_down("s")
        time.sleep(4)
        self._ahk.key_up("s")
        self._ahk.send("e")
        time.sleep(0.3)
        self.macro_controller.logger.info("Pick up tomes")
        self.last_tomes_shrine = datetime.now()

    def go_to_hardcore_tomes_shrine(self):
        self.macro_controller.logger.debug("Going to hardcore tomes shrine map")
        self.move_to_map(*self.SHOPS_MAPS["hardcore_tomes_shrine"])

        self._ahk.key_down("w")
        time.sleep(9)
        self._ahk.key_up("w")
        self._ahk.key_down("d")
        time.sleep(1)
        self._ahk.key_up("d")
        self._ahk.send("e")
        time.sleep(0.3)
        self.macro_controller.logger.info("Pick up hardcore tomes")
        self.last_hardcore_tomes_shrine = datetime.now()
