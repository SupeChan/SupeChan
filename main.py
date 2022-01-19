import random
import wx
import wx.adv
import threading

from PIL import Image, ImageSequence

import game
from config import *
import ctypes


class MenuFrame(wx.Frame):
    RANDOM = "ランダム"
    STYLE_MENU = wx.CAPTION | wx.CLOSE_BOX | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP

    def __init__(self, parent):
        super().__init__(None, -1, "めにゅー", style=self.STYLE_MENU)
        self.is_set_no_entry = False
        self.parent = parent
        self.lst_widget = []

        self.panel = wx.Panel(self)
        self.sbmp_background = None

        self.lst_tanuki = self.get_lst_path_tanuki()
        self.dic_tanuki = {path_tanuki.name: path_tanuki for path_tanuki in self.lst_tanuki}
        choices = [self.RANDOM] + [path_tanuki.name for path_tanuki in self.lst_tanuki]
        self.cb_tanuki = wx.ComboBox(self.panel, -1, choices=choices, style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.cb_tanuki.SetValue(self.RANDOM)

        self.btn_no_entry = wx.Button(self.panel, -1, "エリア設定")
        self.btn_memo = wx.Button(self.panel, -1, "メモ帳")

        self.setting_widgets()

    def setting_widgets(self):
        self.panel.SetBackgroundColour("ff0000")
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        fxsizer_command = wx.FlexGridSizer(rows=3, cols=2, gap=(5, 15))
        fxsizer_command.AddGrowableCol(0)
        fxsizer_command.AddGrowableCol(1)

        btn_enter = wx.Button(self.panel, -1, "出走")
        btn_terminate = wx.Button(self.panel, -1, "アプリ終了")

        self.Bind(wx.EVT_CLOSE, self.on_close)
        btn_enter.Bind(wx.EVT_BUTTON, self.on_enter)
        self.btn_no_entry.Bind(wx.EVT_BUTTON, self.on_no_entry)
        self.btn_memo.Bind(wx.EVT_BUTTON, self.on_memo)
        btn_terminate.Bind(wx.EVT_BUTTON, self.on_terminate)

        fxsizer_command.Add(self.cb_tanuki, 1, wx.GROW)
        fxsizer_command.Add(btn_enter, 1, wx.GROW)
        fxsizer_command.Add(wx.StaticText(self.panel, -1, ""))
        fxsizer_command.Add(self.btn_no_entry, 1, wx.GROW)
        fxsizer_command.Add(wx.StaticText(self.panel, -1, ""))
        fxsizer_command.Add(self.btn_memo, 1, wx.GROW)

        sizer_main.Add(fxsizer_command, 0, wx.GROW | wx.ALL, 10)
        sizer_main.Add(btn_terminate, 0, wx.GROW | wx.ALL, 20)

        self.panel.SetSizer(sizer_main)
        sizer_main.Fit(self)
        self.SetIcon(wx.Icon(str(PATH_ICON)))
        self.lst_widget = [self.cb_tanuki, btn_enter, self.btn_no_entry,
                           btn_terminate, self.btn_memo]
        for widget in self.lst_widget:
            self.set_gwl_exstyle(widget.GetHandle())
            self.Refresh()

        self.load_background()
        width, height = self.GetSize()
        pos_frame = (WIDTH_WORKING - width, HEIGHT_WORKING - height)
        self.SetPosition(pos_frame)

    def on_close(self, event):
        self.Hide()

    def on_enter(self, event):
        name_selected = self.cb_tanuki.GetValue() if event.GetEventType() == wx.wxEVT_BUTTON else self.RANDOM
        path_selected = (random.choice(self.lst_tanuki)
                         if name_selected == self.RANDOM
                         else self.dic_tanuki[name_selected])
        event_enter = pg.event.Event(pg.USEREVENT, type_user=TYPE_SYSTEM_ENTER,
                                     path_tanuki=path_selected)
        pg.event.post(event_enter)

    def on_no_entry(self, event):
        if not self.is_set_no_entry:
            event = pg.event.Event(pg.USEREVENT, type_user=TYPE_SYSTEM_CREATE_NO_ENTRY)
            pg.event.post(event)
            self.Hide()
        else:
            event = pg.event.Event(pg.USEREVENT, type_user=TYPE_SYSTEM_RELEASE_NO_ENTRY)
            pg.event.post(event)

        self.is_set_no_entry = not self.is_set_no_entry
        label = "エリア解除" if self.is_set_no_entry else "エリア設定"
        self.btn_no_entry.SetLabel(label)

    def on_memo(self, event):
        is_hide = not self.parent.frame_memo.IsShown()
        # hideが呼び出さす必要があるため
        if is_hide:
            self.parent.frame_memo.Show(is_hide)
        else:
            self.parent.frame_memo.Hide()

    def on_terminate(self, event):
        self.parent.terminate(None)

    def get_lst_path_tanuki(self):
        lst_path_tanuki = [path_tanuki for path_tanuki in PATH_FOLDER_TANUKI.iterdir()
                           if self.is_collect_construction(path_tanuki)]
        return lst_path_tanuki

    # たぬき画像フォルダの構造確認
    def is_collect_construction(self, path_tanuki):
        for action in ACTIONS:
            path_action = path_tanuki / action
            if not path_action.exists():
                return False

            lst_image = [path_image for path_image in path_action.glob("**/*.*")
                         if path_image.suffix in SUFFIXES_IMAGE_TANUKI]
            if not lst_image:
                return False

        return True

    def set_gwl_exstyle(self, hwnd):
        exstyle_extend = (win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) |
                          win32con.WS_EX_LAYERED)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exstyle_extend)
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 230, win32con.LWA_ALPHA)

    def Show(self, show=True):
        super().Show(show)
        self.draw_force()

    def Hide(self):
        super().Hide()
        self.load_background()

    def load_background(self):
        lst_path_road = [path_image for path_image in PATH_FOLDER_ROAD.glob("**/*.*")
                         if path_image.suffix.lower() in SUFFIXES_IMAGE_MEMO]
        path_road = random.choice(lst_path_road)
        image_road = Image.open(path_road).convert("RGBA")
        image_road = image_road.resize(self.panel.GetSize(), Image.LANCZOS)

        lst_path = [path_image for path_image in PATH_FOLDER_MENU_TANUKI.glob("**/*.*")
                    if path_image.suffix.lower() in SUFFIXES_IMAGE_TANUKI]
        path_tanuki = pathlib.Path(random.choice(lst_path))

        image_tanuki = Image.open(path_tanuki)
        lst_image = ([image_frame.copy() for image_frame in ImageSequence.Iterator(image_tanuki)]
                     if image_tanuki.is_animated else
                     [image_tanuki])
        image_tanuki = random.choice(lst_image).convert("RGBA")
        image_tanuki.thumbnail(image_road.size)
        image_clear = Image.new("RGBA", image_road.size, (255, 255, 255, 0))
        image_clear.paste(image_tanuki)
        image_background = Image.alpha_composite(image_road, image_clear)
        bmp = wx.Bitmap.FromBufferRGBA(*image_background.size, image_background.tobytes())
        if self.sbmp_background:
            self.sbmp_background.Destroy()

        self.sbmp_background = wx.StaticBitmap(self.panel, -1, bmp, (0, 0))

    def draw_force(self):
        for widget in self.lst_widget:
            widget.SetFocus()

        width, height = self.GetSize()
        self.SetSize(width + 1, height + 1)
        self.SetSize(width, height)


class MemoFrame(wx.Frame):
    STYLE_FRAME_MEMO = wx.CAPTION | wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP
    TITLE = "メモ帳"
    SIZE_FRAME_INIT = (int(WIDTH_DISPLAY / 5), int(HEIGHT_DISPLAY / 4))

    def __init__(self):
        super().__init__(None, -1, self.TITLE, style=self.STYLE_FRAME_MEMO)
        self.panel = wx.Panel(self)
        self.tc_memo = wx.TextCtrl(self.panel, -1, "", style=wx.TE_MULTILINE | wx.HSCROLL)

        self.image_background = None
        self.sbmp_background = None

        self.load_background()
        self.setting_widgets()

    def setting_widgets(self):
        self.tc_memo.SetBackgroundColour("#ffffff")
        self.set_gwl_exstyle(self.tc_memo.GetHandle())

        sizer = wx.BoxSizer()
        sizer.Add(self.tc_memo, 1, wx.GROW)
        self.panel.SetSizer(sizer)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.SetSize(self.SIZE_FRAME_INIT)
        width, height = self.GetSize()
        pos_frame = (WIDTH_WORKING - width, HEIGHT_WORKING - height)
        self.SetPosition(pos_frame)
        self.SetIcon(wx.Icon(str(PATH_ICON)))

    def on_resize(self, evt):
        size_panel = self.panel.GetSize()
        if not all(size_panel):
            size_panel = (1, 1)

        image = self.image_background.copy()
        image = image.resize(size_panel, Image.LANCZOS).convert("RGBA")
        image = wx.Bitmap.FromBufferRGBA(*image.size, image.tobytes())
        if self.sbmp_background:
            self.sbmp_background.Destroy()

        self.sbmp_background = wx.StaticBitmap(self.panel, -1, image, pos=(0, 0))
        if evt:
            evt.Skip()

    def on_close(self, evt):
        self.Hide()

    def Hide(self):
        super().Hide()
        self.load_background()

    def load_background(self):
        path_background = random.choice([path for path in PATH_FOLDER_MEMO.glob("**/*.*")
                                         if path.suffix in SUFFIXES_IMAGE_MEMO])

        self.image_background = Image.open(path_background)
        self.on_resize(None)

    def set_gwl_exstyle(self, hwnd):
        # 透過、入力不可の設定
        exstyle_extend = (win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) |
                          win32con.WS_EX_LAYERED)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exstyle_extend)
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 200, win32con.LWA_ALPHA)


class TerminateConfirmDialog(wx.Dialog):
    STYLE_CONFIRM = wx.CAPTION | wx.CLOSE_BOX | wx.STAY_ON_TOP

    def __init__(self, parent):
        super().__init__(parent, -1, "終了確認", style=self.STYLE_CONFIRM)
        self.panel = wx.Panel(self)
        self.setting_widgets()

    def setting_widgets(self):
        icon = wx.Icon(str(PATH_ICON))
        self.SetIcon(icon)

        st_message = wx.StaticText(self.panel, -1, "すぺちゃんを終了しますか？",
                                   style=wx.TEXT_ALIGNMENT_CENTER)
        btn_yes = wx.Button(self.panel, wx.ID_OK, "はい！")
        btn_no = wx.Button(self.panel, wx.ID_CANCEL, "いいえ！")

        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_btn = wx.BoxSizer()

        sizer_btn.Add(btn_yes, 1, wx.GROW | wx.ALL, 5)
        sizer_btn.Add(btn_no, 1, wx.GROW | wx.ALL, 5)

        sizer_main.Add(st_message, 1, wx.GROW | wx.ALL, 10)
        sizer_main.Add(sizer_btn, 1, wx.GROW | wx.ALL, 5)
        self.panel.SetSizer(sizer_main)
        sizer_main.Fit(self)
        width, height = self.GetSize()
        pos_dial = (WIDTH_WORKING - width, HEIGHT_WORKING - height)
        self.SetPosition(pos_dial)


class SpecialTaskBar(wx.adv.TaskBarIcon):
    def __init__(self):
        super().__init__(wx.adv.TBI_CUSTOM_STATUSITEM)
        self.frame_menu = MenuFrame(self)
        self.frame_memo = MemoFrame()
        self.ignore_click = False
        self.setting_widgets()
        self.game = game.SpecialGame()
        self.thread = threading.Thread(target=self.start_game, daemon=True)
        self.thread.start()

    def setting_widgets(self):
        icon = wx.Icon(str(PATH_ICON))
        self.SetIcon(icon)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.show_menu)

    def start_game(self):
        self.game.main()

    def CreatePopupMenu(self):
        if self.ignore_click:
            return

        label_enter_random = "ランダム出走"
        label_memo = "メモ帳非表示" if self.frame_memo.IsShown() else "メモ帳表示"
        label_no_entry = "エリア解除" if self.frame_menu.is_set_no_entry else "エリア設定"
        menu = wx.Menu()
        self.append_menuitem(menu, label_enter_random, self.frame_menu.on_enter)
        self.append_menuitem(menu, label_memo, self.show_memo)
        self.append_menuitem(menu, label_no_entry, self.frame_menu.on_no_entry)
        self.append_menuitem(menu, "終了", self.terminate)
        return menu

    @staticmethod
    def append_menuitem(menu, label, func):
        item = wx.MenuItem(menu, wx.ID_ANY, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.Append(item)

    def execute(self, event):
        pass

    def show_menu(self, event):
        if self.ignore_click:
            return

        if self.frame_menu.IsShown():
            self.frame_menu.Hide()
        else:
            self.frame_menu.Show()

    def show_memo(self, event):
        if self.frame_memo.IsShown():
            self.frame_memo.Hide()
        else:
            self.frame_memo.Show()

    def terminate(self, event):
        if self.ignore_click:
            return

        self.ignore_click = True
        with TerminateConfirmDialog(self.frame_menu) as dial:
            result = dial.ShowModal()

        if not result == wx.ID_OK:
            self.ignore_click = False
            return

        event_quit = pg.event.Event(pg.QUIT)
        pg.event.post(event_quit)
        self.frame_memo.Destroy()
        self.frame_menu.Destroy()
        self.Destroy()


if __name__ == '__main__':
    ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
    app = wx.App()
    # 多重実行の防止
    name_instance = f"{app.GetAppName()}-{wx.GetUserId()}"
    instance = wx.SingleInstanceChecker(name_instance)
    if instance.IsAnotherRunning():
        wx.Exit()

    SpecialTaskBar()
    app.MainLoop()
