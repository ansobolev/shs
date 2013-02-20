#! /usr/bin/env python
# -*- coding : utf-8 -*-

import os, glob, random
import numpy as N

import const as Const
import errors as Err
import options as Opts
import sio as SIO

import voronoi.dump as Dump
import voronoi.numpy.ngbr as NN



class Geom():
    ''' Class for storing model geometry, model in Voronoi calc  
        Can be read from : 
          -- FDF (done)
          -- XV (done)
          -- SPH (integrated RHO)
          -- ANI (done)
          -- output (almost done)
    ''' 
    keys = {'NumberOfSpecies' : ['n', None], 
            'NumberOfAtoms' : ['n', None],
            'ChemicalSpeciesLabel' : ['b', None],
            'LatticeConstant' : ['m', None],
            'LatticeVectors' : ['b', None],
            'AtomicCoordinatesFormat' : ['s', None],
            'AtomicCoordinatesFormatOut' : ['s', None],
            'AtomicCoordinatesAndAtomicSpecies' : ['b', None]}
    
# Init ---

    def __init__(self, dtype = None, data = None):
        ''' Initializing geometry
        '''
        self.alat = 1.        
        self.unit = 'Ang'
        self.vc = N.array([[1., 0., 0.], 
                           [0., 1., 0.],
                           [0., 0., 1.]])
        self.atoms = None
        self.types = None
        # reading if we need to
        if dtype is not None:
            self.read(dtype, data)

# Reading ---
        
    def read(self, dtype, data):
        ''' Reading geometry
        Input:
          -> dtype - data type (can be 'fdf', 'es', 'xv')
          -> data - data of requested type 
            - data (dict) - FDF dictionary
            - data (EvolStep) - Evolution step class

        '''
        act = {'fdf' : self.fdf2geom,
               'es': self.es2geom,
               'xv' : self.xv2geom
               }
# as usual, switch triggering
        act.get(dtype, self.unsupported2geom)(data)

    def fdf2geom(self, data):
        ''' Geometry init from options data
        '''
        self.opts = data
# TODO: there may be no LatticeConstant and LatticeVectors!
        self.alat = self.opts['LatticeConstant'].value
        self.unit = self.opts['LatticeConstant'].unit
        try:
            self.vc = N.array(self.opts['LatticeVectors'].value).astype(float) * self.alat
        except (KeyError,):
            self.vc = N.eye(3, dtype='f4') * self.alat
        self.types = N.rec.fromarrays(N.transpose(self.opts['ChemicalSpeciesLabel'].value), names = 'i,z,label', formats = '|i1,|i2,|S2')
        acas = N.array(self.opts['AtomicCoordinatesAndAtomicSpecies'].value)
        crd = acas[:,0:3]
        typ = acas[:,3]
        self.atoms = N.rec.fromarrays([crd, typ], names = 'crd,itype', formats = '|3f8,|i2')
# converting crd array to self.alat units
# crd units dictionary
        cud = {'Ang' : 'Ang',
               'Bohr' : 'Bohr',
               'NotScaledCartesianAng' : 'Ang',
               'NotScaledCartesianBohr' : 'Bohr',
               'ScaledCartesian' : 'scale'}
# crd units
        cu = cud[self.opts['AtomicCoordinatesFormat'].value]
        self.atoms['crd'] = convert(self.atoms['crd'], alat = self.alat, inunit = cu, outunit = self.unit)

    def es2geom(self, data):
        ''' initialize geom from EvolStep instance
        '''
# alat = 1 unit of crd
        self.alat = 1.
        self.unit = data.aunit
# atoms array is in data
        self.atoms = data.atoms
# vc - convert from vcunit to aunit
        self.vc = convert(data.vc, inunit=data.vcunit, outunit=data.aunit)
# now get types
        ilabel, ind = N.unique(data.atoms['label'], return_index = True)
        iz = N.array([Const.PeriodicTable[l] for l in ilabel])
        try:
            ityp = data.atoms['itype'][ind]
        except ValueError:
            ityp = N.arange(len(iz)) + 1    
        ilabel = N.array([Const.PeriodicTable[z] for z in iz])
        self.types = N.rec.fromarrays([ityp,iz,ilabel], names = 'i,z,label', formats = '|i1,|i2,|S2')
        if type(data.data) == type({}):
            for name, field in data.data.iteritems():
                self.add_fields(name, field)

    def xv2geom(self, cdir):
        ''' Read geometry from XV file 
        In:
          -> cdir - directory where XV file is located
          If no or many XV files in directory, readxv returns -1 

        '''
        xvf = glob.glob(os.path.join(cdir, '*.XV'))
        if len(xvf) != 1:
            print 'Geom.ReadXV: Either no or too many XV files in %s' % (dir, )
            return -1
# alat = 1. Bohr, because later we read absolute coordinates of lattice vectors in Bohr
        self.alat = 1.
        self.unit = 'Bohr'
        xv = SIO.XVFile(xvf[0])
        self.vc = N.array(xv.vc)
# get atomic positions (in Bohr, I assume)
        self.atoms = N.rec.fromarrays([xv.crd, xv.v, xv.ityp], names = 'crd,v,itype', formats = '|3f8,|3f8,|i2')
# now get types
        ityp, ind = N.unique(N.array(xv.ityp), return_index = True)
        iz = N.array(xv.z)[ind]
        ilabel = N.array([Const.PeriodicTable[z] for z in iz])
        self.types = N.rec.fromarrays([ityp,iz,ilabel], names = 'i,z,label', formats = '|i1,|i2,|S2')

    def unsupported2geom(self, data):
        ''' Raise exception when one wants to read geometry from strange place
        '''
        raise Err.UnsupportedError('Now Geom instance supports reading only from fdf, evolstep (es) and xv file')

# Auxiliary routines --- 
    
    def fdf_options(self):
        ''' Returns a set of fdf options needed for Geom
        '''
        return self.keys.keys()
    
    def write(self, calcdir):
        ''' Writes geometry to STRUCT.fdf file
        In:
          -> calcdir - directory where the file will be located 
        '''
        fn = os.path.join(calcdir, 'STRUCT.fdf')
        self.opts.write(fn)

    def filter(self, name, value, cmprsn = 'eq'):
        ''' Filters geometry atoms by field name & value 
        '''
# TODO: make filtering with other comparison operators
        return N.where(self.atoms[name] == value)
    
    def unique(self, name):
        ''' Returns a list of unique properties of the model 
        '''
        return list(N.unique(self.atoms[name]))


    def to_cell(self):
        crd = self.atoms['crd']
        vc = self.vc
# Get fractional coordinates
        vc_inv = N.linalg.inv(vc)
        crd_vc = N.dot(crd, vc_inv)
# Fractional coordinates - to cell
        crd_vc[crd_vc > 1.] -= 1.
        crd_vc[crd_vc < 1.] += 1.
        crd = N.dot(crd_vc, vc)
        self.atoms['crd'] = crd
        
# End Auxiliary routines --- 

    
    def distance_to_group(self, group):
        ''' Finds distance to the nearest of the atoms belonging to group
        In:
         -> group (list of indexes) - list of atom indexes
        '''
        ngroup = len(group)
        nat = len(self.atoms)
        rij = r(self.atoms['crd'], self.vc, n = (group, range(nat)))
        dist = N.sqrt((rij**2.0).sum(axis = 1)) 
        dist = N.min(dist.reshape(ngroup, nat), axis = 0)
        return dist

# Voronoi tesselation routines ---    
    def voronoi(self, pbc = True, ratio = 0.5):
        ''' Get Voronoi tesselation based on the libraries available:
         -> numpy: QHull library
         -> pyvoro: Python interface to Voro++ library (~3 times faster than Numpy)
        
        Input:
         -> pbc - whether to use periodic boundary conditions 

        '''
        # import first pyvoro:
        try:
            import voronoi.pyvoro.voronoi as VN            
            print 'Geom.Voronoi: Found pyvoro module!'
        except ImportError:
            import voronoi.numpy.voronoi as VN
            print 'Geom.Voronoi: Failure finding pyvoro module, resorting to scipy.spatial.Delaunay'

        vd = Dump.dump_shs()
        d = vd.shs_geom(self)
        self.vp = VN.model_voronoi(d)
        self.vp.voronoi(pbc, ratio)
    
    
    def voronoi_med(self):
        ''' Get voronoi tesselation of geometry by pure python Medvedev algorithm
        '''
        vd = Dump.dump_shs()
        d = vd.shs_geom(self)
        ngbr = NN.model_ngbr(d)
        ngbr.make_ngbr()
        mv = ngbr.toMV()
        mv.make_voronoi(1)
        sq, vol, k_sph, pl_mv = mv.get_voronoi_param()
        self.add_fields('sq', N.array(sq))
        self.add_fields('vol', N.array(vol))
        self.add_fields('k_sph', N.array(k_sph))
        self.nb = pl_mv

    def voronoi_params(self, pbc = True, ratio = 0.5):
        ''' Finds parameters of Voronoi tesselation (face areas, volumes of VPs etc)
        '''
        if not hasattr(self,'vp'): self.voronoi(pbc, ratio)
        vps = self.vp.separate_vp()
        for vp in vps:
            vp.remove_small_faces()
# TODO: incomplete function        
        
    def voronoi_facearea(self, pbc = True, ratio = 0.5, rm_small = True, eps = 0.5):
        ''' Finds face areas of Voronoi tesselation
        '''
        if not hasattr(self,'vp'): self.voronoi(pbc, ratio)
        f = self.vp.vp_faces()        
        if rm_small:
            fa = self.vp.vp_face_area(f)
            f = self.vp.remove_small_faces(f, fa, eps)
        fa = self.vp.vp_face_area(f)
        return fa
    
    def vp_totfacearea(self, pbc = True, ratio = 0.5):
        ''' Finds total face areas for resulting Voronoi polihedra 
        '''
        if not hasattr(self,'vp'): self.voronoi(pbc, ratio)
        if hasattr(self.vp, 'vp_area'): return self.vp.vp_area
        f = self.vp.vp_faces()        
        _, a = self.vp.vp_volumes(f, partial = False)
        return a

    def vp_totvolume(self, pbc = True, ratio = 0.5):
        ''' Finds total volumes for resulting Voronoi polihedra 
        '''
        if not hasattr(self,'vp'): self.voronoi(pbc, ratio)
        if hasattr(self.vp, 'vp_volume'): return self.vp.vp_volume
        f = self.vp.vp_faces()        
        v, _ = self.vp.vp_volumes(f, partial = False)
        return v

    def vp_ksph(self, pbc = True, ratio = 0.5):
        ''' Finds total volumes for resulting Voronoi polihedra 
        '''
        if not hasattr(self,'vp'): self.voronoi(pbc, ratio)
        if not hasattr(self.vp, 'vp_volume'): 
            f = self.vp.vp_faces()        
            v, a = self.vp.vp_volumes(f, partial = False)
        else:
            v = self.vp.vp_volume
            a = self.vp.vp_area
        ksph = 36. * N.pi * v * v / (a * a * a)
        return ksph

    def mmagmom(self, abs_mm):
        if abs_mm:
            return N.abs(self.atoms['up'] - self.atoms['dn'])
        else:
            return self.atoms['up'] - self.atoms['dn']
    
    def add_fields(self,name,field):
        ''' Add fields to self.atoms
        Input:
         -> name (str) - name of field
         -> field - data to append
          - field(ndarray) - field is added with input name
          - field (recarray) - self.atoms is joined with field (thus preserving names from field recarray)
        '''
        import numpy.lib.recfunctions  as nlrf
        fcn = field.__class__.__name__
        if fcn == 'ndarray':
            self.atoms = nlrf.append_fields(self.atoms, name, field, asrecarray=True, usemask=False)
        elif fcn == 'recarray':
            for name in field.dtype.names:
                self.atoms = nlrf.append_fields(self.atoms, name, field[name], asrecarray=True, usemask=False)
        else:
            raise TypeError ('Geom.add_fields: Only arrays or recarrays can be added to self.atoms as fields!')

    def has_fields(self, *fields):
        'Returns True if fields are present in self.atoms.dtype.names'
        return all([(f in self.atoms.dtype.names) for f in fields])

    def __getitem__(self, item):
        try:
            return self.atoms[item]
        except ValueError:
            if item == 'vc':
                return self.vc
            else:
                raise TypeError('Geom: Only int or string key is allowed')
        
        
    def geom2opts(self):
        ''' Converts geometry (read from anywhere / altered) to the list of values 
        '''
        data = {'NumberOfSpecies' : [1, str(len(self.types))], 
                'NumberOfAtoms' : [2, str(len(self.atoms))],
                'ChemicalSpeciesLabel' : [3, ] + array2block(self.types),
                'LatticeConstant' : [4, str(self.alat), self.unit],
                'LatticeVectors' : [5, ] + array2block(self.vc),
                'AtomicCoordinatesFormat' : [6, 'NotScaledCartesian'+self.unit],
                'AtomicCoordinatesAndAtomicSpecies' : [7, ] + N.concatenate([self.atoms['crd'].T.astype('S20'), self.atoms['itype'][N.newaxis,:].astype('S2')], axis = 0).T.tolist()
                }
        print 'Geom.Geom2Opts : Geometry data -> Options'
        self.opts = Opts.Options(data)


    def initialize(self, LatticeType, Composition, SCellSize, LatticeConstant, LCUnit = 'Ang', Basis = None, DistLevel = 0.):
        ''' Initializes geometry for CG run. 
        Possible initialization sources:
         - distorted lattice (BCC, FCC, SC)
        In:
         -> LatticeType - lattice type ('BCC', 'FCC', 'SC', 'OR' - orthorombic)
         -> LatticeConstant - lattice constant for a cell in the supercell
         -> LCUnit - lattice constant unit ('Ang' or 'Bohr')
         -> SCellSize - supercell size ([3 integers], eg [2,2,2])
         -> DistLevel - distortion level (in % of lattice parameter, default = 0.)
         -> Composition - a dictionary of atomic types {'element' : concentration in fractions}
        '''

        print 'Geom.Initialize: Initializing geometry from %s lattice' % (LatticeType, )
        self.alat = 1.
        self.unit = LCUnit
        if LatticeType != 'OR':
            LatticeConstant = [LatticeConstant] * 3
        vc = N.array(SCellSize) * N.array(LatticeConstant)
        self.vc = N.diag(vc)
      
        crd = crd_list(LatticeType,SCellSize,LatticeConstant,Basis,DistLevel)
        nat = len(crd)
        if not ((type(Composition) == type({})) or (type(Composition) == type([]))):
            raise Err.NotImplementedError('Geom.Initialize : Composition has to be a dict or a list!')
        if type(Composition) == type([]):
            c = N.array(Composition)
            ntyp = len(N.unique(c))
            i = N.arange(1, ntyp + 1)
            label = N.unique(c)
            z = N.array([Const.PeriodicTable[l] for l in label])
            self.types = N.rec.fromarrays([i,z,label], names = 'i,z,label', formats = '|i1,|i2,|S2')
            sc = SCellSize[0] * SCellSize[1] * SCellSize[2]
            ityp = N.concatenate((c, ) * sc)
            self.atoms = N.rec.fromarrays([crd, ityp], names = 'crd,itype', formats = '|3f8,|S2')
            return
        ntyp = len(Composition.keys())
        i = N.arange(1, ntyp + 1)
        label = N.array(Composition.keys())
        z = N.array([Const.PeriodicTable[l] for l in label])
        self.types = N.rec.fromarrays([i,z,label], names = 'i,z,label', formats = '|i1,|i2,|S2')            
# now calculate number of atoms of each type
# fractions
        f = N.array([Composition[x] for x in self.types['label']])
# sum of fractions
        sf = sum(f)
        percask = f / float(sf) * 100.0
# number of atoms of each type = nat * fraction / sum of fractions
        na = (nat * f / float(sf)).round().astype(int)
        perc = na / float(nat) * 100.0
        
        if sum(na) != nat:
            raise Err.Error ('Can not determine the number of atoms of each type!')
# print number of atoms of each type
        head = ['Label', 'Fract. asked', '% asked', 'Atoms', '%']
        head2 = [' --- ', ' ---------- ', ' ----- ', ' --- ', ' ----- ']
# head format string for printing        
        hf = '{0[0]:5}   {0[1]:12}   {0[2]:^9}   {0[3]:5}   {0[4]:^9} '
# data format string for printing
        df = '{0:^5}   {1:^12}   {2:^9.3f}   {3:^5}   {4:^9} '
        print hf.format(head)       
        print hf.format(head2)
        for i in range(ntyp):
            print df.format(label[i], f[i], percask[i], na[i], perc[i])
        print ''
        res = range(nat)
        random.shuffle(res)
        ityp = N.ones(nat)
# atomic index (for type)
        ai = 0        
        for i in range(1, ntyp + 1):
            ityp[res[ai:ai + na[i-1]]] = i
            ai += na[i-1]
        self.atoms = N.rec.fromarrays([crd, ityp], names = 'crd,itype', formats = '|3f8,|i2')
        
# METHODS ---
    
def array2block(arr):
    ''' Returns a list of strings from record array
    '''
    l = []
    for r in arr:
        l.append([str(x) for x in r])
    return l

# TODO: get rid of all functions
def convert(crd, alat = None, inunit = 'Bohr', outunit = 'Ang'):
    ''' Converts crd array from inunits to outunits
    Units could be:  
      -> 'Ang'   : Angstroms
      -> 'Bohr'  : Bohr radii
      -> 'scale' : alat units  
    '''
# conversion matrix
    if inunit != outunit:
        print 'Geom.Convert : Converting geometry coordinates' 
        print '               %s -> %s\n' % (inunit, outunit)
    convm = [[Const.Identity, Const.Bohr2Ang, Const.Unit2Alat],
             [Const.Ang2Bohr, Const.Identity, Const.Unit2Alat],
             [Const.Alat2Unit, Const.Alat2Unit, Const.Identity]]
# units dictionary
    ud = {'Ang'   : 0,
          'Bohr'  : 1,
          'scale' : 2}
    i = ud[inunit]
    o = ud[outunit]
# conversion factor
    cf = convm[i][o]
    return crd * cf(alat)

def basis(lattice):
    ''' Returns basis atom coordinates according to given lattice
    '''
    bas = {'BCC' : [[0.,0.,0.],[0.5,0.5,0.5]],
           'FCC' : [[0.,0.,0.],[0.5,0.5,0.],[0.5,0.,0.5],[0.,0.5,0.5]],
           'SC' :  [[0.,0.,0.]]}
    try:
        return bas[lattice]
    except (KeyError,):
        raise NameError, lattice + " is not in the list of available lattice types"        

def crd(a, p, b, d):
    ''' Returns atomic coordinate using given alat, place, basis atom coordinate and 
    maximum random distortion value
    In: 
     -> a - lattice constant
     -> p - cell number in a supercell
     -> b - basis coordinate
     -> d - maximum random distortion (in fractions of lattice constant)
    Out: 
     -> crd - an atomic coordinate (float)
    '''
    return a*(p+b+random.uniform(-d,d))

def crd_list(lat,sc,alat,bas,dist):
    ''' Creates a list of atomic coordinates in a given supercell in ScaledCartesian format
    In:
     -> lat - lattice type (bcc, fcc or sc)
     -> sc - supercell (list of 3 integers)
     -> alat - lattice constant (for a cell in the supercell)
     -> bas - lattice basis 
     -> dist - random distortion of atoms in % of lattice parameter

    '''
    if bas is None:
        bas = basis(lat)
    atoms = []
    for i in range(sc[0]):
        for j in range(sc[1]):
            for k in range(sc[2]):
                for b in bas:
                    at = [crd(alat[0],i,b[0],dist/100.),crd(alat[1],j,b[1],dist/100.),crd(alat[2],k,b[2],dist/100.)]
                    atoms.append(at)
    return atoms

def r(crd, vc, n = None):
    ''' Find distances between atoms based on PBC in a supercell built on vc vectors
    In:
     -> crd - coordinates array
     -> vc - lattice vectors
     -> n - a tuple of 2 crd index lists (or None if we need to find all-to-all distances) 
    ''' 
    vc_inv = N.linalg.inv(vc)
    crd_vc = N.dot(crd, vc_inv)
    if n is None:
        crd1 = crd_vc
        crd2 = crd_vc
    else:
        if len(n) != 2:
            raise ValueError ('N must be a tuple of 2 elements!')
        crd1 = crd_vc[n[0]]
        crd2 = crd_vc[n[1]]
    n1 = len(crd1)
    n2 = len(crd2)
    sij = crd1[:, None,...]-crd2[None,...]
# periodic boundary conditions
    sij[sij > 0.5] -= 1.0
    sij[sij < -0.5] += 1.0
#    print sij.shape
    sij = sij.reshape(n1*n2, 3)
    rij = N.dot(sij, vc)
    return rij
