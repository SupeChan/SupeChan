import pathlib
import random
import wx
import wx.adv
import threading
import pygame as pg

import game
from config import *


class MenuFrame(wx.Frame):
    RANDOM = "ランダム"

    def __init__(self, parent):
        super().__init__(None, -1, "めにゅー",style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.parent = parent
        self.panel = wx.Panel(self)

        self.lst_tanuki = self.get_lst_path_tanuki()
        self.dic_tanuki = {path_tanuki.name: path_tanuki for path_tanuki in self.lst_tanuki}
        choices = [self.RANDOM] + [path_tanuki.name for path_tanuki in self.lst_tanuki]
        self.cb_tanuki = wx.ComboBox(self.panel, -1, choices=choices, style=wx.CB_DROPDOWN)
        self.cb_tanuki.SetValue(self.RANDOM)

        self.sizer_main = wx.BoxSizer(wx.VERTICAL)
        self.setting_widgets()

    def setting_widgets(self):
        sizer_caption = wx.BoxSizer()
        sizer_enter = wx.BoxSizer()
        sizer_close = wx.BoxSizer()

        st_caption = wx.StaticText(self.panel, -1, "めにゅー画面です！", style=wx.ALIGN_CENTER)
        btn_enter = wx.Button(self.panel, -1, "出走")
        btn_close = wx.Button(self.panel, -1, "アプリ終了")

        btn_enter.Bind(wx.EVT_BUTTON, self.on_enter)
        btn_close.Bind(wx.EVT_BUTTON, self.on_close)

        sizer_caption.Add(st_caption, 1, wx.GROW)

        sizer_enter.Add(self.cb_tanuki, 1, wx.GROW | wx.ALL, 5)
        sizer_enter.Add(btn_enter, 0, wx.ALL, 5)

        sizer_close.Add(btn_close, 1, wx.GROW | wx.ALL, 10)

        self.sizer_main.Add(sizer_caption, 1, wx.GROW)
        self.sizer_main.Add(sizer_enter, 1, wx.GROW)
        self.sizer_main.Add(sizer_close, 0, wx.ALIGN_RIGHT | wx.TOP, 30)

        self.panel.SetSizer(self.sizer_main)
        self.sizer_main.Fit(self)
        self.SetIcon(wx.Icon(PATH_ICON))
        self.Centre()

    def on_enter(self, event):
        name_selected = self.cb_tanuki.GetValue()
        path_selected = (random.choice(self.lst_tanuki)
                         if name_selected == self.RANDOM
                         else self.dic_tanuki[name_selected])
        event_enter = pg.event.Event(pg.USEREVENT, type_user=TYPE_USER_ENTER,
                                     path_tanuki=path_selected)
        pg.event.post(event_enter)

    def on_close(self, event):
        event_quit = pg.event.Event(pg.QUIT)
        pg.event.post(event_quit)
        self.Destroy()
        self.parent.Destroy()

    def get_lst_path_tanuki(self):
        lst_path_tanuki = [path_tanuki for path_tanuki in PATH_ROOT_TANUKI.iterdir()
                           if self.is_collect_construction(path_tanuki)]
        return lst_path_tanuki

    def is_collect_construction(self, path_tanuki):
        for action in ACTIONS:
            path_action = path_tanuki / action
            if not path_action.exists():
                return False

            lst_image = [path_image for path_image in path_action.glob("**/*.*")
                         if path_image.suffix in SUFFIXES_IMAGE]
            if not lst_image:
                return False

        return True


class SpecialTaskBar(wx.adv.TaskBarIcon):
    def __init__(self):
        super().__init__()

        # instance_name = u"%s-%s" % (self.GetAppName(), wx.GetUserId())
        # self.instance=wx.SingleInstanceChecker()

        self.frame_menu = None
        self.is_showing_dial = False
        self.setting_widgets()
        self.game = game.SpecialGame()
        self.thread = threading.Thread(target=self.start_game, daemon=True)
        self.thread.start()

    def setting_widgets(self):
        icon = wx.Icon(PATH_ICON)
        self.SetIcon(icon)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.show_frame)

    def start_game(self):
        self.game.main()

    def CreatePopupMenu(self):
        label_show = "メニュー非表示" if self.frame_menu else "メニュー表示"
        menu = wx.Menu()
        self.append_menuitem(menu, label_show, self.show_frame)
        self.append_menuitem(menu, "終了", self.terminate)
        return menu

    @staticmethod
    def append_menuitem(menu, label, func):
        item = wx.MenuItem(menu, wx.ID_ANY, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.Append(item)

    def execute(self, event):
        pass

    def show_frame(self, event):
        if self.frame_menu:
            self.frame_menu.Destroy()
            self.frame_menu = None
        else:
            self.frame_menu = MenuFrame(self)
            self.frame_menu.Show()

    def terminate(self, event):
        event_quit = pg.event.Event(pg.QUIT)
        pg.event.post(event_quit)
        if self.frame_menu:
            self.frame_menu.Destroy()

        self.Destroy()


if __name__ == '__main__':
    app = wx.App()
    # 多重実行の防止
    name_instance = f"{app.GetAppName()}-{wx.GetUserId()}"
    instance = wx.SingleInstanceChecker(name_instance)
    if instance.IsAnotherRunning():
        wx.Exit()

    SpecialTaskBar()
    app.MainLoop()
