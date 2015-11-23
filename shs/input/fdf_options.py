import wx

from shs.input import fdf_wx


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
        self.switch = None

    @property
    def sizer(self):
        return self._sizer

    def IsShown(self):
        return not self.hidden

    def IsEnabled(self):
        if not self.optional:
            return self.IsShown()
        else:
            return self.IsShown() and self.switch.IsChecked()

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
        check_event = wx.CommandEvent(wx.EVT_CHECKBOX.typeId, self.switch.GetId())
        check_event.SetInt(int(self.switch.IsChecked()))
        wx.PostEvent(self.switch.GetEventHandler(), check_event)

    def Show(self, flag):
        self._sizer.ShowItems(flag)
        self.parent.Layout()
        self.hidden = not flag

    def GetValue(self):
        return self.widgets[0].GetValue()

    def GetFDFValue(self):
        return self.GetValue()

    def SetFDFValue(self, value):
        self.Enable(True)
        self._sizer.value.SetValue(value)

    def SetLabel(self, label):
        self._sizer.SetLabel(label)

    def FDF_string(self, *args):
        return "{0:<25}\t{1}".format(self.fdf_text, self.GetFDFValue())

    def __str__(self):
        return self.FDF_string()


class Block(FDFOption):

    def FDF_string(self, k):
        print "%block", k


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

    def GetFDFValue(self):
        value = self.FS.GetValue()
        if self.digits == 0:
            value = int(value)
        return "{0}".format(value)


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

    def GetValue(self):
        return self.FS.GetValue(), self.CB.GetValue()

    def GetFDFValue(self):
        value = self.FS.GetValue()
        if self.digits == 0:
            value = int(value)
        units = self.CB.GetValue()
        return "{0} {1}".format(value, units)


class RadioLine(Line):
    choices = None

    def __init__(self, parent, *args, **kwds):
        super(Line, self).__init__(parent, *args, **kwds)
        self._sizer = fdf_wx.RadioSizer(parent, self.label, self.choices, self.optional)
        super(RadioLine, self).__init__(parent, *args, **kwds)
        self.RBs = self.widgets
        for RB in self.RBs:
            RB.Bind(wx.EVT_RADIOBUTTON, self.on_change)

    def on_change(self, evt):
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


class ThreeNumberLine(Line):
    values = [1, 1, 1]

    def __init__(self, parent, *args, **kwds):
        super(Line, self).__init__(*args, **kwds)
        kwds = {"values": self.values}
        self._sizer = fdf_wx.ThreeNumSizer(parent, self.label, self.optional, **kwds)
        super(ThreeNumberLine, self).__init__(parent, *args, **kwds)

    def GetValue(self):
        return self._sizer.value.value
