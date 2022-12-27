#!/usr/bin/env python3
import wx
import wx.lib.scrolledpanel as scrolled


class MainWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Title", pos=wx.DefaultPosition, size=wx.Size(800, 480),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.panel = wx.Panel(self)
        notebook = wx.Notebook(self.panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)


        scrolled_window = scrolled.ScrolledPanel(notebook, wx.ID_ANY)
        scrolled_window.SetupScrolling()
        notebook.AddPage(scrolled_window, "Tab %d", False)
        bsizer = wx.GridSizer(0, 5, 0, 0)
        for btn in range(0, 50):
            button = wx.Button(scrolled_window, wx.ID_ANY, str(btn), wx.DefaultPosition, wx.DefaultSize, 0)
            button.SetMinSize((-1, 90))
            bsizer.Add(button, 0, wx.ALL | wx.EXPAND, 5)
        scrolled_window.SetSizer(bsizer)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        self.panel.SetSizer(sizer)
        self.Layout()
        self.Refresh()


app = wx.App(False)
main_window = MainWindow(parent=None)
main_window.Show(True)
app.MainLoop()