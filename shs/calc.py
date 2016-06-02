#! /usr/bin/env python
# -*- coding : utf8 -*-

#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2011-2015
#


import os
import glob
import numpy as np

from calctypes import CalcType
from errors import FileError, UnsupportedError
from evolution import Evolution
from geom import Geom
from options import Options
from plot import plotmde
import sio
from data import Data
import vtkxml.xml_write as VTKxml


class Calc(object):
    """ Generic class for Siesta & TranSiesta calculations
    """
    def __init__(self, *args, **kwargs):
        pass

class SiestaCalc(Calc):
    """ Class for Siesta calculations
        Global variables:
            SC.keys : all possible FDF keys for the calculation options (dict)
            SC.geom : a calculation model geometry (Geom class)
            SC.opts : calculation options (dict with values as FDFTypes objects)
    """

    def __init__(self, calc_dir, calc_type=None, steps=None):
        """ Initialize a Siesta calculation
            :param calc_dir: calculation directory (relative or absolute)
            :param calc_type: calculation type (can be one of 'fdf', 'out' or 'ani')
            :param steps: time step number (or an iterable made of time step numbers).
            Negative numbers are also supported.
            :return: SiestaCalc instance
            """
        super(SiestaCalc, self).__init__()
        self.dir = calc_dir
        self.opts = Options({})
        self.geom = Geom()
        self.ctype = CalcType()
        self.data = {}
        if calc_type is not None:
            self.dtype = calc_type
            self.read(calc_type, steps)

    def __len__(self):
        """ The length of the calculation equals to the length of its evolution
        """
        if hasattr(self, 'evol'):
            return len(self.evol)
        else:
            return 1

# Read ---
    def read(self, calc_type, steps):
        """ Reading calculation options

        :param calc_type: calculation type (can be 'fdf', 'ani' or 'out')
        :param steps: number of steps needed
        """
        act = {'fdf': self.readfdf,
               'out': self.readout,
               'ani': self.readani
               }
        act.get(calc_type, self.readunsupported)(steps)
    
    def readfdf(self, steps):
        fdfnl = glob.glob(os.path.join(self.dir, '*.fdf'))
        if os.path.join(self.dir, 'CALC.fdf') in fdfnl:
            fdfn = os.path.join(self.dir, 'CALC.fdf')
        elif len(fdfnl) > 0:
            fdfn = fdfnl[0]
        else:
            raise FileError("Calc.ReadFDF: no fdf files in selected directory!")
        print 'Calc.ReadFDF: Took %s as a FDF file\n' % (fdfn, )
        fdff = sio.FDFFile(fdfn)
        # Reading calculation options (in blocks?) 
        self.opts = Options(fdff.d)

        # Taking from opts only those needed by Geom:
        self.geom.read('fdf', self.opts.divide(self.geom.fdf_options()))

        self.sl = self.opts['SystemLabel'].value
        # Reading calculation type
        ctype = self.opts['MD.TypeOfRun'].value
        self.ctype.read(self.opts.divide(self.ctype.fdf_options(ctype)))

    def readout(self, steps):
        'Reading calculation options and geometry from output files'
        outfns = '*.output'
        outf = sio.OUTFile(outfns, self.dir, steps)
        self.steps = outf.steps
        self.evol = Evolution(outf.steps, outf.atoms, outf.vc, outf.aunit, outf.vcunit, {'spins':outf.spins})

    def readani(self, steps):
        'Reading calculation options and geometry from output files'
        anifn = glob.glob(os.path.join(self.dir, '*.ANI'))
        anif = sio.ANIFile(anifn[0], steps)
        self.sl = anif.sl
        self.steps = anif.steps
        self.evol = Evolution(anif.steps, anif.atoms, anif.vc, anif.aunit, anif.vcunit)

    def readunsupported(self, steps):
        raise UnsupportedError('Reading calculation options is supported only from fdf or out file')

# Change ---

    def write(self, calcdir):
        import shutil
        if not os.path.isdir(calcdir):
            print 'SiestaCalc.Write: Creating calc directory %s' % (calcdir)
            os.makedirs(calcdir)
        fn = os.path.join(calcdir, 'CALC.fdf')
        self.opts.write(fn, includes = ['STRUCT.fdf', 'CTYPE.fdf'])
        self.geom.write(calcdir)
        self.ctype.write(calcdir)
        # Copying pseudos
        for atype in self.geom.types.labels:
            pseudo = atype + '.psf'
            shutil.copy(os.path.join(self.dir, pseudo), calcdir)

    def alter(self, altdata):
        self.opts.alter(altdata)

    # Get information ---
    def get_info(self, info_type):
        """ Gets information of desired type

        :param info_type:
        :return:
        """

    def get_data(self, data_type):
        """ Returns data of desired type

        :param data_type:
        :return:
        """
        DataClass = Data().get_type_by_name(data_type)
        self.data[data_type] = DataClass(self)


    def animate(self):
        def sign(x):
            return 1 if x >= 0 else -1
        
        pvpath = os.path.join(self.dir, 'pview')
        os.mkdir(pvpath)
        vtk_writer = VTKxml.VTK_XML_Serial_Unstructured()
        for step, geom in self.evol:
            spins = geom.atoms['up'] - geom.atoms['dn']
#            colors = geom.atoms['itype']
            colors = [sign(spins[i]) if typ == 2 else 0 for (i, typ) in enumerate(geom.atoms['itype'])]
            vtk_writer.snapshot(os.path.join(pvpath, "%i.vtu" % (step,)), geom.atoms['crd'], colors = colors,\
                                spins = spins)
        vtk_writer.writePVD(os.path.join(pvpath, "SL.pvd"))
    

# Dealing with LAMMPS dumps for sas
class LammpsCalc(Calc):
    ''' Class for Lammps calculations
        Global variables:
            SC.geom : a calculation model geometry (Geom class)
    '''

    def __init__(self, calc_dir, steps = None):
        self.dir = calc_dir
        # Default geom
        self.geom = Geom()

        # reading calc
        self.read(steps)

# Read ---
    def read(self, steps):
        ''' Reading model
        Input:
          -> steps - number of steps needed 
        '''
        lmpfn =  glob.glob(os.path.join(self.dir, '*.lmp'))
        lmpf = sio.LMPFile(lmpfn[0])
        self.evol = Evolution(lmpf.steps, lmpf.atoms, lmpf.vc, lmpf.aunit, lmpf.vcunit)

# Get information ---
    def rdf(self, partial = True, n = None):
        ''' Get RDF of evolution
        In:
         -> partial (bool) - indicates whether we need partial RDF
         -> n (tuple of index lists or None) - if partial, then indicates which atoms we need to find geometry of 
        '''
        title = ['R',]
        total_rdf = []
# get r_max
        vc = np.diag(self.evol[0].vc)
        rmax = np.min(vc/1.6)
        if partial:
            if n is None:
# get the list of atom types (from the first geometry in evolution)
                types = self.evol[0].types['label']
                for i, ityp in enumerate(types):
                    for jtyp in types[i:]:
                        n1 = self.evol[0].filter('label', ityp)
                        n2 = self.evol[0].filter('label', jtyp)
                        title.append(ityp+'-'+jtyp)
                        r, rdf = self.evol.rdf(rmax = rmax, n = (n1,n2))
                        total_rdf.append(rdf)
        else:
            n = None
            title.append('Total RDF')
            r, rdf = self.evol.rdf(n)
            total_rdf.append(rdf)
        return title, r, total_rdf

