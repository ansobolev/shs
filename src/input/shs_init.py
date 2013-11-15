#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import fdf_base as fb
from root import RootFrame


class TestFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, *args, **kwds)
        self.sn = fb.TESizer(self, 'String edit')
        self.sl = fb.NumSizer(self, 'Number select')
        self.cb = fb.ComboSizer(self, 'Combo box', ['1','2','3','5'])
        self.rs = fb.RadioSizer(self, 'Radio sizer', ['one','two','three','five'])
        self.chb = fb.ChBoxSizer(self, 'Check box')
        self.meas = fb.MeasuredSizer(self, 'Measured variable', ['Ang','Bohr'])

        LS = wx.BoxSizer(wx.VERTICAL)
        LS.Add(self.sn, 0, wx.EXPAND, 0)
        LS.Add(self.sl, 0, wx.EXPAND, 0)
        LS.Add(self.cb, 0, wx.EXPAND, 0)
        LS.Add(self.rs, 0, wx.EXPAND, 0)
        LS.Add(self.chb, 0, wx.EXPAND, 0)
        LS.Add(self.meas, 0, wx.EXPAND, 0)
        self.SetSizer(LS)
        self.Layout()
        self.Fit()
        self.Centre()        

        self.Bind(fb.EVT_RADIOSIZER, self.onrs, self.rs)
    
    def onrs(self, evt):
        print 'Selected RB: %i' % (evt.value) 

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    rf = RootFrame(None, -1, "Init SIESTA run", size = (680, 800))
#    rf = TestFrame(None, -1, "Init SIESTA run")
    app.SetTopWindow(rf)
    rf.Show()
    app.MainLoop()