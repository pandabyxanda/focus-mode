#!/usr/bin/env python3
import wx
import wx.lib.scrolledpanel as scrolled


class MainWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Title", pos=wx.DefaultPosition, size=wx.Size(800, 480),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        # self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.panel1 = wx.Panel(self)

        tabs = wx.Notebook(self.panel1, id=wx.ID_ANY)

        vbox_main9 = wx.BoxSizer(wx.VERTICAL)
        vbox_main9.Add(tabs, 1, wx.ALL | wx.EXPAND, 5)

        self.panel1.SetSizer(vbox_main9)
        self.panel1.SetBackgroundColour("#2222fe")

        scrolled_window = scrolled.ScrolledPanel(tabs, wx.ID_ANY)
        scrolled_window.SetupScrolling()

        tabs.AddPage(scrolled_window, "Tab %d", False)
        self.panel2 = wx.Panel(tabs)
        tabs.AddPage(self.panel2, "Tab 2", False)

        vbox_main = wx.BoxSizer(wx.VERTICAL)
        scrolled_window.SetSizer(vbox_main)
        self.pn1_main = wx.Panel(scrolled_window, size=(200, 100))
        self.pn2_main = wx.Panel(scrolled_window, size=(200, 100))
        hbox_main = wx.BoxSizer(wx.HORIZONTAL)
        vbox_main.Add(hbox_main, flag=wx.EXPAND | wx.ALIGN_LEFT, border=10, proportion=1)

        hbox_main.Add(self.pn1_main, flag=wx.EXPAND, border=10, proportion=1)
        hbox_main.Add(self.pn2_main, flag=wx.EXPAND, border=10)
        self.pn1_main.SetBackgroundColour("#dfedfd")
        self.pn2_main.SetBackgroundColour("#e7f2fe")

        button = wx.Button(scrolled_window, wx.ID_ANY, "str(btn)", pos=(300, 200))







        # self.Layout()
        # self.Refresh()


app = wx.App(False)
main_window = MainWindow(parent=None)
main_window.Show(True)
app.MainLoop()




# #!/usr/bin/env python3
# import wx
# import wx.lib.scrolledpanel as scrolled
#
#
# class MainWindow(wx.Frame):
#     def __init__(self, parent):
#         wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Title", pos=wx.DefaultPosition, size=wx.Size(800, 480),
#                           style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
#         # self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
#         self.panel = wx.Panel(self)
#         notebook = wx.Notebook(self.panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
#
#
#         scrolled_window = scrolled.ScrolledPanel(notebook, wx.ID_ANY)
#         scrolled_window.SetupScrolling()
#         notebook.AddPage(scrolled_window, "Tab %d", False)
#         bsizer = wx.GridSizer(0, 5, 0, 0)
#
#         button = wx.Button(scrolled_window, wx.ID_ANY, "str(btn)", wx.DefaultPosition, wx.DefaultSize, 0)
#         # button.SetMinSize((-1, 90))
#         bsizer.Add(button, 0, wx.ALL | wx.EXPAND, 5)
#
#         # for btn in range(0, 10):
#         #     button = wx.Button(scrolled_window, wx.ID_ANY, str(btn), wx.DefaultPosition, wx.DefaultSize, 0)
#         #     button.SetMinSize((-1, 90))
#         #     bsizer.Add(button, 0, wx.ALL | wx.EXPAND, 5)
#
#
#         scrolled_window.SetSizer(bsizer)
#
#         sizer = wx.BoxSizer(wx.VERTICAL)
#         sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
#         self.panel.SetSizer(sizer)
#
#
#
#         self.Layout()
#         self.Refresh()
#
#
# app = wx.App(False)
# main_window = MainWindow(parent=None)
# main_window.Show(True)
# app.MainLoop()