import wx
import json  # for saving information
import math
import sqlite3
import datetime
from focus1 import get_active_window

app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.


# TODO: using this tool

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        self.Button1Name = "but1"
        self.LastActiveWindow = None
        self.TimeAppOpened = datetime.datetime.now()
        self.all_rows = self.get_rows_from_database()

        # self.text = [None] * 30
        try:
            with open('data_file.json', 'r') as outfile:
                self.apps = json.load(outfile)
        except Exception:
            self.apps = {}

        wx.Frame.__init__(self, parent, title=title, size=(800, 700),
                          style=wx.MINIMIZE_BOX | wx.RESIZE_BORDER | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        # self.CreateStatusBar() # A Statusbar in the bottom of the window

        tabs = wx.Notebook(self, id=wx.ID_ANY)
        self.panel1 = wx.Panel(tabs)
        self.panel1.SetBackgroundColour("#f1f7fe")

        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(14)
        self.panel1.SetFont(font)
        tabs.InsertPage(0, self.panel1, "Tracker", select=True)
        self.panel2 = wx.Panel(tabs)

        self.panel2.SetBackgroundColour("#367bef")
        tabs.InsertPage(1, self.panel2, "Relax")

        self.LineHeight = 30
        # self.Show(True)
        # self.SetTransparent(205)
        # self.SetBackgroundColour("#367bef")

        # self.Bind(wx.EVT_MENU, self.onQuit, id=wx.ID_EXIT)
        # self.Bind(wx.EVT_COMMAND_LEFT_CLICK, self.LMBpressed)
        self.panel1.Bind(wx.EVT_LEFT_DOWN, self.lmb_pressed)
        # self.Bind(wx.EVT_BUTTON, self.onButton1, id=self.btn1.GetId())

        self.timer1 = wx.Timer(self, id=50)
        self.timer1.Start(1000)  # 25 changes per second.
        self.timer2 = wx.Timer(self, id=60)
        self.timer2.Start(3000)  # 25 changes per second.

        self.Bind(wx.EVT_TIMER, self.func1, id=50)
        self.Bind(wx.EVT_TIMER, self.func2, id=60)
        self.Bind(wx.EVT_MOVING, self.on_move)
        self.Bind(wx.EVT_SIZE, self.on_resize)

        self.panel1.Bind(wx.EVT_PAINT, self.on_paint)
        self.panel1.Bind(wx.EVT_SET_FOCUS, self.on_focus)

        self.list = wx.ListCtrl(self.panel2, wx.ID_ANY, style=wx.LC_REPORT, size=(600, 200))
        self.list.SetFont(wx.Font(wx.FontInfo(12)))
        self.list.SetBackgroundColour("#f0f0f0")

        self.list.InsertColumn(0, 'Название', width=100)
        self.list.InsertColumn(1, 'Автор', width=100)
        self.list.InsertColumn(2, 'Год издания', wx.LIST_FORMAT_RIGHT, 140)
        self.list.InsertColumn(3, 'Цена', wx.LIST_FORMAT_RIGHT, 90)

        books = [('Евгений Онегин', 'Пушкин А.С.', 2000, 192),
                 ('Пиковая дама', 'Пушкин А.С.', 2004, 150.53),
                 ('Мастер и Маргарита', 'Булгаков М.А.', 2005, 500),
                 ('Роковые яйца', 'Булгаков М.А.', 2003, 400),
                 ('Белая гвардия', 'Булгаков М.А.', 2010, 340)]

        for b in books:
            self.list.Append(b)

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

    def on_paint(self, event):
        print("onPaint")

        self.get_rows_from_database()

        dc = wx.PaintDC(self.panel1)
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
            if i >= 20:
                break
            if len(data) > 40:
                data = data[:40] + "..."
            if duration > 0:
                dc.DrawRectangle(0, self.LineHeight * i, int(math.log(duration, 1.01)), self.LineHeight)
                dc.DrawText(f"{data} {int(duration)} s", 20, self.LineHeight * i)

        # for key, value in self.apps.items():
        #     width = value["time"]
        #     if i >= 10:
        #         break
        #     if width > 0:
        #         dc.DrawRectangle(0, self.LineHeight * i, int(math.log(width, 1.01)), self.LineHeight)
        #         dc.DrawText(f"{key} {value['time']} s", 20, self.LineHeight * i)
        #     i += 1

    def on_quit(self, event):
        print(event)
        print("ccccccccccccc")
        self.Close()

    def lmb_pressed(self, event):
        print("LMB pressed")
        self.Refresh()
        wx.Event.Skip(event)

        # wx.StaticText(self, id=14, label="Heydddddyy678")
        # self.tx1.SetLabel("ffffff")
        # print(event)

    def on_button1(self, event):
        print("pressed button...")
        # self.btn1.SetLabel("1245")
        # self.btn1

    def func2(self, event):
        # print(event.GetId(), "func2")
        # self.getrowsfromdatabase()
        pass

    @staticmethod
    def get_rows_from_database():
        database_cursor.execute("""select full_name, sum((julianday(time_end)-julianday(time_start))*24*60*60) 
        from data 
        group by full_name 
        order by sum(julianday(time_end)-julianday(time_start)) desc""")
        return database_cursor.fetchall()
        # [print(x) for x in self.all_rows]

    def func1(self, event):
        # print(event.GetId())
        # print("Func called")
        # appName, windowName = getActiveWindow()
        self.save_to_db()

    def save_to_db(self):
        active_window = get_active_window()
        if active_window:
            full_app_name = ' '.join(active_window)
            if full_app_name != self.LastActiveWindow:
                if self.LastActiveWindow:
                    database_cursor.execute("select count(*) from data")
                    number_of_rows = database_cursor.fetchone()[0]
                    # print(f"{number_of_rows = }")
                    database_cursor.execute("""
                        INSERT INTO data VALUES
                            (?, ?, ?, ?, NULL)
                    """,
                                            (number_of_rows + 1, self.LastActiveWindow, self.TimeAppOpened,
                                             datetime.datetime.now()))
                    database_connection.commit()
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
            print(app)

        # self.Refresh()


database_connection = sqlite3.connect("database.db")
database_cursor = database_connection.cursor()

# frame = wx.Frame(None, wx.ID_ANY, "Hello World", size=(700, 500)) # A Frame is a top-level window.
frame = MainWindow(None, "Focus mode")  # A Frame is a top-level window.
frame.Centre()
frame.Show(True)  # Show the frame.
# frame.Close()
app.MainLoop()
database_cursor.close()

print('sss')
# with open('data_file.json', 'w') as outfile:
#     json.dump(frame.apps, outfile, indent=4)
