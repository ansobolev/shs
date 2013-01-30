# -*- coding: utf-8 -*-

import wx
from wx.lib.agw.floatspin import FloatSpin

import fdf_base as fdf
from shs.geom import Geom

''' This file contains various dialogs for siesta init gui
'''

class ACInitDialog(wx.Dialog):
    
    def __init__(self, *args, **kwds):
        self.types = kwds.pop('types')
        wx.Dialog.__init__(self, *args, **kwds)
        self.bravais = fdf.ComboSizer(self, 'Lattice symmetry', ['BCC', 'FCC', 'SC'], opt = False)
        self.typel = []
        self.typefs = []
        self.sc = []
        for t in self.types:
            self.typel.append(wx.StaticText(self, -1, t))
            self.typefs.append(FloatSpin(self, -1, min_val = 0, value = 1., digits = 0))
        for _ in range(3):
            self.sc.append(FloatSpin(self, -1, min_val = 0, value = 2., digits = 0))
        
        self.alat = fdf.MeasuredSizer(self, 'Lattice constant', ['Ang','Bohr'], digits = 4, inc = 0.01, defVal = 1., opt = False)
        self.dist = fdf.NumSizer(self, 'Distortion level (in %)', digits = 1, range = (0, 100), defVal = 0., inc = 0.1, opt = False)
        self.__set_properties()
        self.__do_layout()
        
        
    def __set_properties(self):
        self.SetTitle("Initialize geometry")

    def __do_layout(self):
        comp_label = wx.StaticBox(self, -1, 'Composition')
        comp_sizer = wx.StaticBoxSizer(comp_label, wx.HORIZONTAL)
        comp_inside = wx.GridSizer(len(self.types), 2, 2, 2)
        
        for l in self.typel:
            comp_inside.Add(l, 0, wx.ALIGN_CENTER, 0) 
        for fs in self.typefs:
            comp_inside.Add(fs, 0, wx.ALIGN_CENTER, 0) 

        comp_sizer.Add(comp_inside, 1, wx.ALL|wx.EXPAND, 5)
        sc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sc_sizer.Add((25,20), 0, wx.ALL|wx.EXPAND, 5)
        sc_sizer.Add(wx.StaticText(self, -1, 'Supercell'), 1, wx.ALL|wx.EXPAND, 5) 
        for sc in self.sc:
            sc_sizer.Add(sc, 1, wx.ALL|wx.EXPAND, 5)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.bravais, 0, wx.EXPAND, 0) 
        sizer.Add(comp_sizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.alat, 0, wx.EXPAND, 0)
        sizer.Add(sc_sizer, 0, wx.EXPAND, 0)
        sizer.Add(self.dist, 0, wx.EXPAND, 0)
        sizer.Add(self.CreateSeparatedButtonSizer(wx.OK|wx.CANCEL), 0, wx.ALL|wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        self.Fit()
        self.Layout()
    
    def init_geom(self):
        bravais = self.bravais.GetValue()
        alat, unit = self.alat.GetValue()
        sc = [int(isc.GetValue()) for isc in self.sc]
        dist = self.dist.GetValue()
        comp = dict(zip(self.types, [ifs.GetValue() for ifs in self.typefs]))
        g = Geom()
        g.initialize(bravais, comp, sc, alat, unit, DistLevel = dist)
        g.geom2opts()
        return g.opts
        

class AddBlockDlg(wx.Dialog):
    
    def __init__(self, *args, **kwds):
        if 'def_opt' in kwds.keys():            
            def_opt = kwds.pop('def_opt')
        else:
            def_opt = ''
        if 'def_val' in kwds.keys():            
            def_val = kwds.pop('def_val')
        else:
            def_val = ''

        wx.Dialog.__init__(self, *args, **kwds)
        self.OptL = wx.StaticText(self, -1, 'Option')
        self.ValL = wx.StaticText(self, -1, 'Value')
        self.OptTE = wx.TextCtrl(self, -1, def_opt)
        self.ValTE = wx.TextCtrl(self, -1, def_val, style = wx.TE_MULTILINE)
        self.__set_properties()
        self.__do_layout()
        
    def GetBlock(self):
        'Returns option and block value'
        return self.OptTE.GetValue(), self.ValTE.GetValue() 
        
    def __set_properties(self):
        self.SetTitle("Add block to extra options")

    def __do_layout(self):
        opt_sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=15)
        opt_sizer.Add(self.OptL, 0, wx.ALL, 0)
        opt_sizer.Add(self.OptTE, 0, wx.ALL|wx.EXPAND, 0)
        opt_sizer.Add(self.ValL, 0, wx.ALL, 0)
        opt_sizer.Add(self.ValTE, 0, wx.ALL|wx.EXPAND, 0)
        opt_sizer.AddGrowableRow(1, 1)
        opt_sizer.AddGrowableCol(1, 1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(opt_sizer, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.CreateSeparatedButtonSizer(wx.OK|wx.CANCEL), 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(sizer)
        self.Layout()

if __name__ == '__main__':
    app = wx.App()
    types = [u'Fe', u'C']
    dlg = AddBlockDlg(None, -1, )
    app.SetTopWindow(dlg)
    if dlg.ShowModal() ==wx.ID_OK:
        dlg.init_geom()
#    dlg.Destroy()
    
