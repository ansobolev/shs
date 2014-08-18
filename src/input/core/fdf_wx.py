import sys
import wx
import wx.lib.newevent as newevent
from wx.lib.mixins.listctrl import TextEditMixin
import fdf_values

EvtRL, EVT_RADIOLINE = newevent.NewCommandEvent()


class TEListCtrl(wx.ListCtrl, TextEditMixin):
    """ Editable list control
    """
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        TextEditMixin.__init__(self)

    def SetValue(self, Tval):
        'Sets block value'
        self.DeleteAllItems()
        ncol = self.GetColumnCount()
        if ncol < max([len(s) for s in Tval.value]):
            print 'Warning: can\'t populate ListCtrl with block data'
            return
        for s in Tval.value:
            ind = self.InsertStringItem(sys.maxint, str(s[0]))
            for i, item in enumerate(s[1:]):
                self.SetStringItem(ind, i+1, item) 


class NumberedTEListCtrl(wx.ListCtrl, TextEditMixin):
    """ Editable list control with numbered rows
    """
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        TextEditMixin.__init__(self)

    def SetValue(self, Tval):
        'Sets block value'
        self.DeleteAllItems()
        ncol = self.GetColumnCount()
        if (ncol - 1) < max([len(s) for s in Tval.value]):
            print 'Warning: can\'t populate ListCtrl with block data'
            return
        for i, s in enumerate(Tval.value):
            ind = self.InsertStringItem(sys.maxint, str(i + 1))
            for i, item in enumerate(s):
                self.SetStringItem(ind, i+1, str(item)) 


class LineSizer(wx.BoxSizer):

    value = None
    
    def __init__(self, parent, label, optional):
        self.parent = parent
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        self._is_optional = optional
        self.label = wx.StaticText(parent, -1, label = label) 
        if self._is_optional:
            self.switch = wx.CheckBox(parent, -1, '')
            self.Add(self.switch, 0, wx.ALL|wx.EXPAND, 5)
            self.label.Enable(False)
            self.switch.Bind(wx.EVT_CHECKBOX, self.onEnable)
        else:
            self.Add((25,20), 0, wx.ALL|wx.EXPAND, 5)

        self.Add(self.label, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        # binding events

    @property
    def widgets(self):
        return self.value.widgets
    
    def onEnable(self, event):
        is_enabled = self.switch.GetValue()
        self.label.Enable(is_enabled)
        self.value.Enable(is_enabled)
        event.Skip()

    def SetLabel(self, label):
        self.label.SetLabel(label)

class BooleanSizer(LineSizer):
    ''' Sizer with a checkbox
    '''

    def __init__(self, parent, label, optional):
        LineSizer.__init__(self, parent, label, optional)
        self.value = fdf_values.BoolValue(parent)
        if self._is_optional:
            self.value.Enable(False)
        cb = self.value.widgets[0]
        self.Add(cb, 2, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)


class TextEditSizer(LineSizer):
    ''' Sizer with a TextCtrl
    '''

    def __init__(self, parent, label, optional):
        LineSizer.__init__(self, parent, label, optional)
        self.value = fdf_values.TextValue(parent)
        if self._is_optional:
            self.value.Enable(False)
        te = self.value.widgets[0]
        self.Add(te, 2, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)


class ChoiceSizer(LineSizer):
    ''' Sizer with a Choice
    '''

    def __init__(self, parent, label, choices, optional):
        LineSizer.__init__(self, parent, label, optional)
        self.value = fdf_values.ChoiceValue(parent, choices)
        if self._is_optional:
            self.value.Enable(False)
        cb = self.value.widgets[0]
        self.Add(cb, 2, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)


class NumberSizer(LineSizer):
    ''' Sizer with a FloatSpin
    '''

    def __init__(self, parent, label, optional, **kwds):
        LineSizer.__init__(self, parent, label, optional)
        self.value = fdf_values.NumberValue(parent, **kwds)
        if self._is_optional:
            self.value.Enable(False)
        num = self.value.widgets[0]
        self.Add(num, 2, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)


class MeasuredSizer(LineSizer):
    ''' Sizer with a FloatSpin for value and Combobox for unit 
    '''

    def __init__(self, parent, label, optional, **kwds):
        LineSizer.__init__(self, parent, label, optional)
        self.value = fdf_values.MeasuredValue(parent, **kwds)
        if self._is_optional:
            self.value.Enable(False)
        num = self.value.widgets[0]
        unit = self.value.widgets[1]
        self.Add(num, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.Add(unit, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)


class RadioSizer(LineSizer):
    ''' Sizer with a set of RadioButtons
    ''' 

    def __init__(self, parent, label, choices, optional):
        LineSizer.__init__(self, parent, label, optional)
        self.value = fdf_values.RadioValue(parent, choices)
        if self._is_optional:
            self.value.Enable(False)
        radios = self.value.widgets
        radio_sizer = wx.BoxSizer(wx.VERTICAL)
        for radio in radios:
            radio_sizer.Add(radio, 0, wx.ALL | wx.EXPAND, 2)
        self.Add(radio_sizer, 2, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
