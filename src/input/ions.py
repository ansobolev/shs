#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx

import fdf_base as fdf

'A class collection representing ions panel'

class IonsPN(wx.ScrolledWindow):
    
    def __init__(self, *args, **kwds):
        wx.ScrolledWindow.__init__(self, *args, **kwds)
        
        self.NCGSteps = fdf.NumSizer(self, 'Number of CG steps')
        self.ForceTol = fdf.MeasuredSizer(self, 'Max force tolerance', ['eV/Ang', 'Ry/Bohr', 'N'])
        self.VarCell = fdf.ChBoxSizer(self, 'Variable Cell')
        self.StressTol = fdf.MeasuredSizer(self, 'Max stress tolerance', ['Pa', 'MPa', 'GPa', 'atm', 'bar', 'Mbar', 'Ry/Bohr**3', 'eV/Ang**3'])
        self.CGDispl = fdf.MeasuredSizer(self, 'Max CG displacement', ['Ang', 'Bohr', 'm', 'cm', 'nm'])
        
        self.fdf_opts = {'ions' : {}}
        
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetScrollRate(0, 10)

    def __do_layout(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.NCGSteps, 0, wx.EXPAND, 0)
        self.sizer.Add(self.CGDispl, 0, wx.EXPAND, 0)
        self.sizer.Add(self.ForceTol, 0, wx.EXPAND, 0)
        self.sizer.Add(self.VarCell, 0, wx.EXPAND, 0)
        self.sizer.Add(self.StressTol, 0, wx.EXPAND, 0)
        self.SetSizer(self.sizer)
        self.Layout()

    
    def OnCT(self, evt):
        opts2hide = {self.NCGSteps : ['CG', 'Broyden'],
                     self.CGDispl : ['CG', 'Broyden', 'FIRE'],
                     self.ForceTol : ['CG', 'Broyden', 'FIRE'],
                     self.VarCell : ['CG', 'Broyden', 'FIRE'],
                     self.StressTol : ['CG', 'Broyden', 'FIRE']}
        # hide all items
        self.sizer.ShowItems(False)
        # show only needed controls
        ctrls = []
        for key, value in opts2hide.iteritems():
            if evt.text in value:
                ctrls.append(key)
        for ctrl in ctrls:
            ctrl.ShowItems(True)
        self.Layout()


if __name__ == '__main__':
    'A simple test'
    app = wx.App()
    f = wx.Frame(None, -1)
    p = IonsPN(f, -1)

    s = wx.BoxSizer(wx.VERTICAL)
    s.Add(p, 1, wx.EXPAND, 0)
    f.SetSizer(s)
    f.Layout()
    app.SetTopWindow(f)
    f.Show()
    app.MainLoop()
