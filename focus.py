import json
import wx
import wx.adv
import wx.lib.scrolledpanel as scrolled
import wx.lib.mixins.inspection
import datetime
import time
import pyautogui

from active_windows import get_active_window
import sql

TRAY_TOOLTIP = 'Focus mode'
MAIN_ICON = 'Main.ico'
TRAY_ICON = 'tray1.png'
TRAY_ICON2 = 'tray2.png'
DATABASE_NAME = "database.db"


# TODO: using this tool

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

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Site', self.on_hello)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.Icon(path)
        self.SetIcon(icon, TRAY_TOOLTIP)

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
        print('Hello, world!')

    def on_exit(self, event):

        print('Closing from the tray')
        wx.CallAfter(self.Destroy)
        self.frame.Destroy()


class DarkWindow(wx.Frame):
    def __init__(self, parent, title, duration):
        screen_size = wx.GetDisplaySize()
        self.parent = parent

        print(screen_size)
        wx.Frame.__init__(self, parent, title=title, size=(400, 400), pos=(0, 0),
                          style=wx.DEFAULT_FRAME_STYLE & ~wx.CAPTION | wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR)
        self.panel5 = wx.Panel(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=screen_size,
                               style=wx.TAB_TRAVERSAL, name=wx.PanelNameStr)
        self.panel5.SetBackgroundColour("#1f2525")
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(14)
        self.panel5.SetFont(font)
        self.opacity = 50
        self.SetTransparent(self.opacity)
        self.Centre()
        self.Show()
        self.Iconize(False)
        self.mouse_coord = (0, 0)
        self.mouse_last_coord = (0, 0)
        self.timer2 = wx.Timer(self, id=104)
        self.timer2.Start(1000)

        self.timer3 = wx.Timer(self, id=105)
        self.timer3.Start(100)

        self.Bind(wx.EVT_TIMER, self.count_down, id=104)
        self.Bind(wx.EVT_TIMER, self.on_timer_change_opacity, id=105)

        self.break_duration = duration
        t = time.strftime('%M:%S', time.gmtime(duration))
        self.button_label = t + " \n" + "Press to close"
        self.button_stop = wx.Button(self.panel5, id=90, label=self.button_label, size=(300, 200), style=wx.BORDER_NONE)
        self.button_stop.Centre()
        self.panel5.Bind(wx.EVT_BUTTON, self.on_button_stop, id=90)
        self.Maximize()

    def on_timer_change_opacity(self, event):
        if self.opacity <= 240:
            self.opacity += 10
            self.SetTransparent(self.opacity)
        else:
            self.timer3.Stop()

    def on_button_stop(self, event):
        self.close_break_window(event)

    def end_of_relax_mode(self, event):
        self.close_break_window(event)

    def close_break_window(self, event):
        self.parent.time_before_break = self.parent.spin_ctrl1.GetValue() * 60
        self.Close()
        self.timer2.Stop()
        wx.Event.Skip(event)

    def count_down(self, event):
        if self.break_duration > 1:
            self.break_duration -= 1
        else:
            self.close_break_window(event)

        t = time.strftime('%M:%S', time.gmtime(self.break_duration))
        self.button_label = t + " \n" + "Press to close"
        self.button_stop.Label = self.button_label


class MainWindow(wx.Frame):
    def __init__(self, parent, title, db):
        self.Button1Name = "but1"
        self.db = db
        self.LastActiveWindow = None
        self.TimeAppOpened = datetime.datetime.now()
        self.user_active = True
        self.mouse_last_coord = pyautogui.position()

        max_id = self.db.query_select_max_id()
        self.max_id = max_id if max_id else 1

        self.new_line_added_to_db = False
        self.line_height = 30
        self.max_rows_to_show_on_main = 200

        try:
            with open('parametrs.json', 'r') as outfile:
                params = json.load(outfile)
            if len(params) != 4:
                raise ValueError
        except Exception:
            params = {
                "work time": 20,
                "break time": 15,
                "time inactive": 5,
                "time to renew": 15
            }

        wx.Frame.__init__(self, parent, title=title, size=(800, 700),
                          style=wx.RESIZE_BORDER | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.SetIcon(wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_ICO))


        self.panel1 = wx.Panel(self)
        self.font1 = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font1.SetPointSize(14)
        self.font2 = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font2.SetPointSize(14)
        self.font2.MakeBold()
        self.panel1.SetFont(self.font1)

        tabs = wx.Notebook(self.panel1, id=wx.ID_ANY)

        # region create tab 1
        self.vbox_main9 = wx.BoxSizer(wx.VERTICAL)
        self.vbox_main9.Add(tabs, 1, wx.ALL | wx.EXPAND, 0)

        self.panel1.SetSizer(self.vbox_main9)

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
        self.checkBox1 = wx.CheckBox(self.pn3_main, wx.ID_ANY, u"Extended", wx.DefaultPosition, wx.DefaultSize,
                                     style=wx.ALIGN_RIGHT)
        self.hbox_main3.Add(self.checkBox1, flag=wx.EXPAND | wx.LEFT, border=50)
        self.pn3_main.SetSizer(self.hbox_main3)
        self.vbox_main.Add(self.pn3_main, flag=wx.ALIGN_CENTER | wx.DOWN | wx.UP, border=5)

        self.pn1_main = wx.Panel(self.scrolled_window,
                                 size=(200, 0))

        self.pn2_main = wx.Panel(self.scrolled_window, size=(200, 0))

        self.hbox_main = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox_main.Add(self.hbox_main, flag=wx.EXPAND | wx.ALIGN_LEFT, border=0)

        self.hbox_main.Add(self.pn1_main, flag=wx.EXPAND, border=0, proportion=1)
        self.hbox_main.Add(self.pn2_main, flag=wx.EXPAND, border=0)

        current_date = datetime.date.today()
        self.on_date_picker(None)

        self.all_rows = self.get_rows_from_database()
        self.check_box_pressed = False
        # endregion

        # region create tab 2
        self.panel2 = wx.Panel(tabs)

        self.panel2.SetFont(self.font1)

        tabs.AddPage(self.panel2, "Relax", select=True)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.panel2.SetSizer(vbox)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        pn = wx.Panel(self.panel2)
        sb1 = wx.StaticBox(pn, label="Timer:", size=(150, 50))
        self.rd1 = wx.RadioButton(pn, label="On", pos=(10, 20), style=wx.RB_GROUP, id=92)
        rd2 = wx.RadioButton(pn, label="Off", pos=(100, 20), id=93)
        rd2.SetValue(False)

        hbox1.Add(pn, flag=wx.LEFT | wx.TOP, border=10)
        # hbox.Add(rd1, flag=wx.LEFT | wx.TOP, border=10)
        # hbox.Add(rd2, flag=wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox1, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        # hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        # st1 = wx.StaticText(
        #     self.panel2, id=wx.ID_ANY, label="Work time, seconds", pos=(10, 0),
        #     size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        # )
        # self.spin_ctrl1 = wx.SpinCtrl(self.panel2, id=71, value="30", pos=(200, 0),
        #                               size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, min=10, max=1000, initial=0,
        #                               name="wxSpinCtrl")
        # hbox2.Add(st1, flag=wx.LEFT | wx.TOP, border=10)
        # hbox2.Add(self.spin_ctrl1, flag=wx.LEFT | wx.TOP, border=10)
        # vbox.Add(hbox2, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        g_sizer1 = wx.FlexGridSizer(rows=5, cols=2, vgap=0, hgap=0)
        g_sizer1.SetFlexibleDirection(direction=wx.HORIZONTAL)
        st1 = wx.StaticText(
            self.panel2, id=wx.ID_ANY, label="Work time, minutes", pos=(10, 0),
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )
        self.spin_ctrl1 = wx.SpinCtrl(self.panel2, id=71, value=str(params["work time"]), pos=(200, 0),
                                      size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, min=1, max=1000, initial=0,
                                      name="wxSpinCtrl")
        st2 = wx.StaticText(
            self.panel2, id=wx.ID_ANY, label="Break time, seconds", pos=(10, 50),
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )
        self.spin_ctrl2 = wx.SpinCtrl(self.panel2, id=wx.ID_ANY, value=str(params["break time"]), pos=(200, 50),
                                      size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, min=1, max=1000, initial=0,
                                      name="wxSpinCtrl2")
        self.st3 = wx.StaticText(
            self.panel2, id=wx.ID_ANY, label="Time till next break",
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )

        self.time_before_break = self.spin_ctrl1.GetValue() * 60

        t = time.strftime('%M:%S', time.gmtime(self.time_before_break))
        self.st4 = wx.StaticText(
            self.panel2, id=wx.ID_ANY, label=t,
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )

        self.st5 = wx.StaticText(
            self.panel2, id=wx.ID_ANY, label="Time inactive, seconds",
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )

        self.spin_ctrl3 = wx.SpinCtrl(self.panel2, id=wx.ID_ANY, value=str(params["time inactive"]), pos=(200, 50),
                                      size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, min=1, max=1000, initial=0,
                                      name="wxSpinCtrl2")

        self.st6 = wx.StaticText(
            self.panel2, id=wx.ID_ANY, label="Time to renew, seconds",
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )

        self.spin_ctrl4 = wx.SpinCtrl(self.panel2, id=wx.ID_ANY, value=str(params["time to renew"]), pos=(200, 50),
                                      size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, min=1, max=1000, initial=0,
                                      name="wxSpinCtrl2")

        # t = datetime.timedelta(seconds=10)
        # t = str(t)
        # # t = time.strftime('%M:%S', time.gmtime(t))

        g_sizer1.Add(st1, flag=wx.LEFT | wx.TOP, border=10)
        g_sizer1.Add(self.spin_ctrl1, flag=wx.LEFT | wx.TOP, border=10)

        g_sizer1.Add(st2, flag=wx.LEFT | wx.TOP, border=10)
        g_sizer1.Add(self.spin_ctrl2, flag=wx.LEFT | wx.TOP, border=10)

        g_sizer1.Add(self.st5, flag=wx.LEFT | wx.TOP, border=10)
        g_sizer1.Add(self.spin_ctrl3, flag=wx.LEFT | wx.TOP, border=10)

        g_sizer1.Add(self.st6, flag=wx.LEFT | wx.TOP, border=10)
        g_sizer1.Add(self.spin_ctrl4, flag=wx.LEFT | wx.TOP, border=10)

        g_sizer1.Add(self.st3, flag=wx.LEFT | wx.TOP, border=10)
        g_sizer1.Add(self.st4, flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(g_sizer1, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.button_start = wx.Button(self.panel2, id=91, label="Start break", pos=(200, 200), size=(200, 100))
        hbox5.Add(self.button_start, flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(hbox5, flag=wx.ALL | wx.ALIGN_CENTER, border=10)
        # endregion

        self.panel2.Bind(wx.EVT_BUTTON, self.break_begin, id=91)

        self.timer1 = wx.Timer(self, id=50)
        self.timer1.Start(1000)

        self.timer2 = wx.Timer(self, id=60)
        self.timer2.Start(self.spin_ctrl3.GetValue() * 1000)

        self.timer3 = wx.Timer(self, id=61)
        self.timer3.Start(1000)

        self.timer4 = wx.Timer(self, id=62)
        self.Bind(wx.EVT_TIMER, self.check_inactivity_timer, id=62)

        self.Bind(wx.EVT_TIMER, self.check_activity, id=60)
        self.Bind(wx.EVT_TIMER, self.time_till_break, id=61)
        self.Bind(wx.EVT_SPINCTRL, self.on_spinctrl1, id=71)
        self.Bind(wx.EVT_SPINCTRL, self.on_spinctrl3, id=self.spin_ctrl3.GetId())
        self.Bind(wx.EVT_SPINCTRL, self.on_spinctrl2, id=self.spin_ctrl2.GetId())
        self.Bind(wx.EVT_SPINCTRL, self.on_spinctrl4, id=self.spin_ctrl4.GetId())

        self.panel1.Bind(wx.EVT_LEFT_DOWN, self.lmb_pressed)
        # self.Bind(wx.EVT_BUTTON, self.onButton1, id=self.btn1.GetId())

        self.Bind(wx.EVT_TIMER, self.func1, id=50)
        # self.Bind(wx.EVT_TIMER, self.relax_darken, id=60)
        self.Bind(wx.EVT_MOVING, self.on_move)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        # self.Bind(wx.EVT_CLOSE, self.on_exit)

        self.Bind(wx.EVT_CLOSE, self.on_minimize)
        self.Bind(wx.EVT_CLOSE, self.on_minimize)
        self.Bind(wx.EVT_CHECKBOX, self.on_check_box)
        self.datePicker1.Bind(wx.adv.EVT_DATE_CHANGED, self.on_date_picker)

        self.pn1_main.Bind(wx.EVT_PAINT, self.on_paint1)
        self.pn2_main.Bind(wx.EVT_PAINT, self.on_paint2)

        self.panel1.Bind(wx.EVT_SET_FOCUS, self.on_focus)

    def on_date_picker(self, event):
        a = self.datePicker1.GetValue()
        print(f"{a = }")
        b = wx.DateTime.FormatISOCombined(a).split("T")[0]
        # b = f"{time.strftime('%H:%M:%S', time.gmtime(b))}"
        # print(f"{b = }")
        # d1 = "2022-12-29"
        t1 = "07:00:00"
        d1 = datetime.datetime.fromisoformat(f"{b} {t1}")
        print(f"{d1 = }")
        one_day = datetime.timedelta(days=1)
        self.date_start = d1
        self.date_end = d1 + one_day
        print(f"{self.date_start = }")
        print(f"{self.date_end = }")
        self.check_box_pressed = True
        self.Refresh()
        print("self.refreshed")

    def on_check_box(self, event):
        # self.v = self.checkBox1.GetValue()
        self.check_box_pressed = True
        self.Refresh()

    def on_spinctrl1(self, event):
        self.time_before_break = self.spin_ctrl1.GetValue() * 60
        t = time.strftime('%M:%S', time.gmtime(self.time_before_break))
        # print(f"{t = }")
        self.st4.Label = str(t)
        self.save_params_to_json()

    def on_spinctrl3(self, event):
        print("on_spinctrl3")
        self.timer2.Stop()
        self.timer2.Start(self.spin_ctrl3.GetValue() * 1000)
        self.save_params_to_json()

    def on_spinctrl2(self, event):
        self.save_params_to_json()

    def on_spinctrl4(self, event):
        self.save_params_to_json()

    def time_till_break(self, event):
        if self.rd1.GetValue() == True:
            if self.user_active:
                if self.time_before_break > 1:
                    self.time_before_break -= 1
                    t = time.strftime('%M:%S', time.gmtime(self.time_before_break))
                    # print(f"{t = }")
                    self.st4.Label = str(t)
                elif self.time_before_break == 1:
                    self.time_before_break = -1
                    self.break_begin(event)

    #     if self.time_of_inactivity < 10:
    #         self.time_of_inactivity += 1
    #     else:
    #         self.time_of_inactivity = 0
    #
    #     if self.time_of_inactivity == 10:
    #         self.check_activity()
    #
    def check_activity(self, event):

        # self.mouse_coord = pyautogui.position()
        mouse_new_coord = pyautogui.position()
        if mouse_new_coord != self.mouse_last_coord:
            self.mouse_last_coord = mouse_new_coord
            self.user_active = True
            self.timer4.Stop()
        else:
            self.user_active = False
            if self.timer4.IsRunning() == False:
                self.timer4.Start(self.spin_ctrl4.GetValue() * 1000)

        print(f"{self.user_active = }")

    def check_inactivity_timer(self, event):
        self.time_before_break = self.spin_ctrl1.GetValue() * 60
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
        print("OnMove")
        self.Refresh()
        wx.Event.Skip(event)

    # def on_exit(self, event):
    #     print("closing window")
    #     wx.CallAfter(self.Destroy)
    #     self.Close()

    def on_minimize(self, event):
        print("minimizing window")
        self.Iconize()
        self.Hide()
        # wx.CallAfter(self.Destroy)
        # self.Close()

    def on_paint1(self, event):
        print("onPaint1")
        width_of_panel_with_names = self.pn1_main.GetVirtualSize()[0]
        # self.task_bar_icon.set_icon(TRAY_ICON2)
        if self.new_line_added_to_db == True or self.check_box_pressed == True:
            self.all_rows = self.get_rows_from_database()
            self.new_line_added_to_db = False
            self.check_box_pressed = False

        dc = wx.PaintDC(self.pn1_main)
        # dc2 = wx.PaintDC(self.pn2_main)
        dc.SetPen(wx.Pen('#fdc073', style=wx.TRANSPARENT))

        dc.DrawLine(0, 0, 500, 700)
        dc.SetBrush(wx.Brush('#d5dde6', wx.SOLID))

        for i, row in enumerate(self.all_rows):
            if len(row) > 2:
                data = f"({row[2]}) {row[0]} "
            else:
                data = f"{row[0]}"

            duration = row[1]
            # print(f"{duration = }")
            if i >= self.max_rows_to_show_on_main:
                # print(f"{self.max_rows_to_show_on_main = }")
                break
            if dc.GetTextExtent(data)[0] > width_of_panel_with_names - 35:
                while dc.GetTextExtent(data)[0] > width_of_panel_with_names - 35:
                    data = data[:len(data) - 1]
                data = data[:len(data)] + '...'
            # if duration > 0:
            # dc.DrawRectangle(0, self.LineHeight * i, int(math.log(duration, 50)), self.LineHeight)
            if i != len(self.all_rows) - 1:
                # print(int(duration // self.all_rows[-1][1] * width_of_panel_with_names))
                dc.DrawRectangle(0, self.line_height * i,
                                 int(duration / self.all_rows[-1][1] * width_of_panel_with_names), self.line_height)
                f = dc.DrawText(f"{data}", 20, self.line_height * i)
            else:
                dc.SetFont(self.font2)
                f = dc.DrawText(f"{data}", 20, self.line_height * i)
                dc.SetFont(self.font1)

    def on_paint2(self, event):
        print("onPaint2")
        # print(event)
        # self.task_bar_icon.set_icon(TRAY_ICON2)

        dc2 = wx.PaintDC(self.pn2_main)
        # dc2 = wx.PaintDC(self.pn2_main)
        dc2.SetPen(wx.Pen('#fdc073', style=wx.TRANSPARENT))

        dc2.DrawLine(0, 0, 500, 700)
        dc2.SetBrush(wx.Brush('#d5dde6', wx.SOLID))
        for i, row in enumerate(self.all_rows):
            duration = row[1]
            if i >= self.max_rows_to_show_on_main:
                break
            if i == len(self.all_rows) - 1:
                dc2.SetFont(self.font2)
                dc2.DrawText(f"{time.strftime('%H:%M:%S', time.gmtime(duration))}", 10, self.line_height * i)
                dc2.SetFont(self.font1)
            else:
                dc2.DrawText(f"{time.strftime('%H:%M:%S', time.gmtime(duration))}", 10, self.line_height * i)

    def on_quit(self, event):
        print(event)
        print("ccccccccccccc")
        self.Close()

    def break_begin(self, event):
        frame = DarkWindow(self, "Focus mode33", self.spin_ctrl2.GetValue())
        wx.Event.Skip(event)

    def lmb_pressed(self, event):
        print("LMB pressed")
        self.Refresh()
        wx.Event.Skip(event)

    def on_button1(self, event):
        print("pressed button...")
        # self.btn1.SetLabel("1245")
        # self.btn1

    # def relax_darken(self, event):
    #     print("darken")
    #     # print(event.GetId(), "func2")
    #     # self.getrowsfromdatabase()
    #     pass

    def get_rows_from_database(self):
        if self.checkBox1.GetValue():
            res = self.db.query_extended_load_on_date(self.date_start, self.date_end)
        else:
            res = self.db.query_simple_load_on_date(self.date_start, self.date_end)

        self.all_rows = res
        # print(f"{len(self.all_rows) = }")
        if len(self.all_rows) > 0:
            if len(self.all_rows[0]) > 2:
                result_row = (f"({sum([x[2] for x in self.all_rows])})", sum([x[1] for x in self.all_rows]))
            else:
                result_row = (f"Result", sum([x[1] for x in self.all_rows]))


        else:
            result_row = (f"No result for that day", 0)
        self.all_rows.append(result_row)
        # print(f"{self.all_rows = }")

        print("Loaded from db")

        size1 = (100, (min(self.max_rows_to_show_on_main, len(self.all_rows))) * self.line_height)
        size2 = (100,
                 (min(self.max_rows_to_show_on_main, len(self.all_rows))) * self.line_height + self.pn3_main.GetSize()[
                     1] + 10)
        self.pn1_main.SetMinSize(size1)
        self.scrolled_window.SetVirtualSize(size2)
        return res

    def func1(self, event):
        # print(event.GetId())
        # appName, windowName = getActiveWindow()

        self.save_to_db()

    def save_to_db(self):
        active_window = get_active_window()
        if active_window:
            full_app_name = '-'.join(active_window)
            if full_app_name != self.LastActiveWindow:
                print("act wind changed")
                if datetime.datetime.now() - self.TimeAppOpened > datetime.timedelta(seconds=0):
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

        # self.Refresh()

    def save_params_to_json(self):
        x = {
            "work time": self.spin_ctrl1.GetValue(),
            "break time": self.spin_ctrl2.GetValue(),
            "time inactive": self.spin_ctrl3.GetValue(),
            "time to renew": self.spin_ctrl4.GetValue()
        }
        # convert into JSON:
        y = json.dumps(x)
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
        # wx.lib.inspection.InspectionTool().Show()
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
