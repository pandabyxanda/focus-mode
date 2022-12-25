"""
Static text with transparent background
"""

import wx
app = wx.App()
class TransparentText(wx.StaticText):
  def __init__(self, parent, id=wx.ID_ANY, label='sdfsd',
               pos=wx.DefaultPosition, size=(700,200),
               style=wx.TRANSPARENT_WINDOW, name='transparenttext'):
    wx.StaticText.__init__(self, parent, id, label, pos, size, style, name)

    self.Bind(wx.EVT_PAINT, self.on_paint)
    # self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
    self.Bind(wx.EVT_SIZE, self.on_size)

  def on_paint(self, event):
    dc = wx.PaintDC(self)
    # dc = wx.GCDC(bdc)

    # font_face = self.GetFont()
    # font_color = self.GetForegroundColour()
    dc.GradientFillLinear((10, 10, 600, 600), '#98cc00', '#004444', wx.NORTH)

    # dc.SetFont(font_face)
    # dc.SetTextForeground(font_color)
    dc.DrawText(self.GetLabel(), 0, 0)

  def on_size(self, event):
    self.Refresh()
    event.Skip()


class MainWindow(wx.Frame):
    def __init__(self, parent, title):


        # wx.Frame.__init__(self, parent, title=title, size=(900,700), style=wx.DEFAULT_FRAME_STYLE)

        wx.Frame.__init__(self, parent, title=title, size=(1400, 700),
                          style=wx.MINIMIZE_BOX | wx.RESIZE_BORDER | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.panel1 = wx.Panel(self)
        self.panel1.SetBackgroundColour("#367bef")
        x = TransparentText(self.panel1)

frame = MainWindow(None, "Focus mode") # A Frame is a top-level window.
frame.Centre()
frame.Show(True)     # Show the frame.
# frame.Close()
app.MainLoop()