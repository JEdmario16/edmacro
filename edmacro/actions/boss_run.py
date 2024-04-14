import time
from typing import Optional

from edmacro.actions import Action
from edmacro.enums import HyperCoreHealth


class bossRunAction(Action):
    def execute(self):
        self.macro_controller.logger.info("Running boss")

    def go_to_boss(self):
        """
        Move to the boss location. Requires the character to already be in the boss map.

        This method determines the type of boss specified in the configuration file and
        delegates the action to the corresponding private method.

        Possible boss types:
        - "HYPERCORE": Navigate to the Hypercore boss location.
        - "SLIME": Navigate to the Slime boss location.
        - "KRACKEN": Navigate to the Kracken boss location.

        Raises:
            ValueError: If an invalid boss name is specified in the configuration.
        """
        target_boss = self.macro_controller.configs.get(
            "PLAYER_STATS", "GRIND_BOSS", fallback="HYPERCORE"
        )

        match target_boss:
            case "HYPERCORE":
                self.__go_to_hypercore_boss()
            case "SLIME":
                self.__go_to_slime_boss()
            case "KRACKEN":
                self.__go_to_kracken_boss()
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
        self.restart_char()

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

    def __go_to_slime_boss(self):
        """
        Navigate to the Slime boss location.

        This method is not implemented. To navigate to the Slime boss location, an implementation
        must be provided in a subclass or in this method itself.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError("Method not implemented")

    def __go_to_kracken_boss(self):
        """
        Navigate to the Kracken boss location.

        This method is not implemented. To navigate to the Kracken boss location, an implementation
        must be provided in a subclass or in this method itself.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError("Method not implemented")

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

        self.macro_controller.logger.info(f"Freezing game for {seconds} seconds")

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
            "PLAYER_STATS", "base_damage", fallback=100
        )
        player_critical_multiplier = self.macro_controller.configs.getfloat(
            "PLAYER_STATS", "critical_multiplier", fallback=2.0
        )
        player_critical_chance = self.macro_controller.configs.getfloat(
            "PLAYER_STATS", "CRITICAL_CHANCE", fallback=0.25
        )
        boss_level = self.macro_controller.configs.getint(
            "PLAYER_STATS", "BOSS_LEVEL", fallback=1
        )

        # Get boss health
        boss_health = HyperCoreHealth(boss_level).value

        # Calculate expected damage per hit
        expected_damage = (
            player_base_damage * (1 - player_critical_chance)
            + player_base_damage * player_critical_chance * player_critical_multiplier
        )

        # Calculate estimated time to defeat boss
        estimated_time = boss_health / expected_damage

        return estimated_time
