from typing import Optional

from edmacro import MacroController
from edmacro.actions import Action


class crabBeardBounty(Action):

    __export__name__ = "crab_beard_bounty"

    REQUIRED_ACTIONS = ["quest_detector"]

    def __init__(self, macro_controller: MacroController):
        super().__init__(macro_controller)

        self.current_quest: Optional[str] = None

    def execute(self):
        self.macro_controller.logger.info("Running crab beard bounty")
