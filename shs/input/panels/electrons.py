import wx
from shs.input import fdf_wx
from shs.input import fdf_options

__title__ = "Electrons"
__page__ = 2


class XCFunctional(fdf_options.ChoiceLine):
    label = 'XC functional'
    fdf_text = 'XC.Functional'
    optional = True
    box = None
    choices = ['LDA', 'GGA']
    priority = 10


class XCAuthors(fdf_options.ChoiceLine):
    label = 'XC authors'
    fdf_text = 'XC.Authors'
    optional = True
    choices = ['CA', 'PW92','PBE', 'revPBE', 'RPBE', 'WC', 'PBEsol', 'LYP']
    priority = 20


class MaxSCFIterations(fdf_options.NumberLine):
    label = 'Max SCF iterations'
    fdf_text = 'MaxSCFIterations'
    value = 200
    digits = 0
    increment = 10
    optional = True
    priority = 25


class DMTolerance(fdf_options.NumberLine):
    label = 'DM tolerance'
    fdf_text = 'DM.Tolerance'
    value = 0.00001
    digits = 5
    increment = 0.00001
    optional = True
    priority = 27


class SolutionMethod(fdf_options.ChoiceLine):
    label = 'Solution method'
    fdf_text = 'SolutionMethod'
    optional = True
    choices = ['diagon', 'orderN']
    priority = 30


class KPointsGrid(fdf_options.Block):
    box = "K points"
    priority = 32
    fdf_text = ["kgrid_Monkhorst_Pack", "kgrid_cutoff"]

    class Choice(fdf_options.RadioLine):
        """ Radio buttons line with choice
        """
        label = 'K points sampling'
        optional = True
        choices = ['using K-point grid', 'using cutoff radius']

    class KGrid(fdf_options.ThreeNumberLine):
        label = 'K grid Monkhorst-Pack sampling'

    class KGridDisplacement(fdf_options.ChoiceLine):
        label = 'K grid displacement'
        choices = ['0.0', '0.5']

    class KGridCutoff(fdf_options.MeasuredLine):
        label = 'K grid cutoff radius'
        fdf_text = 'kgrid_cutoff'
        value = 20.
        digits = 0
        increment = 1.
        units = ['Ang', 'Bohr']

    def __init__(self, parent):
        super(KPointsGrid, self).__init__()
        self.parent = parent
        self._sizer = self.__create_sizer(parent)
        # create bindings here
        self.parent.Bind(fdf_wx.EVT_RADIOLINE, self.on_choice, self.GridOrCutoff)
        self.parent.Bind(wx.EVT_CHECKBOX, self.on_enable, self.GridOrCutoff.switch)

    def __create_sizer(self, parent):

        self.GridOrCutoff = self.Choice(parent)
        self._grid_sizer = self.__create_grid(parent)
        self.cutoff = self.KGridCutoff(parent)
        self.__set_properties()
        return self.__do_layout()

    def __create_grid(self, parent):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.grid = self.KGrid(parent)
        self.displacement = self.KGridDisplacement(parent)
        sizer.Add(self.grid.sizer, 0, wx.ALL | wx.EXPAND, 2)
        sizer.Add(self.displacement.sizer, 0, wx.ALL | wx.EXPAND, 2)
        return sizer

    def __set_properties(self):
        self._grid_sizer.ShowItems(False)
        self.cutoff.Show(False)

    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.GridOrCutoff.sizer, 0, wx.ALL | wx.EXPAND, 2)
        main_sizer.Add(self._grid_sizer, 0, wx.ALL | wx.EXPAND, 2)
        main_sizer.Add(self.cutoff.sizer, 0, wx.ALL | wx.EXPAND, 2)
        return main_sizer

    def on_choice(self, event):
        self.show_by_value(event.value)

    def show_by_value(self, value):
        if value == 0:
            self._grid_sizer.ShowItems(True)
            self.cutoff.Show(False)
        else:
            self._grid_sizer.ShowItems(False)
            self.cutoff.Show(True)
        self.parent.Layout()

    def on_enable(self, event):
        if self.GridOrCutoff.IsEnabled():
            self.show_by_value(self.GridOrCutoff.GetValue())
        else:
            self.hide()

    def hide(self):
        self._grid_sizer.ShowItems(False)
        self.cutoff.Show(False)
        self.parent.Layout()

    def SetFDFValue(self, value):
        self.GridOrCutoff.Enable(True)
        if value.key == "kgrid_cutoff":
            self.GridOrCutoff.SetValue(1)
            self.show_by_value(1)
            self.cutoff.SetFDFValue(value)
        else:
            self.GridOrCutoff.SetValue(0)
            self.show_by_value(0)
            self._set_grid_value(value)

    def _set_grid_value(self, value):
        kpoints = [[int(x) for x in s[:3]] for s in value.value]
        kpoints = [kpoints[i][i] for i in range(3)]
        displacements = [float(x[-1]) for x in value.value]
        assert len(set(displacements)) == 1
        self.grid.SetFDFValue(kpoints)
        self.displacement.SetFDFValue(displacements[0])

    def FDF_string(self, k):
        if not self.GridOrCutoff.IsEnabled():
            return ""
        if k.lower() == "kgrid_cutoff".lower():
            return self.cutoff.FDF_string(k)
        elif k.lower() == "kgrid_monkhorst_pack".lower():
            values = self.grid.GetValue()
            displ = self.displacement.GetValue()
            s = "%block kgrid_Monkhorst_Pack\n"
            s += ("{0}  0  0 {3}\n"
                  "0  {1}  0 {3}\n"
                  "0  0  {2} {3}\n".format(*(values + [displ, ])))
            s += "%endblock kgrid_Monkhorst_Pack"
            return s


class MeshCutoff(fdf_options.MeasuredLine):
    label = 'Mesh cutoff'
    fdf_text = 'MeshCutoff'
    optional = True
    value = 1.
    digits = 1
    increment = 1.
    units = ['K', 'eV', 'Ry']
    priority = 35    


class ElectronicTemperature(fdf_options.MeasuredLine):
    label = 'Electronic temperature'
    fdf_text = 'ElectronicTemperature'
    optional = True
    value = 1.
    digits = 1
    increment = 1.
    units = ['K', 'eV', 'Ry']
    priority = 40    


class PAOBasisType(fdf_options.ChoiceLine):
    label = 'Basis type'
    fdf_text = 'PAO.BasisType'
    optional = True
    choices = ['split', 'splitgauss', 'nodes', 'nonodes']
    box = 'PAO basis'
    priority = 50


class PAOBasisSize(fdf_options.ChoiceLine):
    label = 'Basis size'
    fdf_text = 'PAO.BasisSize'
    optional = True
    choices = ['SZ', 'SZP', 'DZ', 'DZP', 'DZDP', 'TZ', 'TZP', 'TZDP']
    box = 'PAO basis'
    priority = 60


class PAOEnergyShift(fdf_options.MeasuredLine):
    label = 'Energy shift'
    fdf_text = 'PAO.EnergyShift'
    optional = True
    value = 1.
    digits = 1
    increment = 1.
    units = ['Ry', 'eV', 'meV']
    box = 'PAO basis'
    priority = 70    


class SpinPolarized(fdf_options.BooleanLine):
    label = 'Spin polarization'
    fdf_text = 'SpinPolarized'
    optional = True
    priority = 80

    def __init__(self, parent):
        super(SpinPolarized, self).__init__(parent)
        self.bindings = [(self.CB,
                          wx.EVT_CHECKBOX,
                          self.show_spin_options
                          ),
                         (self.switch,
                          wx.EVT_CHECKBOX,
                          self.show_spin_options
                          )]

    def show_spin_options(self, event, NonCollinearSpin, DMInitSpinAF):
        NonCollinearSpin.Show(self.IsEnabled() and self.CB.IsChecked())
        DMInitSpinAF.Show(self.IsEnabled() and self.CB.IsChecked())
        event.Skip()


class NonCollinearSpin(fdf_options.BooleanLine):
    label = 'Non-collinear spin'
    fdf_text = 'NonCollinearSpin'
    optional = True
    priority = 90
    hidden = True


class DMInitSpinAF(fdf_options.BooleanLine):
    label = 'Antiferromagnetic run'
    fdf_text = 'DM.InitSpinAF'
    optional = True
    priority = 100
    hidden = True
