#! /usr/bin/env python
# -*- coding : utf8 -*-


'Plots topological indices of Voronoi polihedra'

import os, sys
import wx
import numpy as N

try:
    from shs.calc import SiestaCalc
except (ImportError,):
    from calc import SiestaCalc


class RootFrame(wx.Frame):
    
    root = '/home/andrey/calc'
    calcs = []
    
    def __init__(self, *args, **kwds):
        # begin wxGlade: RootFrame.__init__
        self.searchString = ""
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.CalcTree = wx.TreeCtrl(self, -1, style=wx.TR_HAS_BUTTONS|wx.TR_NO_LINES|wx.TR_HIDE_ROOT|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        self.DownBtn = wx.Button(self, -1, ">>")
        self.UpBtn = wx.Button(self, -1, "<<")
        self.CListLabel = wx.StaticText(self, -1, 'Carbon atoms')
        self.CList = wx.ListBox(self, -1, style=wx.LB_MULTIPLE)
        self.PropChoiceBtn = wx.Button(self, -1, "Plot VP")
        self.CreateStatusBar()
        
        self.__set_properties()
        self.__do_layout()

        # initialize the tree
        self.buildTree(self.root)

        self.Bind(wx.EVT_BUTTON, self.DownBtnPress, self.DownBtn)
        self.Bind(wx.EVT_BUTTON, self.UpBtnPress, self.UpBtn)
        self.Bind(wx.EVT_BUTTON, self.PlotVP, self.PropChoiceBtn)

    def buildTree(self,root,ctype=".ANI"):
        '''Add a new root element and then its children'''        
        self.CalcTree.DeleteAllItems()
        r = len(root.split(os.sep))
        ids = {root : self.CalcTree.AddRoot(root)}
        for (dirpath, dirnames, filenames) in os.walk(root):
            if isCalcOfType(ctype, dn = dirnames, fn = filenames):
                ancdirs = dirpath.split('/')[r:]
                ad = root
                for ancdir in ancdirs:
                    d = os.path.join(ad, ancdir)
                    if not ids.has_key(d):
                        ids[d] = self.CalcTree.AppendItem(ids[ad], ancdir)
                    self.CalcTree.SortChildren(ids[ad])
                    ad = d

    def __set_properties(self):
        # begin wxGlade: RootFrame.__set_properties
        self.SetTitle("Plot VP GUI")
        self.SetSize((820, 430))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: RootFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        LeftSizer = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        BtnSizer = wx.BoxSizer(wx.VERTICAL)
        RightSizer = wx.BoxSizer(wx.VERTICAL)
        RightSizer.Add(self.CalcTree, 1, wx.EXPAND, 0)

        sizer_1.Add(RightSizer, 1, wx.ALL|wx.EXPAND, 5)
        BtnSizer.Add(self.DownBtn, 0, wx.ALL|wx.EXPAND, 5)
        BtnSizer.Add(self.UpBtn, 0, wx.ALL|wx.EXPAND, 5)
        sizer_1.Add(BtnSizer, 0, wx.EXPAND, 0)
        LeftSizer.Add(self.CListLabel, 0, wx.ALL|wx.EXPAND, 5)
        LeftSizer.Add(self.CList, 2, wx.ALL|wx.EXPAND, 5)
        sizer_2.Add(self.PropChoiceBtn, 1, wx.ALIGN_RIGHT, 0)
        LeftSizer.Add(sizer_2, 0, wx.ALL|wx.EXPAND|wx.SHAPED, 5)
        sizer_1.Add(LeftSizer, 1, wx.EXPAND, 5)
        self.SetSizer(sizer_1)
        self.Layout()
        self.Centre()

    def PlotVP(self, evt):
        self.calc.evol[0].voronoi()
        cats = []
        for i in self.CList.GetSelections():
            cats.append(int(self.CList.GetItems()[i]))
        print cats
        self.calc.evol[0].vp.plot_vps(cats)

    def DownBtnPress(self, event): # wxGlade: RootFrame.<event_handler>
        # current list count
        self.CList.Clear()
        item =  self.CalcTree.GetSelection()
        parent = self.CalcTree.GetItemParent(item)
        path = [self.CalcTree.GetItemText(item)]
        while self.CalcTree.GetItemText(parent) != '':
            path.append(self.CalcTree.GetItemText(parent))
            parent = self.CalcTree.GetItemParent(parent)
# calculation directory
        cdir = os.sep.join(path[::-1])
        if not isCalcOfType(ctype = '.ANI', dir = cdir):
            wx.MessageBox(cdir + ' doesn\'t contain SIESTA results of type ' + '.ANI', 'Warning', 
                  wx.OK | wx.ICON_WARNING)
            return 1
        dlg = StepDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            step = dlg.GetStep()
        else:
            dlg.Destroy()
            return
        dlg.Destroy()
        self.calc = getcalc(cdir, ctype='.ANI', steps = [step,])
        cats = self.calc.evol[0].filter('label',lambda x: x == 'Fe')
        self.CList.InsertItems([str(cat) for cat in cats], 0)        
        
    
    def UpBtnPress(self, event): # wxGlade: RootFrame.<event_handler>
        # current list count
        pass

class StepDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: StepsDialog.__init__
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_1 = wx.StaticText(self, -1, "Step No")
        self.StartTC = wx.TextCtrl(self, -1, "-1")

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        # begin wxGlade: StepsDialog.__set_properties
        self.SetTitle("Select step")

    def __do_layout(self):
        # begin wxGlade: StepsDialog.__do_layout
        StepsSizer = wx.BoxSizer(wx.VERTICAL)
        RangeSizer = wx.GridSizer(1, 2, 2, 2)
        RangeSizer.Add(self.label_1, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        RangeSizer.Add(self.StartTC, 0, wx.EXPAND, 2)
        StepsSizer.Add(RangeSizer, 0, wx.ALL|wx.EXPAND, 5)
        StepsSizer.Add(self.CreateButtonSizer(wx.OK|wx.CANCEL),0,wx.ALL|wx.EXPAND,5)         
        self.SetSizer(StepsSizer)
        StepsSizer.Fit(self)
        self.Layout()
        
    def GetStep(self):
        return int(self.StartTC.GetValue())

def isCalcOfType(ctype, **kwargs):
    if 'fn' in kwargs.keys():
        options = {'.FDF' : [f for f in kwargs['fn'] if f.endswith('.fdf')],
               '.ANI' : [f for f in kwargs['fn'] if f.endswith('.ANI')],
               '.output' : [d for d in kwargs['dn'] if d == 'stdout'],
               'pdos.xml' : [f for f in kwargs['fn'] if f == 'pdos.xml']}
    elif 'dir' in kwargs.keys():
        options = {'.FDF' : [f for f in os.listdir(kwargs['dir']) if f.endswith('.fdf')],
               '.ANI' : [f for f in os.listdir(kwargs['dir']) if f.endswith('.ANI')],
               '.output' : [d for d in os.listdir(kwargs['dir']) if d == 'stdout'],
               'pdos.xml' : [f for f in os.listdir(kwargs['dir']) if f == 'pdos.xml']}
    return options[ctype]

def getcalc(cdir, ctype, steps):
    copts = {'.FDF':'fdf',
             '.ANI':'ani',
             '.output':'out',
             'pdos.xml':'fdf'}
    
    return SiestaCalc(cdir, dtype = copts[ctype], steps = steps)

if __name__== '__main__':
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    rf = RootFrame(None, -1, "")
    app.SetTopWindow(rf)
    rf.Show()
    app.MainLoop()    
      