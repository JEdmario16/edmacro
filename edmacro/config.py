import configparser
import os

from loguru import logger

# List of actions that will be loaded when the program starts
# all listed actions must be in dot notation, e.g. "edmacro.actions.boss_run"
# stands for the file edmacro/actions/boss_run.py
# if you want to add a new action, add it to this list, like
# yourproject.actions.your_action (yourproject is in sys.path or current directory)
# Then it will be avaible in macro_controller instance as a method to call
# e.g. macro_controller.actions.__your_action_name__
# See: Extending the macro guide (TODO: Create this guide)
INSTALLED_ACTIONS = [
    "edmacro.actions.boss_run",
    "edmacro.actions.quest_detector",
    "edmacro.actions.crab_beard_bounty",
    "edmacro.actions.mob_hunt",
    "edmacro.actions.shrines_and_shops",
]


def get_config() -> configparser.ConfigParser:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config = configparser.ConfigParser()

    if not os.path.exists(os.path.join(BASE_DIR, "config.ini")):
        build_default_config_file()

    config.read(os.path.join(BASE_DIR, "config.ini"))
    return config


def build_default_config_file():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    config = configparser.ConfigParser()

    config.add_section("PLAYER_STATS")
    config.set("PLAYER_STATS", "base_demage", "100")
    config.set("PLAYER_STATS", "critical_multiplier", "2.0")
    config.set("PLAYER_STATS", "CRITICAL_CHANCE", "0.25")
    config.set("PLAYER_STATS", "BOSS_LEVEL", "1")
    config.set("PLAYER_STATS", "BOSS_RUNS_MAX", "6")
    config.set("PLAYER_STATS", "MINIGAME_RUNS_MAX", "6")
    config.set("PLAYER_STATS", "SHOULD_PLAY_MINIGAME", "True")
    config.set("PLAYER_STATS", "GRIND_BOSS", "HYPERCORE")

    config.add_section("OTHERS")
    config.set("OTHERS", "OUTPUT_FOLDER", "")
    config.set("OTHERS", "LOG_LEVEL", "DEBUG")

    with open(os.path.join(BASE_DIR, "config.ini"), "w") as file:
        config.write(file)
        logger.debug("Config file created.")
