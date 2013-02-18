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
        # reading calc if we have to
        if dtype is not None:
            self.dtype = dtype
            self.read(dtype, steps)

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
        self.evol = Evol.Evolution(outf.steps, outf.atoms, outf.vc, outf.aunit, outf.vcunit, {'spins':outf.spins})

    def readani(self, steps):
        'Reading calculation options and geometry from output files'
        anifn =  glob.glob(os.path.join(self.dir, '*.ANI'))
        anif = SIO.ANIFile(anifn[0], steps)
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
             
    def msd(self, atype = None):
        ''' Get MSD of evolution (type-wise)
        NB: As it uses only one cell vector set, when calculating MSD for NPT ensemble one should expect getting strange results. 
        In:
         -> atype (int?) - atomic type we need to calculate MSD for 
        '''
        title = ['T',]
        total_msd = []
#        self.opts[]
        if atype is None:
            types = self.evol[0].types['label']
            for ityp in types:
                n1 = self.evol[0].filter('label', ityp)
                title.append(ityp)
                t, msd = self.evol.msd(n = n1)
                total_msd.append(msd)
        return title, t, total_msd
    
    def vaf(self, atype = None):
        ''' Get VAF of evolution (type-wise)
        NB: As it uses only one cell vector set, when calculating VAF for NPT ensemble one should expect getting strange results. 
        In:
         -> atype (int?) - atomic type we need to calculate VAF for 
        '''
        title = ['T',]
        total_vaf = []
#        self.opts[]
        if atype is None:
            types = self.evol[0].types['label']
            for ityp in types:
                n1 = self.evol[0].filter('label', ityp)
                title.append(ityp)
                t, vaf = self.evol.vaf(n = n1)
                total_vaf.append(vaf)
        return title, t, total_vaf



    def dos(self, fname = ''):
        if not fname:
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

    def cn(self, dr = 0.2, atype = None, ratio = 0.7):
        ''' Get full and partial atomic coordination numbers (type-wise);
        also return nearest neighbors RDF (found using VP analysis)
        In:
         -> dr (float) - bin width, with which RDFVP is built
         -> atype (int?) - atomic type we need to calculate CNs for
        '''
        steps = len(self.evol.geom)
        n, typs, parts, typrdf, partrdf, pcn = self.evol.rdfvp(part = True, dr = dr, ratio = ratio)

        r_max = N.ceil(max([i for s in typrdf+partrdf for i in s])/dr) * dr
        nbins = r_max / dr
# make recarray out of data
        data = []
        names = []
        for it in range(len(typs)):           
            tr = typrdf[it]
            hist, bin_edges = N.histogram(N.array(tr), bins = nbins, range = (0., r_max))
            data.append((hist/(steps * len(n[it]) * dr))[1:])
            names.append(typs[it])

        for ip, pr in zip(parts,partrdf):
            n1 = len(n[typs.index(ip[0])])           
            hist, bin_edges = N.histogram(N.array(pr), bins = nbins, range = (0., r_max))
            data.append((hist/(steps * n1 * dr))[1:])
            names.append('-'.join(ip))
        
        names = ['R',] + names
        r = (bin_edges[:-1]+dr/2.)[1:]
        return (names, r, data), pcn                     

    def pcn_evolution(self, ratio = 0.7, part = True):
        title = ['step']
        data = []
        part_cn, typ_cn = self.evol.pcn_evolution(ratio, part)
        for typ in typ_cn.keys():
            title.append(typ)
            data.append(N.array(typ_cn[typ]))
        for part in part_cn.keys():
            title.append('-'.join(part))
            data.append(N.array(part_cn[part]))
        x = N.arange(len(data[0]))
        return (title, x, data), None
    
    def vp_facearea(self, da = 0.05, ratio = 0.7, part = True):
        'Returns partial face areas for calculations'
        typs, fa = self.evol.vp_facearea(ratio, part)
        a_max = N.ceil(max([i for typfa in fa for i in typfa])/da) * da
        nbins = a_max / da
# make recarray out of data
        data = []
        for typfa in fa:
            hist, bin_edges = N.histogram(N.array(typfa), bins = nbins, range = (0., a_max))
            data.append(hist[1:])

        names = ['area'] + typs
        area = (bin_edges[:-1]+da/2.)[1:]
        return (names, area, data), None                     
    
    def vp_totfacearea(self, da = 0.1, ratio = 0.7, part = True):
        'Returns total face areas for every VP'
        typs, tfa = self.evol.vp_totfacearea(ratio, part)
        ta_max = N.ceil(max([i for typfa in tfa for i in typfa])/da) * da
        ta_min = N.ceil(min([i for typfa in tfa for i in typfa])/da) * da
        nbins = (ta_max - ta_min) / da
# make recarray out of data
        data = []
        names = ['area'] + typs
        formats = ['f8']        
        for typfa in tfa:
            hist, bin_edges = N.histogram(N.array(typfa), bins = nbins, range = (ta_min, ta_max))
            data.append(hist[1:]/float(len(typfa)))
            formats.append('f8')
        data = [((bin_edges[:-1]+da/2.))[1:],] + data
        vp_fa = N.rec.fromarrays(data, formats = formats, names = names)
        return vp_fa
    
    def vp_totvolume(self, dv = 0.05, ratio = 0.7, part = True):
        'Returns total volume for every VP'
        typs, tv = self.evol.vp_totvolume(ratio, part)
        tv_max = N.ceil(max([i for typv in tv for i in typv])/dv) * dv
        tv_min = N.ceil(min([i for typv in tv for i in typv])/dv) * dv
        nbins = (tv_max - tv_min) / dv
# make recarray out of data
        data = []
        names = ['vol'] + typs
        formats = ['f8']        
        for typfa in tv:
            hist, bin_edges = N.histogram(N.array(typfa), bins = nbins, range = (tv_min, tv_max))
            data.append(hist[1:]/float(len(typfa)))
            formats.append('f8')
        data = [((bin_edges[:-1]+dv/2.))[1:],] + data
        vp_v = N.rec.fromarrays(data, formats = formats, names = names)
        return vp_v
    
    def vp_ksph(self, dk=0.01, ratio = 0.7, part = True):
        'Returns sphericity coefficient for every VP'
        typs, tk = self.evol.vp_ksph(ratio, part)
        tk_max = N.ceil(max([i for typk in tk for i in typk])/dk) * dk
        tk_min = N.ceil(min([i for typk in tk for i in typk])/dk) * dk
        nbins = (tk_max - tk_min) / dk
# make recarray out of data
        data = []
        names = ['ksph'] + typs
        formats = ['f8']        
        for typk in tk:
            hist, bin_edges = N.histogram(N.array(typk), bins = nbins, range = (tk_min, tk_max))
            data.append(hist[1:]/float(len(typk)))
            formats.append('f8')
        data = [((bin_edges[:-1]+dk/2.))[1:],] + data
        vp_k = N.rec.fromarrays(data, formats = formats, names = names)
        return vp_k

    def mmagmom(self):
        'Returns evolution of mean magnetic moment on atoms'
        typs, tmm = self.evol.mmagmom()
        data = [self.evol.steps,] + tmm
        names = ['step',] + typs
        formats = ['f8',] + ['f8' for _ in typs]
        mmm = N.rec.fromarrays(data, formats = formats, names = names)
        return mmm
        
    def mabsmagmom(self):
        'Returns evolution of mean magnetic moment on atoms'
        typs, tmm = self.evol.mmagmom(abs_mm = True)
        data = [self.evol.steps,] + tmm
        names = ['step',] + typs
        formats = ['f8',] + ['f8' for _ in typs]
        mmm = N.rec.fromarrays(data, formats = formats, names = names)
        return mmm

    def spinflips(self):
        'Returns the number of spin flips over time'
        typs, sf = self.evol.spinflips()
        data = [self.evol.steps,] + sf
        names = ['step',] + typs
        formats = ['f8',] + ['f8' for _ in typs]
        nsf = N.rec.fromarrays(data, formats = formats, names = names)
        return nsf
    
    def readmde(self):
        ' Reads information from MDE file'
        mdef = glob.glob(os.path.join(self.dir, '*.MDE'))
        if len(mdef) != 1:
            print 'Calc.ReadMDE: Either no or too many MDE files in %s' % (dir, )
            return -1
        mde = SIO.MDEFile(mdef[0])
        self.nsteps = mde.nsteps
        self.mdedata = mde.data
        return self.mdedata
    
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
    
    def __init__(self, dir, steps = None):
        self.dir = dir
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

