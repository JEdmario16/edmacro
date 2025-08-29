import time
from typing import Dict, List, Literal, Optional, Tuple, TypeAlias

from edmacro.actions import Action, utils

TargetBoss: TypeAlias = Literal[
    "HYPERCORE", "KINGSLIME", "KRAKEN", "MECHKRAKEN", "QUEENSLIME"
]


class bossRunAction(Action):

    __export__name__ = "boss_run"

    HYPERCORE_HEALTHS: List[int] = [
        1_500_000,
        2_230_000,
        2_914_000,
        3_569_000,
        4_200_500,
        4_814_000,
        5_412_500,
        5_998_000,
        6_573_000,
        7_138_000,
        7_694_500,
        8_243_500,
        8_785_000,
        9_320_000,
        9_849_500,
        10_373_500,
        10_892_000,
        11_406_000,
        11_915_000,
        12_420_500,
        12_921_500,
        13_419_000,
        13_913_000,
        14_403_500,
        14_890_500,
        15_374_000,
    ]

    KRAKEN_HEALTHS: List[int] = [3_000_000] * 25  # TODO: get the real kraken healths
    SLIME_HEALTHS: List[int] = [400_000] * 25  # TODO: get the real slime healths

    BOSS_HEALTH_MAP = {
        "HYPERCORE": HYPERCORE_HEALTHS,
        "KRAKEN": KRAKEN_HEALTHS,
        "KINGSLIME": SLIME_HEALTHS,
    }
    BOSS_MAP: Dict[TargetBoss, Tuple[int, int]] = {
        "KINGSLIME": (2, 0),
        "KRAKEN": (4, 0),
        "HYPERCORE": (8, 0),
        "MECHKRAKEN": (9, 0),
        "QUEENSLIME": (9, 0),
    }

    BOSS_HEALTHBAR_CONFIDENCE_THRESHOLD = 0.90
    RESPAWN_TRASHOLD = 0.90

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.target_boss: None | TargetBoss = None

    def execute(self, repeat: int = 1, target_boss: TargetBoss = "HYPERCORE"):
        bound = utils.Rect(0, 0, *self.macro_controller.user_resolution)
        target_boss_map = self.BOSS_MAP[target_boss]
        self.move_to_map(*target_boss_map)

        self.target_boss = target_boss

        run_start = time.time()
        times: list[float] = []
        utils.activate_roblox()
        self.go_to_boss(target_boss)
        for _ in range(repeat):

            self.resolve_interruns_path()

            sc = utils.screenshot(
                region=bound,
                hwnd=self.macro_controller.roblox_hwnd,
            )

            # Click on respawn tome
            needle = self.macro_controller.assets["respawn_tome"]
            conf, pos = utils.locate(needle, sc, bound=bound)
            x, y = pos.center

            if conf >= self.RESPAWN_TRASHOLD:
                self.macro_controller.logger.info("Clicking on respawn tome")
                self._ahk.mouse_move(x, y, speed=5)
                self._ahk.click()

            time.sleep(0.5)
            sc = utils.screenshot(
                region=(0, 0, *self.macro_controller.user_resolution),
                hwnd=self.macro_controller.roblox_hwnd,
            )
            needle = self.macro_controller.assets["respawn_button"]

            conf, pos = utils.locate(needle, sc, bound=bound)
            x, y = pos.center

            if conf >= self.RESPAWN_TRASHOLD:
                self.macro_controller.logger.info("Clicking on respawn button")
                self._ahk.mouse_move(x + 20, y + 20, speed=5)
                self._ahk.click()
                time.sleep(0.5)

            # finally click on start button
            needle = self.macro_controller.assets["start"]
            sc = utils.screenshot(
                region=(0, 0, *self.macro_controller.user_resolution),
                hwnd=self.macro_controller.roblox_hwnd,
            )
            _, pos = utils.locate(needle, sc, bound=bound)
            x, y = pos.center

            # this needle is a little bit off, so we need to move the mouse a little bit
            self._ahk.mouse_move(x + 20, y + 20, speed=5)
            self._ahk.click()
            self.macro_controller.logger.info("clicked on start button")

            # then wait for the boss to spawn
            boss_spawn_delay = 5 if target_boss == "HYPERCORE" else 10
            time.sleep(boss_spawn_delay)
            self.__freeze_game()
            times.append(time.time() - run_start)
            self.macro_controller.logger.info(
                f"Boss run {repeat} finished. Took {times[-1]} seconds"
            )
            sc = utils.screenshot(
                region=bound,
                hwnd=self.macro_controller.roblox_hwnd,
            )

            time.sleep(15)  # wait exit from boss map

            sc = utils.screenshot(region=bound, hwnd=self.macro_controller.roblox_hwnd)
            needle = self.macro_controller.assets["claim"]
            _, pos = utils.locate(needle, sc, bound=bound)
            # vamos denovo salvar uma screen shot e desenhar o retangulo
            # para ver se o needle esta correto
            import cv2

            rectangulo = cv2.rectangle(
                sc, (pos.left, pos.top), (pos.right, pos.bottom), (0, 255, 0), 2
            )
            cv2.imwrite("sc.png", rectangulo)

            self._ahk.mouse_move(*pos.center, speed=5)
            self._ahk.click()
            time.sleep(0.3)

        self.macro_controller.logger.info(
            f"Boss run finished. Total time: {round(sum(times), 2)} s, Average time: {round(sum(times) / len(times), 2)} s"
        )

    def resolve_interruns_path(self):

        match self.target_boss:
            case "HYPERCORE":
                self.__hypercore_interruns_path()
            case "KRAKEN":
                self.__kraken_interruns_path()
            case "KINGSLIME":
                self.__kingslime_interruns_path()
            case _:
                self.macro_controller.logger.error("Invalid boss name")
                raise ValueError("Invalid boss name")

    def __hypercore_interruns_path(self):
        """
        This method will move the character from the point where the character after kill
        the boss to the point where the character can kill the boss again.
        Note that its different from the `go_to_hypercore_boss` method, that will move the character from spawn point
        to the boss location.
        """
        self._ahk.key_down("s")
        time.sleep(1)
        self._ahk.key_up("s")
        return

    def __kraken_interruns_path(self):
        """
        This method will move the character from the point where the character after kill
        the boss to the point where the character can kill the boss again.
        Note that its different from the `go_to_kraken_boss` method, that will move the character from spawn point
        to the boss location.
        """
        self._ahk.key_down("w")
        time.sleep(1)
        self._ahk.key_up("w")
        time.sleep(0.5)
        return

    def __kingslime_interruns_path(self):
        """
        This method will move the character from the point where the character after kill
        the boss to the point where the character can kill the boss again.
        Note that its different from the `go_to_kingslime_boss` method, that will move the character from spawn point
        to the boss location.
        """
        self._ahk.key_down("w")
        self._ahk.key_down("d")
        time.sleep(1)
        self._ahk.key_up("w")
        self._ahk.key_up("d")
        time.sleep(0.5)

    def go_to_boss(self, target_boss: TargetBoss):
        """
        Move to the boss location. Requires the character to already be in the boss map.

        This method determines the type of boss specified in the configuration file and
        delegates the action to the corresponding method.

        Raises:
            ValueError: If an invalid boss name is specified in the configuration.
        """
        match target_boss:
            case "HYPERCORE":
                self.__go_to_hypercore_boss()
            case "KINGSLIME":
                self.__go_to_kingslime_boss()
            case "KRAKEN":
                self.__go_to_kraken_boss()
            case _:
                self.macro_controller.logger.error("Invalid boss name")
                raise ValueError("Invalid boss name")

    def __go_to_hypercore_boss(self) -> None:
        """
        Navigate to the Hypercore boss location.

        This method resets the character's position to the spawn point and moves them
        to the Hypercore boss location. The character is assumed to already be in the Hyperwave map.

        Actions performed:
        1. Reset character position to spawn point.
        2. Move character to the Hypercore boss location by pressing the 'a' and 's' keys.

        Note:
        - The character's position must be in the Hyperwave map before calling this method.
        """
        self.macro_controller.logger.info("Going to Hypercore boss")
        self.reset_if_needed()

        # Move from spawn point to boss hallway
        self._ahk.key_down("a")
        time.sleep(6.5)
        self._ahk.key_up("a")

        # walk to the boss
        time.sleep(0.3)
        self._ahk.key_down("s")
        time.sleep(2.5)
        self._ahk.key_up("s")

        time.sleep(0.3)

    def __go_to_kingslime_boss(self):
        """
        Navigate to the Slime boss location.
        """
        self.macro_controller.logger.info("Going to Slime boss")
        # Move from spawn point to boss hallway
        self._ahk.key_down("s")
        time.sleep(2.5)
        self._ahk.key_up("s")
        self._ahk.key_down("a")
        time.sleep(1)
        self._ahk.key_up("a")
        self._ahk.key_down("s")
        time.sleep(1.3)
        self._ahk.key_up("s")
        self._ahk.key_down("a")
        time.sleep(3.5)
        self._ahk.key_up("a")

    def __go_to_kraken_boss(self):
        """
        Navigate to the Kracken boss location.
        """

        self.macro_controller.logger.info("Going to Kracken boss")
        # Move from spawn point to boss hallway
        self._ahk.key_down("w")
        time.sleep(5)
        self._ahk.key_up("w")
        self._ahk.key_down("a")
        time.sleep(3)
        self._ahk.key_up("a")
        self._ahk.key_down("w")
        time.sleep(7)
        self._ahk.key_up("w")
        self._ahk.key_down("a")
        time.sleep(1)
        self._ahk.key_up("a")

    def __freeze_game(self, seconds: Optional[float | int] = None):
        """
        Freeze game is a bug in roblox that makes the game freeeze for a while.
        When game is frozen, you can't take any demage, but your pet's still can.
        We are using it to kill the boss withou dealing within complex mechanics.
        This approuch literally frozen the gamescreen, wich means that we cant know the boss health.
        It will be done in `estimated_time_to_kill_boss` method.
        When the estimated time to kill the boss is reached, we will unfreeze the game, and look at specific pixel to check if the boss is dead.
        If the boss is dead, we will continue the script, otherwise, we will freeze the game again, calling this method recursively.
        This not perfect because we lost some time to check the boss health, what can make the player die. In my tests, with 1k HP, you can
        recall this method 3 times without dying.

        :param seconds: The time to freeze the game. If None, we will estimate it.
        :return: None
        """

        seconds = seconds or self.estimated_time_to_kill_boss()

        assert seconds is not None
        assert self.target_boss is not None

        freeze_button = self.macro_controller.assets["freeze"]
        boss_health_bar = self.macro_controller.assets[
            f"{self.target_boss.lower()}_healthbar"
        ]

        bound_region = (0, 0, *self.macro_controller.user_resolution)
        self.macro_controller.logger.info(f"Freezing game for {seconds}")

        sc = utils.screenshot(region=bound_region, hwnd=None)  # must be entire screen
        conf, frozen_pos = utils.locate(
            needle=freeze_button, haystack=sc, bound=bound_region
        )

        x_freeze, y_freeze = frozen_pos.center

        self._ahk.mouse_move(x_freeze, y_freeze)
        self._ahk.send("{RButton down}")
        time.sleep(seconds)
        self._ahk.mouse_move(100, 100)
        self._ahk.send("{RButton up}")

        while True:
            time.sleep(0.5)
            # this block will check if the boss still alive
            sc = utils.screenshot(
                region=bound_region, hwnd=self.macro_controller.roblox_hwnd
            )
            # now that we already have the sc, lets freeze the screen again until check if boss was dead
            conf, pos = utils.locate(
                needle=boss_health_bar, haystack=sc, bound=bound_region
            )

            self._ahk.mouse_move(x_freeze, y_freeze)
            self._ahk.send("{RButton down}")

            if conf <= self.BOSS_HEALTHBAR_CONFIDENCE_THRESHOLD:
                self._ahk.mouse_move(100, 100)
                self._ahk.send("{RButton up}")
                break

            self.macro_controller.logger.warning(
                f"Boss still alive with {conf} of confidence, freezing game again"
            )
            time.sleep(seconds * 0.10)
            self._ahk.mouse_move(100, 100)
            self._ahk.send("{RButton up}")

    def estimated_time_to_kill_boss(self) -> float:
        """
        Estimate the time to defeat the boss using expected damage per hit.

        This method calculates the estimated time to defeat the boss without directly
        knowing the boss's health. It uses the Expected Value approach, which works as follows:
        - Obtain the boss's health at the start of the fight.
        - Retrieve the player's base damage, critical chance, and critical multiplier from the configuration.
        - Calculate the Expected Value of the damage per hit, assuming a rate of 1 hit per second.

        Returns:
            The estimated time (in seconds) required to defeat the boss.
        """
        # Get player stats from configuration
        player_base_damage = self.macro_controller.configs.getint(
            "PLAYER_STATS", "base_damage"
        )
        player_critical_multiplier = self.macro_controller.configs.getfloat(
            "PLAYER_STATS", "critical_multiplier"
        )
        player_critical_chance = self.macro_controller.configs.getfloat(
            "PLAYER_STATS", "critical_chance"
        )

        # Get boss health
        boss_health = self.BOSS_HEALTH_MAP[self.target_boss][-1]

        # Calculate expected damage per hit
        expected_damage = (
            player_base_damage * (1 - player_critical_chance)
            + player_base_damage * player_critical_chance * player_critical_multiplier
        )

        # Calculate estimated time to defeat boss
        estimated_time = boss_health / expected_damage

        return estimated_time
