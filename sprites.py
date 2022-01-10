import pathlib
import pygame as pg
import random
import math
import win32api, win32gui, win32con
from pynput.keyboard import Key

import manager
from config import *


class TanukiSprite(pg.sprite.Sprite):
    def __init__(self, path_root: pathlib.Path, pos_center=(0, 0)):
        super().__init__(self.containers)
        self.image = None
        self.rect = pg.Rect(0, 0, 0, 0)
        self.rect.center = pos_center

        self.path_root = path_root
        self.manager_anime = None
        self.manager_action = None

        self.init_manager()

    def init_manager(self):
        self.manager_anime = manager.AnimationManager(self.path_root)
        self.set_image()
        self.manager_action = manager.ActionManager(self.rect)

    def update(self) -> None:
        self.set_image()
        self.rect, mode_changed = self.manager_action.update(self.rect)
        self.manager_anime.set_flip(self.manager_action.get_is_flip_x())

        if mode_changed:
            self.load_animation(mode_changed)

    def on_mouse(self, event) -> bool:
        is_target = False
        if event.type_user == TYPE_USER_CLICK:
            if event.button == BUTTON_LEFT:
                is_target = self.drag_and_drop(event)
            elif event.button == BUTTON_RIGHT:
                is_target = self.fix_position(event)
            elif event.button == BUTTON_MIDDLE:
                is_target = self.remove_screen(event)
        elif event.type_user == TYPE_USER_SCROLL:
            is_target = self.scroll_wheel(event)

        return is_target

    def drag_and_drop(self, event) -> bool:
        if event.is_pressed:
            if self.rect.collidepoint(*event.pos):
                self.manager_anime.load_animation_in_folder(self.path_root / "drag&drop")
                self.set_image()
                self.manager_action.change_mode(event, "drag&drop")
                for con in self.containers:
                    con.remove(self)
                    con.add(self)

                return True

        elif self.manager_action.mode == "drag&drop":
            mode = self.manager_action.change_mode()
            self.load_animation(mode)
            return True

        return False

    def fix_position(self, event) -> bool:
        if not event.is_pressed:
            return False

        if self.rect.collidepoint(*event.pos):
            self.manager_action.fix_position()
            return True

        return False

    def remove_screen(self, event) -> bool:
        if not event.is_pressed:
            return False

        if self.rect.collidepoint(*event.pos):
            self.kill()
            return True

    def scroll_wheel(self, event):
        if self.rect.collidepoint(event.pos):
            self.manager_anime.scale_rate_zoom(event.dy)
            return True

        return False

    def load_animation(self, mode):
        self.manager_anime.load_animation_in_folder(self.path_root / mode)
        self.set_image()

    def set_image(self):
        center = self.rect.center
        self.image = self.manager_anime.get_image_display()
        self.rect.size = self.rect.size = [int(s * RATE_RECT_MINIMIZE) for s in
                                           self.image.get_size()]
        self.rect.center = center

    def scale_rect(self, is_minimize):
        center = self.rect.center
        rate_scale = RATE_RECT_MINIMIZE if is_minimize else 1
        self.rect.size = [int(s * rate_scale) for s in self.image.get_size()]
        self.rect.center = center
