# -*- coding: utf-8 -*-

import wx
from fdf_base import TESizer, ComboSizer, ChBoxSizer

class ControlPN(wx.ScrolledWindow):
    
    
    def __init__(self, *args, **kwds):
        ctypes = ['CG', 'Nose', 'ParrinelloRahman', 'NoseParrinelloRahman', 'Anneal',  
                   'Broyden', 'FIRE', 'Verlet', 'FC', 'Phonon', 'Forces']
        
        wx.ScrolledWindow.__init__(self, *args, **kwds)
        self.SysName = TESizer(self, 'System name', opt = False)    
        self.SysLabel = TESizer(self, 'System label', opt = False)
        self.CalcType = ComboSizer(self, 'Calculation type', ctypes, opt = False)

        self.InputSizer = self.CreateInputSizer()        
        self.OutputSizer = self.CreateOutputSizer()

        # fdf options that could be set by control panel
        self.fdf_opts = {'general': {'SystemName': self.SysName, 
                                     'SystemLabel' : self.SysLabel},
                         'ions': {'MD.TypeOfRun' : self.CalcType},
                         'input' : {'UseSaveData' : self.UseData,
                                    'DM.UseSaveDM' : self.UseDM,
                                    'MD.UseSaveXV' : self.UseXV},
                         'output': {'AtomCoorFormatOut': self.ACOutFormat,
                                    'LongOutput' : self.LongOut,
                                    'WriteKPoints' : self.KPOut,
                                    'WriteKBands': self.KBOut,
                                    'WriteCoorStep': self.CoorStepOut,
                                    'WriteForces' : self.ForcesOut,
                                    'WriteWaveFunctions': self.WFOut,
                                    'WriteMullikenPop' : self.MullikenOut,
                                    'SaveTotalPotential' : self.TotPotOut,
                                    'SaveElectrostaticPotential' : self.ESPotOut,
                                    'SaveRho' : self.ChDensityOut,
                                    'WriteCoorXmol' : self.XmolOut,
                                    'WriteMDhistory' : self.MDHist,
                                    'WriteCoorCerius' : self.CeriusOut,
                                    'WriteMDXmol' : self.AniOut}
                        }

        
        self.__set_properties()
        self.__do_layout()
    
    def CreateInputSizer(self):
        InLabel = wx.StaticBox(self, -1, 'Input options')
        
        self.UseData = ChBoxSizer(self, 'Use save data')
        self.UseDM = ChBoxSizer(self, 'Use density matrix')
        self.UseXV = ChBoxSizer(self, 'Use data from XV file')
        
        
        sizer = wx.StaticBoxSizer(InLabel, wx.VERTICAL)
        sizer.Add(self.UseData, 0, wx.EXPAND, 0)
        sizer.Add(self.UseDM, 0, wx.EXPAND, 0)
        sizer.Add(self.UseXV, 0, wx.EXPAND, 0)
        
        
        return sizer        
    
    
    def CreateOutputSizer(self):
        OutLabel = wx.StaticBox(self, -1, 'Output options')

        acf = ['NotScaledCartesianBohr', 'NotScaledCartesianAng', 
               'ScaledCartesian', 'ScaledByLatticeVectors'] 
    
        self.ACOutFormat = ComboSizer(self, 'Coordinates output format', acf)
        self.LongOut = ChBoxSizer(self, 'Long output')
        self.KPOut = ChBoxSizer(self, 'K points')
        self.KBOut = ChBoxSizer(self, 'K bands')
        self.CoorStepOut = ChBoxSizer(self, 'Coordinates (stepwise)')
        self.ForcesOut = ChBoxSizer(self, 'Atomic forces')
        self.TotPotOut = ChBoxSizer(self, 'Total potential')
        self.ESPotOut = ChBoxSizer(self, 'Electrostatic potential')
        self.ChDensityOut = ChBoxSizer(self, 'Charge density (.RHO)')
        self.EigenOut = ChBoxSizer(self, 'Eigenvalues')
        self.WFOut = ChBoxSizer(self, 'Wave functions')
        self.MullikenOut = ComboSizer(self, 'Mulliken population', ['0','1','2','3'])
        self.XmolOut = ChBoxSizer(self, 'Coordinates for Xmol')
        self.CeriusOut = ChBoxSizer(self, 'Coordinates for Cerius')
        self.AniOut = ChBoxSizer(self, 'MD file for Xmol (.ANI)')
        self.MDHist = ChBoxSizer(self, 'MD history (.MD, .MDE)')
        sizer = wx.StaticBoxSizer(OutLabel, wx.VERTICAL)
        sizer.Add(self.LongOut, 0, wx.EXPAND, 0)
        sizer.Add(self.CoorStepOut, 0, wx.EXPAND, 0)
        sizer.Add(self.MDHist, 0, wx.EXPAND, 0)
        sizer.Add(self.ACOutFormat, 0, wx.EXPAND, 0)
        sizer.Add(self.ForcesOut, 0, wx.EXPAND, 0)
        sizer.Add(self.AniOut, 0, wx.EXPAND, 0)
        sizer.Add(self.XmolOut, 0, wx.EXPAND, 0)
        sizer.Add(self.CeriusOut, 0, wx.EXPAND, 0)
        sizer.Add(self.MullikenOut, 0, wx.EXPAND, 0)
        sizer.Add(self.TotPotOut, 0, wx.EXPAND, 0)
        sizer.Add(self.ESPotOut, 0, wx.EXPAND, 0)
        sizer.Add(self.ChDensityOut, 0, wx.EXPAND, 0)
        sizer.Add(self.KPOut, 0, wx.EXPAND, 0)
        sizer.Add(self.KBOut, 0, wx.EXPAND, 0)
        sizer.Add(self.EigenOut, 0, wx.EXPAND, 0)
        sizer.Add(self.WFOut, 0, wx.EXPAND, 0)
        return sizer
    
    def __set_properties(self):
        self.SetScrollRate(0, 10)
    
    def __do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.SysName, 0, wx.EXPAND, 0)    
        sizer.Add(self.SysLabel, 0, wx.EXPAND, 0)
        sizer.Add(self.CalcType, 0, wx.EXPAND, 0)
        sizer.Add(self.InputSizer, 0, wx.EXPAND, 0)
        sizer.Add(self.OutputSizer, 0, wx.EXPAND, 0)
        self.SetSizer(sizer)
        
        
if __name__ == '__main__':
    'A simple test'
    app = wx.App()
    f = wx.Frame(None, -1)
    p = ControlPN(f, -1)

    s = wx.BoxSizer(wx.VERTICAL)
    s.Add(p, 1, wx.EXPAND, 0)
    f.SetSizer(s)
    f.Layout()
    app.SetTopWindow(f)
    f.Show()
    app.MainLoop()
