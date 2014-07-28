from ..fdf_wx import LineSizer
from ..fdf_options import Line, ChoiceLine, MeasuredLine, NumberLine 
import wx
from wx.lib.agw.floatspin import FloatSpin
try:
    from geom import Geom
except ImportError:
    from shs.geom import Geom


class Bravais(ChoiceLine):
    label = 'Composition'
    choices = ['BCC', 'FCC', 'SC']
    optional = False


class LatticeConstant(MeasuredLine):
    label = 'Lattice constant'
    value = 1.
    digits = 2
    increment = 0.01
    units = ['Bohr', 'Ang']
    optional = False


class DistortionLevel(NumberLine):
    label = 'Distortion level (in %)'
    value = 0.
    digits = 0
    increment = 1.
    range_val = (0., 100.)
    optional = False


class SuperCell(Line):
    label = 'Supercell'
    optional = False

    class ThreeNumSizer(LineSizer):
        
        def __init__(self, parent, label, optional):
            LineSizer.__init__(parent, label, optional)
            #self.value = 
    
    def __init__(self, parent, *args, **kwds):
        self._sizer = self.ThreeNumSizer() 
        super(SuperCell, self).__init__(parent, *args, **kwds)  
    
class ACInitDialog(wx.Dialog):
    
    def __init__(self, *args, **kwds):
        self.types = kwds.pop('types')
        wx.Dialog.__init__(self, *args, **kwds)
        self.bravais = Bravais(self)
        self.typel = []
        self.typefs = []
        self.sc = []
        for t in self.types:
            self.typel.append(wx.StaticText(self, -1, t))
            self.typefs.append(FloatSpin(self, -1, min_val = 0, value = 1., digits = 0))
        for _ in range(3):
            self.sc.append(FloatSpin(self, -1, min_val = 0, value = 2., digits = 0))
        
        self.alat = LatticeConstant(self) 
        self.dist = DistortionLevel(self)
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