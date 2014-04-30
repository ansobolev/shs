import wx
from core import fdf_options

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
    choices = ['CA','PW92','PBE', 'revPBE', 'RPBE', 'WC', 'PBEsol', 'LYP']
    priority = 20

class MaxSCFIterations(fdf_options.NumberLine):
    label = 'Max SCF iterations'
    fdf_text = 'MaxSCFIterations'
    value = 200
    digits = 0
    increment = 10
    optional = True
    priority = 25

class SolutionMethod(fdf_options.ChoiceLine):
    label = 'Solution method'
    fdf_text = 'SolutionMethod'
    optional = True
    choices = ['diagon', 'orderN']
    priority = 30

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
        print self.IsEnabled()
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
