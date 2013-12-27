#! /usr/bin/env python
# -*- coding : utf8 -*-

#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2011-2013
#


import os, glob
import numpy as N

import calctypes as CT
import errors as Err
import evolution as Evol
import geom as G
import options as Opts
import plot as Plot
import sio as SIO
import vtkxml.xml_write as VTKxml

class Calc():
    ''' Generic class for Siesta & TranSiesta calculations 
    '''
    pass

class SiestaCalc(Calc):
    ''' Class for Siesta calculations
        Global variables:
            SC.keys : all possible FDF keys for the calculation options (dict)
            SC.geom : a calculation model geometry (Geom class)
            SC.opts : calculation options (dict with values as FDFTypes objects)
    '''

    def __init__(self, cdir, dtype = None, steps = None):
        self.dir = cdir
        # Default calc
        self.opts = Opts.Options({})
        # Default geom
        self.geom = G.Geom()
        # Default calctype = None
        self.ctype = CT.CalcType()
        self.data = {}
        # reading calc if we have to
        if dtype is not None:
            self.dtype = dtype
            self.read(dtype, steps)

    def __len__(self):
        """ The length of the calculation equals the length of its evolution
        """
        if hasattr(self, 'evol'):
            return len(self.evol)
        else:
            return 1

# Read ---
    def read(self, dtype, steps):
        ''' Reading calculation options
        Input:
          -> dtype  - data type (can be 'fdf' or 'out')
          -> steps - number of steps needed 
        '''
        act = {'fdf' : self.readfdf,
               'out' : self.readout, 
               'ani' : self.readani
               }
        act.get(dtype, self.readunsupported)(steps)
    
    def readfdf(self, steps):
        fdfnl = glob.glob(os.path.join(self.dir, '*.fdf'))
        if os.path.join(self.dir, 'CALC.fdf') in fdfnl:
            fdfn = os.path.join(self.dir, 'CALC.fdf')
        else:
            fdfn = fdfnl[0]        
        print 'Calc.ReadFDF: Took %s as a FDF file\n' % (fdfn, )
        fdff = SIO.FDFFile(fdfn)
        # Reading calculation options (in blocks?) 
        self.opts = Opts.Options(fdff.d)

        # Taking from opts only those needed by Geom:
        self.geom.read('fdf', self.opts.divide(self.geom.fdf_options()))

        self.sl = self.opts['SystemLabel'].value
        # Reading calculation type
        ctype = self.opts['MD.TypeOfRun'].value
        self.ctype.read(self.opts.divide(self.ctype.fdf_options(ctype)))

    def readout(self, steps):
        'Reading calculation options and geometry from output files'
        outfns = '*.output'
        outf = SIO.OUTFile(outfns, self.dir, steps)
        self.steps = outf.steps
        self.evol = Evol.Evolution(outf.steps, outf.atoms, outf.vc, outf.aunit, outf.vcunit, {'spins':outf.spins})

    def readani(self, steps):
        'Reading calculation options and geometry from output files'
        anifn =  glob.glob(os.path.join(self.dir, '*.ANI'))
        anif = SIO.ANIFile(anifn[0], steps)
        self.sl = anif.sl
        self.steps = anif.steps
        self.evol = Evol.Evolution(anif.steps, anif.atoms, anif.vc, anif.aunit, anif.vcunit)

    def readunsupported(self, steps):
        raise Err.UnsupportedError('Reading calculation options is supported only from fdf or out file')

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
        for atype in self.geom.types['label']:
            pseudo = atype + '.psf'
            shutil.copy(os.path.join(self.dir,pseudo), calcdir)

    def alter(self, altdata):
        self.opts.alter(altdata)

# Get information ---
    def get_info(self, itype):
        ''' Returns information of desired type
        '''

# TODO: get data with data object
    def get_data(self, dtype):
        ''' Returns data of desired type
        '''
      
    def mde(self):
        ' Reads information from MDE file'
        mdef = glob.glob(os.path.join(self.dir, '*.MDE'))
        if len(mdef) != 1:
            print 'Calc.ReadMDE: Either no or too many MDE files in %s' % (dir, )
            return -1
        mde = SIO.MDEFile(mdef[0])
        self.nsteps = mde.nsteps
        return mde.data
           
    def dos(self):
        if os.path.isfile(os.path.join(self.dir, 'pdos.xml')):
            fname = os.path.join(self.dir, 'pdos.xml')
        elif os.path.isfile(os.path.join(self.dir, self.sl + '.PDOS')):
            fname = os.path.join(self.dir, self.sl + '.PDOS')
        else:
            raise Exception('No possible DOS files found!')
        print 'calc.DOS : Took %s as DOS file' % (fname, )                
        dom = SIO.ReadPDOSFile(fname)
        nspin = SIO.GetPDOSnspin(dom)
        ev = SIO.GetPDOSenergyValues(dom)
        names = ['energy']
        data = []
        raw_names, raw_data = SIO.GetPDOSfromOrbitals(dom,species = [],ldict = {})
        if nspin == 2:
            for n, d in zip(raw_names, raw_data):
                names.append(n + '_up')
                data.append(d[::2])
                names.append(n + '_dn')
                data.append(-1.0 * d[1::2])
        elif nspin == 1:
            names += raw_names
            data += raw_data
        return (names, ev, data), {'nspin': nspin}
 
    def vp_ti(self, ratio = 0.7, part = True):
        'Returns topological indices for VPs'
        from collections import defaultdict
        typs, ti = self.evol.vp_ti(ratio, part)
        names = ['TI'] + typs

        d = [defaultdict(int) for _ in typs]
        for ityp in range(len(typs)):
            # Count number of VP occurrences    
            for elt in ti[ityp]:
                d[ityp][tuple(elt)] += 1
        return names, d 
    
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
    
    def plotmde(self,cols):
        ''' Plots information found in MDE file.
        Input:
         -> cols (list) : a list of columns to be plotted
        '''
        if 'step' not in cols:
            cols = ['step', ] + cols
        Plot.plotmde(self.mdedata[cols])

# Dealing with LAMMPS dumps for sas
class LammpsCalc(Calc):
    ''' Class for Lammps calculations
        Global variables:
            SC.geom : a calculation model geometry (Geom class)
    '''

    def __init__(self, calc_dir, steps = None):
        self.dir = calc_dir
        # Default geom
        self.geom = G.Geom()

        # reading calc
        self.read(steps)

# Read ---
    def read(self, steps):
        ''' Reading model
        Input:
          -> steps - number of steps needed 
        '''
        lmpfn =  glob.glob(os.path.join(self.dir, '*.lmp'))
        lmpf = SIO.LMPFile(lmpfn[0])
        self.evol = Evol.Evolution(lmpf.steps, lmpf.atoms, lmpf.vc, lmpf.aunit, lmpf.vcunit)        

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
        vc = N.diag(self.evol[0].vc)
        rmax = N.min(vc/1.6)
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

