"""
This program uses wxpython lib to track active windows and sets timer for a break.
1st window is main. Dark window/screen is activated by timer, or button.
Different widgets are placed in sizers for better spacing or panels/scrolled panels.
Program analysis active window every second.
Binds (region timers and bindings) are used to bind widgets and events on those widgets with functions.
"""
import datetime
import json  # save parameters
import time

import pyautogui
import vlc
import wx
import wx.adv
import wx.lib.mixins.inspection  # tool to inspect windows\widgets parameters
import wx.lib.scrolledpanel as scrolled


import sql  # all data saved in database
from active_windows import get_active_window

TRAY_TOOLTIP = 'Focus mode lol'
MAIN_ICON = 'Images/Main.ico'
TRAY_ICON = 'Images/tray1.png'
TRAY_ICON2 = 'Images/tray2.png'
DATABASE_NAME = "database.db"
SHORTEST_TIME = 1  # to show data if time period is greater than this time
DAY_START_TIME = "07:00:00"  # data for the day is showed between 07:00:00 of chosen day and 06:59:59 of the next day


def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        frame.task_bar_icon = self
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.frame.task_bar_icon = self

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Site', self.on_hello)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path, text=""):
        icon = wx.Icon(path)
        self.SetIcon(icon, text)

    def on_left_down(self, event):
        print('Tray icon was left-clicked.')
        print(f"{self.frame.IsIconized() = }")

        if self.frame.IsIconized():
            self.set_icon(TRAY_ICON)
            self.frame.Show()
            self.frame.Iconize(iconize=False)

        else:
            self.frame.Hide()
            self.frame.Iconize(iconize=True)
            self.set_icon(TRAY_ICON2)

    def on_hello(self, event):
        print('Clicked on site menu')

    def on_exit(self, event):

        print('Closing from the tray')
        wx.CallAfter(self.Destroy)
        self.frame.Destroy()


class DarkWindow(wx.Frame):
    def __init__(self, parent, title, duration):
        screen_size = wx.GetDisplaySize()
        self.parent = parent

        print(f"{screen_size = }")
        wx.Frame.__init__(self, parent, title=title, size=(400, 400), pos=(0, 0),
                          style=wx.DEFAULT_FRAME_STYLE & ~wx.CAPTION | wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR)
        self.dark_window_panel_1 = wx.Panel(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=screen_size,
                                            style=wx.TAB_TRAVERSAL, name=wx.PanelNameStr)
        self.dark_window_panel_1.SetBackgroundColour("#1f2525")
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(14)
        self.dark_window_panel_1.SetFont(font)
        self.opacity = 55
        self.SetTransparent(self.opacity)
        self.Centre()
        self.Show()
        self.Iconize(False)
        self.mouse_coord = (0, 0)
        self.mouse_last_coord = (0, 0)
        self.timer_till_break_end = wx.Timer(self, id=wx.ID_ANY)
        self.timer_till_break_end.Start(1000)

        self.timer_change_opacity = wx.Timer(self, id=wx.ID_ANY)
        self.timer_change_opacity.Start(100)

        self.Bind(wx.EVT_TIMER, self.count_down, id=self.timer_till_break_end.GetId())
        self.Bind(wx.EVT_TIMER, self.on_timer_change_opacity, id=self.timer_change_opacity.GetId())

        self.break_duration = duration
        t = time.strftime('%M:%S', time.gmtime(duration))
        self.button_label = t + " \n" + "Press to close"
        self.button_stop = wx.Button(self.dark_window_panel_1, id=wx.ID_ANY, label=self.button_label, size=(300, 200),
                                     style=wx.BORDER_NONE)
        self.button_stop.Centre()
        self.dark_window_panel_1.Bind(wx.EVT_BUTTON, self.on_button_stop, id=self.button_stop.GetId())
        self.Maximize()

        # notification = wx.adv.NotificationMessage("Title", "This is the message.")
        #
        # # show the notification
        # notification.Show()

    def on_timer_change_opacity(self, event):
        if self.opacity < 255:
            self.opacity += 10
            self.SetTransparent(self.opacity)
        else:
            self.timer_change_opacity.Stop()

    def on_button_stop(self, event):
        self.end_of_relax_mode(event)

    def end_of_relax_mode(self, event):
        self.close_break_window(event)

    def count_down(self, event):
        if self.break_duration > 1:
            self.break_duration -= 1
        else:
            self.close_break_window(event)

        t = time.strftime('%M:%S', time.gmtime(self.break_duration))
        self.button_label = t + " \n" + "Press to close"
        self.button_stop.Label = self.button_label

    def close_break_window(self, event):
        self.parent.time_before_break = self.parent.spin_ctrl_work_time.GetValue() * 60 + 1
        self.parent.sound_end.stop()
        self.parent.sound_end.play()

        self.Close()
        self.timer_till_break_end.Stop()
        wx.Event.Skip(event)


class MainWindow(wx.Frame):
    def __init__(self, parent, title, db):
        self.sound_begin = vlc.MediaPlayer("/Sounds/start.mp3")
        self.sound_end = vlc.MediaPlayer("/Sounds/end.mp3")
        self.Button1Name = "but1"
        self.db = db
        self.LastActiveWindow = None
        self.TimeAppOpened = datetime.datetime.now()
        self.user_active = True
        self.mouse_last_coord = pyautogui.position()

        max_id = self.db.query_select_max_id()
        self.max_id = max_id if max_id else 1

        self.new_line_added_to_db = False

        self.LINE_HEIGHT = 30
        self.MAX_ROWS_TO_SHOW = 200

        try:
            with open('parametrs.json', 'r') as outfile:
                params = json.load(outfile)
            if len(params) != 4:
                raise IOError('Invalid parameters')
        except IOError:
            params = {
                "work time": 20,
                "break time": 15,
                "time inactive": 5,
                "time to renew": 15
            }

        wx.Frame.__init__(self, parent, title=title, size=(800, 700),
                          style=wx.RESIZE_BORDER | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.SetIcon(wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_ICO))

        self.tab1_panel1 = wx.Panel(self)
        self.font1 = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font1.SetPointSize(14)
        self.font2 = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font2.SetPointSize(14)
        self.font2.MakeBold()
        self.tab1_panel1.SetFont(self.font1)

        tabs = wx.Notebook(self.tab1_panel1, id=wx.ID_ANY)

        self.vbox_main9 = wx.BoxSizer(wx.VERTICAL)
        self.vbox_main9.Add(tabs, 1, wx.ALL | wx.EXPAND, 0)

        self.tab1_panel1.SetSizer(self.vbox_main9)

        # region create tab 1

        self.scrolled_window = scrolled.ScrolledPanel(tabs, wx.ID_ANY)
        self.scrolled_window.SetupScrolling(scroll_x=False, scroll_y=True)

        tabs.AddPage(self.scrolled_window, "Tracker", select=True)

        self.vbox_main = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_window.SetSizer(self.vbox_main)

        self.pn3_main = wx.Panel(self.scrolled_window,
                                 size=wx.DefaultSize)
        self.datePicker1 = wx.adv.DatePickerCtrl(self.pn3_main, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition,
                                                 wx.DefaultSize, wx.adv.DP_DEFAULT)
        # self.pn3_main.SetBackgroundColour("#4444fe")
        self.hbox_main3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_main3.Add(self.datePicker1, border=0)
        self.check_box_extended_mode = wx.CheckBox(
            self.pn3_main, wx.ID_ANY, u"Extended", wx.DefaultPosition, wx.DefaultSize, style=wx.ALIGN_RIGHT
        )
        self.hbox_main3.Add(self.check_box_extended_mode, flag=wx.EXPAND | wx.LEFT, border=50)
        self.pn3_main.SetSizer(self.hbox_main3)
        self.vbox_main.Add(self.pn3_main, flag=wx.ALIGN_CENTER | wx.DOWN | wx.UP, border=5)

        self.tab1_panel_1_1 = wx.Panel(self.scrolled_window, size=(200, 0))

        self.tab1_panel_1_2 = wx.Panel(self.scrolled_window, size=(200, 0))

        self.hbox_main = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox_main.Add(self.hbox_main, flag=wx.EXPAND | wx.ALIGN_LEFT, border=0)

        self.hbox_main.Add(self.tab1_panel_1_1, flag=wx.EXPAND, border=0, proportion=1)
        self.hbox_main.Add(self.tab1_panel_1_2, flag=wx.EXPAND, border=0)

        # current_date = datetime.date.today()
        self.on_date_picker(None)

        self.all_rows = self.get_rows_from_database()
        self.check_box_pressed = False
        # endregion

        # region create tab 2
        self.tab2_panel_1 = wx.Panel(tabs)

        self.tab2_panel_1.SetFont(self.font1)

        tabs.AddPage(self.tab2_panel_1, "Relax", select=True)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.tab2_panel_1.SetSizer(vbox)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        pn = wx.Panel(self.tab2_panel_1)
        wx.StaticBox(pn, label="Timer:", size=(150, 50))
        self.rd1 = wx.RadioButton(pn, label="On", pos=(10, 20), style=wx.RB_GROUP, id=wx.ID_ANY)
        rd2 = wx.RadioButton(pn, label="Off", pos=(100, 20), id=wx.ID_ANY)
        rd2.SetValue(False)

        hbox1.Add(pn, flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(hbox1, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        g_sizer1 = wx.FlexGridSizer(rows=5, cols=2, vgap=0, hgap=0)
        g_sizer1.SetFlexibleDirection(direction=wx.HORIZONTAL)
        st1 = wx.StaticText(
            self.tab2_panel_1, id=wx.ID_ANY, label="Work time, minutes", pos=(10, 0),
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )
        self.spin_ctrl_work_time = wx.SpinCtrl(
            self.tab2_panel_1, id=wx.ID_ANY, value=str(params["work time"]), pos=(200, 0),
            size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, min=1, max=1000, initial=0,
            name="wxSpinCtrl"
        )
        st2 = wx.StaticText(
            self.tab2_panel_1, id=wx.ID_ANY, label="Break time, seconds", pos=(10, 50),
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )
        self.spin_ctrl_break_time = wx.SpinCtrl(
            self.tab2_panel_1, id=wx.ID_ANY, value=str(params["break time"]),
            pos=(200, 50),
            size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, min=1, max=1000, initial=0,
            name="wxSpinCtrl2"
        )
        self.st3 = wx.StaticText(
            self.tab2_panel_1, id=wx.ID_ANY, label="Time till next break",
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )

        self.time_before_break = self.spin_ctrl_work_time.GetValue() * 60

        t = time.strftime('%M:%S', time.gmtime(self.time_before_break))
        self.st4 = wx.StaticText(
            self.tab2_panel_1, id=wx.ID_ANY, label=t,
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )

        self.st5 = wx.StaticText(
            self.tab2_panel_1, id=wx.ID_ANY, label="Time inactive, seconds",
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )

        self.spin_ctrl_time_inactive = wx.SpinCtrl(
            self.tab2_panel_1, id=wx.ID_ANY, value=str(params["time inactive"]), pos=(200, 50),
            size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, min=1, max=1000, initial=0, name="wxSpinCtrl2"
        )

        self.st6 = wx.StaticText(
            self.tab2_panel_1, id=wx.ID_ANY, label="Time to renew, seconds",
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )

        self.spin_ctrl_time_to_renew = wx.SpinCtrl(
            self.tab2_panel_1, id=wx.ID_ANY, value=str(params["time to renew"]), pos=(200, 50),
            size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, min=1, max=1000, initial=0, name="wxSpinCtrl2"
        )

        g_sizer1.Add(st1, flag=wx.LEFT | wx.TOP, border=10)
        g_sizer1.Add(self.spin_ctrl_work_time, flag=wx.LEFT | wx.TOP, border=10)

        g_sizer1.Add(st2, flag=wx.LEFT | wx.TOP, border=10)
        g_sizer1.Add(self.spin_ctrl_break_time, flag=wx.LEFT | wx.TOP, border=10)

        g_sizer1.Add(self.st5, flag=wx.LEFT | wx.TOP, border=10)
        g_sizer1.Add(self.spin_ctrl_time_inactive, flag=wx.LEFT | wx.TOP, border=10)

        g_sizer1.Add(self.st6, flag=wx.LEFT | wx.TOP, border=10)
        g_sizer1.Add(self.spin_ctrl_time_to_renew, flag=wx.LEFT | wx.TOP, border=10)

        g_sizer1.Add(self.st3, flag=wx.LEFT | wx.TOP, border=10)
        g_sizer1.Add(self.st4, flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(g_sizer1, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.button_start = wx.Button(self.tab2_panel_1, id=wx.ID_ANY, label="Start break", pos=(200, 200),
                                      size=(200, 100)
                                      )
        hbox5.Add(self.button_start, flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(hbox5, flag=wx.ALL | wx.ALIGN_CENTER, border=10)
        # endregion

        # region timers and bindings
        self.timer1 = wx.Timer(self, id=wx.ID_ANY)
        self.timer1.Start(1000)
        self.timer_activity = wx.Timer(self, id=wx.ID_ANY)
        self.timer_till_break = wx.Timer(self, id=wx.ID_ANY)
        self.timer_till_break.Start(1000)
        self.timer_inactivity = wx.Timer(self, id=wx.ID_ANY)

        self.Bind(wx.EVT_TIMER, self.on_timer_1, id=self.timer1.GetId())
        self.Bind(wx.EVT_TIMER, self.check_inactivity_timer, id=self.timer_inactivity.GetId())
        self.Bind(wx.EVT_TIMER, self.check_activity, id=self.timer_activity.GetId())
        self.Bind(wx.EVT_TIMER, self.time_till_break, id=self.timer_till_break.GetId())

        self.Bind(wx.EVT_SPINCTRL, self.on_spin_ctrl_work_time, id=self.spin_ctrl_work_time.GetId())
        self.Bind(wx.EVT_SPINCTRL, self.on_spin_ctrl_break_time, id=self.spin_ctrl_break_time.GetId())
        self.Bind(wx.EVT_SPINCTRL, self.on_spin_ctrl_time_till_break, id=self.spin_ctrl_time_to_renew.GetId())
        self.Bind(wx.EVT_SPINCTRL, self.on_spin_ctrl_time_inactive, id=self.spin_ctrl_time_inactive.GetId())

        self.Bind(wx.EVT_MOVING, self.on_move)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_CLOSE, self.on_minimize)
        self.Bind(wx.EVT_CHECKBOX, self.on_check_box_extended_mode)

        self.datePicker1.Bind(wx.adv.EVT_DATE_CHANGED, self.on_date_picker)

        self.tab1_panel1.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.tab1_panel1.Bind(wx.EVT_LEFT_DOWN, self.lmb_pressed)

        self.tab1_panel_1_1.Bind(wx.EVT_PAINT, self.on_paint1)
        self.tab1_panel_1_2.Bind(wx.EVT_PAINT, self.on_paint2)

        self.tab2_panel_1.Bind(wx.EVT_BUTTON, self.break_begin, id=self.button_start.GetId())
        # endregion

    def on_date_picker(self, event):
        a = self.datePicker1.GetValue()
        print(f"{a = }")
        b = wx.DateTime.FormatISOCombined(a).split("T")[0]
        d1 = datetime.datetime.fromisoformat(f"{b} {DAY_START_TIME}")
        one_day = datetime.timedelta(hours=23, minutes=59, seconds=59)
        self.date_start = d1
        self.date_end = d1 + one_day
        self.check_box_pressed = True
        self.Refresh()

    def on_check_box_extended_mode(self, event):
        self.check_box_pressed = True
        self.Refresh()

    def on_spin_ctrl_work_time(self, event):
        self.time_before_break = self.spin_ctrl_work_time.GetValue() * 60
        t = time.strftime('%M:%S', time.gmtime(self.time_before_break))
        self.st4.Label = str(t)
        self.save_params_to_json()

    def on_spin_ctrl_break_time(self, event):
        self.save_params_to_json()

    def on_spin_ctrl_time_inactive(self, event):
        self.timer_inactivity.Stop()
        self.timer_inactivity.Start(self.spin_ctrl_time_inactive.GetValue() * 1000)
        self.save_params_to_json()

    def on_spin_ctrl_time_till_break(self, event):
        self.save_params_to_json()

    def time_till_break(self, event):
        if self.rd1.GetValue():
            if self.user_active:
                if self.time_before_break > 1:
                    self.time_before_break -= 1
                    t = time.strftime('%M:%S', time.gmtime(self.time_before_break))
                    # print(f"{t = }")
                    self.st4.Label = str(t)
                    if self.IsIconized():
                        self.task_bar_icon.set_icon(TRAY_ICON2, t)
                    else:
                        self.task_bar_icon.set_icon(TRAY_ICON, t)
                elif self.time_before_break == 1:
                    self.time_before_break = -1
                    self.break_begin(event)

    def check_activity(self, event):
        self.user_active = False
        if not self.timer_inactivity.IsRunning():
            if self.spin_ctrl_time_to_renew.GetValue() > self.spin_ctrl_time_inactive.GetValue():
                self.timer_inactivity.Start((self.spin_ctrl_time_to_renew.GetValue() -
                                             self.spin_ctrl_time_inactive.GetValue()) * 1000)
            else:
                self.timer_inactivity.Start(self.spin_ctrl_time_to_renew.GetValue() * 1000)
        self.timer_activity.Stop()

        print(f"{self.user_active = }")

    def check_inactivity_timer(self, event):
        self.time_before_break = self.spin_ctrl_work_time.GetValue() * 60 + 1
        self.timer_inactivity.Stop()

        print(f"inactive for some time")
        self.Refresh()

    def on_resize(self, event):
        print("OnResize")
        self.Refresh()
        wx.Event.Skip(event)

    def on_focus(self, event):
        print("OnFocus")
        self.save_to_db()
        self.Refresh()
        wx.Event.Skip(event)

    def on_move(self, event):
        # print("OnMove")
        # self.Refresh()
        # wx.Event.Skip(event)
        pass

    def on_minimize(self, event):
        print("minimizing window")
        self.Iconize()
        self.Hide()
        self.task_bar_icon.set_icon(TRAY_ICON2)
        # wx.CallAfter(self.Destroy)
        # self.Close()

    # def on_quit(self, event):
    #     print(event)
    #     self.Close()

    def break_begin(self, event):
        DarkWindow(self, "Focus mode Break time", self.spin_ctrl_break_time.GetValue() + 1)

        self.sound_begin.stop()
        self.sound_begin.play()

        wx.Event.Skip(event)

    def lmb_pressed(self, event):
        print("LMB pressed")
        self.Refresh()
        wx.Event.Skip(event)

    def on_button1(self, event):
        print("pressed button...")

    def get_rows_from_database(self):
        if self.check_box_extended_mode.GetValue():
            res = self.db.query_extended_load_on_date(self.date_start, self.date_end, SHORTEST_TIME)
        else:
            res = self.db.query_simple_load_on_date(self.date_start, self.date_end, SHORTEST_TIME)

        self.all_rows = res
        if len(self.all_rows) > 0:
            if len(self.all_rows[0]) > 2:
                result_row = (f"({sum([x[2] for x in self.all_rows])})", sum([x[1] for x in self.all_rows]))
            else:
                result_row = (f"Result", sum([x[1] for x in self.all_rows]))
        else:
            result_row = (f"No result for current day", 0)
        self.all_rows.append(result_row)

        print("Loaded from db")

        size1 = (100, (min(self.MAX_ROWS_TO_SHOW, len(self.all_rows))) * self.LINE_HEIGHT)
        size2 = (
            100,
            (min(self.MAX_ROWS_TO_SHOW, len(self.all_rows))) *
            self.LINE_HEIGHT + self.pn3_main.GetSize()[1] + 10
        )
        self.tab1_panel_1_1.SetMinSize(size1)
        self.scrolled_window.SetVirtualSize(size2)
        return res

    def on_paint1(self, event):
        print("onPaint1")
        width_of_panel_with_names = self.tab1_panel_1_1.GetVirtualSize()[0]
        if self.new_line_added_to_db or self.check_box_pressed:
            self.all_rows = self.get_rows_from_database()
            self.new_line_added_to_db = False
            self.check_box_pressed = False

        dc = wx.PaintDC(self.tab1_panel_1_1)
        dc.SetPen(wx.Pen('#fdc073', style=wx.TRANSPARENT))
        dc.SetBrush(wx.Brush('#d5dde6', wx.SOLID))

        for i, row in enumerate(self.all_rows):
            if len(row) > 2:
                data = f"({row[2]}) {row[0]} "
            else:
                data = f"{row[0]}"

            duration = row[1]

            if i >= self.MAX_ROWS_TO_SHOW:
                break

            if dc.GetTextExtent(data)[0] > width_of_panel_with_names - 35:
                while dc.GetTextExtent(data)[0] > width_of_panel_with_names - 35:
                    data = data[:len(data) - 1]
                data = data[:len(data)] + '...'

            if i != len(self.all_rows) - 1:
                dc.DrawRectangle(0, self.LINE_HEIGHT * i,
                                 int(duration / self.all_rows[-1][1] * width_of_panel_with_names), self.LINE_HEIGHT
                                 )
                dc.DrawText(data, 20, self.LINE_HEIGHT * i)
            else:
                dc.SetFont(self.font2)
                dc.DrawText(data, 20, self.LINE_HEIGHT * i)
                dc.SetFont(self.font1)

    def on_paint2(self, event):
        print("onPaint2")
        dc2 = wx.PaintDC(self.tab1_panel_1_2)
        for i, row in enumerate(self.all_rows):
            duration = row[1]
            if i >= self.MAX_ROWS_TO_SHOW:
                break
            if i == len(self.all_rows) - 1:
                dc2.SetFont(self.font2)
                dc2.DrawText(f"{time.strftime('%H:%M:%S', time.gmtime(duration))}", 10, self.LINE_HEIGHT * i)
                dc2.SetFont(self.font1)
            else:
                dc2.DrawText(f"{time.strftime('%H:%M:%S', time.gmtime(duration))}", 10, self.LINE_HEIGHT * i)

    def on_timer_1(self, event):
        self.save_to_db()

        mouse_new_coord = pyautogui.position()
        if mouse_new_coord != self.mouse_last_coord:
            self.mouse_last_coord = mouse_new_coord
            self.user_active = True
            if self.timer_activity.IsRunning():
                self.timer_activity.Stop()
            if self.timer_inactivity.IsRunning():
                self.timer_inactivity.Stop()
        else:
            if self.user_active and not self.timer_activity.IsRunning():
                self.timer_activity.Start(self.spin_ctrl_time_inactive.GetValue() * 1000)

    def save_to_db(self):
        active_window = get_active_window()
        if active_window:
            full_app_name = '-'.join(active_window)
            if full_app_name != self.LastActiveWindow:
                print("act wind changed")
                # if datetime.datetime.now() - self.TimeAppOpened > datetime.timedelta(seconds=0):
                if self.LastActiveWindow:
                    self.max_id += 1
                    self.db.query_save(self.max_id, self.LastActiveWindow, self.TimeAppOpened,
                                       datetime.datetime.now())
                    self.new_line_added_to_db = True
                    print("Saved to db")

                self.LastActiveWindow = full_app_name
                self.TimeAppOpened = datetime.datetime.now()
        else:
            print(active_window)

    def save_params_to_json(self):
        x = {
            "work time": self.spin_ctrl_work_time.GetValue(),
            "break time": self.spin_ctrl_break_time.GetValue(),
            "time inactive": self.spin_ctrl_time_inactive.GetValue(),
            "time to renew": self.spin_ctrl_time_to_renew.GetValue()
        }

        with open('parametrs.json', 'w') as outfile:
            json.dump(x, outfile, indent=4)


class App(wx.App):
    def __init__(self, redirect, db=None):
        self.db = db
        super().__init__(redirect=redirect)

    def OnInit(self):
        frame = MainWindow(None, "Focus mode", self.db)
        frame.Centre()
        frame.Show(True)
        # wx.lib.inspection.InspectionTool().Show()  # to inspect all parameters of windows\panels\widgets
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True


def main():
    db = sql.DataBase(DATABASE_NAME)
    db.connect()
    db.create_table_if_not_exists()

    app = App(redirect=False, db=db)
    app.MainLoop()

    print('Everything closed correctly')


if __name__ == '__main__':
    main()
