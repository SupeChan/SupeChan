from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
import pygame as pg
import win32api

from config import *
import ctypes

# dpiのスケーリングを無効にする
PROCESS_PER_MONITOR_DPI_AWARE = 2
ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)


class PGMouseListener:
    def __init__(self):
        self.listener = None

    def start(self):
        self.listener = MouseListener(on_move=None, on_click=self.on_click,
                                      on_scroll=self.on_scroll)
        self.listener.start()

    def stop(self):
        self.listener.stop()

    def on_click(self, x, y, button, is_pressed):
        pos = (x, y)
        event_mouse = pg.event.Event(pg.USEREVENT, type_user=TYPE_USER_CLICK, pos=pos,
                                     button=button,
                                     is_pressed=is_pressed)
        pg.event.post(event_mouse)

    def on_scroll(self, x, y, dx, dy):
        pos = (x, y)
        event_mouse = pg.event.Event(pg.USEREVENT, type_user=TYPE_USER_SCROLL, pos=pos, dy=dy)
        pg.event.post(event_mouse)


class PGKeyboardListener:
    def __init__(self):
        self.listener = None

    def start(self):
        self.listener = KeyboardListener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def stop(self):
        self.listener.stop()

    def on_press(self, key):
        event_key = pg.event.Event(pg.USEREVENT, type_user=TYPE_USER_KEY, key=key, is_pressed=True)
        pg.event.post(event_key)

    def on_release(self, key):
        event_key = pg.event.Event(pg.USEREVENT, type_user=TYPE_USER_KEY, key=key, is_pressed=False)
        pg.event.post(event_key)


def test():
    pg.init()
    pg.display.set_mode((100, 100))
    clock = pg.time.Clock()

    lst_block = [pg.MOUSEBUTTONUP, pg.MOUSEBUTTONUP, pg.MOUSEMOTION, pg.MOUSEWHEEL,
                 pg.KEYUP, pg.KEYDOWN]

    for event_mouse in lst_block:
        pg.event.set_blocked(event_mouse)

    listener_mouse = PGMouseListener()
    listener_mouse.start()

    listener_key = PGKeyboardListener()
    listener_key.start()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return

            elif event.type == pg.USEREVENT:
                print(event)

        clock.tick(10)


if __name__ == '__main__':
    test()
