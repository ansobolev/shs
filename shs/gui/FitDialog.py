# -*- coding: utf-8 -*-

import wx

class FitDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        sets = kwds.pop('sets')
        wx.Dialog.__init__(self, *args, **kwds)
        fit_opts_list = ['1-peak Gaussian','2-Peak Gaussian','Linear fit'] 

        self.FitOpts = wx.RadioBox ( self, -1,'Fit options', choices = fit_opts_list, majorDimension = 0, style = wx.RA_SPECIFY_ROWS)
        self.DataSets = wx.ListBox(self, -1, choices = sets)
        
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("Select fitting parameters")

    def __do_layout(self):
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        FitSizer =  wx.BoxSizer(wx.HORIZONTAL)
        FitSizer.Add(self.FitOpts, 1, wx.ALL|wx.EXPAND, 5)
        SetLabel = wx.StaticBox(self, -1, 'Data set')
        SetSizer = wx.StaticBoxSizer(SetLabel, wx.HORIZONTAL)
        SetSizer.Add(self.DataSets, 1, wx.ALL|wx.EXPAND, 5)
        FitSizer.Add(SetSizer, 1, wx.ALL|wx.EXPAND, 5)
        MainSizer.Add(FitSizer, 1, wx.ALL|wx.EXPAND, 5)
        MainSizer.Add(self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(MainSizer)
        self.Layout()
    
    def GetFitOptions(self):
        return self.FitOpts.GetSelection(), self.DataSets.GetSelection()

if __name__ == '__main__':
    app = wx.App()
    sets = ['a', 'b']
    dlg = FitDialog(None, -1, sets = sets)
    app.SetTopWindow(dlg)
    if dlg.ShowModal() ==wx.ID_OK:
        print dlg.GetFitOptions()
#    dlg.Destroy()
    

