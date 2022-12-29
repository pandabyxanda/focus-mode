import wx
import wx.adv
import wx.lib.scrolledpanel as scrolled
import json  # for saving information
import math
import sqlite3
import datetime
import time
from focus1 import get_active_window
import wx.lib.mixins.inspection
import sql
import screen_brightness_control

TRAY_TOOLTIP = 'Name'
TRAY_ICON = 'star.png'
TRAY_ICON2 = 'star (2).png'
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
        # self.frame.RequestUserAttention(flags=wx.USER_ATTENTION_INFO)

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
                          style=wx.DEFAULT_FRAME_STYLE & ~wx.CAPTION | wx.FRAME_FLOAT_ON_PARENT | wx.STAY_ON_TOP)
        # wx.Frame.__init__(self, parent, title=title, size=screen_size, pos=(0,0),
        #                   style=wx.MINIMIZE_BOX | wx.RESIZE_BORDER | wx.CAPTION
        #                         | wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.FRAME_FLOAT_ON_PARENT)
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

        self.timer2 = wx.Timer(self, id=104)
        self.timer2.Start(1000)

        self.timer3 = wx.Timer(self, id=105)
        self.timer3.Start(100)

        self.Bind(wx.EVT_TIMER, self.count_down, id=104)
        self.Bind(wx.EVT_TIMER, self.on_timer_change_opacity, id=105)

        self.break_duration = duration
        t = time.strftime('%M:%S', time.gmtime(duration))
        self.button_label = t + " \n" + "Press to close"
        self.button_stop = wx.Button(self.panel5, id=90, label=self.button_label, size=(300, 200))
        self.button_stop.Centre()
        self.panel5.Bind(wx.EVT_BUTTON, self.on_button_stop, id=90)
        self.Maximize()

        # self.timer1 = wx.Timer(self, id=103)
        # self.timer1.Start(self.break_duration)  # 25 changes per second.
        # self.Bind(wx.EVT_TIMER, self.end_of_relax_mode, id=103)

        # self.MAXIMIZE_BOX()
        # self.STAY_ON_TOP()

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
        self.parent.time_before_break = self.parent.spin_ctrl1.GetValue()
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


        self.max_id = self.db.query_select_max_id()
        self.new_line_added_to_db = False
        self.line_height = 30
        self.max_rows_to_show_on_main = 200


        # screen_size = wx.GetDisplaySize()
        # print(f"{screen_size = }")

        # self.text = [None] * 30
        try:
            with open('data_file.json', 'r') as outfile:
                self.apps = json.load(outfile)
        except Exception:
            self.apps = {}

        wx.Frame.__init__(self, parent, title=title, size=(800, 700),
                          style=wx.MINIMIZE_BOX | wx.RESIZE_BORDER | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)



        self.SetIcon(wx.Icon('favicon.ico', wx.BITMAP_TYPE_ICO))

        self.panel1 = wx.Panel(self)
        self.font1 = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font1.SetPointSize(14)
        self.font2 = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font2.SetPointSize(14)
        self.font2.MakeBold()
        self.panel1.SetFont(self.font1)

        tabs = wx.Notebook(self.panel1, id=wx.ID_ANY)
        # tabs.
        # tabs.SetBackgroundColour("#dfedfd")
        # tabs.SetOwnForegroundColour("#dfedfd")

        # creating tab 1
        self.vbox_main9 = wx.BoxSizer(wx.VERTICAL)
        self.vbox_main9.Add(tabs, 1, wx.ALL | wx.EXPAND, 0)

        self.panel1.SetSizer(self.vbox_main9)
        # self.panel1.SetBackgroundColour("#dfedfd")

        self.scrolled_window = scrolled.ScrolledPanel(tabs, wx.ID_ANY)
        self.scrolled_window.SetupScrolling(scroll_x=False, scroll_y=True)

        tabs.AddPage(self.scrolled_window, "Tracker", select=True)
        # self.panel2 = wx.Panel(tabs)
        # tabs.AddPage(self.panel2, "Tab 2", False)

        self.vbox_main = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_window.SetSizer(self.vbox_main)



        self.pn3_main = wx.Panel(self.scrolled_window,
                                 size=wx.DefaultSize)
        self.datePicker1 = wx.adv.DatePickerCtrl(self.pn3_main, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition,
                                                   wx.DefaultSize, wx.adv.DP_DEFAULT)
        # self.pn3_main.SetBackgroundColour("#4444fe")
        self.hbox_main3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_main3.Add(self.datePicker1, border=0)
        self.checkBox1 = wx.CheckBox(self.pn3_main, wx.ID_ANY, u"Extended", wx.DefaultPosition, wx.DefaultSize, style=wx.ALIGN_RIGHT)
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
        self.pn1_main.SetBackgroundColour("#dfedfd")
        self.pn2_main.SetBackgroundColour("#dfedfd")

        self.all_rows = self.get_rows_from_database()
        self.check_box_pressed = False

        # size1 = (100, 100)
        #
        # self.pn1_main.SetMinSize(size1)
        # self.pn2_main.SetSize(size1)
        # hbox_main.Fit(self.pn1_main)
        # hbox_main.Fit(self.pn2_main)
        # vbox_main.Fit(self.scrolled_window)
        # self.SetSize(size1)
        # self.panel1.SetSize(size1)

        self.panel2 = wx.Panel(tabs)

        self.panel2.SetFont(self.font1)

        self.panel2.SetBackgroundColour("#f1f7fe")
        # tabs.InsertPage(1, self.panel2, "Relax", select=False)
        tabs.AddPage(self.panel2, "Relax", select=False)


        # self.Show(True)
        # self.SetTransparent(205)
        # self.SetBackgroundColour("#367bef")



        self.panel1.Bind(wx.EVT_LEFT_DOWN, self.lmb_pressed)
        # self.Bind(wx.EVT_BUTTON, self.onButton1, id=self.btn1.GetId())

        self.Bind(wx.EVT_TIMER, self.func1, id=50)
        self.Bind(wx.EVT_TIMER, self.relax_darken, id=60)
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

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.panel2.SetSizer(vbox)

        # break_on_timer_mode = wx.ToggleButton(self.panel2, id=93, label='red', pos=(20, 25))

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        pn = wx.Panel(self.panel2)
        sb1 = wx.StaticBox(pn, label="Timer:", size=(150, 50))
        self.rd1 = wx.RadioButton(pn, label="On", pos=(10, 20), style=wx.RB_GROUP, id=92)
        rd2 = wx.RadioButton(pn, label="Off", pos=(100, 20), id=93)
        rd2.SetValue(True)

        hbox1.Add(pn, flag=wx.LEFT | wx.TOP, border=10)
        # hbox.Add(rd1, flag=wx.LEFT | wx.TOP, border=10)
        # hbox.Add(rd2, flag=wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox1, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(
            self.panel2, id=wx.ID_ANY, label="Work time, seconds", pos=(10, 0),
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )
        self.spin_ctrl1 = wx.SpinCtrl(self.panel2, id=71, value="30", pos=(200, 0),
                                      size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, min=10, max=1000, initial=0,
                                      name="wxSpinCtrl")
        hbox2.Add(st1, flag=wx.LEFT | wx.TOP, border=10)
        hbox2.Add(self.spin_ctrl1, flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(hbox2, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(
            self.panel2, id=wx.ID_ANY, label="Break time, seconds", pos=(10, 50),
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )
        self.spin_ctrl2 = wx.SpinCtrl(self.panel2, id=wx.ID_ANY, value="10", pos=(200, 50),
                                      size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, min=0, max=100, initial=0,
                                      name="wxSpinCtrl2")
        hbox3.Add(st2, flag=wx.LEFT | wx.TOP, border=10)
        hbox3.Add(self.spin_ctrl2, flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(hbox3, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        self.st3 = wx.StaticText(
            self.panel2, id=wx.ID_ANY, label="Time till next break",
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )

        # tc1 = wx.TextCtrl(
        #     self.panel2, id=wx.ID_ANY, value="ggg", pos=(100, 0),
        #     size=wx.DefaultSize, style=0, validator=wx.DefaultValidator,
        #     name=wx.TextCtrlNameStr
        # )

        self.time_before_break = self.spin_ctrl1.GetValue()

        t = time.strftime('%M:%S', time.gmtime(self.time_before_break))
        # print(f"{t = }")
        self.st4 = wx.StaticText(
            self.panel2, id=wx.ID_ANY, label=t,
            size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr
        )
        hbox4.Add(self.st3, flag=wx.LEFT | wx.TOP, border=10)
        hbox4.Add(self.st4, flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(hbox4, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.button_start = wx.Button(self.panel2, id=91, label="Start break", pos=(200, 200), size=(200, 100))
        hbox5.Add(self.button_start, flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(hbox5, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        self.m_calendar1 = wx.adv.CalendarCtrl(self.panel2, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition,
                                               wx.DefaultSize, wx.adv.CAL_SHOW_HOLIDAYS)
        hbox6.Add(self.m_calendar1, flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(hbox6, flag=wx.ALL | wx.ALIGN_CENTER, border=10)


        self.panel2.Bind(wx.EVT_BUTTON, self.break_begin, id=91)

        # print(self.spin_ctrl1.GetValue())

        self.timer1 = wx.Timer(self, id=50)
        self.timer1.Start(1000)

        self.timer2 = wx.Timer(self, id=60)
        self.timer2.Start(self.spin_ctrl1.GetValue() * 1000)

        self.timer3 = wx.Timer(self, id=61)
        self.timer3.Start(1000)

        self.Bind(wx.EVT_TIMER, self.time_till_break, id=61)
        self.Bind(wx.EVT_SPINCTRL, self.on_spinctrl1, id=71)

    def on_date_picker(self, event):
        a = self.datePicker1.GetValue()
        print(f"{a = }")
        b = wx.DateTime.FormatISOCombined(a).replace("-", ":").replace("T", " ")
        # b = f"{time.strftime('%H:%M:%S', time.gmtime(b))}"
        print(f"{b = }")

    def on_check_box(self, event):
        # self.v = self.checkBox1.GetValue()
        self.check_box_pressed = True
        self.Refresh()


    def on_spinctrl1(self, event):
        self.time_before_break = self.spin_ctrl1.GetValue()
        t = time.strftime('%M:%S', time.gmtime(self.time_before_break))
        # print(f"{t = }")
        self.st4.Label = str(t)

    def time_till_break(self, event):
        if self.rd1.GetValue() == True:
            if self.time_before_break > 1:
                self.time_before_break -= 1
                t = time.strftime('%M:%S', time.gmtime(self.time_before_break))
                # print(f"{t = }")
                self.st4.Label = str(t)
            elif self.time_before_break == 1:
                self.time_before_break = -1
                self.break_begin(event)

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
        # print("size = ", self.pn1_main.GetVirtualSize())
        # print(event)
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
        # max_time = max([x["time"] for x in self.apps.values()])
        # print(max_time)

        # [print(x) for x in self.all_rows]
        # self.apps = {k: v for k, v in sorted(self.apps.items(), key=lambda item: item[1]['time'], reverse=True)}

        for i, row in enumerate(self.all_rows):
            data = row[0]
            duration = row[1]
            # print(f"{duration = }")
            if i >= self.max_rows_to_show_on_main:
                print(f"{self.max_rows_to_show_on_main = }")
                break
            if dc.GetTextExtent(data)[0] > width_of_panel_with_names-35:
                while dc.GetTextExtent(data)[0] > width_of_panel_with_names-35:
                    data = data[:len(data)-1]
                    # print(len(data))
                    # print(len(data)-(dc.GetTextExtent(data)[0]-width_of_panel_with_names) // (dc.GetTextExtent(data)[0] // len(data)))
                    # print(len(data))
                    # data = data[:len(data)-(dc.GetTextExtent(data)[0]-width_of_panel_with_names) // (dc.GetTextExtent(data)[0] // len(data))-5] + "..."
                data = data[:len(data)]+'...'
            if duration > 0:
                # dc.DrawRectangle(0, self.LineHeight * i, int(math.log(duration, 50)), self.LineHeight)
                if i != len(self.all_rows)-1:
                    dc.DrawRectangle(0, self.line_height * i, int(duration * 1000 / 21600), self.line_height)
                    f = dc.DrawText(f"{data}", 20, self.line_height * i)
                else:
                    dc.SetFont(self.font2)
                    f = dc.DrawText(f"{data}", 20, self.line_height * i)
                    dc.SetFont(self.font1)
                # print(dc.GetTextExtent(data))

                # dc2.DrawText(f"{time.strftime('%H:%M:%S', time.gmtime(duration))}", 450, self.LineHeight * i)

        # for key, value in self.apps.items():
        #     width = value["time"]
        #     if i >= 10:
        #         break
        #     if width > 0:
        #         dc.DrawRectangle(0, self.LineHeight * i, int(math.log(width, 1.01)), self.LineHeight)
        #         dc.DrawText(f"{key} {value['time']} s", 20, self.LineHeight * i)
        #     i += 1

    def on_paint2(self, event):
        print("onPaint2")
        # print(event)
        # self.task_bar_icon.set_icon(TRAY_ICON2)

        dc2 = wx.PaintDC(self.pn2_main)
        # dc2 = wx.PaintDC(self.pn2_main)
        dc2.SetPen(wx.Pen('#fdc073', style=wx.TRANSPARENT))

        dc2.DrawLine(0, 0, 500, 700)
        dc2.SetBrush(wx.Brush('#d5dde6', wx.SOLID))
        # max_time = max([x["time"] for x in self.apps.values()])
        # print(max_time)

        # [print(x) for x in self.all_rows]
        # self.apps = {k: v for k, v in sorted(self.apps.items(), key=lambda item: item[1]['time'], reverse=True)}
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
        # self.break_begin(event)
        # self.Refresh()
        # frame.Centre()
        # frame.Show(True)

        # wx.StaticText(self, id=14, label="Heydddddyy678")
        # self.tx1.SetLabel("ffffff")
        # print(event)

    def on_button1(self, event):
        print("pressed button...")
        # self.btn1.SetLabel("1245")
        # self.btn1

    def relax_darken(self, event):
        print("darken")
        # print(event.GetId(), "func2")
        # self.getrowsfromdatabase()
        pass

        # get current brightness value
        # prev = screen_brightness_control.get_brightness()
        # print(prev)
        # screen_brightness_control.set_brightness(1)
        # print(screen_brightness_control.get_brightness())
        # time.sleep(4)
        # screen_brightness_control.set_brightness(prev[0])
        # print(screen_brightness_control.get_brightness())


    def get_rows_from_database(self):
        # database_cursor.execute("""select full_name, sum((julianday(time_end)-julianday(time_start))*24*60*60)
        # from data
        # group by full_name
        # order by sum(julianday(time_end)-julianday(time_start)) desc""")
        # print(f"{self.checkBox1.GetValue() = }")
        # print(f"{self.checkBox1.GetValue() = }")
        if self.checkBox1.GetValue():
            res = self.db.query_extended_load_on_date('2022-12-29 00:00:00', '2022-12-29 23:59:59')
        else:
            res = self.db.query_simple_load_on_date('2022-12-29 00:00:00', '2022-12-29 23:59:59')
        self.all_rows = res
        # print(f"{len(self.all_rows) = }")
        self.all_rows.append(("Result:", sum([x[1] for x in self.all_rows])))
        # print(f"{self.all_rows = }")

        print("Loaded from db")

        size1 = (100, (min(self.max_rows_to_show_on_main, len(self.all_rows))) * self.line_height)
        size2 = (100, (min(self.max_rows_to_show_on_main, len(self.all_rows))) * self.line_height+self.pn3_main.GetSize()[1]+10)
        self.pn1_main.SetMinSize(size1)
        # self.SetVirtualSize(size1)
        self.scrolled_window.SetVirtualSize(size2)
        # self.SendSizeEvent()
        # self.PostSizeEvent()
        # self.Layout()
        # self.Fit()
        # self.vbox_main.SetMinSize(size1)
        # self.SetSize(self.GetSize())
        # self.Refresh()
        return res
        # [print(x) for x in self.all_rows]

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
                if datetime.datetime.now()-self.TimeAppOpened > datetime.timedelta(seconds = 5):
                    if self.LastActiveWindow:
                        self.max_id += 1
                        self.db.query_save(self.max_id, self.LastActiveWindow, self.TimeAppOpened,
                                                 datetime.datetime.now())
                        self.new_line_added_to_db = True
                        print("Saved to db")

                self.LastActiveWindow = full_app_name
                self.TimeAppOpened = datetime.datetime.now()

            if full_app_name not in self.apps:
                self.apps[full_app_name] = {"time": 0, "line_number": len(self.apps)}
                # print(self.apps)
                # self.text[len(self.apps)-1].SetLabel(f"{fullAppName}")
            else:
                self.apps[full_app_name]["time"] += 1
                # self.text[self.apps[fullAppName]["line_number"]].SetLabel(f"{fullAppName} {self.apps[fullAppName]['time']}s")

                # with open('data_file.json', 'w') as outfile:
                #     json.dump(self.apps, outfile, indent=4)
        else:
            print(active_window)

        # self.Refresh()


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
    # app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.

    # frame = wx.Frame(None, wx.ID_ANY, "Hello World", size=(700, 500)) # A Frame is a top-level window.
    # frame = MainWindow(None, "Focus mode")  # A Frame is a top-level window.
    # frame.Centre()
    # frame.Show(True)  # Show the frame.
    # frame.Close()
    db = sql.DataBase(DATABASE_NAME)
    db.connect()
    db.create_table_if_not_exists()

    app = App(redirect=False, db=db)
    app.MainLoop()
    # database_cursor.close()

    print('sss')
    # with open('data_file.json', 'w') as outfile:
    #     json.dump(frame.apps, outfile, indent=4)


# database_connection = sqlite3.connect("database.db")
# database_cursor = database_connection.cursor()
if __name__ == '__main__':
    main()

# database_cursor.close()
