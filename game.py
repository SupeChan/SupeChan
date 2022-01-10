from contextlib import contextmanager
import pygame as pg
import win32api, win32gui, win32con

import listener
import sprites
from config import *


class SpecialGame:
    def __init__(self):
        self.rect_screen = None
        self.screen = None
        self.background = None
        self.clock = pg.time.Clock()

        self.group_all = None
        self.group_mouse = None
        self.group_keyboard = None

        self.listener_mouse = None
        self.listener_keyboard = None

        self.init_display()
        self.init_containers()
        self.set_gwl_exstyle()
        self.set_listener()

    def main(self):
        sprites.TanukiSprite(PATH_RUDOLF, self.rect_screen.center)
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return

                elif event.type == pg.USEREVENT:
                    if event.type_user in [TYPE_USER_CLICK, TYPE_USER_SCROLL]:
                        self.on_mouse(event)
                    elif event.type_user in [TYPE_USER_KEY]:
                        self.on_keyboard(event)

                    elif event.type_user == TYPE_USER_ENTER:
                        sprites.TanukiSprite(event.path_tanuki)

                elif event.type == pg.DROPFILE:
                    pass

            self.update_display()

    # pgディスプレイの初期化
    def init_display(self):
        pg.init()
        info_display = pg.display.Info()
        self.rect_screen = pg.Rect(0, 0, info_display.current_w, info_display.current_h)
        self.screen = pg.display.set_mode(self.rect_screen.size, pg.NOFRAME)
        self.background = pg.Surface(self.rect_screen.size)
        self.background.fill(COLOR_TRANSPARENT)
        self.screen.blit(self.background, self.rect_screen.topleft)
        pg.display.update()
        icon = pg.image.load(PATH_ICON)
        pg.display.set_icon(icon)

    # 使用するスプライトのコンテナを設定
    def init_containers(self):
        self.group_all = pg.sprite.RenderUpdates()
        self.group_mouse = pg.sprite.Group()
        self.group_keyboard = pg.sprite.Group()

        sprites.TanukiSprite.containers = self.group_all, self.group_mouse

    # ウインドウスタイルの設定
    def set_gwl_exstyle(self):
        hwnd = pg.display.get_wm_info()["window"]

        # ウインドウを最前面に
        swp_topmost = (win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, swp_topmost)

        # 透過、入力不可の設定
        exstyle_extend = (win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) |
                          win32con.WS_EX_LAYERED |  # 透過設定を可能にする。
                          win32con.WS_DISABLED)  # ユーザー入力を受け付けない。
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exstyle_extend)

        # 透過色の設定
        color_key = win32api.RGB(*COLOR_TRANSPARENT)
        win32gui.SetLayeredWindowAttributes(hwnd, color_key, 0, win32con.LWA_COLORKEY)

    # マウス、キーボードの入力リスナーを設定
    def set_listener(self):
        for type_input in TYPES_INPUT_BLOCK:
            pg.event.set_blocked(type_input)

        self.listener_mouse = listener.PGMouseListener()
        self.listener_keyboard = listener.PGKeyboardListener()
        self.listener_mouse.start()
        self.listener_keyboard.start()

    def on_mouse(self, event):
        for sp in self.group_mouse.sprites()[::-1]:
            is_target = sp.on_mouse(event)
            if is_target:
                break

    def on_keyboard(self, event):
        pass
        # for sp in self.group_keyboard:
        #     sp.on_keyboard(event)

    # 画面の更新
    def update_display(self):
        self.group_all.clear(self.screen, self.background)
        self.group_all.update()
        with self.context_scale_rect_tanuki(self.group_mouse):
            self.group_all.draw(self.screen)

        pg.display.update()
        self.clock.tick(FPS)

    # 描画の間のみrectのサイズを原寸に戻す
    @contextmanager
    def context_scale_rect_tanuki(self, group):
        for sp in group:
            sp.scale_rect(False)

        yield

        for sp in group:
            sp.scale_rect(True)


if __name__ == '__main__':
    game = SpecialGame()
    game.main()
