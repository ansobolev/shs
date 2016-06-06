#! /usr/bin/env python
# -*- coding : utf8 -*-

#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2011-2015
#


import os
import glob
from calctypes import CalcType
from errors import FileError, UnsupportedError
from evolution import Evolution
from geom import Geom
from options import Options
import sio
from data import Data
from vtkxml.xml_write import VTK_XML_Serial_Unstructured


class Calc(object):
    """ Generic class for Siesta & TranSiesta calculations
    """
    def __init__(self, *args, **kwargs):
        pass


class SiestaCalc(Calc):
    """ Class for Siesta calculations
        Global variables:
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
        self.label = None
        self.dir = calc_dir
        self.opts = Options({})
        self.evol = None
        self.geom = Geom()
        self.calc_type = CalcType()
        self.data = {}
        self.steps = None
        if calc_type is not None:
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
        act = {'fdf': self.read_fdf,
               'out': self.read_out,
               'ani': self.read_ani
               }
        act.get(calc_type, self.read_unsupported)(steps)

    def read_fdf(self, _):
        fdf_name_list = glob.glob(os.path.join(self.dir, '*.fdf'))
        if os.path.join(self.dir, 'CALC.fdf') in fdf_name_list:
            fdf_name = os.path.join(self.dir, 'CALC.fdf')
        elif len(fdf_name_list) > 0:
            fdf_name = fdf_name_list[0]
        else:
            raise FileError("Calc.ReadFDF: no fdf files in selected directory!")
        print 'Calc.ReadFDF: Took %s as a FDF file\n' % (fdf_name, )
        fdf_file = sio.FDFFile(fdf_name)
        # Reading calculation options (in blocks?) 
        self.opts = Options(fdf_file.d)

        # Taking from opts only those needed by Geom:
        self.geom.read('fdf', self.opts.divide(self.geom.fdf_options()))

        self.label = self.opts['SystemLabel'].value
        # Reading calculation type
        ctype = self.opts['MD.TypeOfRun'].value
        self.calc_type.read(self.opts.divide(self.calc_type.fdf_options(ctype)))

    def read_out(self, steps):
        """
        Reading calculation options and geometry from output files
        :param steps:
        :return:
        """
        outfns = '*.output'
        outf = sio.OUTFile(outfns, self.dir, steps)
        self.steps = outf.steps
        self.evol = Evolution(outf.steps, outf.atoms, outf.vc, outf.aunit, outf.vcunit, {'spins': outf.spins})

    def read_ani(self, steps):
        """
        Reading calculation options and geometry from output files
        :param steps:
        :return:
        """
        anifn = glob.glob(os.path.join(self.dir, '*.ANI'))
        anif = sio.ANIFile(anifn[0], steps)
        self.label = anif.sl
        self.steps = anif.steps
        self.evol = Evolution(anif.steps, anif.atoms, anif.vc, anif.aunit, anif.vcunit)

    @staticmethod
    def read_unsupported(steps):
        raise UnsupportedError('Reading calculation options is supported only from fdf or out file')

# Change ---

    def write(self, calc_dir):
        import shutil
        if not os.path.isdir(calc_dir):
            print 'SiestaCalc.Write: Creating calc directory %s' % calc_dir
            os.makedirs(calc_dir)
        fn = os.path.join(calc_dir, 'CALC.fdf')
        self.opts.write(fn, includes=['STRUCT.fdf', 'CTYPE.fdf'])
        self.geom.write(calc_dir)
        self.calc_type.write(calc_dir)
        # Copying pseudos
        for atom_type in self.geom.types.labels:
            pseudo = atom_type + '.psf'
            shutil.copy(os.path.join(self.dir, pseudo), calc_dir)

    def alter(self, altdata):
        self.opts.alter(altdata)

    # Get information ---
    @staticmethod
    def get_info(info_type):
        """ Gets information of desired type

        :param info_type:
        :return:
        """
        pass

    def get_data(self, data_type):
        """ Returns data of desired type

        :param data_type:
        :return:
        """
        data_class = Data().get_type_by_name(data_type)
        self.data[data_type] = data_class(self)

    def animate(self):
        def sign(x):
            return 1 if x >= 0 else -1
        
        pvpath = os.path.join(self.dir, 'pview')
        os.mkdir(pvpath)
        vtk_writer = VTK_XML_Serial_Unstructured()
        for step, geom in self.evol:
            spins = geom.atoms['up'] - geom.atoms['dn']
#            colors = geom.atoms['itype']
            colors = [sign(spins[i]) if typ == 2 else 0 for (i, typ) in enumerate(geom.atoms['itype'])]
            vtk_writer.snapshot(os.path.join(pvpath, "%i.vtu" % (step,)), geom.atoms['crd'], colors=colors,
                                spins=spins)
        vtk_writer.writePVD(os.path.join(pvpath, "SL.pvd"))
    

# Dealing with LAMMPS dumps for sas
class LAMMPSCalc(Calc):
    """ Class for Lammps calculations
        Global variables:
            SC.geom : a calculation model geometry (Geom class)
    """

    def __init__(self, calc_dir, steps=None, *args, **kwargs):
        super(LAMMPSCalc, self).__init__(*args, **kwargs)
        self.dir = calc_dir
        self.evol = None
        # Default geom
        self.geom = Geom()
        # reading calc
        self.read(steps)

# Read ---
    def read(self, _):
        """ Reading model
        Input:
          -> steps - number of steps needed
        """
        lmp_file_name = glob.glob(os.path.join(self.dir, '*.lmp'))
        lmp_file = sio.LMPFile(lmp_file_name[0])
        self.evol = Evolution(lmp_file.steps, lmp_file.atoms, lmp_file.vc, lmp_file.aunit, lmp_file.vcunit)
