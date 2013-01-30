# -*- coding: utf-8 -*-

import wx

import fdf_base as fdf

'A class collection representing electrons panel'

class ElectronsPN(wx.ScrolledWindow):
    
    def __init__(self, *args, **kwds):
        wx.ScrolledWindow.__init__(self, *args, **kwds)
        self.XCFunc = fdf.ComboSizer(self, 'XC functional', ['LDA', 'GGA'])
        self.XCAuth = fdf.ComboSizer(self, 'XC authors', ['CA', 'PW92'])
        self.solution = fdf.ComboSizer(self, 'Solution method', ['diagon', 'orderN'])
        self.et = fdf.MeasuredSizer(self, 'Electronic temperature', ['K', 'eV', 'Ry'], digits = 1)
        self.BasisSizer = self.CreatePAOBasis()
        self.SpinPol = fdf.ChBoxSizer(self, 'Spin polarization')
        self.NCSpin = fdf.ChBoxSizer(self, 'Non-collinear spin')
        self.AFSpin = fdf.ChBoxSizer(self, 'Antiferromagnetic run')
        
        # binding events
        self.Bind(fdf.EVT_COMBOSIZER, self.OnXCfunc, self.XCFunc)
        self.Bind(fdf.EVT_CHBOXSIZER, self.OnSpin, self.SpinPol)

        # fdf options that could be set by control panel
        self.fdf_opts = {'electrons': {'xc.functional': self.XCFunc, 
                                       'xc.authors' : self.XCAuth,
                                       'SolutionMethod' : self.solution,
                                       'ElectronicTemperature' : self.et,
                                       'SpinPolarized' : self.SpinPol,
                                       'NonCollinearSpin' : self.NCSpin,
                                       'DM.InitSpinAF': self.AFSpin,
                                       'PAO.BasisType' : self.BasisType,
                                       'PAO.BasisSize' : self.BasisSize,
                                       'PAO.EnergyShift' : self.EnergyShift}
                        }
        
        self.__set_properties()
        self.__do_layout()

    def CreatePAOBasis(self):
        BasisL = wx.StaticBox(self, -1, 'PAO basis')
        self.BasisType = fdf.ComboSizer(self, 'Basis type', ['split', 'splitgauss', 'nodes', 'nonodes'])
        self.BasisSize = fdf.ComboSizer(self, 'Basis size', ['SZ', 'SZP', 'DZ', 'DZP'])
        self.EnergyShift = fdf.MeasuredSizer(self, 'Energy shift', ['Ry', 'eV', 'meV'], digits = 1)
        sizer = wx.StaticBoxSizer(BasisL, wx.VERTICAL)
        sizer.Add(self.BasisType, 0, wx.EXPAND, 0)
        sizer.Add(self.BasisSize, 0, wx.EXPAND, 0)
        sizer.Add(self.EnergyShift, 0, wx.EXPAND, 0)
        return sizer
    
    def OnXCfunc(self, evt):
        if evt.value == 1:
            self.XCAuth.SetChoices(['PBE', 'revPBE', 'RPBE', 'WC', 'PBEsol', 'LYP'])
        else:
            self.XCAuth.SetChoices(['CA', 'PW92'])
    
    def OnSpin(self, evt):
        self.NCSpin.Enable(evt.value)
        self.AFSpin.Enable(evt.value)
        self.NCSpin.Check(False)
        self.AFSpin.Check(False)
        
    
    def __set_properties(self):
        self.SetScrollRate(0, 10)
        self.NCSpin.Enable(False)
        self.AFSpin.Enable(False)


    def __do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.XCFunc, 0, wx.EXPAND, 0)
        sizer.Add(self.XCAuth, 0, wx.EXPAND, 0)
        sizer.Add(self.solution, 0, wx.EXPAND, 0)
        sizer.Add(self.et, 0, wx.EXPAND, 0)
        sizer.Add(self.BasisSizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.SpinPol, 0, wx.EXPAND, 0)
        sizer.Add(self.NCSpin, 0, wx.EXPAND, 0)
        sizer.Add(self.AFSpin, 0, wx.EXPAND, 0)

        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        
if __name__ == '__main__':
    'A simple test'
    app = wx.App()
    f = wx.Frame(None, -1)
    p = ElectronsPN(f, -1)

    s = wx.BoxSizer(wx.VERTICAL)
    s.Add(p, 1, wx.EXPAND, 0)
    f.SetSizer(s)
    f.Layout()
    app.SetTopWindow(f)
    f.Show()
    app.MainLoop()
