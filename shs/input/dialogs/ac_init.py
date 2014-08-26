import wx
from wx.lib.agw.floatspin import FloatSpin, EVT_FLOATSPIN

from input.fdf_wx import LineSizer
from input.fdf_options import Line, ChoiceLine, MeasuredLine, NumberLine
from input.fdf_values import FDFValue

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

class ThreeNumValue(FDFValue):

    def __init__(self, parent, values=None):
        if values is None:
            self._value = [1,1,1]
        else:
            assert type(values) == list and all([type(i) == int for i in values])
            self._value = values

        self.widgets = []
        for _ in range(3):
            fs = FloatSpin(parent, -1, min_val=0, value=1., digits=0)
            fs.Bind(EVT_FLOATSPIN, self.on_change)
            self.widgets.append(fs)

    def on_change(self, event):
        self._value = [int(fs.GetValue()) for fs in self.widgets]
        event.Skip()

    @property
    def value(self):
        return self._value

class ThreeNumSizer(LineSizer):

    def __init__(self, parent, label, optional):
        super(ThreeNumSizer, self).__init__(parent, label, optional)
        self.value = ThreeNumValue(parent)
        if self._is_optional:
            self.value.Enable(False)
        for widget in self.value.widgets:
            self.Add(widget, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

class SuperCell(Line):
    label = 'Supercell'
    optional = False

    def __init__(self, parent, *args, **kwds):
        super(Line, self).__init__(*args, **kwds)
        self._sizer = ThreeNumSizer(parent, self.label, self.optional)
        super(SuperCell, self).__init__(parent, *args, **kwds)

    def GetValue(self):
        return self._sizer.value.value
    
class ACInitDialog(wx.Dialog):
    
    def __init__(self, *args, **kwds):
        self.types = kwds.pop('types')
        wx.Dialog.__init__(self, *args, **kwds)
        self.bravais = Bravais(self)
        self.type_label = []
        self.typefs = []
        if len(self.types) == 0:
            self.add_type_btn = wx.Button(self, -1, "Add type")
            self.add_type_btn.Bind(wx.EVT_BUTTON, self.add_type)
        else:
            for t in self.types:
                self.type_label.append(wx.StaticText(self, -1, t))
                self.typefs.append(FloatSpin(self, -1, min_val=0, value=1., digits=0))

        self.sc = SuperCell(self)

        self.alat = LatticeConstant(self) 
        self.dist = DistortionLevel(self)
        self.__set_properties()
        self.__do_layout()
        
    def __set_properties(self):
        self.SetTitle("Initialize geometry")

    def __do_layout(self):
        comp_label = wx.StaticBox(self, -1, 'Composition')
        comp_sizer = wx.StaticBoxSizer(comp_label, wx.HORIZONTAL)
        self.comp_inside = wx.GridSizer(2, len(self.types), 2, 2)
        
        for l in self.type_label:
            self.comp_inside.Add(l, 0, wx.ALIGN_CENTER, 0)
        for fs in self.typefs:
            self.comp_inside.Add(fs, 0, wx.ALIGN_CENTER, 0)

        comp_sizer.Add(self.comp_inside, 1, wx.ALL | wx.EXPAND, 5)
        if len(self.types) == 0:
            comp_sizer.Add(self.add_type_btn, 0, wx.ALL | wx.EXPAND, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.bravais.sizer, 0, wx.EXPAND, 0)
        sizer.Add(comp_sizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.alat.sizer, 0, wx.EXPAND, 0)
        sizer.Add(self.sc.sizer, 0, wx.EXPAND, 0)
        sizer.Add(self.dist.sizer, 0, wx.EXPAND, 0)
        sizer.Add(self.CreateSeparatedButtonSizer(wx.OK|wx.CANCEL), 0, wx.ALL|wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        self.Fit()
        self.Layout()

    def add_type(self, evt):
        self.comp_inside.Clear()
        self.comp_inside.SetCols(self.comp_inside.GetCols()+1)
        self.type_label.append(wx.TextCtrl(self, -1))
        self.typefs.append(FloatSpin(self, -1, min_val=0, value=1., digits=0))
        for l in self.type_label:
            self.comp_inside.Add(l, 0, wx.ALIGN_CENTER, 0)
        for fs in self.typefs:
            self.comp_inside.Add(fs, 0, wx.ALIGN_CENTER, 0)
        self.Fit()
        self.Layout()

    def init_geom(self):
        bravais = self.bravais.GetValue()
        alat, unit = self.alat.GetValue()
        sc = self.sc.GetValue()
        dist = self.dist.GetValue()
        if len(self.types) == 0:
            comp = dict(zip([il.GetValue() for il in self.type_label], [ifs.GetValue() for ifs in self.typefs]))
        else:
            comp = dict(zip(self.types, [ifs.GetValue() for ifs in self.typefs]))
        g = Geom()
        g.initialize(bravais, comp, sc, alat, unit, DistLevel=dist)
        g.geom2opts()
        return g.opts["AtomicCoordinatesAndAtomicSpecies"]