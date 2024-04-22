from edmacro.actions import Action
from typing import TypeAlias, Union, Literal

import time

TargetMob: TypeAlias = Literal[
    "ANGLEFISH",
    "MOLTEN_CRAB",
    "MUTANT_SLIMES",
    "SLIMES",
    "ARMORED_SNOWMAN",
    "SNOWMAN",
    "CRAB",
]
Direction: TypeAlias = Literal["W", "A", "S", "D"]
Pattern: TypeAlias = Literal["row", "T"]


class MobHunt(Action):

    __export__name__ = "mob_hunt"

    mob_maps = {
        "ANGLEFISH": (9, 0),
        "MOLTEN_CRAB": (7, 0),
        "MUTANT_SLIMES": (6, 0),
        "ARMORED_SNOWMAN": (3, 0),
        "SNOWMAN": (2, 0),
        "SLIMES": (2, 0),
        "CRAB": (4, 0),
    }

    pattern_map = {
        "ANGLEFISH": ("row", "W"),
        "MOLTEN_CRAB": ("row", "W"),
        "SLIMES": ("row", "A"),
        "MUTANT_SLIMES": ("t_pattern", "S"),
        "ARMORED_SNOWMAN": ("row", "W"),
        "SNOWMAN": ("row", "S"),
        "CRAB": ("row", "D"),
    }  # mob: (pattern, direction)

    def execute(self, target_mob: TargetMob, seconds: int = 60):
        self.macro_controller.logger.info(
            f"Starting mob hunt {target_mob} for {seconds} seconds"
        )
        self.go_to_mob_spot(target_mob)
        start = time.time()
        while time.time() - start < seconds:
            pattern, direction = self.pattern_map[target_mob]
            self.resolve_pattern(pattern, direction)
        return

    def go_to_mob_spot(self, target_mob: TargetMob):
        match target_mob:
            case "ANGLEFISH":
                self.__go_to_anglefish()
            case "MOLTEN_CRAB":
                self.__go_to_molten_crab()
            case "MUTANT_SLIMES":
                self.__go_to_mutant_slimes()
            case "SLIMES":
                self.__go_to_slimes()
            case "ARMORED_SNOWMAN":
                self.__go_to_armored_snowman()

            case "SNOWMAN":
                self.__go_to_snowman()

            case "CRAB":
                self.__go_to_crab()
            case _:
                raise ValueError("Invalid target mob")

    def resolve_pattern(self, pattern: Pattern, direction: Direction):
        match pattern:
            case "row":
                self.__row_pattern(direction)
            case "t_pattern":
                self.__t_pattern(direction)
            case _:
                raise ValueError("Invalid pattern")

    def __go_to_anglefish(self):

        self.move_to_map(*self.mob_maps["ANGLEFISH"])

        self._ahk.key_down("w")
        time.sleep(4)
        self._ahk.key_up("w")
        self._ahk.key_down("a")
        time.sleep(4)
        self._ahk.key_up("a")
        self._ahk.key_down("s")
        time.sleep(6)
        self._ahk.key_up("s")

    def __go_to_molten_crab(self):
        self.move_to_map(*self.mob_maps["MOLTEN_CRAB"])

        self._ahk.key_down("a")
        time.sleep(1.5)
        self._ahk.key_up("a")
        self._ahk.key_down("w")
        time.sleep(4)
        self._ahk.key_up("w")

    def __go_to_slimes(self):
        self.move_to_map(*self.mob_maps["SLIMES"])

        self._ahk.key_down("s")
        time.sleep(3)
        self._ahk.key_up("s")
        self._ahk.key_down("d")
        time.sleep(2)
        self._ahk.key_up("d")
        self._ahk.key_down("s")
        time.sleep(2)
        self._ahk.key_up("s")
        self._ahk.key_down("a")
        time.sleep(1.5)
        self._ahk.key_up("a")

    def __go_to_mutant_slimes(self):
        self.move_to_map(*self.mob_maps["MUTANT_SLIMES"])

        self._ahk.key_down("s")
        time.sleep(6)
        self._ahk.key_up("s")
        self._ahk.key_down("a")
        time.sleep(0.5)
        self._ahk.key_up("a")
        self._ahk.key_down("s")
        time.sleep(0.75)
        self._ahk.key_up("s")
        self._ahk.key_down("d")
        time.sleep(0.5)
        self._ahk.key_up("d")

    def __go_to_armored_snowman(self):
        self.move_to_map(*self.mob_maps["ARMORED_SNOWMAN"])

        self._ahk.key_down("a")
        time.sleep(6)
        self._ahk.key_up("a")

    def __go_to_snowman(self):
        self.move_to_map(*self.mob_maps["SNOWMAN"])

        self._ahk.key_down("w")
        time.sleep(3.5)
        self._ahk.key_up("w")
        self._ahk.key_down("a")
        time.sleep(3)
        self._ahk.key_up("a")
        self._ahk.key_down("w")
        time.sleep(10)
        self._ahk.key_up("w")
        self._ahk.key_down("a")
        time.sleep(0.5)
        self._ahk.key_up("a")

    def __go_to_crab(self):

        self.move_to_map(*self.mob_maps["CRAB"])
        self._ahk.key_down("w")
        time.sleep(5)
        self._ahk.key_up("w")
        self._ahk.key_down("d")
        time.sleep(1)
        self._ahk.key_up("d")
        self._ahk.key_down("w")
        time.sleep(6.5)
        self._ahk.key_up("w")

    def __row_pattern(self, direction: str):
        directions = ["w", "a", "s", "d"]
        direction = direction.lower()
        inverse_direction = directions[directions.index(direction) - 2]
        self._ahk.key_down(direction)
        time.sleep(4)
        self._ahk.key_up(direction)
        self._ahk.key_down(inverse_direction)
        time.sleep(4)
        self._ahk.key_up(inverse_direction)

    def __t_pattern(self, straight_direction: str):
        directions = ["w", "a", "s", "d"]
        straight_direction = straight_direction.lower()
        inverse_direction = directions[directions.index(straight_direction) - 2]
        side_direction = directions[directions.index(straight_direction) - 1]
        inverse_side_direction = directions[directions.index(straight_direction) - 3]
        self._ahk.key_down(straight_direction)
        time.sleep(4)
        self._ahk.key_up(straight_direction)
        self._ahk.key_down(side_direction)
        time.sleep(2)
        self._ahk.key_up(side_direction)
        self._ahk.key_down(inverse_side_direction)
        time.sleep(4)
        self._ahk.key_up(inverse_side_direction)
        self._ahk.key_down(side_direction)
        time.sleep(2)
        self._ahk.key_up(side_direction)
        self._ahk.key_down(inverse_direction)
        time.sleep(4)
        self._ahk.key_up(inverse_direction)
