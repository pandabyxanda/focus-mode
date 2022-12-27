import wx


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(600, 450))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(vbox)
        st = wx.StaticText(panel, label="Адрес: ")

        vbox.Add(st, flag=wx.ALL | wx.ALIGN_RIGHT, border=10)

        inp = wx.TextCtrl(panel, value="г. Москва")
        vbox.Add(inp, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)


        inp2 = wx.TextCtrl(panel, value="г. Москва")
        hbox.Add(inp2, flag=wx.RIGHT | wx.BOTTOM, border=10)
        inp3 = wx.TextCtrl(panel, value="г. Москва")
        inp3.Centre()
        hbox.Add(inp3, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        vbox.Add(hbox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)




app = wx.App()
frame = MyFrame(None, 'wxPython')
frame.Show()
app.MainLoop()