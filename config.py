import pathlib
from pynput.mouse import Button
import pygame as pg
import sys
import os
import winreg
import win32api, win32gui, win32con
import ctypes

# ディスプレイ
PROCESS_PER_MONITOR_DPI_AWARE = 2
INFO_MONITOR_SCALED = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0)))
ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
INFO_MONITOR_FULL = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0)))
WIDTH_SCALED = INFO_MONITOR_SCALED.get("Monitor")[2]
WIDTH_DISPLAY, HEIGHT_DISPLAY = (INFO_MONITOR_FULL.get("Monitor")[2],
                                 INFO_MONITOR_FULL.get("Monitor")[3])
RATE_SCALED = WIDTH_DISPLAY / WIDTH_SCALED

RATE_DPI2PIXEL = -15
path_window = r"Control Panel\Desktop\WindowMetrics"
key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, path_window)
HEIGHT_CAPTION = int(int(winreg.QueryValueEx(key, 'CaptionHeight')[0])
                     / RATE_DPI2PIXEL * RATE_SCALED)
winreg.CloseKey(key)

AREA_WORKING = INFO_MONITOR_FULL.get("Work")
WIDTH_WORKING, HEIGHT_WORKING = AREA_WORKING[2], AREA_WORKING[3]
SIZE_WORKING = (WIDTH_WORKING, HEIGHT_WORKING)
SIZE_SCREEN = (WIDTH_WORKING, HEIGHT_WORKING - HEIGHT_CAPTION)

# プリセットパス
PATH_FOLDER_IMAGE = pathlib.Path(sys.prefix) / "image"
PATH_ICON = PATH_FOLDER_IMAGE / "Icon/SupeChan.ico"
PATH_FOLDER_TANUKI = PATH_FOLDER_IMAGE / "Tanuki"
PATH_IMAGE_IKUNOENTRY = PATH_FOLDER_IMAGE / "IkuNoEntry"
PATH_FOLDER_MENU = PATH_FOLDER_IMAGE / r"BackGround\Menu"
PATH_FOLDER_ROAD = PATH_FOLDER_MENU / r"Background"
PATH_FOLDER_MENU_TANUKI = PATH_FOLDER_MENU / r"Tanuki_Bg"
PATH_FOLDER_MEMO = PATH_FOLDER_IMAGE / r"Background\Memo"
PATH_SPECIAL_WEEK = PATH_FOLDER_TANUKI / "スペシャルウィーク"

COLOR_KEY_GAME = (5, 6, 4)
FPS = 30

# pygame用イベント定数
TYPES_INPUT_BLOCK = (pg.MOUSEMOTION, pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEWHEEL,
                     pg.KEYDOWN, pg.KEYUP)

TYPE_USER_MOVE = "user_move"
TYPE_USER_CLICK = "user_click"
TYPE_USER_SCROLL = "user_scroll"
TYPES_MOUSE = [TYPE_USER_MOVE, TYPE_USER_CLICK, TYPE_USER_SCROLL]

TYPE_USER_KEYBOARD = "user_keyboard"
TYPES_KEYBOARD = [TYPE_USER_KEYBOARD]

TYPE_SYSTEM_ENTER = "system_enter"
TYPE_SYSTEM_CREATE_NO_ENTRY = "system_create_no_entry"
TYPE_SYSTEM_SET_NO_ENTRY = "system_set_no_entry"
TYPE_SYSTEM_RELEASE_NO_ENTRY = "system_release_no_entry"
TYPES_SYSTEM = [TYPE_SYSTEM_ENTER, TYPE_SYSTEM_CREATE_NO_ENTRY, TYPE_SYSTEM_RELEASE_NO_ENTRY]

# PGMouseListener用のボタン定数
BUTTON_LEFT = Button.left
BUTTON_RIGHT = Button.right
BUTTON_MIDDLE = Button.middle

# Tanukiのアクションモード
WALK = "WALK"
DANCE = "DANCE"
DRAGDROP = "DRAG&DROP"
ACTIONS = [WALK, DANCE, DRAGDROP]

SUFFIXES_IMAGE_TANUKI = [".gif", ".png"]
SUFFIXES_IMAGE_MEMO = [".jpeg", ".jpg", ".png"]
# 画像サイズの統一
HEIGHT_UNIFIED = 500
# 画像の内側に判定を縮小
RATE_RECT_MINIMIZE = 0.7

# たぬき画像の縮小倍率
ZOOM_DEFAULT = 1
ZOOM_INTERVAL = 0.1
ZOOM_MIN = 0.1
ZOOM_MAX = 3

# walk中の方向制御
SET_DIRECT_ALL = set([i for i in range(0, 360)])
SET_DIRECT_BOTTOM = set([i for i in range(1, 180)])
SET_DIRECT_LEFT = set([i for i in range(91, 270)])
SET_DIRECT_TOP = set([i for i in range(181, 360)])
SET_DIRECT_RIGHT = set([i for i in range(0, 90)] + [j for j in range(271, 360)])
LST_SET_DIRECT = [SET_DIRECT_TOP, SET_DIRECT_RIGHT, SET_DIRECT_BOTTOM, SET_DIRECT_LEFT]
EDGES_COLLIDE_SCREEN = ["top", "right", "bottom", "left"]
EDGES_COLLIDE_NO_ENTRY = ["bottom", "left", "top", "right"]
