
import wx
from core import fdf_options

__title__ = "Control"
__page__ = 0

class SystemName(fdf_options.TextEditLine):
    label = 'System name'
    fdf_text = 'SystemName'
    priority = 10

class SystemLabel(fdf_options.TextEditLine):
    label = 'System label'
    fdf_text = 'SystemLabel'
    priority = 20

class MDTypeOfRun(fdf_options.ChoiceLine):
    label = 'Calculation type'
    fdf_text = 'MD.TypeOfRun'
    choices = ['CG', 'Nose', 'ParrinelloRahman', 'NoseParrinelloRahman', 'Anneal',
               'Broyden', 'FIRE', 'Verlet', 'FC', 'Phonon', 'Forces']
    priority = 30

    def __init__(self, parent):
        super(MDTypeOfRun, self).__init__(parent)
        self.bindings = [(self.CB,
                          wx.EVT_CHOICE,
                          self.show_by_calctype,
                       )]

    def show_by_calctype(self, event, MDNumCGSteps,
                      MDMaxForceTol,
                      MDMaxCGDispl,
                      MDVariableCell,
                      MDTargetPressure,
                      MDFinalTimeStep,
                      MDLengthTimeStep,
                      MDInitialTemperature,
                      MDTargetTemperature,
                      MDNoseMass,
                      MDParrinelloRahmanMass):
        args = locals()
        args.pop('self')
        args.pop('event')
        for name, instance in args.iteritems():
            instance.show_by_calctype(self.GetValue())
        event.Skip()

class UseSaveData(fdf_options.BooleanLine):
    label = 'Use save data'
    fdf_text = 'UseSaveData'
    box = "Input options"
    optional = True
    priority = 40

class DMUseSaveDM(fdf_options.BooleanLine):
    label = 'Use density matrix'
    fdf_text = 'DM.UseSaveDM'
    box = "Input options"
    optional = True
    priority = 50

class MDUseSaveXV(fdf_options.BooleanLine):
    label = 'Use data from XV file'
    fdf_text = 'MD.UseSaveXV'
    box = "Input options"
    optional = True
    priority = 60

class LongOutput(fdf_options.BooleanLine):
    label = 'Long output'
    fdf_text = 'LongOutput'
    box = "Output options"
    optional = True
    priority = 70

class WriteCoorStep(fdf_options.BooleanLine):
    label = 'Coordinates (stepwise)'
    fdf_text = 'WriteCoorStep'
    box = "Output options"
    optional = True
    priority = 80

class WriteMDhistory(fdf_options.BooleanLine):
    label = 'MD history (.MD, .MDE)'
    fdf_text = 'WriteMDhistory'
    box = "Output options"
    optional = True
    priority = 90

class WriteMDXmol(fdf_options.BooleanLine):
    label = 'MD file for Xmol (.ANI)'
    fdf_text = 'WriteMDXmol'
    box = "Output options"
    optional = True
    priority = 100

class AtomCoorFormatOut(fdf_options.ChoiceLine):
    label = 'Coordinates output format'
    fdf_text = 'AtomCoorFormatOut'
    choices = ['NotScaledCartesianBohr', 'NotScaledCartesianAng', 
                'ScaledCartesian', 'ScaledByLatticeVectors']
    box = "Output options"
    optional = True
    priority = 110

class WriteForces(fdf_options.BooleanLine):
    label = 'Atomic forces'
    fdf_text = 'WriteForces'
    box = "Output options"
    optional = True
    priority = 120

class WriteCoorXmol(fdf_options.BooleanLine):
    label = 'Coordinates for Xmol'
    fdf_text = 'WriteCoorXmol'
    box = "Output options"
    optional = True
    priority = 130

class WriteCoorCerius(fdf_options.BooleanLine):
    label = 'Coordinates for Cerius'
    fdf_text = 'WriteCoorCerius'
    box = "Output options"
    optional = True
    priority = 140

class WriteMulllikenPop(fdf_options.ChoiceLine):
    label = 'Mulliken population'
    fdf_text = 'WriteMullikenPop'
    choices = ['0', '1', '2', '3']
    box = "Output options"
    optional = True
    priority = 150

class SaveTotalPotential(fdf_options.BooleanLine):
    label = 'Total potential'
    fdf_text = 'SaveTotalPotential'
    box = "Output options"
    optional = True
    priority = 160

class SaveElectrostaticPotential(fdf_options.BooleanLine):
    label = 'Electrostatic potential'
    fdf_text = 'SaveElectrostaticPotential'
    box = "Output options"
    optional = True
    priority = 170

class SaveRho(fdf_options.BooleanLine):
    label = 'Charge density (.RHO)'
    fdf_text = 'SaveRho'
    box = "Output options"
    optional = True
    priority = 180

class WriteKPoints(fdf_options.BooleanLine):
    label = 'K-points'
    fdf_text = 'WriteKPoints'
    box = "Output options"
    optional = True
    priority = 190

class WriteKBands(fdf_options.BooleanLine):
    label = 'K-bands'
    fdf_text = 'WriteKBands'
    box = "Output options"
    optional = True
    priority = 200

class WriteEigenvalues(fdf_options.BooleanLine):
    label = 'Eigenvalues'
    fdf_text = 'WriteEigenvalues'
    box = "Output options"
    optional = True
    priority = 210

class COOPWrite(fdf_options.BooleanLine):
    label = 'COOP wavefunctions (.WFSX)'
    fdf_text = 'COOP.Write'
    box = "Output options"
    optional = True
    priority = 220

class WriteWaveFunctions(fdf_options.BooleanLine):
    label = 'Wavefunctions'
    fdf_text = 'WriteWaveFunctions'
    box = "Output options"
    optional = True
    priority = 230
