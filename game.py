from contextlib import contextmanager
import win32api, win32gui, win32con

import listener
import sprites
from config import *


class SpecialGame:
    def __init__(self, frame_menu=None):
        self.frame_menu = frame_menu

        self.rect_screen = None
        self.screen = None
        self.background = None
        self.clock = pg.time.Clock()

        self.group_all = None
        self.group_mouse = None
        self.group_keyboard = None
        self.group_system = None

        self.listener_mouse = None
        self.listener_keyboard = None

        self.sp_no_entry = None
        self.rect_no_entry = None

        self.has_priority_system = False

        self.init_display()
        self.init_containers()
        self.set_gwl_exstyle()
        self.set_listener()

    def main(self):
        sprites.TanukiSprite(PATH_SPECIAL_WEEK, self.rect_no_entry, self.rect_screen.center)
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return

                elif event.type == pg.USEREVENT:
                    if event.type_user in TYPES_SYSTEM:
                        self.on_system(event)
                    if event.type_user in TYPES_MOUSE:
                        self.on_mouse(event)
                    elif event.type_user in TYPES_KEYBOARD:
                        self.on_keyboard(event)


                elif event.type == pg.DROPFILE:
                    pass

            self.update_display()

    # pgディスプレイの初期化
    def init_display(self):
        pg.init()
        self.rect_screen = pg.Rect(0, HEIGHT_CAPTION, *SIZE_SCREEN)
        self.screen = pg.display.set_mode((WIDTH_WORKING, HEIGHT_WORKING), pg.NOFRAME)
        self.background = pg.Surface(SIZE_WORKING)
        self.background.fill(COLOR_KEY_GAME)
        self.screen.blit(self.background, (0, 0))
        pg.display.update()
        icon = pg.image.load(PATH_ICON)
        pg.display.set_icon(icon)

    # 使用するスプライトのコンテナを設定
    def init_containers(self):
        self.group_all = pg.sprite.RenderUpdates()
        self.group_mouse = pg.sprite.Group()
        self.group_keyboard = pg.sprite.Group()
        self.group_system = pg.sprite.Group()

        sprites.TanukiSprite.containers = self.group_all, self.group_mouse
        sprites.IkuNoEntrySprite.containers = self.group_all, self.group_system

    # ウインドウスタイルの設定
    def set_gwl_exstyle(self):
        hwnd = pg.display.get_wm_info()["window"]

        # ウインドウを最前面に
        swp_topmost = (win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, swp_topmost)
        # SetWindowPosを使っても自動的に画面中央に寄せられてしまうので位置を変更
        win32gui.MoveWindow(hwnd, 0, 0, *SIZE_WORKING, True)

        # 透過、入力不可の設定
        exstyle_extend = (win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) |
                          win32con.WS_EX_LAYERED |  # 透過設定を可能にする。
                          win32con.WS_DISABLED)  # ユーザー入力を受け付けない。
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exstyle_extend)

        # 透過色の設定
        color_key = win32api.RGB(*COLOR_KEY_GAME)
        win32gui.SetLayeredWindowAttributes(hwnd, color_key, 0, win32con.LWA_COLORKEY)

    # マウス、キーボードの入力リスナーを設定
    def set_listener(self):
        for type_input in TYPES_INPUT_BLOCK:
            pg.event.set_blocked(type_input)

        self.listener_mouse = listener.PGMouseListener()
        self.listener_keyboard = listener.PGKeyboardListener()
        self.listener_mouse.start()
        self.listener_keyboard.start()

    def on_system(self, event) -> None:
        if event.type_user == TYPE_SYSTEM_CREATE_NO_ENTRY:
            self.has_priority_system = True
            self.sp_no_entry = sprites.IkuNoEntrySprite()
        elif event.type_user == TYPE_SYSTEM_SET_NO_ENTRY:
            for sp in self.group_mouse:
                sp.set_no_entry(self.rect_no_entry)
        elif event.type_user == TYPE_SYSTEM_RELEASE_NO_ENTRY:
            for sp in self.group_mouse:
                sp.set_no_entry(None)
            self.rect_no_entry = None

        elif event.type_user == TYPE_SYSTEM_ENTER:
            sprites.TanukiSprite(event.path_tanuki, self.rect_no_entry)

    def on_mouse(self, event) -> None:
        if self.has_priority_system:
            self.create_no_entry(event)
            return

        for sp in self.group_mouse.sprites()[::-1]:
            is_target = sp.on_mouse(event)
            if is_target:
                break

    def create_no_entry(self, event):
        if event.type_user == TYPE_USER_CLICK and event.button == BUTTON_LEFT:
            rect_no_entry = self.sp_no_entry.on_mouse(event)
            if type(rect_no_entry) is pg.Rect:
                self.sp_no_entry = None
                for sp in self.group_mouse:
                    sp.set_no_entry(rect_no_entry)

                self.rect_no_entry = rect_no_entry
                self.has_priority_system = False

    def on_keyboard(self, event):
        pass
        # for sp in self.group_keyboard:
        #     sp.on_keyboard(event)

    # 画面の更新
    def update_display(self):
        self.group_all.clear(self.screen, self.background)
        self.group_all.update()
        self.group_all.draw(self.screen)

        pg.display.update()
        self.clock.tick(FPS)

    # デバッグ用にrectを可視化する
    def visualize_rect(self):
        self.background.fill((186, 125, 207))
        surface_screen = pg.Surface(self.rect_screen.size)
        surface_screen.fill((150, 0, 150))
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(surface_screen, self.rect_screen.topleft)
        if self.rect_no_entry:
            sur_entry = pg.Surface(self.rect_no_entry.size)
            sur_entry.fill((0, 255, 255))
            self.screen.blit(sur_entry, self.rect_no_entry.topleft)


if __name__ == '__main__':
    game = SpecialGame()
    game.main()
