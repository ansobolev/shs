#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generated by wxGlade HG on Fri Jan 13 14:51:14 2012

import os, time
import wx
from wx.lib.pubsub import Publisher 

import shs.gui.PlotFrame as PF
import shs.gui.interface as interface

class RootFrame(wx.Frame):

    calcs = [interface.getCalc('../examples/FeCANI', '.output', steps = range(-100, 0))]

    def __init__(self, *args, **kwds):
        # begin wxGlade: RootFrame.__init__
        self.searchString = ""
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self.propChoices = interface.dataClasses()
        self.propType = wx.Choice(self, -1, choices=self.propChoices.types())
        pt_num = self.propType.GetSelection()
        pt = self.propType.GetItems()[pt_num]
        self.propChoice = wx.Choice(self, -1, choices = self.propChoices.classes(pt))

        self.CorrXChoice = wx.Choice(self, -1, choices=self.propChoices.classes("Function"))
        self.CorrYChoice = wx.Choice(self, -1, choices=self.propChoices.classes("Function"))

        self.PropChoiceBtn = wx.Button(self, -1, "Plot property")
        self.CorrelateBtn = wx.Button(self, -1, "Plot correlations")
        self.CreateStatusBar()

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.propTypeChange, self.propType)
        self.Bind(wx.EVT_BUTTON, self.plotProperty, self.PropChoiceBtn)
        self.Bind(wx.EVT_BUTTON, self.Correlate, self.CorrelateBtn)
        # end wxGlade
    
    def __set_properties(self):
        self.SetTitle("Siesta help scripts GUI")

    def __do_layout(self):
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        LeftSizer = wx.BoxSizer(wx.VERTICAL)

        plotSizer = wx.FlexGridSizer(rows=2, cols=2, hgap=5, vgap=2)        
        plotSizer.SetFlexibleDirection(wx.HORIZONTAL)
        PropSizer = wx.BoxSizer(wx.VERTICAL)
        CorrSizer = wx.BoxSizer(wx.VERTICAL)

        PropSizer.Add(self.propType, 1, wx.ALL|wx.EXPAND, 0)
        PropSizer.Add(self.propChoice, 1, wx.ALL|wx.EXPAND, 0)
        plotSizer.Add(PropSizer, 1, wx.ALL|wx.EXPAND, 2)
        plotSizer.Add(self.PropChoiceBtn, 0, wx.ALL|wx.EXPAND, 2)
        CorrSizer.Add(self.CorrXChoice, 1, wx.ALL|wx.EXPAND, 0)
        CorrSizer.Add(self.CorrYChoice, 1, wx.ALL|wx.EXPAND, 0)
        plotSizer.Add(CorrSizer, 1, wx.ALL|wx.EXPAND, 2)
        plotSizer.Add(self.CorrelateBtn, 0, wx.ALL|wx.EXPAND, 2)

        LeftSizer.Add(plotSizer, 1, wx.ALL|wx.EXPAND, 2)

        mainSizer.Add(LeftSizer, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(mainSizer)
        self.Layout()
        self.Centre()
        # end wxGlade

    def propTypeChange(self, event):
        # property type
        pt_num = self.propType.GetSelection()
        pt = self.propType.GetItems()[pt_num]
        self.propChoice.SetItems(self.propChoices.classes(pt))
        self.propChoice.SetSelection(0)

    def plotProperty(self, event): # wxGlade: RootFrame.<event_handler>
# plot options - get all the data to plot
        ptype = self.propType.GetItems()[self.propType.GetSelection()]
        pchoice = self.propChoice.GetItems()[self.propChoice.GetSelection()]
        data_class = self.propChoices.dataClass(ptype, pchoice)

        leg = ['example']
        calcs = self.calcs
        t1 = time.clock()
        plot_data = interface.getData(ptype, data_class, leg, calcs)
        self.SetStatusText('Calculation time: %7.2f s.' % (time.clock() - t1))
        msg = plot_data
        try:
            self.pf.Raise()
        except (AttributeError, wx._core.PyDeadObjectError):
            self.pf = PF.PlotFuncFrame(self)
            self.pf.Show()
        Publisher().sendMessage(('data.plot'), msg)

    def Correlate(self, event):
# correlate options - get all the data to plot
        xchoice = self.CorrXChoice.GetSelection()
        ychoice = self.CorrYChoice.GetSelection()
        leg = [self.CalcList.GetItemText(i) for i in getListCtrlSelection(self.CalcList)]
        t1 = time.clock()
        data, info = interface.get_corr(xchoice, ychoice, [self.calcs[i] for i in getListCtrlSelection(self.CalcList)])
        msg = [leg, data, info]
        try:
            self.cf.Raise()
        except (AttributeError, wx._core.PyDeadObjectError):
            self.cf = PF.PlotCorrFrame(self)
            self.cf.Show()
        Publisher().sendMessage(('corr.plot'), msg)
# end of class RootFrame

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    rf = RootFrame(None, -1, "")
    app.SetTopWindow(rf)
    rf.Show()
    app.MainLoop()

