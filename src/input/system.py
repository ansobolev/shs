# -*- coding: utf-8 -*-

import sys
import wx
import fdf_base as fb
import dialogs
from wx.lib.agw.floatspin import FloatSpin
from shs.const import PeriodicTable 

class LatParam(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self, *args, **kwds)
        self.a = FloatSpin(self, -1, digits = 2, increment = 0.01, value = 1.0)
        self.b = FloatSpin(self, -1, digits = 2, increment = 0.01, value = 1.0)
        self.c = FloatSpin(self, -1, digits = 2, increment = 0.01, value = 1.0)
        
        self.alpha = FloatSpin(self, -1, digits = 2, increment = 0.01, min_val = 0., max_val = 180., value = 90.0)
        self.beta = FloatSpin(self, -1, digits = 2, increment = 0.01, min_val = 0., max_val = 180., value = 90.0)
        self.gamma = FloatSpin(self, -1, digits = 2, increment = 0.01, min_val = 0., max_val = 180., value = 90.0)

        self.al = wx.StaticText(self, -1, '   a = ')
        self.bl = wx.StaticText(self, -1, '   b = ')
        self.cl = wx.StaticText(self, -1, '   c = ')
        self.alphal = wx.StaticText(self, -1, '   alpha = ')
        self.betal = wx.StaticText(self, -1, '   beta = ')
        self.gammal = wx.StaticText(self, -1, '   gamma = ')

        sizer = wx.GridSizer(rows=3, cols=4, vgap=2, hgap=2)
        sizer.Add(self.al, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.a, 0, wx.EXPAND, 0)
        sizer.Add(self.alphal, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.alpha, 0, wx.EXPAND, 0)
        sizer.Add(self.bl, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.b, 0, wx.EXPAND, 0)
        sizer.Add(self.betal, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.beta, 0, wx.EXPAND, 0)
        sizer.Add(self.cl, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.c, 0, wx.EXPAND, 0)
        sizer.Add(self.gammal, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.gamma, 0, wx.EXPAND, 0)
        
        self.SetSizer(sizer)
        self.Layout()

class LatVec(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self, *args, **kwds)
        self.ax = FloatSpin(self, -1, digits = 2, increment = 0.01, value = 1.0)
        self.ay = FloatSpin(self, -1, digits = 2, increment = 0.01)
        self.az = FloatSpin(self, -1, digits = 2, increment = 0.01)
        self.bx = FloatSpin(self, -1, digits = 2, increment = 0.01)
        self.by = FloatSpin(self, -1, digits = 2, increment = 0.01, value = 1.0)
        self.bz = FloatSpin(self, -1, digits = 2, increment = 0.01)
        self.cx = FloatSpin(self, -1, digits = 2, increment = 0.01)
        self.cy = FloatSpin(self, -1, digits = 2, increment = 0.01)
        self.cz = FloatSpin(self, -1, digits = 2, increment = 0.01, value = 1.0)

        self.al = wx.StaticText(self, -1, '   vec1 = ')
        self.bl = wx.StaticText(self, -1, '   vec2 = ')
        self.cl = wx.StaticText(self, -1, '   vec3 = ')
        
        sizer = wx.GridSizer(rows=3, cols=4, vgap=2, hgap=2)
        sizer.Add(self.al, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.ax, 0, wx.EXPAND, 0)
        sizer.Add(self.ay, 0, wx.EXPAND, 0)
        sizer.Add(self.az, 0, wx.EXPAND, 0)
        sizer.Add(self.bl, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.bx, 0, wx.EXPAND, 0)
        sizer.Add(self.by, 0, wx.EXPAND, 0)
        sizer.Add(self.bz, 0, wx.EXPAND, 0)
        sizer.Add(self.cl, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.cx, 0, wx.EXPAND, 0)
        sizer.Add(self.cy, 0, wx.EXPAND, 0)
        sizer.Add(self.cz, 0, wx.EXPAND, 0)
        self.SetSizer(sizer)
        self.Layout()

    def SetValue(self, val):
        self.ax.SetValue(val[0,0])
        self.ay.SetValue(val[0,1])
        self.az.SetValue(val[0,2])
        self.bx.SetValue(val[1,0])
        self.by.SetValue(val[1,1])
        self.bz.SetValue(val[1,2])
        self.cx.SetValue(val[2,0])
        self.cy.SetValue(val[2,1])
        self.cz.SetValue(val[2,2])



class SystemPN(wx.ScrolledWindow):
    
    def __init__(self, *args, **kwds):
        wx.ScrolledWindow.__init__(self, *args, **kwds)
        self.CSLSizer = self.CreateChemSpecLabel()
        self.ACSizer = self.CreateAtomicCrd()
        
        self.fdf_opts = {}
        self.fdf_opts = {'system' : {'ChemicalSpeciesLabel' : self.CSL,
                                     'AtomicCoordinatesFormat' : self.ACFormat,
                                     'LatticeConstant' : self.ACalat},
                         'crd' : {'AtomicCoordinatesAndAtomicSpecies' : self.AC}}
        # Binding events
        self.Bind(wx.EVT_BUTTON, self.CSLAddBtnPress, self.CSLAddBtn)
        self.Bind(wx.EVT_BUTTON, self.CSLRmBtnPress, self.CSLRmBtn)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.CSLSel, self.CSL)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.CSLSel, self.CSL)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.CSLEdit, self.CSL)


        self.Bind(fb.EVT_RADIOSIZER, self.byParOrVecSel, self.byParOrVec)

        self.Bind(wx.EVT_BUTTON, self.ACAddBtnPress, self.ACAddBtn)
        self.Bind(wx.EVT_BUTTON, self.ACRmBtnPress, self.ACRmBtn)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.ACSel, self.AC)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.ACSel, self.AC)
        
        self.Bind(wx.EVT_BUTTON, self.ACInitBtnPress, self.ACInitBtn)
        
        self.__set_properties()
        self.__do_layout()
    
    def CreateChemSpecLabel(self):
        CSLLabel = wx.StaticBox(self, -1, 'Chemical species')

        self.CSL = fb.TEListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.CSL.InsertColumn(0, 'No.', width = 50)
        self.CSL.InsertColumn(1, 'Charge', width = 100)
        self.CSL.InsertColumn(2, 'Label', width = 150)       
        self.CSL.InsertColumn(3, 'Mass', width = 100)

        self.CSLAddBtn = wx.Button(self, -1, 'Add')
        self.CSLRmBtn = wx.Button(self, -1, 'Remove')
        # turn off rm btn 
        self.CSLRmBtn.Enable(False)               
        
        CSLBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        CSLBtnSizer.Add(self.CSLAddBtn, 1, wx.ALL | wx.EXPAND, 5)
        CSLBtnSizer.Add(self.CSLRmBtn, 1, wx.ALL | wx.EXPAND, 5)
        
        sizer = wx.StaticBoxSizer(CSLLabel, wx.VERTICAL)
        sizer.Add(self.CSL, 1, wx.EXPAND, 0)
        sizer.Add(CSLBtnSizer, 0, wx.EXPAND, 0)
        return sizer

    def CreateAtomicCrd(self):
        ACLabel = wx.StaticBox(self, -1, 'Atomic coordinates and species')
        acf = ['NotScaledCartesianBohr', 'NotScaledCartesianAng',
               'ScaledCartesian', 'ScaledByLatticeVectors'] 
    
        self.ACFormat = fb.ComboSizer(self, 'Coordinates format', acf)
        self.ACalat = fb.MeasuredSizer(self, 'Lattice constant', ['Bohr','Ang'], digits = 4, inc = 0.01, defVal = 1.)
        self.byParOrVec = fb.RadioSizer(self, 'Cell construction', ['by lattice parameters', 'by lattice vectors'], opt = False) 
        self.LP = LatParam(self)
        self.LV = LatVec(self)
        self.LV.Show(False)

        self.ACAddBtn = wx.Button(self, -1, 'Add')
        self.ACRmBtn = wx.Button(self, -1, 'Remove')
        # turn off rm btn 
        self.ACRmBtn.Enable(False)               

        self.ACInitBtn = wx.Button(self, -1, 'Initialize')
        self.ACImportBtn = wx.Button(self, -1, 'Import')

        self.AC = fb.NumberedTEListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.AC.InsertColumn(0, 'No.', width = 50)
        self.AC.InsertColumn(1, 'X', width = 112)
        self.AC.InsertColumn(2, 'Y', width = 112)       
        self.AC.InsertColumn(3, 'Z', width = 112)
        self.AC.InsertColumn(4, 'Species', width = 58)

        ACBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        ACBtnSizer.Add(self.ACAddBtn, 1, wx.ALL | wx.EXPAND, 5)
        ACBtnSizer.Add(self.ACRmBtn, 1, wx.ALL | wx.EXPAND, 5)
        ACBtnSizer.Add(self.ACInitBtn, 1, wx.ALL | wx.EXPAND, 5)
        ACBtnSizer.Add(self.ACImportBtn, 1, wx.ALL | wx.EXPAND, 5)
        
        sizer = wx.StaticBoxSizer(ACLabel, wx.VERTICAL)
        sizer.Add(self.ACFormat, 0, wx.EXPAND, 0)
        sizer.Add(self.ACalat, 0, wx.EXPAND, 0)
        sizer.Add(self.byParOrVec, 0, wx.EXPAND, 0)
        sizer.Add(self.LP, 0, wx.EXPAND, 0)
        sizer.Add(self.LV, 0, wx.EXPAND, 0)
        sizer.Add(ACBtnSizer, 0, wx.EXPAND, 0)
        sizer.Add(self.AC, 1, wx.EXPAND, 0)
        return sizer
    
    def CSLAddBtnPress(self, evt):
        self.CSL.InsertStringItem(sys.maxint, str(self.CSL.GetItemCount() + 1))

    def CSLRmBtnPress(self, evt):
        # delete
        for _ in range(self.CSL.GetSelectedItemCount()):
            self.CSL.DeleteItem(self.CSL.GetFirstSelected())
        #renumber
        for i in range(self.CSL.GetItemCount()):
            self.CSL.SetStringItem(i, 0, str(i + 1))
        self.CSLRmBtn.Enable(False)

    def CSLSel(self, evt):
        self.CSLRmBtn.Enable(self.CSL.GetSelectedItemCount())               

    def CSLEdit(self, evt):
        'Gets default charge for atoms in CSL block'
        row = evt.m_itemIndex
        col = evt.m_col
        if col == 2:
            self.CSL.SetStringItem(row, 1, str(PeriodicTable.get(evt.GetText(), 0)))                         
            
    def ACAddBtnPress(self, evt):
        self.AC.InsertStringItem(sys.maxint, str(self.AC.GetItemCount() + 1))

    def ACRmBtnPress(self, evt):
        # delete
        for _ in range(self.AC.GetSelectedItemCount()):
            self.AC.DeleteItem(self.AC.GetFirstSelected())
        #renumber
        for i in range(self.AC.GetItemCount()):
            self.AC.SetStringItem(i, 0, str(i + 1))
        self.ACRmBtn.Enable(False)

    def ACSel(self, evt):
        self.ACRmBtn.Enable(self.AC.GetSelectedItemCount())               

    def ACInitBtnPress(self, evt):
        data = self.GetCSLData()
        dlg = dialogs.ACInitDialog(None, types = [d['label'] for d in data])
        if dlg.ShowModal() == wx.ID_OK:
            g_opts = dlg.init_geom()
            self.SetGeom(g_opts)
        dlg.Destroy()

    def SetGeom(self, g):
        'Sets system panel according to given geometry options'
        acf = {'Bohr' : 'NotScaledCartesianBohr', 'Ang' : 'NotScaledCartesianAng'}
        ctrls = {}

        for key in self.fdf_opts.keys():
            ctrls.update(self.fdf_opts[key])
        ctrls.pop('ChemicalSpeciesLabel')
        for option, value in g.opts.items():
            if option in ctrls.keys():
                ctrls[option].SetValue(value)

    
    def byParOrVecSel(self, evt):
        if evt.value == 1:
            self.LP.Show(False)
            self.LV.Show(True)
        else:
            self.LP.Show(True)
            self.LV.Show(False)
        self.Layout()
    
    def GetCSLData(self):
        'Gets data from Chemical Species block in a dictionary'
        data = []
        for row in range(self.CSL.GetItemCount()):
            data.append({})
            data[row]['label'] = self.CSL.GetItem(row,2).GetText()
            data[row]['charge'] = int(self.CSL.GetItem(row,1).GetText()) 
            try:
                data[row]['mass'] = float(self.CSL.GetItem(row,3).GetText())
            except:
                data[row]['mass'] = None
        # check
        return data

    
    def __set_properties(self):
        self.SetScrollRate(0, 10)


    def __do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.CSLSizer, 1, wx.EXPAND, 0)
        sizer.Add(self.ACSizer, 2, wx.EXPAND, 0)
        self.SetSizer(sizer)
        self.Layout()
        
if __name__ == '__main__':
    'A simple test'
    app = wx.App()
    f = wx.Frame(None, -1)
    p = SystemPN(f, -1)

    s = wx.BoxSizer(wx.VERTICAL)
    s.Add(p, 1, wx.EXPAND, 0)
    f.SetSizer(s)
    f.Layout()
    app.SetTopWindow(f)
    f.Show()
    app.MainLoop()        
