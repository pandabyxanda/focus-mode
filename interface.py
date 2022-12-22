import wx
from focus1 import getActiveWindow

app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        self.Button1Name = "but1"
        self.apps = []

        # wx.Frame.__init__(self, parent, title=title, size=(900,700), style=wx.DEFAULT_FRAME_STYLE)
        wx.Frame.__init__(self, parent, title=title, size=(900, 700),
                          style=wx.MINIMIZE_BOX | wx.RESIZE_BORDER |
                                wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN |
                                wx.BORDER_DOUBLE)
        # self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu.
        filemenu= wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        panel = wx.Panel(self)
        panel.SetBackgroundColour("#367bef")

        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(14)
        panel.SetFont(font)

        # vbox = wx.BoxSizer(wx.VERTICAL)
        #
        # st = wx.StaticText(panel, label="Heyyy")
        # st2 = wx.StaticText(panel, label="Heyyy2")
        #
        # vbox.Add(st, flag=wx.ALL, border=10)
        # vbox.Add(st2, flag=wx.ALL, border=50)
        #
        # panel.SetSizer(vbox)

# """
#         gr = wx.GridBagSizer(5, 5)
#         text = wx.StaticText(panel, label="Email:")
#         gr.Add(text, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
#
#         tc = wx.TextCtrl(panel)
#         gr.Add(tc, pos=(1, 0), span=(1, 5), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
#
#         button1 = wx.Button(panel, label="Восстановить", size=(120, 28))
#         button2 = wx.Button(panel, label="Отмена", size=(90, 28))
#
#         gr.Add(button1, pos=(3, 3))
#         gr.Add(button2, pos=(3, 4), flag=wx.RIGHT | wx.BOTTOM, border=10)
#
#         gr.AddGrowableCol(1)
#         # gr.AddGrowableRow(0)
#
#         panel.SetSizer(gr)
# """
        gr = wx.GridBagSizer(5, 16)
        self.text = [None] * 15
        for i in range(0, len(self.text)):
            self.text[i] = wx.StaticText(panel, label="Empty"+str(i))

        for i in range(0, len(self.text)):
            gr.Add(self.text[i], pos=(i, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=0)

        self.btn1 = wx.Button(panel, wx.ID_ANY, self.Button1Name)
        gr.Add(self.btn1, pos=(16, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # gr.AddGrowableCol(0)
        panel.SetSizer(gr)
        # self.tx1 = wx.StaticText(self, id=15, label="Heyyy678")
        # self.tx2 = wx.StaticText(self, id=15, label="Heyyy67")

        # self.btn1 = wx.Button(self, wx.ID_ANY, self.Button1Name)
        # self.btn1.SetPosition(wx.Point(100, 200))


        # self.Show(True)
        # self.SetTransparent(245)

        # self.Bind(wx.EVT_MENU, self.onQuit, id=wx.ID_EXIT)
        # self.Bind(wx.EVT_COMMAND_LEFT_CLICK, self.LMBpressed)
        self.Bind(wx.EVT_LEFT_DOWN, self.LMBpressed)
        # self.Bind(wx.EVT_BUTTON, self.onButton1, id=self.btn1.GetId())

        self.timer = wx.Timer(self)
        self.timer.Start(1000)  # 25 changes per second.
        self.Bind(wx.EVT_TIMER, self.Func1)



        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(gr, e):
        dc = wx.PaintDC(gr)
        dc.SetPen(wx.Pen('#fdc073'))

        dc.DrawLine(0, 0, 200, 100)




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
        appName, windowName = getActiveWindow()
        if windowName not in [x["window_name"] for x in self.apps]:
            self.apps.append({"app_name": appName, "window_name": windowName, "time": 0})
            self.text[len(self.apps)-1].SetLabel(f"{appName} {windowName}")
        else:
            i = [x["window_name"] for x in self.apps].index(windowName)
            self.apps[i]["time"] += 1
            self.text[i].SetLabel(f"{appName} {windowName} {self.apps[i]['time']}s")



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