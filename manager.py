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
    def __init__(self, path_root: pathlib.Path, mode_init=""):
        self.path_root = path_root

        self.gen_image = None
        self.gen_duration = None
        self.image_cur = None
        self.duration_cur = 0
        self.ticks_animated = -1

        self.rate_zoom = ZOOM_DEFAULT
        self.is_flip_x = False
        self.is_flip_y = False

        path_image_init = self.select_random_image(self.path_root / mode_init)
        self.load_animation(path_image_init)

    def select_random_image(self, path_folder: pathlib.Path) -> pathlib.Path:
        lst_path = [path_image for path_image in path_folder.glob("**/*.*")
                    if path_image.suffix.lower() in SUFFIXES_IMAGE_TANUKI]
        path_selected = random.choice(lst_path)
        return path_selected

    def load_animation(self, path_image: pathlib.Path) -> None:
        image_load = Image.open(path_image)
        lst_image = ([image_frame.copy() for image_frame in ImageSequence.Iterator(image_load)]
                     if image_load.is_animated else
                     [image_load])

        lst_surface = []
        lst_duration = []
        for image_frame in lst_image:
            image_pil = image_frame.convert("RGBA")
            mode, size, data = image_pil.mode, image_pil.size, image_pil.tobytes()
            surface_frame = pg.image.fromstring(data, size, mode).convert_alpha()
            width, height = surface_frame.get_size()
            rate_unified = HEIGHT_UNIFIED / height
            size_unified = (int(width * rate_unified), HEIGHT_UNIFIED)
            surface_frame = pg.transform.smoothscale(surface_frame, size_unified)
            lst_surface.append(surface_frame)
            duration = image_frame.info["duration"] if image_load.is_animated else 0
            lst_duration.append(duration)

        self.gen_image = itertools.cycle(lst_surface)
        self.gen_duration = itertools.cycle(lst_duration)
        self.image_cur = next(self.gen_image)
        self.duration_cur = next(self.gen_duration)
        self.ticks_animated = pg.time.get_ticks()

    def load_animation_in_folder(self, path_mode: pathlib.Path):
        path_image = self.select_random_image(path_mode)
        self.load_animation(path_image)

    def get_image_display(self) -> pg.Surface:
        if self.has_over_duration():
            self.image_cur = next(self.gen_image)
            self.duration_cur = next(self.gen_duration)
            self.ticks_animated = pg.time.get_ticks()

        size_zoom = [int(s * self.rate_zoom) for s in self.image_cur.get_size()]
        image_zoom = pg.transform.smoothscale(self.image_cur, size_zoom)
        image_display = pg.transform.flip(image_zoom, self.is_flip_x, self.is_flip_y)
        return image_display

    def has_over_duration(self) -> bool:
        ticks_passed = pg.time.get_ticks() - self.ticks_animated
        return ticks_passed >= self.duration_cur

    def scale_rate_zoom(self, dy) -> None:
        rate_zoom = self.rate_zoom + ZOOM_INTERVAL * dy
        self.rate_zoom = np.clip(rate_zoom, ZOOM_MIN, ZOOM_MAX)

    def set_flip(self, is_flip_x, is_flip_y=False):
        self.is_flip_x = is_flip_x
        self.is_flip_y = is_flip_y

    def get_duration_cur(self):
        return self.duration_cur


class ActionManager:
    MODE_WALK = "walk"
    MODE_DANCE = "dance"
    MODE_DRAG = "drag&drop"
    LST_MODE = [MODE_WALK, MODE_DANCE]

    SPEED_WALK = 10000
    DURATION_MIN = 10000
    DURATION_MAX = 15000

    def __init__(self, rect, rect_no_entry, duration_image):
        self.mode = self.MODE_WALK
        self.rect = rect
        self.rect_screen = pg.Rect(0, 0, *pg.display.get_window_size())
        self.rect_no_entry = rect_no_entry
        self.duration_image = duration_image

        self.speed = self.SPEED_WALK / FPS / duration_image
        self.direction = 0
        self.pos_delta = (0, 0)
        self.is_fixed = False

        self.ticks_changed = pg.time.get_ticks()
        self.duration_mode = random.randint(self.DURATION_MIN, self.DURATION_MAX)

    def update(self, rect):
        if self.mode == self.MODE_DRAG:
            self.drag_and_drop()
            return self.rect, None

        if self.mode == self.MODE_WALK:
            self.move(rect)
        elif self.mode == self.MODE_DANCE:
            # self.dance(rect)
            pass

        mode_changed = None
        if pg.time.get_ticks() - self.ticks_changed >= self.duration_mode:
            mode_changed = self.change_mode()

        self.clamp_screen()
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
            self.set_direction(self.rect_screen)
            self.duration_mode = random.randint(self.DURATION_MIN, self.DURATION_MAX)

        elif self.mode == self.MODE_DRAG:
            self.duration_mode = 0
            self.pos_delta = [pos_event - pos_rect for pos_rect, pos_event in
                              zip(self.rect.center, event.pos)]

        self.ticks_changed = pg.time.get_ticks()

        return self.mode

    def move(self, rect) -> (pg.Rect, bool):
        self.speed = 0 if self.is_fixed else self.SPEED_WALK / FPS / self.duration_image
        vx, vy = (int(self.speed * math.cos(math.radians(self.direction))),
                  int(self.speed * math.sin(math.radians(self.direction))))
        rect.move_ip(vx, vy)
        if self.rect_no_entry and self.rect_no_entry.colliderect(self.rect):
            self.set_direction(self.rect_no_entry)

        if not self.rect_screen.contains(self.rect):
            self.set_direction(self.rect_screen)

        return self.rect

    # 進行方向のセット
    def set_direction(self, rect_collide) -> None:
        edges_collide = EDGES_COLLIDE_SCREEN if rect_collide is self.rect_screen else EDGES_COLLIDE_NO_ENTRY
        rect_clip = self.rect.clip(rect_collide)
        mask_collide = [getattr(rect_clip, edge) == getattr(rect_collide, edge)
                        for edge in edges_collide]
        lst_set_drop = [set_direct for set_direct, is_collide
                        in zip(LST_SET_DIRECT, mask_collide) if is_collide]

        set_direction = SET_DIRECT_ALL
        for set_drop in lst_set_drop:
            set_direction = set_direction - set_drop

        if not set_direction:
            self.direction = random.choice(list(SET_DIRECT_ALL))
            return

        self.direction = random.choice(list(set_direction))
        return

    def drag_and_drop(self):
        pos_cursor = win32api.GetCursorPos()
        pos_cursor = (pos_cursor[0], pos_cursor[1] - HEIGHT_CAPTION)
        pos = [point_cursor - point_delta for point_cursor, point_delta in
               zip(pos_cursor, self.pos_delta)]
        self.rect.center = pos

    def switch_fixed(self):
        self.is_fixed = not self.is_fixed

    def clamp_screen(self):
        self.rect.clamp_ip(self.rect_screen)
        if self.rect_no_entry and self.rect_no_entry.colliderect(self.rect):
            rect_nearest = self.get_rect_screen_nearest()
            self.rect.clamp_ip(rect_nearest)

        if not self.rect_screen.contains(self.rect):
            rect_opened = self.get_rect_screen_opened()
            self.rect.clamp_ip(rect_opened)

    def get_is_flip_x(self):
        # if not self.mode == self.MODE_WALK:
        #     return False

        is_flip_x = False if math.cos(math.radians(self.direction)) < 0 else True
        is_flip_y = True if math.sin(math.radians(self.direction)) < 0 else False
        return is_flip_x

    def set_no_entry(self, rect_no_entry=None):
        self.rect_no_entry = rect_no_entry

    def set_duration_image(self, duration_image):
        self.duration_image = duration_image

    # 進入禁止エリアに隣接する、たぬきから最も近い範囲
    def get_rect_screen_nearest(self) -> pg.Rect:
        nd_near = np.array([self.rect_no_entry.bottom - self.rect.top,
                            self.rect.right - self.rect_no_entry.left,
                            self.rect.bottom - self.rect_no_entry.top,
                            self.rect_no_entry.right - self.rect.left])
        edge_nearest = EDGES_COLLIDE_NO_ENTRY[np.argmin(nd_near)]
        rect_nearest = self.rect_screen.copy()
        if edge_nearest == "top":
            rect_nearest.bottom = self.rect_no_entry.top - 1
        elif edge_nearest == "right":
            rect_nearest.left = self.rect_no_entry.right + 1
        elif edge_nearest == "bottom":
            rect_nearest.top = self.rect_no_entry.bottom + 1
        elif edge_nearest == "left":
            rect_nearest.right = self.rect_no_entry.left - 1

        return rect_nearest

    # 進入禁止に隣接する、最も大きな範囲
    def get_rect_screen_opened(self) -> pg.Rect:
        if not self.rect_no_entry:
            return self.rect_screen

        nd_margin = np.array([self.rect_no_entry.top,
                              self.rect_screen.width - self.rect_no_entry.right,
                              self.rect_screen.height - self.rect_no_entry.bottom,
                              self.rect_no_entry.left])
        edge_margin = EDGES_COLLIDE_SCREEN[np.argmax(nd_margin)]

        rect_margin = self.rect_screen.copy()
        if edge_margin == "top":
            rect_margin.bottom = self.rect_no_entry.top - 1
        elif edge_margin == "right":
            rect_margin.left = self.rect_no_entry.right + 1
        elif edge_margin == "bottom":
            rect_margin.top = self.rect_no_entry.bottom + 1
        elif edge_margin == "left":
            rect_margin.right = self.rect_no_entry.left - 1

        return rect_margin
