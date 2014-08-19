#! /usr/bin/env python
# -*- coding : utf-8 -*-

import errors as Err

# From Kittel: Introd. Solid State Physics, 7th ed. (1996)
# (c) Inelastica package
Rydberg2eV = 13.6058
#Ang2Bohr = 0.529177
#Bohr2Ang = 1/Ang2Bohr
amu2kg = 1.66053e-27
eV2Joule = 1.60219e-19
hbar2SI = 1.05459e-34

# Map atomnumbers into elemental labels
# (c) Inelastica package
PeriodicTable = {'H':1,1:'H','D':1001,1001:'D','He':2,2:'He','Li':3,3:'Li',
'Be':4,4:'Be','B':5,5:'B','C':6,6:'C','N':7,7:'N','O':8,8:'O','F':9,9:'F','Ne':10,10:'Ne',
'Na':11,11:'Na','Mg':12,12:'Mg','Al':13,13:'Al','Si':14,14:'Si','P':15,15:'P',
'S':16,16:'S','Cl':17,17:'Cl','Ar':18,18:'Ar','K':19,19:'K','Ca':20,20:'Ca',
'Sc':21,21:'Sc','Ti':22,22:'Ti','V':23,23:'V','Cr':24,24:'Cr','Mn':25,25:'Mn',
'Fe':26,26:'Fe','Co':27,27:'Co','Ni':28,28:'Ni','Cu':29,29:'Cu','Zn':30,30:'Zn',
'Ga':31,31:'Ga','Ge':32,32:'Ge','As':33,33:'As','Se':34,34:'Se','Br':35,35:'Br',
'Kr':36,36:'Kr','Rb':37,37:'Rb','Sr':38,38:'Sr','Y':39,39:'Y','Zr':40,40:'Zr',
'Nb':41,41:'Nb','Mo':42,42:'Mo','Tc':43,43:'Tc','Ru':44,44:'Ru','Rh':45,45:'Rh',
'Pd':46,46:'Pd','Ag':47,47:'Ag','Cd':48,48:'Cd','In':49,49:'In','Sn':50,50:'Sn',
'Sb':51,51:'Sb','Te':52,52:'Te','I':53,53:'I','Xe':54,54:'Xe','Cs':55,55:'Cs',
'Ba':56,56:'Ba','La':57,57:'La','Ce':58,58:'Ce','Pr':59,59:'Pr','Nd':60,60:'Nd',
'Pm':61,61:'Pm','Sm':62,62:'Sm','Eu':63,63:'Eu','Gd':64,64:'Gd','Tb':65,65:'Tb',
'Dy':66,66:'Dy','Ho':67,67:'Ho','Er':68,68:'Er','Tm':69,69:'Tm','Yb':70,70:'Yb',
'Lu':71,71:'Lu','Hf':72,72:'Hf','Ta':73,73:'Ta','W':74,74:'W','Re':75,75:'Re',
'Os':76,76:'Os','Ir':77,77:'Ir','Pt':78,78:'Pt','Au':79,79:'Au','Hg':80,80:'Hg',
'Tl':81,81:'Tl','Pb':82,82:'Pb','Bi':83,83:'Bi','Po':84,84:'Po','At':85,85:'At',
'Rn':86,86:'Rn','Fr':87,87:'Fr','Ra':88,88:'Ra','Ac':89,89:'Ac','Th':90,90:'Th',
'Pa':91,91:'Pa','U':92,92:'U','Np':93,93:'Np','Pu':94,94:'Pu','Am':95,95:'Am',
'Cm':96,96:'Cm','Bk':97,97:'Bk','Cf':98,98:'Cf','Es':99,99:'Es','Fm':100,100:'Fm',
'Md':101,101:'Md','No':102,102:'No'}

#list of available siesta options
opts = ['Atom-Setup-Only', 'Atom.Debug.KB.Generation', 'AtomCoorFormatOut', 'AtomicCoordinatesAndAtomicSpecies', 
        'AtomicCoordinatesFormat', 'BasisPressure', 'BornCharge', 'COOP.Write', 'ChangeKgridInMD', 
        'ChemicalSpeciesLabel', 'DM.AllowExtrapolation', 'DM.AllowReuse', 'DM.EnergyTolerance', 
        'DM.FIRE.Mixing', 'DM.FormattedFiles', 'DM.FormattedInput', 'DM.FormattedOutput', 
        'DM.HarrisTolerance', 'DM.InitSpinAF', 'DM.KickMixingWeight', 'DM.MixSCF1', 'DM.MixingWeight',
        'DM.NumberBroyden', 'DM.NumberKick', 'DM.NumberPulay', 'DM.OccupancyTolerance', 
        'DM.Pulay.Avoid.First.After.Kick', 'DM.PulayOnFile', 'DM.RequireEnergyConvergence', 
        'DM.RequireHarrisConvergence', 'DM.Tolerance', 'DM.UseSaveDM', 'Diag.AllInOne', 
        'Diag.DivideAndConquer', 'Diag.Memory', 'Diag.NoExpert', 'Diag.ParallelOverK', 
        'Diag.PreRotate', 'Diag.Use2D', 'DirectPhi', 'ElectronicTemperature', 'FilterCutoff', 
        'FilterTol', 'FixAuxiliaryCell', 'FixSpin', 'ForceAuxCell', 'Harris_functional', 'KB.Rmax',
        'LatticeConstant', 'LatticeVectors', 'LongOutput', 'MD.AnnealOption', 'MD.BulkModulus', 
        'MD.FCDispl', 'MD.FCfirst', 'MD.FClast', 'MD.FinalTimeStep', 'MD.FireQuench', 
        'MD.InitialTemperature', 'MD.InitialTimeStep', 'MD.LengthTimeStep', 'MD.MaxCGDispl', 
        'MD.MaxForceTol', 'MD.MaxStressTol', 'MD.NoseMass', 'MD.NumCGsteps', 'MD.ParrinelloRahmanMass', 
        'MD.Quench', 'MD.RelaxCellOnly', 'MD.RemoveIntraMolecularPressure', 'MD.TargetPressure', 
        'MD.TargetTemperature', 'MD.TauRelax', 'MD.TypeOfRun', 'MD.UseSaveXV', 'MD.UseSaveZM', 
        'MD.UseStructFile', 'MD.VariableCell', 'MM.Cutoff', 'MM.UnitsDistance', 'MM.UnitsEnergy', 
        'MaxBondDistance', 'MaxSCFIterations', 'MeshCutoff', 'MeshSubDivisions', 'MullikenInSCF', 
        'NaiveAuxiliaryCell', 'NeglNonOverlapInt', 'NetCharge', 'NonCollinearSpin', 'NumberOfAtoms', 
        'NumberOfEigenStates', 'NumberOfSpecies', 'ON.ChemicalPotential', 'ON.ChemicalPotentialOrder', 
        'ON.ChemicalPotentialRc', 'ON.ChemicalPotentialTemperature', 'ON.ChemicalPotentialUse', 
        'ON.MaxNumIter', 'ON.UseSaveLWF', 'ON.eta', 'ON.eta_alpha', 'ON.eta_beta', 'ON.etol', 
        'ON.functional', 'OccupationFunction', 'On.RcLWF', 'OpticalCalculation', 
        'Output-Structure-Only', 'PAO.Basis', 'PAO.BasisSize', 'PAO.BasisType', 'PAO.EnergyShift', 'PAO.Filter',
        'PAO.FixSplitTable', 'PAO.NewSplitCode', 'PAO.OldStylePolorbs', 'PAO.SoftDefault', 
        'PAO.SoftInnerRadius', 'PAO.SoftPotential', 'PAO.SplitNorm', 'PAO.SplitNormH', 
        'PAO.SplitTailNorm', 'PCC.Filter', 'PDOS.kgrid_cutoff', 'ProcessorGridX', 
        'ProcessorGridY', 'ProcessorGridZ', 'ProjectedDensityOfStates', 'RcSpatial', 'ReInitialiseDM',
        'ReparametrizePseudos', 'Restricted.Radial.Grid', 'Rmax.Radial.Grid', 'SCF.Read.Charge.NetCDF',
        'SCF.Read.Deformation.Charge.NetCDF', 'SCFMustConverge', 'SaveDeltaRho', 
        'SaveElectrostaticPotential', 'SaveHS', 'SaveInitialChargeDensity', 'SaveIonicCharge',
        'SaveNeutralAtomPotential', 'SaveRho', 'SaveTotalCharge', 'SaveTotalPotential', 
        'SingleExcitation', 'SlabDipoleCorrection', 'SolutionMethod', 'SpinPolarized', 'SystemLabel',
        'SystemName', 'UseNewDiagk', 'UseSaveData', 'UseStructFile', 'Vna.Filter', 'WFS.EnergyMax', 
        'WFS.EnergyMin', 'WarningMinimumAtomicDistance', 'Write.XML', 'WriteBands', 'WriteCoorCerius',
        'WriteCoorInitial', 'WriteCoorStep', 'WriteCoorXmol', 'WriteDM', 'WriteDM.History.NetCDF',
        'WriteDM.NetCDF', 'WriteDMHS.History.NetCDF', 'WriteDMHS.NetCDF', 'WriteDenchar', 
        'WriteEigenvalues', 'WriteForces', 'WriteIonPlotFiles', 'WriteKbands', 'WriteKpoints', 
        'WriteMDXmol', 'WriteMDhistory', 'WriteMullikenPop', 'WriteWaveDebug', 'WriteWaveFunctions', 
        'XML.AbortOnErrors', 'XML.AbortOnWarnings', 'XML.Write', 'ZM.CalcAllForces', 
        'ZM.ForceTolAngle', 'ZM.ForceTolLength', 'ZM.MaxDisplAngle', 'ZM.MaxDisplLength', 
        'ZM.UnitsAngle', 'ZM.UnitsLength', 'alloc_report_level', 'blocksize', 'fdf-debug', 
        'kgrid_cutoff', 'processorY', 'user-basis', 'user-basis-netcdf', 'xc.authors', 'xc.functional']


def Identity(alat):
    return 1.

def Ang2Bohr(alat):
    return 0.529177

def Bohr2Ang(alat):
    return 1/0.529177

def Unit2Alat(alat):
    return 1./alat
    
def Alat2Unit(alat):
    return alat
