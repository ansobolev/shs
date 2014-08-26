#!/usr/bin/env python

import wx
from shs.input.frames.main import MainFrame

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    rf = MainFrame(None, -1, "Init SIESTA run", size=(680, 800))
    app.SetTopWindow(rf)
    rf.Show()
    app.MainLoop()
