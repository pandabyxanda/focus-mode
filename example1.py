import wx


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, pos=(0, 0), size=(700, 400))

        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen('#fdc073'))

        dc.DrawLine(0, 0, 200, 100)
        dc.DrawRectangle(300, 10, 200, 100)

        dc.GradientFillLinear((10, 10, 600, 50), '#00cc00', '#444444', wx.NORTH)
        dc.GradientFillLinear((10, 80, 600, 50), '#0000cc', '#444444', wx.SOUTH)
        dc.GradientFillLinear((10, 140, 600, 50), '#cc0000', '#444444', wx.EAST)
        dc.GradientFillLinear((10, 200, 600, 50), '#ffccff', '#444444', wx.WEST)


app = wx.App()
frame = MyFrame(None, 'wxPython')
frame.Show()
app.MainLoop()



