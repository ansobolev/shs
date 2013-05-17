#! -*- coding: utf-8 -*-
'''
Created on 10.05.2013

@author: andrey
'''

import wx

import interface
from mbox import ValueIsEmpty, ValueIsNotANumber, TypeNameIsEmpty

class TypeDialog(wx.Dialog):
    '''
    Dialog of changing atomic type
    '''

    def __init__(self, *args, **kwds):
        '''
        Constructor
        '''
        # begin wxGlade: StepsDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        props = kwds.pop("props")
        wx.Dialog.__init__(self, *args, **kwds)
        self.condition = None
        self.types = {}
        
        self.propChoice = wx.Choice(self, -1, choices = props)
        self.condChoice = wx.Choice(self, -1, choices = ["==", "!=", "<", ">", "<=", ">="])
        self.valueTC = wx.TextCtrl(self, -1, "")
        self.condList = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_NO_HEADER)
        self.btnAdd = wx.Button(self, -1, "Add")
        self.btnRemove = wx.Button(self, -1, "Clear")
        self.btnToTypes = wx.Button(self, -1, "↓")
        self.btnFromTypes = wx.Button(self, -1, "↑")
        self.typeNameTC = wx.TextCtrl(self, -1, "")
        
        self.typeList = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_NO_HEADER)
        self.btnOkCancel = self.CreateButtonSizer(wx.OK|wx.CANCEL)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.btnAddPress, self.btnAdd)
        self.Bind(wx.EVT_BUTTON, self.btnRemovePress, self.btnRemove)
        self.Bind(wx.EVT_BUTTON, self.btnToTypesPress, self.btnToTypes)

        
    def __set_properties(self):
        self.SetTitle("Change atomic type")
# initialize CalcList
        self.condList.InsertColumn(0,'Property', width = 100)
        self.condList.InsertColumn(1,'Condition', width = 50)
        self.condList.InsertColumn(2,'Value', width = 100)
        self.typeList.InsertColumn(0,'Name', width = 50)
        self.typeList.InsertColumn(1,'Condition', width = 200)
    
    
    def __do_layout(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        condSizer = wx.BoxSizer(wx.HORIZONTAL)
        condSizer.Add(self.propChoice, 1, wx.ALL|wx.EXPAND, 2)
        condSizer.Add(self.condChoice, 0, wx.ALL|wx.EXPAND, 2)
        condSizer.Add(self.valueTC, 1, wx.ALL|wx.EXPAND, 2)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(self.btnAdd, 0, wx.ALL|wx.EXPAND, 2)
        btnSizer.Add((1,1), 1, wx.ALL|wx.EXPAND, 2)
        btnSizer.Add(self.btnRemove, 0, wx.ALL|wx.EXPAND, 2)
        mainSizer.Add(condSizer, 0, wx.ALL|wx.EXPAND, 5)
        mainSizer.Add(btnSizer, 0, wx.ALL|wx.EXPAND, 5)
        mainSizer.Add(self.condList, 0, wx.ALL|wx.EXPAND, 5)
        typeSizer = wx.BoxSizer(wx.HORIZONTAL)
        typeSizer.Add(self.typeNameTC, 1, wx.ALL|wx.EXPAND, 2)
        typeSizer.Add(self.btnToTypes, 0, wx.ALL|wx.EXPAND, 2)
        typeSizer.Add(self.btnFromTypes, 0, wx.ALL|wx.EXPAND, 2)
        mainSizer.Add(typeSizer, 0, wx.ALL|wx.EXPAND, 5)
        mainSizer.Add(self.typeList, 0, wx.ALL|wx.EXPAND, 5)
        mainSizer.Add(self.btnOkCancel, 0, wx.ALL|wx.EXPAND, 5)
        
        self.SetSizer(mainSizer)
        self.Fit()
        self.Layout()        

    def btnAddPress(self, event):
        if not self.valueTC.GetValue():
            ValueIsEmpty()
            return -1
        num = self.valueTC.GetValue()
        try:
            float(num)
        except (ValueError,):
            ValueIsNotANumber(num)
            num = "\'" + num + "\'" 
        prop = self.propChoice.GetItems()[self.propChoice.GetSelection()]
        cond = self.condChoice.GetItems()[self.condChoice.GetSelection()]
        if self.condition is None:
            self.condition = interface.getCondition(prop, cond, num)
        else:
            self.condition = interface.addAndToCondition(self.condition, prop, cond, num)
        # Type List:
        tlc = self.condList.GetItemCount()
        self.condList.InsertStringItem(tlc, prop)
        self.condList.SetStringItem(tlc, 1, cond)
        self.condList.SetStringItem(tlc, 2, num)

    def btnRemovePress(self, event):
        self.condition = None
        self.condList.ClearAll()

    def btnToTypesPress(self, event):
        if not self.typeNameTC.GetValue():
            TypeNameIsEmpty()
            return -1
        if self.condition is None:
            ValueIsEmpty()
            return -1
        tlc = self.typeList.GetItemCount()
        self.typeList.InsertStringItem(tlc, self.typeNameTC.GetValue())
        self.typeList.SetStringItem(tlc, 1, str(self.condition))
        self.types[self.typeNameTC.GetValue()] = self.condition
        # Cleaning all temporary vars
        self.condition = None
        self.btnRemovePress(event)
        self.typeNameTC.SetValue("")

    def getTypes(self):
        return self.types
    
if __name__ == '__main__':
    app = wx.App()
    props = ['MagMom', 'b']
    dlg = TypeDialog(None, -1, props=props)
    app.SetTopWindow(dlg)
    print dlg.ShowModal() 
#    dlg.Destroy()