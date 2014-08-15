
import wx
from wx.lib.agw.floatspin import FloatSpin, EVT_FLOATSPIN


""" Classes representing FDF values and wx widgets for them
"""


class FDFValue(object):
    widgets = None
    _value = None

    def Enable(self, value):
        for widget in self.widgets:
            widget.Enable(value)


class BoolValue(FDFValue):

    def __init__(self, parent, value=False):
        assert type(value) == bool
        self._value = value
        self._cb = wx.CheckBox(parent, -1)
        self.widgets = [self._cb, ]
        self._cb.SetValue(self._value)
        self._cb.Bind(wx.EVT_CHECKBOX, self.on_change)

    def __get__(self, instance, owner):
        return self._value

    def on_change(self, event):
        self._value = self._cb.GetValue()
        event.Skip()

    def SetValue(self, value):
        value = value.value
        assert type(value) == bool
        self._value = value
        self._cb.SetValue(self._value)


class TextValue(FDFValue):

    def __init__(self, parent, value=""):
        assert type(value) == str
        self._value = value
        self._te = wx.TextCtrl(parent, -1, value=value)
        self.widgets = [self._te, ]
        self._te.Bind(wx.EVT_TEXT, self.on_change)

    def __get__(self, instance, owner):
        return self._value

    def SetValue(self, value):
        value = value.value
        assert type(value) == str
        self._value = value
        self._te.SetValue(value) # fires EVT_TEXT event

    def on_change(self, event):
        self._value = self._te.GetValue()
        event.Skip()

class ChoiceValue(FDFValue):

    def __init__(self, parent, choices, selection=0):
        assert type(choices) == list and len(choices) != 0
        assert type(selection) == int
        self._choices = choices
        self._value = choices[selection]

        self._cb = wx.Choice(parent, -1, choices=self._choices)
        self._cb.Select(selection)
        self.widgets = [self._cb, ]
        self._cb.Bind(wx.EVT_CHOICE, self.on_change)

    def __get__(self, instance, owner):
        return self._value

    def __set__(self, instance, value):
        assert type(value) == str
        self._value = value
        self._cb.SetValue(self._value) # fires EVT_TEXT event

    def on_change(self, event):
        self._value = self._cb.GetItems()[self._cb.GetSelection()]
        event.Skip()

    def AppendChoice(self, choice):
        self._choices.append(choice)
        self._cb.AppendItems([choice, ])

    def DeleteChoice(self, choice):
        i_choice = self._choices.index(choice)
        self._choices.pop(i_choice)
        self.SetChoices(self._choices)

    def GetCount(self):
        return self._cb.GetCount()

    def SetChoices(self, choices):
        self._choices = choices
        self._cb.Clear()
        self._cb.AppendItems(choices)
        self._cb.Select(0)

    def SetValue(self, value):
        value = str(value.value)
        assert value in self._choices
        self._value = value
        self._cb.SetSelection(self._choices.index(self._value))
        # firing the choice event, as if we changed cb manually
        new_event = wx.CommandEvent(wx.EVT_CHOICE.typeId, self._cb.GetId())
        wx.PostEvent(self._cb.GetEventHandler(), new_event)


class NumberValue(FDFValue):

    def __init__(self, parent, **kwds):
        digits = kwds.get("digits")
        increment = kwds.get("increment")
        (min_val, max_val) = kwds.get("range_val")
        self._value = kwds.get("value")
        self._fs = FloatSpin(parent, -1, digits=digits,
                                         increment=increment,
                                         min_val=min_val,
                                         max_val=max_val,
                                         value=self._value
                                         )
        self._fs.SetValue(self._value)
        self.widgets = [self._fs, ]
        self._fs.Bind(EVT_FLOATSPIN, self.on_change)

    def __get__(self, instance, owner):
        return self._value

    def __set__(self, instance, value):
        assert type(value) == float
        self._value = value
        self._fs.SetValue(self._value)

    def on_change(self, event):
        self._value = self._fs.GetValue()
        event.Skip()

    def SetValue(self, value):
        value = float(value.value)
        self._value = value
        self._fs.SetValue(self._value)


class MeasuredValue(FDFValue):

    def __init__(self, parent, **kwds):
        digits = kwds.get("digits")
        increment = kwds.get("increment")
        (min_val, max_val) = kwds.get("range_val")
        units = kwds.get("units")
        self._value = kwds.get("value")
        self._unit = units[0]
        self._fs = FloatSpin(parent, -1, digits=digits,
                                         increment=increment,
                                         min_val=min_val,
                                         max_val=max_val,
                                         value=self._value
                                         )
        self._cb = wx.ComboBox(parent, -1, choices=units)
        self._cb.Select(0)
        self._fs.SetValue(self._value)
        self.widgets = [self._fs, self._cb]
        self._fs.Bind(EVT_FLOATSPIN, self.on_change)
        self._cb.Bind(wx.EVT_COMBOBOX, self.on_change)

    def on_change(self, event):
        self._value = self._fs.GetValue()
        self._unit = self._cb.GetItems()[self._cb.GetSelection()]
        event.Skip()

    def SetValue(self, value):
        self._value = value.value
        self._unit = value.unit
        self._fs.SetValue(self._value)
        self._cb.SetValue(self._unit)


class RadioValue(FDFValue):

    def __init__(self, parent, choices, selection=0):
        self._choices = choices
        self._value = selection
        self._radios = [wx.RadioButton(parent, -1, choices[0], style=wx.RB_GROUP),] + \
                        [wx.RadioButton(parent, -1, choice) for choice in choices[1:]]
        self.widgets = self._radios
        self._radios[selection].SetValue(True)
        for rb in self._radios:
            rb.Bind(wx.EVT_RADIOBUTTON, self.on_change)

    def __get__(self, instance, owner):
        print 'RadioValue.get ' + str(self._value)
        return self._value

    def __set__(self, instance, value):
        assert type(value) == int
        self._value = value
        self._radios[value].SetValue(True)

    def on_change(self, event):
        for ir, r in enumerate(self._radios):
            if r.GetValue():
                self._value = ir
                break
        event.Skip()