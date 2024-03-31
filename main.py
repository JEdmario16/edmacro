import PIL
import os
import pyautogui
import time
import win32gui
import win32con
from typing import Optional
from loguru import logger
from ahk import AHK
from datetime import datetime

ahk = AHK()


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

    RESPAWN_BUTTON = PIL.Image.open("edmacro/assets/respawn_button.png")
    RESPAWN_TOME = PIL.Image.open("edmacro/assets/respawn_tome.png")
    START_BUTTON = PIL.Image.open("edmacro/assets/start.png")
    CLAIM_BUTTON = PIL.Image.open("edmacro/assets/claim.png")
    CLOSE_AFK_WARNING = PIL.Image.open("edmacro/assets/close.png")

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


def freeze_game(seconds):
    FREEZE_BUTTON = PIL.Image.open("edmacro/assets/freeze.png")
    logger.info(f"Freezing game for {seconds} seconds")
    box = pyautogui.locateCenterOnScreen(FREEZE_BUTTON, confidence=0.95)
    pyautogui.moveTo(box)
    pyautogui.mouseDown()
    time.sleep(seconds)
    pyautogui.moveTo(100, 30, duration=0.3)
    pyautogui.mouseUp()


CLAIM_BUTTON_POSITION = (956, 693)
CLOSE_AFK_WARNING_POSITION = (956, 703)
RESPAWN_BUTTON_POSITION = (882, 573)
RESPAWN_TOME_POSITION = (882, 573)
START_BUTTON_POSITION = (846, 721)


def run_boss():
    times = 0
    while True:
        run_start = time.time()
        logger.info(f"Starting run {times}")
        ahk.win_activate("Roblox")
        ahk.key_down("w")
        time.sleep(1)
        ahk.key_up("w")
        # save a screenshot of the screen before claiming rewards
        pyautogui.screenshot(f"images/({datetime.now()})before_claim.png")
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
        freeze_game(90)
        times += 1
        logger.info("Waiting exit from boss room")
        time.sleep(15)
        logger.info(f"Run {times} took {time.time() - run_start} seconds")


time.sleep(2)
run_boss()
