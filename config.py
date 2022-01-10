import pathlib
from pynput.mouse import Button
import pygame as pg
import sys

PATH_ICON = sys.prefix + "/image/Icon/SupeChan.ico"
COLOR_TRANSPARENT = (5, 6, 4)
FPS = 30

TYPE_USER_MOVE = 0
TYPE_USER_CLICK = 1
TYPE_USER_SCROLL = 2
TYPE_USER_KEY = 3
TYPE_USER_ENTER = 4
TYPES_INPUT_BLOCK = (pg.MOUSEMOTION, pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEWHEEL,
                     pg.KEYDOWN, pg.KEYUP)

BUTTON_LEFT = Button.left
BUTTON_RIGHT = Button.right
BUTTON_MIDDLE = Button.middle

WALK = "walk"
DANCE = "dance"
DRAGDROP = "drag&drop"
ACTIONS = [WALK, DANCE, DRAGDROP]

PATH_ROOT_TANUKI = pathlib.Path(sys.prefix + "/image/Tanuki")
PATH_RUDOLF = pathlib.Path(sys.prefix + "/image/Tanuki/シンボリルドルフ")
SUFFIXES_IMAGE = [".jpg", ".jpeg", ".gif", ".png"]
# 画像サイズの統一
HEIGHT_UNIFIED = 500
# 画像の内側に判定を縮小
RATE_RECT_MINIMIZE = 0.7

ZOOM_DEFAULT = 1
ZOOM_INTERVAL = 0.1
ZOOM_MIN = 0.1
ZOOM_MAX = 3

SET_DIRECT_ALL = set([i for i in range(0, 360)])
SET_DIRECT_BOTTOM = set([i for i in range(1, 180)])
SET_DIRECT_LEFT = set([i for i in range(91, 270)])
SET_DIRECT_TOP = set([i for i in range(181, 360)])
SET_DIRECT_RIGHT = set([i for i in range(0, 90)] + [j for j in range(271, 360)])
LST_SET_DIRECT = [SET_DIRECT_TOP, SET_DIRECT_RIGHT, SET_DIRECT_BOTTOM, SET_DIRECT_LEFT]
EDGES_ATTR = ["top", "right", "bottom", "left"]
