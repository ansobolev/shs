import sys
import wx
from wx.lib.agw import floatspin as fs

from shs.const import PeriodicTable

try:
    from core import fdf_options
    from core import fdf_wx
    from core.dialogs import ac_init
except ImportError:
    from .. import fdf_options
    from .. import fdf_wx
    from ..dialogs import ac_init

__title__ = "System"
__page__ = 1


class ChemicalSpeciesLabel(fdf_options.Block):
    fdf_text = ["NumberOfSpecies", "ChemicalSpeciesLabel"]
    box = "Chemical species"
    priority = 10
    proportion = 1

    def __init__(self, parent):
        super(ChemicalSpeciesLabel, self).__init__()
        self.parent = parent
        self._sizer = self.__create_sizer(parent)

    def __create_sizer(self, parent):
        self.LC = fdf_wx.TEListCtrl(parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.LC.InsertColumn(0, 'No.', width=50)
        self.LC.InsertColumn(1, 'Charge', width=100)
        self.LC.InsertColumn(2, 'Label', width=150)
        self.LC.InsertColumn(3, 'Mass', width=100)

        self.AddBtn = wx.Button(parent, -1, 'Add')
        self.RmBtn = wx.Button(parent, -1, 'Remove')
        # binding events
        self.AddBtn.Bind(wx.EVT_BUTTON, self._on_AddBtn_press)
        self.RmBtn.Bind(wx.EVT_BUTTON, self._on_RmBtn_press)
        self.LC.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_sel)
        self.LC.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_sel)
        self.LC.Bind(wx.EVT_LIST_END_LABEL_EDIT, self._on_edit)

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

    def _on_AddBtn_press(self, evt):
        self.LC.InsertStringItem(sys.maxint, str(self.LC.GetItemCount() + 1))

    def _on_RmBtn_press(self, evt):
        # delete
        for _ in range(self.LC.GetSelectedItemCount()):
            self.LC.DeleteItem(self.LC.GetFirstSelected())
        #renumber
        for i in range(self.LC.GetItemCount()):
            self.LC.SetStringItem(i, 0, str(i + 1))
        self.RmBtn.Enable(False)

    def _on_sel(self, evt):
        self.RmBtn.Enable(self.LC.GetSelectedItemCount())
        evt.Skip()

    def _on_edit(self, evt):
        """
        Event handler; gets default charge for atoms in CSL block
        """
        row = evt.m_itemIndex
        col = evt.m_col
        if col == 2:
            self.LC.SetStringItem(row, 1, str(PeriodicTable.get(evt.GetText(), 0)))                         

    def SetFDFValue(self, value):
        if value.key == 'NumberOfSpecies':
            print 'Number of atomic types: %d' % (value.value,)
            return None
        self.LC.SetValue(value)

    def FDF_string(self, k):
        if k.lower() == "NumberOfSpecies".lower():
            return "{0:<25}\t{1}".format("NumberOfSpecies", self.LC.GetItemCount())
        elif k.lower() == "ChemicalSpeciesLabel".lower():
            s = "%block ChemicalSpeciesLabel\n"
            for i in range(self.LC.GetItemCount()):
                items = [self.LC.GetItem(itemId=i, col=j).GetText() for j in range(3)]
                s += "  {0}\t{1}\t{2}\n".format(*items)
            s += "%endblock ChemicalSpeciesLabel"
            return s
        else:
            raise KeyError


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
        super(LatticeParVec, self).__init__()
        self.parent = parent
        self._sizer = self.__create_sizer(parent)
        # create bindings here
        self.parent.Bind(fdf_wx.EVT_RADIOLINE, self.on_choice, self.LatParOrVec)
        self.parent.Bind(wx.EVT_CHECKBOX, self.on_enable, self.LatParOrVec.switch)

    def __create_sizer(self, parent):

        self.LatParOrVec = self.Choice(parent) 
        self.latPar = self.__create_lat_par(parent)
        self.latVec = self.__create_lat_vec(parent)
        self.__set_properties()
        return self.__do_layout()
    
    def __create_lat_par(self, parent):
        self.a = fs.FloatSpin(parent, -1, digits=2, increment=0.01, value=1.0)
        self.b = fs.FloatSpin(parent, -1, digits=2, increment=0.01, value=1.0)
        self.c = fs.FloatSpin(parent, -1, digits=2, increment=0.01, value=1.0)
        
        self.alpha = fs.FloatSpin(parent, -1, digits=2, increment=0.01, min_val=0., max_val=180., value=90.0)
        self.beta = fs.FloatSpin(parent, -1, digits=2, increment=0.01, min_val=0., max_val=180., value=90.0)
        self.gamma = fs.FloatSpin(parent, -1, digits=2, increment=0.01, min_val=0., max_val=180., value=90.0)

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

    def __create_lat_vec(self, parent):
        self.ax = fs.FloatSpin(parent, -1, digits=3, increment=0.01, value=1.0)
        self.ay = fs.FloatSpin(parent, -1, digits=3, increment=0.01)
        self.az = fs.FloatSpin(parent, -1, digits=3, increment=0.01)
        self.bx = fs.FloatSpin(parent, -1, digits=3, increment=0.01)
        self.by = fs.FloatSpin(parent, -1, digits=3, increment=0.01, value=1.0)
        self.bz = fs.FloatSpin(parent, -1, digits=3, increment=0.01)
        self.cx = fs.FloatSpin(parent, -1, digits=3, increment=0.01)
        self.cy = fs.FloatSpin(parent, -1, digits=3, increment=0.01)
        self.cz = fs.FloatSpin(parent, -1, digits=3, increment=0.01, value=1.0)

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
        main_sizer.Add(self.LatParOrVec.sizer, 0, wx.ALL | wx.EXPAND, 2)
        main_sizer.Add(self.latPar, 0, wx.ALL | wx.EXPAND, 2)
        main_sizer.Add(self.latVec, 0, wx.ALL | wx.EXPAND, 2)

        return main_sizer

    def SetFDFValue(self, value):
        self.LatParOrVec.Enable(True)
        if value.key == "LatticeParameters":
            self.LatParOrVec.SetValue(0)
            self.show_by_value(0)
            self.set_lat_par_value(value.value)
        else:
            self.LatParOrVec.SetValue(1)
            self.show_by_value(1)
            self.set_latVec_value(value.value)

    def set_lat_par_value(self, value):
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

    def FDF_string(self, k):
        if not self.LatParOrVec.IsEnabled():
            return ""
        if k.lower() == "LatticeParameters".lower():
            return ""
        elif k.lower() == "LatticeVectors".lower():
            s = "%block LatticeVectors\n"
            s += "  {0}    {1}    {2}\n".format(self.ax.GetValue(),
                                                self.ay.GetValue(),
                                                self.az.GetValue())
            s += "  {0}    {1}    {2}\n".format(self.bx.GetValue(),
                                                self.by.GetValue(),
                                                self.bz.GetValue())
            s += "  {0}    {1}    {2}\n".format(self.cx.GetValue(),
                                                self.cy.GetValue(),
                                                self.cz.GetValue())
            s += "%endblock LatticeVectors"
            return s

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
    fdf_text = ["NumberOfAtoms", "AtomicCoordinatesAndAtomicSpecies"]
    proportion = 2

    def __init__(self, parent, *args, **kwds):
        super(AtomicCoordinates, self).__init__(*args, **kwds)
        self.parent = parent
        self._sizer = self.__create_sizer(parent)

    def __create_sizer(self, parent):
        self.AddBtn = wx.Button(parent, -1, 'Add')
        self.RmBtn = wx.Button(parent, -1, 'Remove')
        self.InitBtn = wx.Button(parent, -1, 'Initialize')
        self.ImportBtn = wx.Button(parent, -1, 'Import')
        self.LC = fdf_wx.NumberedTEListCtrl(parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.LC.InsertColumn(0, 'No.', width=50)
        self.LC.InsertColumn(1, 'X', width=112)
        self.LC.InsertColumn(2, 'Y', width=112)
        self.LC.InsertColumn(3, 'Z', width=112)
        self.LC.InsertColumn(4, 'Species', width=58)
        # create bindings here
        self.AddBtn.Bind(wx.EVT_BUTTON, self.on_AddBtn_press)
        self.RmBtn.Bind(wx.EVT_BUTTON, self.on_RmBtn_press)
        if self.parent.__class__.__name__ == "NBPage":
            self.bindings = [(self.InitBtn,
                              wx.EVT_BUTTON,
                              self.on_InitBtn_press)]
        else:
            self.InitBtn.Bind(wx.EVT_BUTTON, self.on_InitBtn_press)
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
        self.RmBtn.Enable(False)

    def on_sel(self, evt):
        self.RmBtn.Enable(self.LC.GetSelectedItemCount())
        evt.Skip()

    def on_edit(self, evt):
        row = evt.m_itemIndex
        col = evt.m_col
        try:
            float(evt.GetText())
        except ValueError:
            self.LC.SetStringItem(row, col, '0.0')                         

    def on_InitBtn_press(self, evt, ChemicalSpeciesLabel=None):
        if ChemicalSpeciesLabel is None:
            labels = []
        else:
            lc = ChemicalSpeciesLabel.LC
            labels = [lc.GetItem(itemId=i, col=2).GetText() for i in range(lc.GetItemCount())]
        dlg = ac_init.ACInitDialog(None, types=labels)

        if dlg.ShowModal() == wx.ID_OK:
            g_opts = dlg.init_geom()
            self.set_geom(g_opts)
        dlg.Destroy()

    def set_geom(self, options):
        self.LC.SetValue(options)

    def FDF_string(self, k):
        if k.lower() == "NumberOfAtoms".lower():
            return "{0:<25}\t{1}".format("NumberOfAtoms", self.LC.GetItemCount())
        elif k.lower() == "AtomicCoordinatesAndAtomicSpecies".lower():
            s = "%block AtomicCoordinatesAndAtomicSpecies\n"
            for i in range(self.LC.GetItemCount()):
                items = [float(self.LC.GetItem(itemId=i, col=j+1).GetText()) if j < 3
                         else int(self.LC.GetItem(itemId=i, col=j+1).GetText()) for j in range(4)]
                s += "  {0:<12.8f}\t{1:<12.8f}\t{2:<12.8f}\t{3:<3d}\n".format(*items)
            s += "%endblock AtomicCoordinatesAndAtomicSpecies"
            return s
