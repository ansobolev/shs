# -*- coding: utf-8 -*-

import wx
import mbox

class CorrDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        sets = kwds.pop("sets")
        wx.Dialog.__init__(self, *args, **kwds)

        self.CorrOpts = wx.ListBox(self, -1, choices = sets)
        self.XBtn = wx.Button(self, -1, "-> X")
        self.YBtn = wx.Button(self, -1, "-> Y")
        self.X = wx.TextCtrl(self, -1, "", style = wx.TE_READONLY)
        self.Y = wx.TextCtrl(self, -1, "", style = wx.TE_READONLY)
        self.PlotBtn = wx.Button(self, -1, "Plot")
        self.ClearBtn = wx.Button(self, -1, "Clear")
        self.CancelBtn = wx.Button(self, -1, "Cancel")
        
        self.Bind(wx.EVT_BUTTON, self.PassInfo, self.PlotBtn)
        self.Bind(wx.EVT_BUTTON, self.Clear, self.ClearBtn)
        self.Bind(wx.EVT_BUTTON, self.Cancel, self.CancelBtn)

        self.Bind(wx.EVT_BUTTON, self.ToX, self.XBtn)
        self.Bind(wx.EVT_BUTTON, self.ToY, self.YBtn)
        
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("Correlations")

    def __do_layout(self):
        MainSizer = wx.BoxSizer(wx.HORIZONTAL)
        MainSizer.Add(self.CorrOpts, 0, wx.ALL|wx.EXPAND, 5)

        XYSizer =  wx.BoxSizer(wx.VERTICAL)
        XSizer = wx.BoxSizer(wx.HORIZONTAL)
        XSizer.Add(self.XBtn, 1, wx.ALL|wx.EXPAND, 0)
        XSizer.Add(self.X, 2, wx.ALL|wx.EXPAND, 0)
        YSizer = wx.BoxSizer(wx.HORIZONTAL)
        YSizer.Add(self.YBtn, 1, wx.ALL, 0)
        YSizer.Add(self.Y, 2, wx.ALL, 0)
        BtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        BtnSizer.Add(self.PlotBtn, 1, wx.ALL|wx.EXPAND, 0)
        BtnSizer.Add(self.ClearBtn, 1, wx.ALL|wx.EXPAND, 0)
        BtnSizer.Add(self.CancelBtn, 1, wx.ALL|wx.EXPAND, 0)
        
        XYSizer.Add(XSizer, 0, wx.ALL|wx.EXPAND, 5)
        XYSizer.Add(YSizer, 1, wx.ALL|wx.EXPAND, 5)
        XYSizer.Add(BtnSizer, 0, wx.ALL|wx.EXPAND, 5)
        MainSizer.Add(XYSizer, 1, wx.ALL|wx.EXPAND, 5)
        
        self.SetSizer(MainSizer)
        self.Layout()
    
    def Cancel(self, event):
        self.EndModal(wx.ID_CANCEL)
    
    def Clear(self, event):
        self.X.SetValue("")
        self.Y.SetValue("")
    
    def ToX(self, event):
        sel = self.CorrOpts.GetSelection()
        if sel == wx.NOT_FOUND:
            return -1
        self.X.SetValue(self.CorrOpts.GetItems()[sel])
    
    def ToY(self, event):
        sel = self.CorrOpts.GetSelection()
        if sel == wx.NOT_FOUND:
            return -1
        self.Y.SetValue(self.CorrOpts.GetItems()[sel])
    
    def GetInfo(self):
        pass
    
    def PassInfo(self, event):
        if self.X.GetValue() == "" or self.Y.GetValue() == "":
            mbox.EmptyXY()
            return -1
        self.EndModal(wx.ID_OK) 
        
    
if __name__ == '__main__':
    app = wx.App()
    sets = ['MagMom', 'b']
    dlg = CorrDialog(None, -1, sets = sets)
    app.SetTopWindow(dlg)
    print dlg.ShowModal() 
#    dlg.Destroy()
