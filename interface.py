import wx
import json
import math
from focus1 import getActiveWindow

app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        self.Button1Name = "but1"
        self.text = [None] * 30
        try:
            with open('data_file.json', 'r') as outfile:
                self.apps = json.load(outfile)
        except:
            self.apps = {}

        # wx.Frame.__init__(self, parent, title=title, size=(900,700), style=wx.DEFAULT_FRAME_STYLE)
        wx.Frame.__init__(self, parent, title=title, size=(1400, 700),
                          style=wx.MINIMIZE_BOX | wx.RESIZE_BORDER | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        # self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)

        # self.CreateStatusBar() # A Statusbar in the bottom of the window

        # # Setting up the menu.
        # filemenu= wx.Menu()
        #
        # # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        # filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        # filemenu.AppendSeparator()
        # filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        #
        # # # Creating the menubar.
        # # menuBar = wx.MenuBar()
        # # menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        # # self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

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
        # if len(self.apps)>0:
        #     for key, value in self.apps.items():
        #         st = self.text[value['line_number']] = \
        #             wx.StaticText(self.panel1, pos=wx.Point(400, value['line_number'] * self.LineHeight), size=(400, 30),
        #                           label=f"{key} {value['time']}s", style=wx.ST_ELLIPSIZE_END)
        #         st.SetBackgroundColour((250,250,250,0.8))
        #
        # for i in range(len(self.apps), len(self.text)):
        #     self.text[i] = \
        #         wx.StaticText(self.panel1, pos=wx.Point(10, i * self.LineHeight),
        #                       label=f"empty{i}")

      #   g = wx.Gauge(self.panel1, id=wx.ID_ANY, range=100, pos=wx.DefaultPosition,
      # size=wx.DefaultSize, style=wx.GA_HORIZONTAL, validator=wx.DefaultValidator,
      # name=wx.GaugeNameStr)
      #   g.SetValue(50)
        # self.btn1 = wx.Button(panel, wx.ID_ANY, self.Button1Name)

        # self.tx1 = wx.StaticText(self, id=15, label="Heyyy678")
        # self.tx2 = wx.StaticText(self, id=15, label="Heyyy67")

        # self.btn1 = wx.Button(self, wx.ID_ANY, self.Button1Name)
        # self.btn1.SetPosition(wx.Point(100, 200))


        # self.Show(True)
        # self.SetTransparent(205)
        # self.SetBackgroundColour("#367bef")

        # self.Bind(wx.EVT_MENU, self.onQuit, id=wx.ID_EXIT)
        # self.Bind(wx.EVT_COMMAND_LEFT_CLICK, self.LMBpressed)
        self.Bind(wx.EVT_LEFT_DOWN, self.LMBpressed)
        # self.Bind(wx.EVT_BUTTON, self.onButton1, id=self.btn1.GetId())


        self.timer = wx.Timer(self)
        self.timer.Start(1000)  # 25 changes per second.
        self.Bind(wx.EVT_TIMER, self.Func1)





        self.panel1.Bind(wx.EVT_PAINT, self.OnPaint)

        self.list = wx.ListCtrl(self.panel2, wx.ID_ANY, style=wx.LC_REPORT, size=(600,200))
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







    def OnResize(self, e):
        self.Refresh()

    def OnPaint(self, e):
        dc = wx.PaintDC(self.panel1)
        dc.SetPen(wx.Pen('#fdc073', style=wx.TRANSPARENT))

        dc.DrawLine(0, 0, 500, 700)
        dc.SetBrush(wx.Brush('#d5dde6', wx.SOLID))
        max_time = max([x["time"] for x in self.apps.values()])
        print(max_time)
        for key, value in self.apps.items():
            width = value["time"]
            if width > 0:
                # dc.DrawRectangle(800, self.LineHeight * value["line_number"], width * 500 // max_time, self.LineHeight)
                dc.DrawRectangle(0, self.LineHeight * value["line_number"], int(math.log(width, 1.01)), self.LineHeight)
                dc.DrawText(f"{key} {value['time']} s", 20, self.LineHeight * value["line_number"])
        print("????")
        # dc.DrawText("JJJJJJJJJJJJJJJJDFgdfg222222222222", 300, 100)



    def onQuit(self, event):
        # print(event)
        self.Close()

    def LMBpressed(self, event):
        print("LMB pressed")
        # wx.StaticText(self, id=14, label="Heydddddyy678")
        # self.tx1.SetLabel("ffffff")
        # print(event)

    def onButton1(self, event):
        print("pressed button...")
        self.btn1.SetLabel("1245")
        # self.btn1

    def Func1(self, event):
        # print("Func called")
        # appName, windowName = getActiveWindow()
        app = getActiveWindow()
        if app:
            fullAppName = ' '.join(app)

            if fullAppName not in self.apps:
                self.apps[fullAppName] = {"time": 0, "line_number": len(self.apps)}
                print(self.apps)
                # self.text[len(self.apps)-1].SetLabel(f"{fullAppName}")
            else:
                self.apps[fullAppName]["time"] += 1
                # self.text[self.apps[fullAppName]["line_number"]].SetLabel(f"{fullAppName} {self.apps[fullAppName]['time']}s")

                with open('data_file.json', 'w') as outfile:
                    json.dump(self.apps, outfile, indent=4)
        else:
            print(app)

        self.Refresh()

        # if windowName not in [x["window_name"] for x in self.apps]:
        #     self.apps.append({"app_name": appName, "window_name": windowName, "time": 0})
        #     self.text[len(self.apps) - 1].SetLabel(f"{appName} {windowName}")
        # else:
        #     i = [x["window_name"] for x in self.apps].index(windowName)
        #     self.apps[i]["time"] += 1
        #     self.text[i].SetLabel(f"{appName} {windowName} {self.apps[i]['time']}s")






        # self.OnPaint(event)
        # self.panel.Bind(wx.EVT_PAINT, self.OnPaint)



        # dc = wx.PaintDC(self.panel)
        # dc.SetPen(wx.Pen('#fdc073'))
        #
        # dc.DrawLine(0, 0, 200, 300)



# frame = wx.Frame(None, wx.ID_ANY, "Hello World", size=(700, 500)) # A Frame is a top-level window.
frame = MainWindow(None, "Focus mode") # A Frame is a top-level window.
frame.Centre()
frame.Show(True)     # Show the frame.
# frame.Close()
app.MainLoop()





#
# import wx
#
# class MainWindow(wx.Frame):
#     def __init__(self, parent, title):
#         wx.Frame.__init__(self, parent, title=title, size=(200,100))
#         self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
#         self.CreateStatusBar() # A Statusbar in the bottom of the window
#
#         # Setting up the menu.
#         filemenu= wx.Menu()
#
#         # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
#         filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
#         filemenu.AppendSeparator()
#         filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
#
#         # Creating the menubar.
#         menuBar = wx.MenuBar()
#         menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
#         self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
#         self.Show(True)
#
# app = wx.App(False)
# frame = MainWindow(None, "Sample editor")
# app.MainLoop()













# import wx
#
# class MyFrame(wx.Frame):
#     def __init__(self, parent, id, title):
#         wx.Frame.__init__(self, parent, id, title,size=(250, 250))
#         topPanel = wx.Panel(self, -1)
#         topPanel.SetBackgroundColour('green')
#         panel1 = wx.Panel(topPanel, -1, style=wx.TRANSPARENT_WINDOW)
#         #panel1.SetTransparent(100)
#         panel2 = wx.Panel(topPanel, -1)
#         panel2.SetBackgroundColour('gray')
#
#         sizer = wx.BoxSizer(wx.VERTICAL)
#         sizer.Add(panel1,1,flag = wx.EXPAND|wx.ALL)
#         sizer.Add(panel2,1,flag = wx.EXPAND|wx.ALL)
#
#         topPanel.SetSizer(sizer)
#
#
#
# class MyApp(wx.App):
#      def OnInit(self):
#          frame = MyFrame(None, -1, 'frame')
#          frame.Show(True)
#          return True
#
# app = MyApp(0)
# app.MainLoop()





# # sample_one.py
#
# import wx
#
# # class MyFrame
# # class MyApp
#
# #---------------------------------------------------------------------------
#
# class MyFrame(wx.Frame):
#     def __init__(self):
#         wx.Frame.__init__(self, None, title="Am I transparent ?")
#
#         self.amount = 255
#         self.delta = -3
#
#         p = wx.Panel(self)
#         self.st = wx.StaticText(p, -1, str(self.amount), (25, 25))
#         self.st.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL))
#
#         self.timer = wx.Timer(self)
#         self.timer.Start(25)   # 25 changes per second.
#         self.Bind(wx.EVT_TIMER, self.AlphaCycle)
#
#         self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
#
#     #-----------------------------------------------------------------------
#
#     def OnCloseWindow(self, evt):
#         self.timer.Stop()
#         del self.timer  # Avoid a memory leak.
#         self.Destroy()
#
#
#     def AlphaCycle(self, evt):
#         """
#         The term "alpha" means variable transparency
#         as opposed to a "mask" which is binary transparency.
#         alpha == 255 :  fully opaque
#         alpha ==   0 :  fully transparent (mouse is ineffective!)
#
#         Only top-level controls can be transparent; no other controls can.
#         This is because they are implemented by the OS, not wx.
#         """
#
#         self.amount += self.delta
#         if self.amount == 0 or self.amount == 255:
#             # Reverse the increment direction.
#             self.delta = -self.delta
#         self.st.SetLabel(str(self.amount))
#
#         # Note that we no longer need to use ctypes or win32api to
#         # make transparent windows, however I'm not removing the
#         # MakeTransparent code from this sample as it may be helpful
#         # for somebody someday.
#         #self.MakeTransparent(self.amount)
#
#         # Instead we'll just call the SetTransparent method
#         self.SetTransparent(self.amount)
#
#
#     def MakeTransparent(self, amount):
#         """
#         This is how the method SetTransparent() is
#         implemented on all MS Windows platforms.
#         """
#
#         hwnd = self.GetHandle()
#         try:
#             # DLL library interface constants' definitions.
#             import ctypes
#             # Create object to access DLL file user32.dll
#             _winlib = ctypes.windll.user32
#             # HERE, i'm not sure (for win10 64bit) :
#             # style = _winlib.GetWindowLongA(hwnd, 0xffffffecL)
#             style = _winlib.GetWindowLongA(hwnd, 0x804F700)
#             style |= 0x00080000
#             # _winlib.SetWindowLongA(hwnd, 0xffffffecL, style)
#             _winlib.SetWindowLongA(hwnd, 0x804F700, style)
#             _winlib.SetLayeredWindowAttributes(hwnd, 0, amount, 2)
#
#         except ImportError:
#             import win32api, win32con, winxpgui
#             _winlib = win32api.LoadLibrary("user32")
#             pSetLayeredWindowAttributes = win32api.GetProcAddress(
#                 _winlib, "SetLayeredWindowAttributes")
#             if pSetLayeredWindowAttributes == None:
#                 return
#             exstyle = win32api.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
#             if 0 == (exstyle & 0x80000):
#                 win32api.SetWindowLong(hwnd,
#                                        win32con.GWL_EXSTYLE,
#                                        exstyle | 0x80000)
#             winxpgui.SetLayeredWindowAttributes(hwnd, 0, amount, 2)
#
# #---------------------------------------------------------------------------
#
# class MyApp(wx.App):
#     def OnInit(self):
#
#         #------------
#
#         frame = MyFrame()
#         frame.Show()
#
#         return True
#
# #---------------------------------------------------------------------------
#
# def main():
#     app = MyApp(redirect=False)
#     app.MainLoop()
#
# #---------------------------------------------------------------------------
#
# if __name__ == "__main__" :
#     main()