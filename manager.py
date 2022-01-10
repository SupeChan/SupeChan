from PIL import Image, ImageSequence
import pathlib
import random
import itertools
import math
import numpy as np
import pygame as pg
import win32api

from config import *


class AnimationManager:
    def __init__(self, path_root: pathlib.Path):
        self.path_root = path_root

        self.gen_image = None
        self.image_cur = None
        self.duration = 0
        self.ticks_animated = -1

        self.rate_zoom = ZOOM_DEFAULT
        self.is_flip_x = False
        self.is_flip_y = False

        path_image_init = self.select_random_image(self.path_root / WALK)
        self.load_animation(path_image_init)

    def select_random_image(self, path_folder: pathlib.Path) -> pathlib.Path:
        lst_path = [path_image for path_image in path_folder.glob("**/*.*")
                    if path_image.suffix.lower() in SUFFIXES_IMAGE]
        ix = random.randint(0, len(lst_path) - 1)
        path_selected = pathlib.Path(lst_path[ix])
        return path_selected

    def load_animation(self, path_image: pathlib.Path) -> None:
        image_load = Image.open(path_image)
        lst_image = ([image_frame.copy() for image_frame in ImageSequence.Iterator(image_load)]
                     if image_load.is_animated else
                     [image_load])

        lst_surface = []
        for image_frame in lst_image:
            image_pil = image_frame.convert("RGBA")
            mode, size, data = image_pil.mode, image_pil.size, image_pil.tobytes()
            surface_frame = pg.image.fromstring(data, size, mode).convert_alpha()
            width, height = surface_frame.get_size()
            rate_unified = HEIGHT_UNIFIED / height
            size_unified = (int(width * rate_unified), HEIGHT_UNIFIED)
            surface_frame = pg.transform.smoothscale(surface_frame, size_unified)
            lst_surface.append(surface_frame)

        self.gen_image = itertools.cycle(lst_surface)
        self.image_cur = next(self.gen_image)
        self.duration = image_load.info["duration"] if image_load.is_animated else 0
        self.ticks_animated = pg.time.get_ticks()

    def load_animation_in_folder(self, path_mode: pathlib.Path):
        path_image = self.select_random_image(path_mode)
        self.load_animation(path_image)

    def get_image_display(self) -> pg.Surface:
        if self.has_over_duration():
            image_cur = next(self.gen_image)
            self.image_cur = image_cur
            self.ticks_animated = pg.time.get_ticks()

        size_zoom = [int(s * self.rate_zoom) for s in self.image_cur.get_size()]
        image_zoom = pg.transform.smoothscale(self.image_cur, size_zoom)
        image_display = pg.transform.flip(image_zoom, self.is_flip_x, self.is_flip_y)
        return image_display

    def has_over_duration(self) -> bool:
        ticks_passed = pg.time.get_ticks() - self.ticks_animated
        return ticks_passed >= self.duration

    def scale_rate_zoom(self, dy) -> None:
        rate_zoom = self.rate_zoom + ZOOM_INTERVAL * dy
        self.rate_zoom = np.clip(rate_zoom, ZOOM_MIN, ZOOM_MAX)

    def set_flip(self, is_flip_x, is_flip_y=False):
        self.is_flip_x = is_flip_x
        self.is_flip_y = is_flip_y


class ActionManager:
    MODE_WALK = "walk"
    MODE_DANCE = "dance"
    MODE_DRAG = "drag&drop"

    LST_MODE = [MODE_WALK, MODE_DANCE]

    SPEED_WALK = 150
    SPEED_RUN = 10

    DURATION_MIN = 10000
    DURATION_MAX = 15000

    def __init__(self, rect):
        self.mode = self.MODE_WALK
        self.rect = rect
        self.rect_screen = pg.Rect(0, 0, *pg.display.get_window_size())

        self.ticks_changed = pg.time.get_ticks()
        self.duration_mode = random.randint(self.DURATION_MIN, self.DURATION_MAX)

        self.speed = self.SPEED_WALK / FPS
        self.direction = 0
        self.pos_delta = (0, 0)

    def update(self, rect):
        if self.mode == self.MODE_DRAG:
            pos = [pos_cursor - pos_delta for pos_cursor, pos_delta in
                   zip(win32api.GetCursorPos(), self.pos_delta)]
            self.rect.center = pos
            return self.rect, None

        if self.mode == self.MODE_WALK:
            self.move(rect)
        elif self.mode == self.MODE_DANCE:
            # self.dance(rect)
            pass

        mode_changed = None
        if pg.time.get_ticks() - self.ticks_changed >= self.duration_mode:
            mode_changed = self.change_mode()

        self.rect = self.rect.clamp(self.rect_screen)
        return self.rect, mode_changed

    def change_mode(self, event=None, mode_select=None):
        # モード変更
        if mode_select:
            self.mode = mode_select
        else:
            lst_mode = self.LST_MODE.copy()
            if self.mode in lst_mode:
                lst_mode.remove(self.mode)
            self.mode = random.choice(lst_mode)

        if self.mode in [self.MODE_WALK, self.MODE_DANCE]:
            self.set_direction()
            self.duration_mode = random.randint(self.DURATION_MIN, self.DURATION_MAX)

        elif self.mode == self.MODE_DRAG:
            self.direction = 0
            self.duration_mode = 0
            self.pos_delta = [pos_event - pos_rect for pos_rect, pos_event in
                              zip(self.rect.center, event.pos)]

        self.ticks_changed = pg.time.get_ticks()

        return self.mode

    def move(self, rect) -> (pg.Rect, bool):
        vx, vy = (int(self.speed * math.cos(math.radians(self.direction))),
                  int(self.speed * math.sin(math.radians(self.direction))))

        rect.move_ip(vx, vy)
        if not self.rect_screen.contains(self.rect):
            self.set_direction()
            if self.direction is None:
                self.rect.center = self.rect_screen.center
                self.set_direction()
                return self.rect

        return self.rect

    # 進行方向のセット
    def set_direction(self) -> None:
        rect_clip = self.rect.clip(self.rect_screen)
        mask_collide = [getattr(rect_clip, edge) == getattr(self.rect_screen, edge)
                        for edge in EDGES_ATTR]
        lst_set_drop = [set_direct for set_direct, is_collide
                        in zip(LST_SET_DIRECT, mask_collide) if is_collide]

        set_direction = SET_DIRECT_ALL
        for set_drop in lst_set_drop:
            set_direction = set_direction - set_drop

        if not set_direction:
            self.direction = None
            return

        direction_reflect = random.choice(list(set_direction))
        self.direction = direction_reflect
        return

    def drag_and_drop(self, rect):
        pos = [pos_cursor - pos_delta for pos_cursor, pos_delta in
               zip(win32api.GetCursorPos(), self.pos_delta)]
        self.rect.center = pos

    def fix_position(self):
        self.speed = 0 if self.speed > 0 else self.SPEED_WALK / FPS

    def get_is_flip_x(self):
        if not self.mode == self.MODE_WALK:
            return False

        is_flip_x = False if math.cos(math.radians(self.direction)) < 0 else True
        is_flip_y = True if math.sin(math.radians(self.direction)) < 0 else False
        return is_flip_x
