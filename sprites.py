import win32api

import manager
from config import *


class TanukiSprite(pg.sprite.Sprite):
    def __init__(self, path_root: pathlib.Path, rect_no_entry, pos_center=(0, 0)):
        super().__init__(self.containers)
        self.image = None
        self.rect = pg.Rect(0, 0, 0, 0)
        self.rect.center = pos_center

        self.path_root = path_root
        self.manager_anime = None
        self.manager_action = None

        self.init_manager(rect_no_entry)

    def init_manager(self, rect_no_entry):
        self.manager_anime = manager.AnimationManager(self.path_root, WALK)
        self.set_image()
        duration_image = self.manager_anime.get_duration_cur()
        self.manager_action = manager.ActionManager(self.rect, rect_no_entry, duration_image)

    def update(self) -> None:
        self.set_image()
        self.manager_action.set_duration_image(self.manager_anime.get_duration_cur())
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
            self.scale_rect(True)
            if self.rect.collidepoint(*event.pos):
                self.manager_anime.load_animation_in_folder(self.path_root / "drag&drop")
                self.set_image()
                self.manager_action.change_mode(event, "drag&drop")
                for con in self.containers:
                    con.remove(self)
                    con.add(self)

                self.scale_rect(False)
                return True

            self.scale_rect(False)

        elif self.manager_action.mode == "drag&drop":
            mode = self.manager_action.change_mode()
            self.load_animation(mode)
            return True

        return False

    def fix_position(self, event) -> bool:
        if not event.is_pressed:
            return False

        if self.rect.collidepoint(*event.pos):
            self.manager_action.switch_fixed()
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
        self.rect.size = self.image.get_size()
        self.rect.center = center

    def scale_rect(self, is_minimize):
        center = self.rect.center
        rate_scale = RATE_RECT_MINIMIZE if is_minimize else 1
        self.rect.size = [int(s * rate_scale) for s in self.image.get_size()]
        self.rect.center = center

    def set_no_entry(self, rect_no_entry):
        self.manager_action.set_no_entry(rect_no_entry)


class IkuNoEntrySprite(pg.sprite.Sprite):
    COLOR_BORDER = (255, 0, 0)
    COLOR_KEY_NO_ENTRY = (1, 9, 0)
    WIDTH_BORDER = 3
    SIGHT_LENGTH = 10

    def __init__(self):
        super().__init__(self.containers)
        self.pos_start = None
        self.is_setting_area = False
        self.rect = pg.Rect(0, 0, 100, 100)
        self.image = None

        self.manager_animation = manager.AnimationManager(PATH_IMAGE_IKUNOENTRY)
        self.manager_animation.scale_rate_zoom(dy=-5)

        self.rect.size = self.manager_animation.get_image_display().get_size()

    def update(self):
        if not self.is_setting_area:
            self.set_image_before()
        else:
            self.set_image_after()

    def set_image_before(self):
        pos_cursor = win32api.GetCursorPos()
        pos_cursor = (pos_cursor[0], pos_cursor[1] - HEIGHT_CAPTION)
        sp_ikuno = self.manager_animation.get_image_display()
        pos_topleft = (pos_cursor[0] - self.SIGHT_LENGTH,
                       pos_cursor[1] - self.SIGHT_LENGTH)
        self.rect.topleft = pos_topleft
        self.image = sp_ikuno
        pg.draw.line(self.image, self.COLOR_BORDER,
                     (self.SIGHT_LENGTH, 0), (self.SIGHT_LENGTH, 2 * self.SIGHT_LENGTH),
                     self.WIDTH_BORDER)
        pg.draw.line(self.image, self.COLOR_BORDER,
                     (0, self.SIGHT_LENGTH), (2 * self.SIGHT_LENGTH, self.SIGHT_LENGTH),
                     self.WIDTH_BORDER)

    def set_image_after(self):
        pos_cursor = win32api.GetCursorPos()
        pos_cursor = (pos_cursor[0], pos_cursor[1] - HEIGHT_CAPTION)
        sp_ikuno = self.manager_animation.get_image_display()
        self.resize_rect(pos_cursor)
        width_rect, height_rect = self.rect.size
        width_ikuno, height_ikuno = sp_ikuno.get_size()
        surface_no_entry = pg.Surface(self.rect.size)
        surface_no_entry.fill(COLOR_KEY_GAME)

        self.image = pg.Surface((width_rect + width_ikuno, height_rect + height_ikuno))
        self.image.set_colorkey(self.COLOR_KEY_NO_ENTRY)
        self.image.fill(self.COLOR_KEY_NO_ENTRY)
        self.image.blit(surface_no_entry, (0, 0))
        pg.draw.rect(self.image, self.COLOR_BORDER, (0, 0, *self.rect.size), self.WIDTH_BORDER)
        self.image.blit(sp_ikuno, self.rect.size)

    # タスクバー上というか
    def on_mouse(self, event):
        if not event.button == BUTTON_LEFT:
            return

        if event.is_pressed:
            self.pos_start = event.pos
            self.is_setting_area = True
        else:
            sp_ikuno = self.manager_animation.get_image_display()
            pos_cursor = event.pos
            self.resize_rect(pos_cursor)
            self.kill()
            return self.rect

    def resize_rect(self, pos_cursor):
        width, height = [br - tl for tl, br in zip(self.pos_start, pos_cursor)]
        x, y = self.pos_start
        self.rect.left = x if width >= 0 else x - abs(width)
        self.rect.top = y if height >= 0 else y - abs(height)
        self.rect.size = (abs(width), abs(height))
