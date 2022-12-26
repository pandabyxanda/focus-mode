import wx

app = wx.App()
frame = wx.Frame(None, style = wx.DEFAULT_FRAME_STYLE & ~wx.CAPTION)
frame.Maximize()
frame.Show()
app.MainLoop()