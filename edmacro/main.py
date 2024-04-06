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
import colorama


logger.add("logs/log_{time}.log")
config = configparser.ConfigParser()
config.read("config.ini")
ahk = AHK()


PLAYER_BASE_DAMAGE = config.getint("PLAYER_STATS", "BASE_DEMAGE")
PLAYER_CRITICAL_CHANCE = config.getfloat("PLAYER_STATS", "CRITICAL_CHANCE")
PLAER_CRITICAL_MULTIPLIER = config.getfloat("PLAYER_STATS", "CRITICAL_MULTIPLIER")
TICKETS_MAX_AMOUNT = config.getint("PLAYER_STATS", "TICKETS_MAX_AMOUNT")
MINIGAME_PET_POSITION_ROW = config.getint("PLAYER_STATS", "MINIGAME_PET_POSITION_ROW")
MINIGAME_PET_POSITION_COLUMN = config.getint(
    "PLAYER_STATS", "MINIGAME_PET_POSITION_COLUMN"
)

SHOULD_PLAY_MINIGAME = config.getboolean("OTHER", "SHOULD_PLAY_MINIGAME")
OUTPUT_FOLDER = config.get("OTHER", "OUTPUT_FOLDER")
FREEZE_BUTTON = PIL.Image.open("assets/freeze.png")

COLOR_SIMILARITY_THRESHOLD = 15

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


def get_pet_on_inventory_position(pet_row, pet_column):
    # Position: Point(x=584, y=311), Color: (228, 238, 240)
    PET_SLOT_WIDTH = 128
    PET_SLOT_HEIGHT = 128
    INVENTORY_START_POS = (584, 312)

    pet_x = INVENTORY_START_POS[0] + PET_SLOT_WIDTH * pet_column
    pet_y = INVENTORY_START_POS[1] + PET_SLOT_HEIGHT * pet_row

    # calculate the center of the pet slot
    pet_x += PET_SLOT_WIDTH // 2
    pet_y += PET_SLOT_HEIGHT // 2

    return (pet_x, pet_y)


def start_minigame(pet_row, pet_column):
    # Point(x=813, y=714), Color: (93, 255, 93)
    start_minigame_button_position = (813, 714)

    # open start mini game menu
    ahk.key_down("e")
    ahk.key_up("e")
    time.sleep(0.5)

    # click on the start mini game button
    ahk.mouse_move(*start_minigame_button_position)
    ahk.click()
    time.sleep(1)

    # find the pet position on the inventory
    pet_position = get_pet_on_inventory_position(pet_row, pet_column)
    ahk.mouse_move(*pet_position)
    ahk.click()
    time.sleep(1)

    choose_button_image = PIL.Image.open("assets/choose_button.png")
    choose_button_position = pyautogui.locateCenterOnScreen(choose_button_image)

    ahk.mouse_move(
        choose_button_position[0], choose_button_position[1], relative=False, speed=10
    )
    ahk.click()

    time.sleep(0.3)  # fade in animation

    # the minigame takes 3 seconds to start. let's wait for it
    time.sleep(3)


def restart_char():
    logger.info("Restarting character")
    ahk.key_press("esc")
    time.sleep(0.3)
    ahk.key_press("r")
    time.sleep(0.3)
    ahk.key_press("enter")
    time.sleep(2)


def up_camera():
    logger.info("Resetting camera position")
    # put the mouse on the center of the screen
    ahk.mouse_move(960, 540)
    time.sleep(0.3)

    # now, press right mouse button
    ahk.mouse_drag(
        x=960, y=560, from_position=(960, 540), speed=10, relative=False, button="right"
    )

    # first, up all the way
    ahk.key_down("o")
    time.sleep(0.5)
    ahk.key_up("o")

    # then, down camera a little bit bc of floor
    ahk.key_down("i")
    time.sleep(0.1)
    ahk.key_up("i")


def go_to_minigame():
    logger.info("Going to minigame")
    ahk.key_down("a")
    time.sleep(2.8)
    ahk.key_up("a")
    time.sleep(0.3)
    ahk.key_down("s")
    time.sleep(2.5)
    ahk.key_up("s")
    time.sleep(0.3)
    ahk.key_down("a")
    time.sleep(1.5)
    ahk.key_up("a")
    time.sleep(0.3)


def go_to_boss():
    logger.info("Going to boss")
    ahk.key_down("a")
    time.sleep(6.5)
    ahk.key_up("a")
    time.sleep(0.3)
    ahk.key_down("s")
    time.sleep(2.5)
    ahk.key_up("s")
    time.sleep(0.3)


def play_miniagme(game_duration=60):
    start_time = time.time()
    seek_pixel_position = (963, 596)
    seek_pixel_color = (110, 242, 35)  # use as reference to know when to drop the pet.
    drop_position = (975, 972)
    CLAIM_BUTTON_POSITION = (967, 666)

    is_running = True
    while is_running:
        pixel_color = pyautogui.pixel(*seek_pixel_position)
        color_dist = color_distance(pixel_color, seek_pixel_color)
        if color_dist < COLOR_SIMILARITY_THRESHOLD:
            ahk.mouse_move(*drop_position)
            ahk.click()
            logger.debug(
                f"Dropping pet. Color distance: {color_dist}, Pixel color: {pixel_color}"
            )
        if time.time() - start_time > game_duration:
            is_running = False
        logger.debug(f"Pixel color: {pixel_color}")

    # wait exit muinigame
    time.sleep(8)
    # now claim the reward
    pyautogui.screenshot(f"debug/{time.time()}.png")
    ahk.mouse_move(*CLAIM_BUTTON_POSITION)
    ahk.click()
    time.sleep(0.3)
    ahk.mouse_move(CLAIM_BUTTON_POSITION[0], CLAIM_BUTTON_POSITION[1] + 20)
    ahk.click()
    time.sleep(0.3)


def color_distance(color1, color2):
    return sum((a - b) ** 2 for a, b in zip(color1, color2)) ** 0.5

def run_boss():
    logger.info("=" * 80)
    logger.info(" " * 30 + "Starting boss runs" + " " * 30)
    CLAIM_BUTTON_POSITION = (956, 693)
    CLOSE_AFK_WARNING_POSITION = (956, 703)
    RESPAWN_BUTTON_POSITION = (882, 573)
    RESPAWN_TOME_POSITION = (882, 573)
    START_BUTTON_POSITION = (846, 721)

    times = 0
    while times < TICKETS_MAX_AMOUNT:
        run_start = time.time()
        logger.info(f"Starting run {times}")
        ahk.win_activate("Roblox")
        ahk.key_down("s")
        time.sleep(1)
        ahk.key_up("s")
        # save a screenshot of the screen before claiming rewards
        pic_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        pyautogui.screenshot(f"{OUTPUT_FOLDER}/{pic_time}.png")
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
        ahk.mouse_move(*CLAIM_BUTTON_POSITION)
        ahk.click()
        time.sleep(0.3)
        ahk.mouse_move(*CLOSE_AFK_WARNING_POSITION)
        ahk.click()
        time.sleep(0.3)
        logger.info(f"Run {times} took {time.time() - run_start} seconds")
        time.sleep(5)


def run_minigame():

    times = 0
    logger.info("=" * 80)
    logger.info(" " * 30 + "Starting minigame runs" + " " * 30)
    while times < TICKETS_MAX_AMOUNT:
        run_start = time.time()
        logger.info(f"Starting minigame run {times}")
        start_minigame(MINIGAME_PET_POSITION_ROW, MINIGAME_PET_POSITION_COLUMN)
        play_miniagme()
        times += 1
        logger.info(f"Run {times} took {time.time() - run_start} seconds")
        time.sleep(5)


start_text = f"""{colorama.Fore.GREEN}

███████╗██████╗ ███╗   ███╗ █████╗  ██████╗██████╗  ██████╗ 
██╔════╝██╔══██╗████╗ ████║██╔══██╗██╔════╝██╔══██╗██╔═══██╗
█████╗  ██║  ██║██╔████╔██║███████║██║     ██████╔╝██║   ██║
██╔══╝  ██║  ██║██║╚██╔╝██║██╔══██║██║     ██╔══██╗██║   ██║
███████╗██████╔╝██║ ╚═╝ ██║██║  ██║╚██████╗██║  ██║╚██████╔╝
╚══════╝╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝                                              
{colorama.Fore.RED}For Pet Catchers. version: 0.0.1 {colorama.Style.RESET_ALL}

Welcome to Edmacro - The best macro for Pet Catchers.
This script will help you to catch pets on Roblox game.
Your current configuration is:
 - Game Duration: {colorama.Fore.GREEN} 60 seconds {colorama.Style.RESET_ALL}
 - Minigame Pet Position: {colorama.Fore.GREEN}(2, 2) {colorama.Style.RESET_ALL}
 - Max tickets per run: {colorama.Fore.GREEN} 1 {colorama.Style.RESET_ALL}
 - Should play minigame: {colorama.Fore.GREEN if SHOULD_PLAY_MINIGAME else colorama.Fore.RED} {SHOULD_PLAY_MINIGAME} {colorama.Style.RESET_ALL}
"""


def main(skip_start_text=False):
    if not skip_start_text:
        logger.info(start_text)
    else:
        logger.info("Starting another block of runs...")

    start_time = time.time()
    activate_roblox()
    restart_char()
    up_camera()
    go_to_boss()
    run_boss()
    if SHOULD_PLAY_MINIGAME:
        restart_char()
        up_camera()
        go_to_minigame()
        run_minigame()
        main(skip_start_text=True)
    logger.info(f"Total time: {time.time() - start_time} seconds. Finished!")


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
        - Tickets max Amount: {TICKETS_MAX_AMOUNT}
        - Should play minigame: {SHOULD_PLAY_MINIGAME}
        - Minigame pet position: ({MINIGAME_PET_POSITION_ROW}, {MINIGAME_PET_POSITION_COLUMN})
        Do you want to start the macro?""",
        buttons=MsgBoxButtons.YES_NO,
    )
    if result == "Yes":
        main()
        # for _ in range(8):
            # activate_roblox()
            # start_minigame(1, 5)
            # play_miniagme()
    else:
        raise SystemExit
