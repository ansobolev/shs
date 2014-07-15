
import wx
import fdf_wx

""" Classes representing FDF options
"""


class FDFOption(object):
    label = None
    fdf_text = None
    _sizer = None
    optional = False
    hidden = False
    box = ""
    priority = None
    bindings = None
    proportion = 0

    def __init__(self, *args, **kwds):
        if "optional" in kwds.keys():
            self.optional = kwds["optional"]

    @property
    def sizer(self):
        return self._sizer

    def SetFDFValue(self, value):
        print value


class Line(FDFOption):

    def __init__(self, parent, *args, **kwds):
        self.parent = parent
        self.widgets = self._sizer.widgets
        if self.optional:
            self.switch = self._sizer.switch

    def Enable(self, flag):
        if not self.optional:
            return
        self.switch.SetValue(flag)
        # firing the checkbox event, as if we checked cb manually
        checkEvent = wx.CommandEvent(wx.EVT_CHECKBOX.typeId, self.switch.GetId())
        checkEvent.SetInt(int(self.switch.IsChecked()))
        wx.PostEvent(self.switch.GetEventHandler(), checkEvent)

    def IsEnabled(self):
        return self.IsShown() and self.switch.IsChecked()

    def Show(self, flag):
        self._sizer.ShowItems(flag)
        self.parent.Layout()
        self.hidden = flag

    def IsShown(self):
        return not self.hidden

    def GetValue(self):
        return self.widgets[0].GetValue()

    def SetFDFValue(self, value):
        self.Enable(True)
        self._sizer.value.SetValue(value)

class Block(FDFOption):
    pass

class BooleanLine(Line):

    def __init__(self, parent, *args, **kwds):
        super(Line, self).__init__(parent, *args, **kwds)
        self._sizer = fdf_wx.BooleanSizer(parent, self.label, self.optional)
        super(BooleanLine, self).__init__(parent, *args, **kwds)
        self.CB = self.widgets[0]

class TextEditLine(Line):

    def __init__(self, parent, *args, **kwds):
        super(Line, self).__init__(parent, *args, **kwds)
        self._sizer = fdf_wx.TextEditSizer(parent, self.label, self.optional)
        super(TextEditLine, self).__init__(parent, *args, **kwds)
        self.TE = self.widgets[0]

class ChoiceLine(Line):
    choices = None

    def __init__(self, parent, *args, **kwds):
        super(Line, self).__init__(parent, *args, **kwds)
        self._sizer = fdf_wx.ChoiceSizer(parent, self.label, self.choices, self.optional)
        super(ChoiceLine, self).__init__(parent, *args, **kwds)
        self.CB = self.widgets[0]

    def SetChoices(self, choices):
        self._sizer.value.SetChoices(choices)

    def GetValue(self):
        return self.choices[self.CB.GetSelection()]

class NumberLine(Line):
    digits = 2
    increment = 0.01
    range_val = (0., None)
    value = None

    def __init__(self, parent, *args, **kwds):
        super(Line, self).__init__(parent, *args, **kwds)
        kwds = {"digits": self.digits,
                "increment": self.increment,
                "range_val": self.range_val,
                "value": self.value,
                }
        self._sizer = fdf_wx.NumberSizer(parent, self.label, self.optional, **kwds)
        super(NumberLine, self).__init__(parent, *args, **kwds)
        self.FS = self.widgets[0]

class MeasuredLine(Line):
    digits = 2
    increment = 0.01
    range_val = (0., None)
    value = None
    units = None

    def __init__(self, parent, *args, **kwds):
        super(Line, self).__init__(parent, *args, **kwds)
        kwds = {"digits": self.digits,
                "increment": self.increment,
                "range_val": self.range_val,
                "value": self.value,
                "units": self.units
                }
        self._sizer = fdf_wx.MeasuredSizer(parent, self.label, self.optional, **kwds)
        super(MeasuredLine, self).__init__(parent, *args, **kwds)
        self.FS = self.widgets[0]
        self.CB = self.widgets[1]

class RadioLine(Line):
    choices = None

    def __init__(self, parent, *args, **kwds):
        super(Line, self).__init__(parent, *args, **kwds)
        self._sizer = fdf_wx.RadioSizer(parent, self.label, self.choices, self.optional)
        super(RadioLine, self).__init__(parent, *args, **kwds)
        self.RBs = self.widgets
        for RB in self.RBs:
            RB.Bind(wx.EVT_RADIOBUTTON, self.on_change)

    def on_change(self, event):
        value = self.GetValue()
        new_event = fdf_wx.EvtRL(self.GetId(), value=value)
        wx.PostEvent(self.parent, new_event)        

    def GetId(self):
        return self._sizer.label.GetId()

    def GetValue(self):
        for ir, r in enumerate(self.RBs):
            if r.GetValue():
                return ir

    def SetValue(self, value):
        self.RBs[value].SetValue(True)