import sys
import wx
from shs.const import PeriodicTable 
from core import fdf_options
from core import fdf_wx
from wx.lib.agw import floatspin as fs

__title__ = "System"
__page__ = 1

class ChemicalSpeciesLabel(fdf_options.Block):
    fdf_text = ["NumberOfSpecies", "ChemicalSpeciesLabel"]
    box = "Chemical species"
    priority = 10
    proportion = 1

    def __init__(self, parent):
        self.parent = parent
        self._sizer = self.__create_sizer(parent)

    def __create_sizer(self, parent):
        self.LC = fdf_wx.TEListCtrl(parent, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.LC.InsertColumn(0, 'No.', width = 50)
        self.LC.InsertColumn(1, 'Charge', width = 100)
        self.LC.InsertColumn(2, 'Label', width = 150)       
        self.LC.InsertColumn(3, 'Mass', width = 100)

        self.AddBtn = wx.Button(parent, -1, 'Add')
        self.RmBtn = wx.Button(parent, -1, 'Remove')
        # binding events
        self.AddBtn.Bind(wx.EVT_BUTTON, self.on_AddBtn_press)
        self.RmBtn.Bind(wx.EVT_BUTTON, self.on_RmBtn_press)
        self.LC.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_sel)
        self.LC.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_sel)
        self.LC.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.on_edit)

        self.__set_properties()
        return self.__do_layout()

    def __set_properties(self):
        # turn off rm btn 
        self.RmBtn.Enable(False)

    def __do_layout(self):
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.AddBtn, 1, wx.ALL | wx.EXPAND, 5)
        btn_sizer.Add(self.RmBtn, 1, wx.ALL | wx.EXPAND, 5)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.LC, 1, wx.EXPAND, 0)
        main_sizer.Add(btn_sizer, 0, wx.EXPAND, 0)
        return main_sizer


    def on_AddBtn_press(self, evt):
        self.LC.InsertStringItem(sys.maxint, str(self.LC.GetItemCount() + 1))

    def on_RmBtn_press(self, evt):
        # delete
        for _ in range(self.LC.GetSelectedItemCount()):
            self.LC.DeleteItem(self.LC.GetFirstSelected())
        #renumber
        for i in range(self.LC.GetItemCount()):
            self.LC.SetStringItem(i, 0, str(i + 1))
        self.RmBtn.Enable(False)

    def on_sel(self, evt):
        self.RmBtn.Enable(self.LC.GetSelectedItemCount())
        evt.Skip()

    def on_edit(self, evt):
        'Gets default charge for atoms in CSL block'
        row = evt.m_itemIndex
        col = evt.m_col
        if col == 2:
            self.LC.SetStringItem(row, 1, str(PeriodicTable.get(evt.GetText(), 0)))                         

    def SetFDFValue(self, value):
        if value.key == 'NumberOfSpecies':
            print 'Number of atomic types: %d' % (value.value,)
            return None 
        self.LC.SetValue(value)
    

class AtomicCoordinatesFormat(fdf_options.ChoiceLine):
    label = 'Coordinates format'
    fdf_text = "AtomicCoordinatesFormat"
    choices = ['NotScaledCartesianBohr', 'NotScaledCartesianAng',
               'ScaledCartesian', 'ScaledByLatticeVectors'] 
    box = "Atomic coordinates"
    optional = True
    priority = 20

class LatticeConstant(fdf_options.MeasuredLine):
    label = 'Lattice constant'
    fdf_text = 'LatticeConstant'
    optional = True
    value = 1.
    digits = 2
    increment = 0.01
    units = ['Bohr', 'Ang']
    box = "Atomic coordinates"
    priority = 30    

class LatticeParVec(fdf_options.Block):
    box = "Atomic coordinates"
    priority = 40
    fdf_text = ["LatticeParameters", "LatticeVectors"]

    class Choice(fdf_options.RadioLine):
        ''' Radio buttons line with choice
        '''
        label = 'Cell construction'
        optional = True
        choices = ['by lattice parameters', 'by lattice vectors']

    def __init__(self, parent):
        self.parent = parent
        self._sizer = self.__create_sizer(parent)
        self.bindings = [(self.LatParOrVec, 
                          fdf_wx.EVT_RADIOLINE, 
                          self.on_choice),
                         (self.LatParOrVec.switch,
                          wx.EVT_CHECKBOX,
                          self.on_enable)]

    def __create_sizer(self, parent):

        self.LatParOrVec = self.Choice(parent) 
        self.latPar = self.__create_latPar(parent)
        self.latVec = self.__create_latVec(parent)        
        self.__set_properties()
        return self.__do_layout()
    
    def __create_latPar(self, parent):
        self.a = fs.FloatSpin(parent, -1, digits = 2, increment = 0.01, value = 1.0)
        self.b = fs.FloatSpin(parent, -1, digits = 2, increment = 0.01, value = 1.0)
        self.c = fs.FloatSpin(parent, -1, digits = 2, increment = 0.01, value = 1.0)
        
        self.alpha = fs.FloatSpin(parent, -1, digits = 2, increment = 0.01, min_val = 0., max_val = 180., value = 90.0)
        self.beta = fs.FloatSpin(parent, -1, digits = 2, increment = 0.01, min_val = 0., max_val = 180., value = 90.0)
        self.gamma = fs.FloatSpin(parent, -1, digits = 2, increment = 0.01, min_val = 0., max_val = 180., value = 90.0)

        al = wx.StaticText(parent, -1, '   a = ')
        bl = wx.StaticText(parent, -1, '   b = ')
        cl = wx.StaticText(parent, -1, '   c = ')
        alphal = wx.StaticText(parent, -1, '   alpha = ')
        betal = wx.StaticText(parent, -1, '   beta = ')
        gammal = wx.StaticText(parent, -1, '   gamma = ')

        sizer = wx.GridSizer(rows=3, cols=4, vgap=2, hgap=2)
        sizer.Add(al, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.a, 0, wx.EXPAND, 0)
        sizer.Add(alphal, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.alpha, 0, wx.EXPAND, 0)
        sizer.Add(bl, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.b, 0, wx.EXPAND, 0)
        sizer.Add(betal, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.beta, 0, wx.EXPAND, 0)
        sizer.Add(cl, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.c, 0, wx.EXPAND, 0)
        sizer.Add(gammal, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.gamma, 0, wx.EXPAND, 0)
        return sizer  

    def __create_latVec(self, parent):
        self.ax = fs.FloatSpin(parent, -1, digits = 3, increment = 0.01, value = 1.0)
        self.ay = fs.FloatSpin(parent, -1, digits = 3, increment = 0.01)
        self.az = fs.FloatSpin(parent, -1, digits = 3, increment = 0.01)
        self.bx = fs.FloatSpin(parent, -1, digits = 3, increment = 0.01)
        self.by = fs.FloatSpin(parent, -1, digits = 3, increment = 0.01, value = 1.0)
        self.bz = fs.FloatSpin(parent, -1, digits = 3, increment = 0.01)
        self.cx = fs.FloatSpin(parent, -1, digits = 3, increment = 0.01)
        self.cy = fs.FloatSpin(parent, -1, digits = 3, increment = 0.01)
        self.cz = fs.FloatSpin(parent, -1, digits = 3, increment = 0.01, value = 1.0)

        al = wx.StaticText(parent, -1, '   vec1 = ')
        bl = wx.StaticText(parent, -1, '   vec2 = ')
        cl = wx.StaticText(parent, -1, '   vec3 = ')
        
        sizer = wx.GridSizer(rows=3, cols=4, vgap=2, hgap=2)
        sizer.Add(al, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.ax, 0, wx.EXPAND, 0)
        sizer.Add(self.ay, 0, wx.EXPAND, 0)
        sizer.Add(self.az, 0, wx.EXPAND, 0)
        sizer.Add(bl, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.bx, 0, wx.EXPAND, 0)
        sizer.Add(self.by, 0, wx.EXPAND, 0)
        sizer.Add(self.bz, 0, wx.EXPAND, 0)
        sizer.Add(cl, 0, wx.ADJUST_MINSIZE, 0)
        sizer.Add(self.cx, 0, wx.EXPAND, 0)
        sizer.Add(self.cy, 0, wx.EXPAND, 0)
        sizer.Add(self.cz, 0, wx.EXPAND, 0)
        return sizer

    def __set_properties(self):
        self.latPar.ShowItems(False)
        self.latVec.ShowItems(False)

    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.LatParOrVec.sizer, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(self.latPar, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(self.latVec, 0, wx.ALL|wx.EXPAND, 2)

        return main_sizer

    def SetFDFValue(self, value):
        self.LatParOrVec.Enable(True)
        if value.key == "LatticeParameters":
            self.LatParOrVec.SetValue(0)
            self.show_by_value(0)
            self.set_latPar_value(value.value)
        else:
            self.LatParOrVec.SetValue(1)
            self.show_by_value(1)
            self.set_latVec_value(value.value)

    def set_latPar_value(self, value):
        pass

    def set_latVec_value(self, value):
        self.ax.SetValue(float(value[0][0]))
        self.bx.SetValue(float(value[1][0]))
        self.cx.SetValue(float(value[2][0]))
        self.ay.SetValue(float(value[0][1]))
        self.by.SetValue(float(value[1][1]))
        self.cy.SetValue(float(value[2][1]))
        self.az.SetValue(float(value[0][2]))
        self.bz.SetValue(float(value[1][2]))
        self.cz.SetValue(float(value[2][2]))
    
    def show_by_value(self, value):
        if value == 0:
            self.latPar.ShowItems(True)
            self.latVec.ShowItems(False)
        else:
            self.latPar.ShowItems(False)
            self.latVec.ShowItems(True)
        self.parent.Layout()

    def hide(self):
        self.latPar.ShowItems(False)
        self.latVec.ShowItems(False)
        self.parent.Layout()

    def on_choice(self, event):
        self.show_by_value(event.value)

    def on_enable(self, event):
        if self.LatParOrVec.IsEnabled():
            self.show_by_value(self.LatParOrVec.GetValue())
        else:
            self.hide()

class AtomicCoordinates(fdf_options.Block):
    box = "Atomic coordinates"
    priority = 50
    fdf_text = ["NumberOfAtoms","AtomicCoordinatesAndAtomicSpecies"]
    proportion = 2

    def __init__(self, parent):
        self.parent = parent
        self._sizer = self.__create_sizer(parent)

    def __create_sizer(self, parent):
        self.AddBtn = wx.Button(parent, -1, 'Add')
        self.RmBtn = wx.Button(parent, -1, 'Remove')
        self.InitBtn = wx.Button(parent, -1, 'Initialize')
        self.ImportBtn = wx.Button(parent, -1, 'Import')
        self.LC = fdf_wx.NumberedTEListCtrl(parent, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.LC.InsertColumn(0, 'No.', width = 50)
        self.LC.InsertColumn(1, 'X', width = 112)
        self.LC.InsertColumn(2, 'Y', width = 112)
        self.LC.InsertColumn(3, 'Z', width = 112)
        self.LC.InsertColumn(4, 'Species', width = 58)
        self.__set_properties()
        return self.__do_layout()

    def __set_properties(self):
        # turn off rm btn 
        self.RmBtn.Enable(False)

    def __do_layout(self):
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.AddBtn, 1, wx.ALL | wx.EXPAND, 5)
        btn_sizer.Add(self.RmBtn, 1, wx.ALL | wx.EXPAND, 5)
        btn_sizer.Add(self.InitBtn, 1, wx.ALL | wx.EXPAND, 5)
        btn_sizer.Add(self.ImportBtn, 1, wx.ALL | wx.EXPAND, 5)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(btn_sizer, 0, wx.EXPAND, 0)
        main_sizer.Add(self.LC, 1, wx.EXPAND, 0)
        return main_sizer

    def SetFDFValue(self, value):
        if value.key == 'NumberOfAtoms':
            print 'Number of atoms: %d' % (value.value,)
            return None 
        self.LC.SetValue(value)

    def on_AddBtn_press(self, evt):
        self.LC.InsertStringItem(sys.maxint, str(self.LC.GetItemCount() + 1))

    def on_RmBtn_press(self, evt):
        # delete
        for _ in range(self.LC.GetSelectedItemCount()):
            self.LC.DeleteItem(self.LC.GetFirstSelected())
        #renumber
        for i in range(self.LC.GetItemCount()):
            self.LC.SetStringItem(i, 0, str(i + 1))
        self.LCRmBtn.Enable(False)

    def on_sel(self, evt):
        self.LCRmBtn.Enable(self.LC.GetSelectedItemCount())

    def on_InitBtn_press(self, evt):
        data = self.GetCSLData()
        dlg = dialogs.LCInitDialog(None, types = [d['label'] for d in data])
        if dlg.ShowModal() == wx.ID_OK:
            g_opts = dlg.init_geom()
            self.SetGeom(g_opts)
        dlg.Destroy()
