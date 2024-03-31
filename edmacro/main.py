import PIL
import os
import pyautogui
import time
import win32gui
import win32con
from typing import Optional, Union
from loguru import logger
from ahk import AHK, MsgBoxButtons
from datetime import datetime
from enums import Bosses, HyperCoreHealth
import configparser
import os

config = configparser.ConfigParser()
config.read("config.ini")
ahk = AHK()


PLAYER_BASE_DAMAGE = config.getint("PLAYER_STATS", "BASE_DEMAGE")
PLAYER_CRITICAL_CHANCE = config.getfloat("PLAYER_STATS", "CRITICAL_CHANCE")
PLAER_CRITICAL_MULTIPLIER = config.getfloat("PLAYER_STATS", "CRITICAL_MULTIPLIER")
OUTPUT_FOLDER = config.get("OTHER", "OUTPUT_FOLDER")
FREEZE_BUTTON = PIL.Image.open("assets/freeze.png")

if not os.path.exists(OUTPUT_FOLDER):
    ahk.msg_box(
        title="Error!",
        text="Can't locate your output folder. Please, select another one",
    )
    folder = ahk.folder_select_box(new_dialog_style=True)
    if folder is None:
        raise SystemExit
    # now, update our config
    config["OTHER"]["OUTPUT_FOLDER"] = folder
    with open("config.ini", "w") as configfile:
        config.write(configfile)


def get_roblox_window():
    def callback(hwnd, extra):
        if win32gui.GetWindowText(hwnd) == "Roblox":
            extra.append(hwnd)

    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows[0]


def get_roblox_window_pos(hwnd: Optional[int] = None) -> tuple[int, int, int, int]:
    if not hwnd:
        hwnd = get_roblox_window()
    try:
        return win32gui.GetWindowRect(hwnd)
    except:
        return (0, 0, 0, 0)


def activate_roblox():
    # if the window is showing but not active, win32gui.SetForegroundWindow(hwnd) will not work
    # so we need to click on the window to activate it
    hwnd = get_roblox_window()
    if win32gui.IsWindowVisible(hwnd) and not win32gui.IsIconic(hwnd):
        # then let's hide the window
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        time.sleep(0.3)
    # then let's show the window and activate it
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    time.sleep(0.3)


def get_current_active_window():
    # returns screen title
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())


def click(**kwargs):
    if get_current_active_window() != "Roblox":
        activate_roblox()
    pyautogui.mouseDown()
    time.sleep(0.1)
    pyautogui.click(**kwargs)


def respawn(should_claim: bool = False, needs_respawn: bool = False):

    RESPAWN_BUTTON = PIL.Image.open("assets/respawn_button.png")
    RESPAWN_TOME = PIL.Image.open("assets/respawn_tome.png")
    START_BUTTON = PIL.Image.open("assets/start.png")
    CLAIM_BUTTON = PIL.Image.open("assets/claim.png")
    CLOSE_AFK_WARNING = PIL.Image.open("assets/close.png")

    if should_claim:
        logger.info("Claiming rewards")
        box = pyautogui.locateCenterOnScreen(CLAIM_BUTTON, confidence=0.95)
        pyautogui.moveTo(box, duration=0.3)
        time.sleep(0.3)
        click()
        time.sleep(4)
        tries = 0
        while tries < 5:
            try:
                logger.info("Closing AFK warning")
                box = pyautogui.locateCenterOnScreen(CLOSE_AFK_WARNING, confidence=0.95)
                pyautogui.moveTo(box, duration=0.3)
                time.sleep(0.3)
                click()
                time.sleep(1)
                break
            except:
                logger.info(f"Failed to close AFK warning, retrying({tries}/{5})")
                tries += 1
                time.sleep(1)

    if needs_respawn:
        logger.info("Respawning")
        box = pyautogui.locateCenterOnScreen(RESPAWN_TOME, confidence=0.95)
        pyautogui.moveTo(box, duration=0.3)
        time.sleep(0.3)
        click()
        time.sleep(1)

        box = pyautogui.locateCenterOnScreen(RESPAWN_BUTTON, confidence=0.95)
        pyautogui.moveTo(box, duration=0.3)
        time.sleep(0.3)
        click(clicks=2, interval=0.8)
        time.sleep(2)

    try:
        logger.info("Starting game")
        box = pyautogui.locateCenterOnScreen(START_BUTTON, confidence=0.85)
        pyautogui.moveTo(box, duration=0.3)
        time.sleep(0.3)
        click(clicks=2, interval=0.3)
        time.sleep(1)
        return True
    except Exception as e:
        # save a screenshot of the screen
        pyautogui.screenshot("error.png")
        raise e


def freeze_game(time_needed: Optional[Union[int, float]] = None):
    # let's estimate the time needed to kill the boss
    # at 25 level, bos health is 14.890.500
    # So, the expectation of player damage will be base_dmg *(1-crit_chance) + base_dmg * crit_chance * crit_multiplier
    # Then, let's suppose that the player hit one time per second
    # So, the time needed to kill the boss will be boss_health / player_expected_damage
    # at the end, let's add on it 10 seconds to be sure
    expected_damage = (
        PLAYER_BASE_DAMAGE * (1 - PLAYER_CRITICAL_CHANCE)
        + PLAYER_BASE_DAMAGE * PLAYER_CRITICAL_CHANCE * PLAER_CRITICAL_MULTIPLIER
    )
    boss_health = float(HyperCoreHealth.twenty_five.value)
    time_needed = time_needed or (boss_health / expected_damage) + 10

    # screen size have 1920 of width, life bar in center, wich give us 640 pixels to the left and 640 to the right
    # so, the middle of the life bar will be at 870 of width. Also, bar starts at 70 of height, so we can use this.
    SAFE_PIXEL_POSITION = (675, 88)
    MIDDLE_LIFE_PIXEL_POSITION = (847, 80)

    logger.info(f"Freezing game for {time_needed} seconds")
    box = pyautogui.locateCenterOnScreen(FREEZE_BUTTON, confidence=0.95)
    pyautogui.moveTo(box)
    pyautogui.mouseDown()
    time.sleep(time_needed)
    pyautogui.moveTo(100, 30, duration=0.3)
    pyautogui.mouseUp()
    time.sleep(1)
    pixel_color = pyautogui.pixel(*SAFE_PIXEL_POSITION)
    logger.info(f"Pixel color: {pixel_color}")
    if pixel_color == (0, 234, 255):
        middle_pixel_color = pyautogui.pixel(*MIDDLE_LIFE_PIXEL_POSITION)
        new_time_needed = time_needed
        logger.warning("Was expected that boss is dead, but it's not")
        more_than_middle = middle_pixel_color == (0, 234, 255)
        if more_than_middle:
            logger.warning("Boss is more than middle life bar")
        freeze_game(new_time_needed * (0.25 + 0.5 * more_than_middle))
        logger.info(f"Freezing game for {new_time_needed} seconds again")


def smart_freeze_game():
    """
    This function will freeze the game for a certain amount of time, but will also check the boss health
    and estimate the time needed to kill the boss, then freeze the game for that amount of time
    """
    start = time.time()
    # get the boss health


CLAIM_BUTTON_POSITION = (956, 693)
CLOSE_AFK_WARNING_POSITION = (956, 703)
RESPAWN_BUTTON_POSITION = (882, 573)
RESPAWN_TOME_POSITION = (882, 573)
START_BUTTON_POSITION = (846, 721)


def run_boss():
    times = 0
    while times < 1:
        run_start = time.time()
        logger.info(f"Starting run {times}")
        ahk.win_activate("Roblox")
        ahk.key_down("w")
        time.sleep(1)
        ahk.key_up("w")
        # save a screenshot of the screen before claiming rewards
        pic_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        pyautogui.screenshot(f"{OUTPUT_FOLDER}/{pic_time}.png")
        ahk.mouse_move(*CLAIM_BUTTON_POSITION)
        ahk.click()
        time.sleep(0.3)
        ahk.mouse_move(*CLOSE_AFK_WARNING_POSITION)
        ahk.click()
        time.sleep(0.3)
        ahk.mouse_move(*RESPAWN_TOME_POSITION)
        ahk.click()
        time.sleep(0.3)
        ahk.mouse_move(*RESPAWN_BUTTON_POSITION)
        ahk.click()
        time.sleep(0.3)
        ahk.mouse_move(*START_BUTTON_POSITION)
        ahk.click()
        time.sleep(5)
        freeze_game()
        times += 1
        logger.info("Waiting exit from boss room")
        time.sleep(15)
        logger.info(f"Run {times} took {time.time() - run_start} seconds")


if __name__ == "__main__":
    result = ahk.msg_box(
        title="Welcome!",
        text=f"""Welcome to the Macro! Please, make sure that you have the game opened
        You can change the output folder in the config.ini file
        Your current configuration:
        - Base damage: {PLAYER_BASE_DAMAGE}
        - Critical chance: {PLAYER_CRITICAL_CHANCE}
        - Critical multiplier: {PLAER_CRITICAL_MULTIPLIER}
        - Output folder: {OUTPUT_FOLDER}
        Do you want to start the macro?""",
        buttons=MsgBoxButtons.YES_NO,
    )
    if result == "YES":
        run_boss()
    else:
        raise SystemExit
