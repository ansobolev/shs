
import wx
from input import fdf_options

__title__ = "Ions"
__page__ = 3

class MDNumCGSteps(fdf_options.NumberLine):
    label = 'Number of CG steps'
    fdf_text = 'MD.NumCGSteps'
    value = 0
    digits = 0
    increment = 10.
    optional = True
    priority = 10

    def show_by_calctype(self, calctype):
        good_types = ['CG','Broyden']
        if calctype in good_types:
            self.Show(True)
        else:
            self.Show(False)

class MDMaxForceTol(fdf_options.MeasuredLine):
    label = 'Max force tolerance'
    fdf_text = 'MD.MaxForceTol'
    value = 0.04
    digits = 2
    increment = 0.01
    units = ['eV/Ang', 'Ry/Bohr', 'N']
    optional = True
    priority = 20

    def show_by_calctype(self, calctype):
        good_types = ['CG','Broyden', 'FIRE']
        if calctype in good_types:
            self.Show(True)
        else:
            self.Show(False)

class MDMaxCGDispl(fdf_options.MeasuredLine):
    label = 'Max atom displacement'
    fdf_text = 'MD.MaxCGDispl'
    value = 0.05
    digits = 2
    increment = 0.01
    units = ['Ang', 'Bohr', 'nm', 'cm']
    optional = True
    priority = 30

    def show_by_calctype(self, calctype):
        good_types = ['CG','Broyden', 'FIRE']
        if calctype in good_types:
            self.Show(True)
        else:
            self.Show(False)

class MDVariableCell(fdf_options.BooleanLine):
    label = 'Variable cell'
    fdf_text = 'MD.VariableCell'
    optional = True
    priority = 40

    def show_by_calctype(self, calctype):
        good_types = ['CG','Broyden', 'FIRE']
        if calctype in good_types:
            self.Show(True)
        else:
            self.Show(False)

class MDFinalTimeStep(fdf_options.NumberLine):
    label = 'Number of MD timesteps'
    fdf_text = 'MD.FinalTimeStep'
    value = 0.
    digits = 0
    increment = 1
    optional = True
    priority = 60
    hidden = True

    def show_by_calctype(self, calctype):
        good_types = ['Nose', 'ParrinelloRahman', 'NoseParrinelloRahman', 'FIRE']
        if calctype in good_types:
            self.Show(True)
        else:
            self.Show(False)

class MDLengthTimeStep(fdf_options.MeasuredLine):
    label = 'Length of a timestep'
    fdf_text = 'MD.LengthTimeStep'
    value = 1.
    digits = 2
    increment = 0.1
    units = ['fs', 'ps', 'ns']
    optional = True
    priority = 70
    hidden = True

    def show_by_calctype(self, calctype):
        good_types = ['Nose', 'ParrinelloRahman', 'NoseParrinelloRahman', 'FIRE']
        if calctype in good_types:
            self.Show(True)
        else:
            self.Show(False)

class MDInitialTemperature(fdf_options.MeasuredLine):
    label = 'Initial system temperature'
    fdf_text = 'MD.InitialTemperature'
    value = 0.
    digits = 1
    increment = 1
    units = ['K', 'eV', 'meV', 'Ry', 'mRy']
    optional = True
    priority = 80
    hidden = True

    def show_by_calctype(self, calctype):
        good_types = ['Verlet', 'Nose', 'ParrinelloRahman', 'NoseParrinelloRahman', 'Anneal']
        if calctype in good_types:
            self.Show(True)
        else:
            self.Show(False)

class MDTargetTemperature(fdf_options.MeasuredLine):
    label = 'Target system temperature'
    fdf_text = 'MD.TargetTemperature'
    value = 0.
    digits = 1
    increment = 1
    units = ['K', 'eV', 'meV', 'Ry', 'mRy']
    optional = True
    priority = 90
    hidden = True

    def show_by_calctype(self, calctype):
        good_types = ['Nose', 'NoseParrinelloRahman', 'Anneal']
        if calctype in good_types:
            self.Show(True)
        else:
            self.Show(False)


class MDTargetPressure(fdf_options.MeasuredLine):
    label = 'Target pressure'
    fdf_text = 'MD.TargetPressure'
    value = 0.
    digits = 2
    increment = 0.01
    units = ['GPa', 'MPa', 'Pa', 'atm', 'bar', 'kbar', 'Mbar']
    optional = True
    priority = 95

    def show_by_calctype(self, calctype):
        good_types = ['CG','Broyden', 'ParrinelloRahman', 'NoseParrinelloRahman']
        if calctype in good_types:
            self.Show(True)
        else:
            self.Show(False)

class MDNoseMass(fdf_options.MeasuredLine):
    label = 'Nose mass'
    fdf_text = 'MD.NoseMass'
    value = 100.
    digits = 1
    increment = 5
    units = ['Ry*fs**2', 'kg*m**2']
    optional = True
    priority = 100
    hidden = True

    def show_by_calctype(self, calctype):
        good_types = ['Nose', 'NoseParrinelloRahman']
        if calctype in good_types:
            self.Show(True)
        else:
            self.Show(False)

class MDParrinelloRahmanMass(fdf_options.MeasuredLine):
    label = 'Parrinello-Rahman mass'
    fdf_text = 'MD.ParrinelloRahmanMass'
    value = 100.
    digits = 1
    increment = 5
    units = ['Ry*fs**2', 'kg*m**2']
    optional = True
    priority = 110
    hidden = True

    def show_by_calctype(self, calctype):
        good_types = ['ParrinelloRahman', 'NoseParrinelloRahman']
        if calctype in good_types:
            self.Show(True)
        else:
            self.Show(False)
