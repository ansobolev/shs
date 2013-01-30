#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import wx
import  wx.lib.newevent as newevent
from wx.lib.agw.floatspin import FloatSpin
from wx.lib.mixins.listctrl import TextEditMixin

from shs.fdftypes import str2bool

EvtRS, EVT_RADIOSIZER = newevent.NewCommandEvent()
EvtCS, EVT_COMBOSIZER = newevent.NewCommandEvent()
EvtCB, EVT_CHBOXSIZER = newevent.NewCommandEvent()

class TEListCtrl(wx.ListCtrl, TextEditMixin):
    ''' Editable list control
    '''
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        TextEditMixin.__init__(self)
        
    def SetValue(self, Tval):
        'Sets block value'
        ncol = self.GetColumnCount()
        if ncol < max([len(s) for s in Tval.value]):
            print 'Warning: can\'t populate ListCtrl with block data'
            return
        for s in Tval.value:
            ind = self.InsertStringItem(sys.maxint, str(s[0]))
            for i, item in enumerate(s[1:]):
                self.SetStringItem(ind, i+1, item) 

class NumberedTEListCtrl(wx.ListCtrl, TextEditMixin):
    ''' Editable list control with numbered rows
    '''
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        TextEditMixin.__init__(self)
        
    def SetValue(self, Tval):
        'Sets block value'
        ncol = self.GetColumnCount()
        if (ncol - 1) < max([len(s) for s in Tval.value]):
            print 'Warning: can\'t populate ListCtrl with block data'
            return
        for i, s in enumerate(Tval.value):
            ind = self.InsertStringItem(sys.maxint, str(i + 1))
            for i, item in enumerate(s):
                self.SetStringItem(ind, i+1, str(item)) 

        

class TESizer(wx.BoxSizer):
    ''' Sizer with label and text edit field
    '''
    def __init__(self, parent, label, default = '', opt = True):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        
        self.opt = opt
        self.label = wx.StaticText(parent, -1, label = label) 
        self.te = wx.TextCtrl(parent, -1, default)
        
        if opt:
            self.switch = wx.CheckBox(parent, -1, '')
            self.Add(self.switch, 0, wx.ALL|wx.EXPAND, 5)
            self.label.Enable(False)
            self.te.Enable(False)
            self.switch.Bind(wx.EVT_CHECKBOX, self.onEnable)
        else:
            self.Add((25,20), 0, wx.ALL|wx.EXPAND, 5)
        self.Add(self.label, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.Add(self.te, 2, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
    def onEnable(self, evt = None):
        self.label.Enable(self.switch.GetValue())
        self.te.Enable(self.switch.GetValue())
        
    def SetValue(self, Tval, enable = True):
        if self.opt and enable:
            self.switch.SetValue(True)
            self.onEnable()
        self.te.SetValue(Tval.value)            
        
        

class NumSizer(wx.BoxSizer):
    ''' Sizer with label and numbers edit field
    '''
    def __init__(self, parent, label, opt = True, digits = 0, inc = 1.0, range = (0, None), defVal = 1.):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        
        self.opt = opt
        self.label = wx.StaticText(parent, -1, label = label) 
        self.num = FloatSpin(parent, -1, digits = digits, increment = inc,
                              min_val = range[0], max_val = range[1], value = defVal)
        if opt:
            self.switch = wx.CheckBox(parent, -1, '')
            self.Add(self.switch, 0, wx.ALL|wx.EXPAND, 5)
            self.label.Enable(False)
            self.num.Enable(False)
            self.switch.Bind(wx.EVT_CHECKBOX, self.onEnable)
        else:
            self.Add((25,20), 0, wx.ALL|wx.EXPAND, 5)
        self.Add(self.label, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.Add(self.num, 2, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

    def onEnable(self, evt):
        self.label.Enable(self.switch.GetValue())
        self.num.Enable(self.switch.GetValue())

    def GetValue(self):
        return self.num.GetValue()

    def SetValue(self, Tval, enable = True):
        if self.opt and enable:
            self.switch.SetValue(True)
            self.onEnable()
        self.num.SetValue(float(Tval.value))            


class MeasuredSizer(wx.BoxSizer):
    ''' Sizer with label and numbers edit field
    '''
    def __init__(self, parent, label, units, opt = True, digits = 0, inc = 1.0, range = (0, None), defVal = 1.):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        self.opt = opt
        self.label = wx.StaticText(parent, -1, label = label) 
        self.num = FloatSpin(parent, -1, digits = digits, increment = inc,
                              min_val = range[0], max_val = range[1], value = defVal)
        self.unit = wx.ComboBox(parent, -1, choices = units)
        self.unit.Select(0)
        if opt:
            self.switch = wx.CheckBox(parent, -1, '')
            self.Add(self.switch, 0, wx.ALL|wx.EXPAND, 5)
            self.label.Enable(False)
            self.num.Enable(False)
            self.unit.Enable(False)
            self.switch.Bind(wx.EVT_CHECKBOX, self.onEnable)
        else:
            self.Add((25,20), 0, wx.ALL|wx.EXPAND, 5)

        self.Add(self.label, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.Add(self.num, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.Add(self.unit, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

    def GetValue(self):
        return self.num.GetValue(), self.unit.GetValue()

    def SetValue(self, Tval, enable = True):
        if self.opt and enable:            
            self.switch.SetValue(True)
            self.onEnable()
        self.num.SetValue(float(Tval.value))
        self.unit.SetValue(Tval.unit)

    def onEnable(self, evt = None):
        self.label.Enable(self.switch.GetValue())
        self.num.Enable(self.switch.GetValue())
        self.unit.Enable(self.switch.GetValue())



class RadioSizer(wx.BoxSizer):
    ''' Sizer with label and a bunch of radiobuttons
    '''

    def __init__(self, parent, label, choices, opt = True):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        self.parent = parent
        self.label = wx.StaticText(parent, -1, label = label) 
        self.radios = [wx.RadioButton(parent, -1, choices[0], style = wx.RB_GROUP), ]
        radio = wx.BoxSizer(wx.VERTICAL)
        for choice in choices[1:]:
            self.radios.append(wx.RadioButton(parent, -1, choice))
        if opt:
            self.switch = wx.CheckBox(parent, -1, '')
            self.Add(self.switch, 0, wx.ALL|wx.EXPAND, 5)
            self.label.Enable(False)
            for r in self.radios:
                r.Enable(False)
            self.switch.Bind(wx.EVT_CHECKBOX, self.onEnable)
        else:
            self.Add((25,20), 0, wx.ALL|wx.EXPAND, 5)

        for r in self.radios:
            r.Bind(wx.EVT_RADIOBUTTON, self.OnRB)
            radio.Add(r, 0, wx.EXPAND, 0)
        
        
        self.Add(self.label, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.Add(radio, 2, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
    def OnRB(self, evt):
        # get which radio is selected
        for ir, r in enumerate(self.radios):
            if r.GetValue():
                rb_val = ir
        new_event = EvtRS(self.label.GetId(), value = rb_val) 
        wx.PostEvent(self.parent, new_event)
        
    def GetId(self):
        return self.label.GetId()
    
    def SetValue(self, val):
        self.radios[val].SetValue(True)
        new_event = EvtRS(self.label.GetId(), value = val) 
        wx.PostEvent(self.parent, new_event)

    def onEnable(self, evt):
        self.label.Enable(self.switch.GetValue())
        for r in self.radios:
            r.Enable(self.switch.GetValue())


class ComboSizer(wx.BoxSizer):
    ''' Sizer with label and a combobox
    '''
    def __init__(self, parent, label, choices, opt = True):
        self.parent = parent
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        self.opt = opt
        self.label = wx.StaticText(parent, -1, label = label) 
        self.cb = wx.Choice(parent, -1, choices = choices) # , style = wx.CB_READONLY
        self.cb.Select(0)
        self.cb.Bind(wx.EVT_CHOICE, self.OnCombo)
        if opt:
            self.switch = wx.CheckBox(parent, -1, '')
            self.Add(self.switch, 0, wx.ALL|wx.EXPAND, 5)
            self.label.Enable(False)
            self.cb.Enable(False)
            self.switch.Bind(wx.EVT_CHECKBOX, self.onEnable)
        else:
            self.Add((25,20), 0, wx.ALL|wx.EXPAND, 5)
        
        self.Add(self.label, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.Add(self.cb, 2, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

    def OnCombo(self, evt):
        cb_val = self.cb.GetSelection()
        txt_val = self.cb.GetItems()[cb_val]
        new_event = EvtCS(self.label.GetId(), value = cb_val, text = txt_val) 
        wx.PostEvent(self.parent, new_event)

    def GetId(self):
        return self.label.GetId()

    def GetValue(self):
        return self.cb.GetItems()[self.cb.GetSelection()]

    def SetValue(self, Tval, enable = True):
        if self.opt and enable:
            self.switch.SetValue(True)
            self.onEnable()
        for i, item in enumerate(self.cb.GetItems()):
            if item.lower() == str(Tval.value).lower():
                self.cb.SetSelection(i)
# firing choice event as if we changed selection manually
                choiceEvent = wx.CommandEvent(wx.EVT_CHOICE.typeId, self.cb.GetId())
                choiceEvent.SetInt(i)
                wx.PostEvent(self.cb.GetEventHandler(), choiceEvent)
                return
        print 'Warning: could not find value ' + Tval.value + ' in the list of choices for \'' + self.label.GetLabelText() + '\' ChoiceBox.'
    
    def SetChoices(self, choices):
        self.cb.Clear()
        self.cb.AppendItems(choices)
        self.cb.Select(0)

    def onEnable(self, evt = None):
        self.label.Enable(self.switch.GetValue())
        self.cb.Enable(self.switch.GetValue())


class ChBoxSizer(wx.BoxSizer):
    ''' Sizer with label and a checkbox
    '''
    def __init__(self, parent, label, opt = True):
        self.parent = parent
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        self.opt = opt
        self.label = wx.StaticText(parent, -1, label = label) 
        self.cb = wx.CheckBox(parent, -1)
        self.cb.Bind(wx.EVT_CHECKBOX, self.OnChBox)
        if opt:
            self.switch = wx.CheckBox(parent, -1, '')
            self.Add(self.switch, 0, wx.ALL|wx.EXPAND, 5)
            self.label.Enable(False)
            self.cb.Enable(False)
            self.switch.Bind(wx.EVT_CHECKBOX, self.onEnable)
        else:
            self.Add((25,20), 0, wx.ALL|wx.EXPAND, 5)

        self.Add(self.label, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.Add(self.cb, 2, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        # binding events
        
    def Enable(self, state):
        self.switch.Enable(state)

    def OnChBox(self, evt):
        cb_val = self.cb.GetValue()
        new_event = EvtCB(self.label.GetId(), value = cb_val) 
        wx.PostEvent(self.parent, new_event)

    def GetId(self):
        return self.label.GetId()

    def GetValue(self):
        return self.cb.GetValue()

    def SetValue(self, Tval, enable = True):
        if self.opt and enable:            
            self.switch.SetValue(True)
            self.onEnable()
# this should be done on read
        try:
            self.cb.SetValue(Tval.value)
        except IndexError:
            self.cb.SetValue(True)
# firing the checkbox event, as if we checked cb manually
        checkEvent = wx.CommandEvent(wx.EVT_CHECKBOX.typeId, self.cb.GetId())
        checkEvent.SetInt(int(self.cb.IsChecked()))
        wx.PostEvent(self.cb.GetEventHandler(), checkEvent)


    def Check(self, val):
        self.cb.SetValue(val)

    def onEnable(self, evt = None):
        self.label.Enable(self.switch.GetValue())
        self.cb.Enable(self.switch.GetValue())

