from __future__ import annotations

from edmacro import MacroController
from edmacro.actions import Action

from typing import Optional

from functools import partial


class crabBeardBounty(Action):

    __export__name__ = "crab_beard_bounty"

    REQUIRED_ACTIONS = ["quest_detector", "boss_run", "mob_hunt", "shrines_and_shops"]

    def __init__(self, macro_controller: MacroController):
        super().__init__(macro_controller)

        self.current_quest: Optional[str] = None

    def go_to_hypercore_boss(self) -> None:

        self.move_to_map(*self.HYPERCORE_MAP)

    def execute(self):
        self.macro_controller.logger.info("Running crab beard bounty")

        while True:
            self.macro_controller.shrine_and_shops.execute()
            current_task = self.macro_controller.quest_detector.execute()
            task = self.resolve_quest(current_task)
            task()

    def resolve_quest(self, text: str):
        tokenized_text = set(text.split())

        if not ({"hyper", "cores"} - tokenized_text):
            self.current_quest = "hypercore_hunt"
            return partial(
                self.macro_controller.boss_run.execute, repeat=3, target_boss="HYPERCORE"
            )
        elif not ({"krakens", "defeat"} - tokenized_text):
            self.current_quest = "kraken_hunt"
            return partial(
                self.macro_controller.boss_run.execute, repeat=3, target_boss="KRAKEN"
            )

        elif not ({"defeat", "king", "slimes"} - tokenized_text):
            self.current_quest = "king_slimes"
            return partial(
                self.macro_controller.boss_run.execute,
                repeat=3,
                target_boss="KINGSLIME",
            )

        elif not ({"defeat", "mutant", "slimes"} - tokenized_text):
            self.current_quest = "mutant_slimes"
            return partial(
                self.macro_controller.mob_hunt.execute,
                target_mob="MUTANT_SLIMES",
                seconds=120,
            )

        elif not ({"defeat", "molten", "crabs"} - tokenized_text):
            self.current_quest = "molten_crab"
            return partial(
                self.macro_controller.mob_hunt.execute,
                target_mob="MOLTEN_CRAB",
                seconds=120,
            )

        elif not ({"defeat", "anglerfish"} - tokenized_text):
            self.current_quest = "anglerfish"
            return partial(
                self.macro_controller.mob_hunt.execute,
                target_mob="ANGLERFISH",
                seconds=120,
            )

        elif not ({"defeat", "armored", "snowmen"} - tokenized_text):
            self.current_quest = "armored_snowman"
            return partial(
                self.macro_controller.mob_hunt.execute,
                target_mob="ARMORED_SNOWMAN",
                seconds=120,
            )

        elif not ({"defeat", "slimes"} - tokenized_text):
            self.current_quest = "slimes"
            return partial(
                self.macro_controller.mob_hunt.execute, target_mob="SLIMES", seconds=200
            )

        elif not ({"defeat", "crabs"} - tokenized_text):
            self.current_quest = "crab"
            return partial(
                self.macro_controller.mob_hunt.execute,
                target_mob="CRAB",
                seconds=120,
            )

        elif not ({"defeat", "snowmen"} - tokenized_text):
            self.current_quest = "snowman"
            return partial(
                self.macro_controller.mob_hunt.execute,
                target_mob="SNOWMAN",
                seconds=250,
            )

        elif not ({"defeat", "enemies"} - tokenized_text):
            self.current_quest = "enemies"
            # again, the smartest way is to do another quest, but for now lets just kill anglefish
            return partial(
                self.macro_controller.mob_hunt.execute,
                target_mob="MOLTEN_CRAB",
                seconds=200,
            )

        elif not ({"deal", "damage"} - tokenized_text):
            # The smartest way is do another quest, but for now lets just kill hypercore once
            self.current_quest = "damage_dealer"
            return partial(
                self.macro_controller.boss_run.execute, repeat=2, target_boss="HYPERCORE"
            )

        else:
            self.macro_controller.logger.error(f"Unknown quest: {tokenized_text}, ")
            self.macro_controller.current_map = (None, None)
            self.execute()
