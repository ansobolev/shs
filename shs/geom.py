#! /usr/bin/env python
# -*- coding : utf-8 -*-

import os
import glob
import random
import numpy as np
import numpy.ma as ma

import const
import errors
from .files.xv import XVFile
import options
from atomtype import AtomType

from voronoi import dump
import voronoi.numpy.ngbr as NN
# import first pyvoro:
try:
    import voronoi.pyvoro.voronoi as vn
    print 'Imported pyvoro module!'
except ImportError:
    import voronoi.numpy.voronoi as vn
    print 'Failure finding pyvoro module, resorting to scipy.spatial.Delaunay'


class Geom(object):
    """ Class for storing model geometry, model in Voronoi calc
        Can be read from : 
          -- FDF (done)
          -- XV (done)
          -- SPH (integrated RHO)
          -- ANI (done)
          -- output (almost done)
    """
    keys = {'NumberOfSpecies': ['n', None],
            'NumberOfAtoms': ['n', None],
            'ChemicalSpeciesLabel': ['b', None],
            'LatticeConstant': ['m', None],
            'LatticeVectors': ['b', None],
            'AtomicCoordinatesFormat': ['s', None],
            # 'AtomicCoordinatesFormatOut': ['s', None],
            'AtomicCoordinatesAndAtomicSpecies': ['b', None]}

    def __init__(self, calc_type=None, data=None):
        """ Initializing geometry
        """
        self.alat = 1.
        self.unit = 'Ang'
        self.vc = np.array([[1., 0., 0.], 
                           [0., 1., 0.],
                           [0., 0., 1.]])
        self.atoms = None
        self.names = None
        self.types = None
        self.opts = None
        self.vp = None

        # self.kwds = {'common': {'pbc': True,
        #                         'ratio': 0.5,
        #                         'rm_small': True,
        #                         'eps': 0.5
        #                         },
        #              'absmagmom': {'abs_mm': True},
        #              'magmom': {'abs_mm': False},
        #              }
        # reading if we need to
        if calc_type is not None:
            self.read(calc_type, data)
        
    # Reading ---
        
    def read(self, calc_type, data):
        """ Reading geometry from several types of input

        :param calc_type: calculation type (can be 'fdf', 'es', 'xv')
        :param data - data of requested type
        :param data: FDF dictionary
        :type data: dict or EvolStep - evolution step class

        """
        act = {'fdf': self.fdf2geom,
               'es': self.es2geom,
               'xv': self.xv2geom
               }
        # as usual, switch triggering
        act.get(calc_type, self.unsupported2geom)(data)
        # adjusting coordinates to cell
        self.to_cell()
        # # update props with distances to group
        # labels = self.names['label']
        # for label in labels:
        #     at = self.filter('label', lambda x: x == label)
        #     self.props['distance_' + label] = self.distance_to_group
        #     self.kwds['distance_' + label] = {'group': at}
        # get atomType
        self.types = AtomType(self)

    # def get_prop_names(self):
    #     return sorted(self.props.keys())

    def fdf2geom(self, data):
        """ Geometry init from options data
        """
        self.opts = data
        # TODO: there may be no LatticeConstant and LatticeVectors!
        self.alat = self.opts['LatticeConstant'].value
        self.unit = self.opts['LatticeConstant'].unit
        try:
            self.vc = np.array(self.opts['LatticeVectors'].value).astype(float) * self.alat
        except (KeyError,):
            self.vc = np.eye(3, dtype='f4') * self.alat
        self.names = np.rec.fromarrays(np.transpose(self.opts['ChemicalSpeciesLabel'].value),
                                       names='i,z,label',
                                       formats='|i1,|i2,|S2'
                                       )
        acas = np.array(self.opts['AtomicCoordinatesAndAtomicSpecies'].value)
        crd = acas[:, 0:3]
        typ = acas[:, 3]
        i_sorted = np.argsort(self.names['i'])
        typ_pos = np.searchsorted(self.names['i'][i_sorted], typ)
        labels = self.names['label'][typ_pos]
        self.atoms = np.rec.fromarrays([crd, typ, labels], names='crd, itype, label', formats='|3f8,|i2,|S2')
        # converting crd array to self.alat units
        # crd units dictionary
        cud = {'Ang': 'Ang',
               'Bohr': 'Bohr',
               'NotScaledCartesianAng': 'Ang',
               'NotScaledCartesianBohr': 'Bohr',
               'ScaledCartesian': 'scale'}
        # crd units
        cu = cud[self.opts['AtomicCoordinatesFormat'].value]
        self.atoms['crd'] = convert(self.atoms['crd'], alat=self.alat, inunit=cu, outunit=self.unit)

    def es2geom(self, data):
        """ initialize geom from EvolStep instance
        """
        # alat = 1 unit of crd
        self.alat = 1.
        self.unit = data.aunit
        # atoms array is in data
        self.atoms = data.atoms
        # vc - convert from vcunit to aunit
        self.vc = convert(data.vc, inunit=data.vcunit, outunit=data.aunit)
        # now get types
        ilabel, ind = np.unique(data.atoms['label'], return_index=True)
        iz = np.array([const.PeriodicTable[l] for l in ilabel])
        try:
            ityp = data.atoms['itype'][ind]
        except ValueError:
            ityp = np.arange(len(iz)) + 1    
        ilabel = np.array([const.PeriodicTable[z] for z in iz])
        self.names = np.rec.fromarrays([ityp, iz, ilabel], names='i,z,label', formats='|i1,|i2,|S2')
        if isinstance(data.data, dict):
            for name, field in data.data.iteritems():
                self.add_fields(name, field)

    def xv2geom(self, calc_dir):
        """ Reads geometry from XV file

         :param calc_dir: directory where XV file is located
        If no or many XV files in directory, readxv returns -1

        """
        # alat = 1. Bohr, because later we read absolute coordinates of lattice vectors in Bohr
        self.alat = 1.
        self.unit = 'Bohr'
        xv = XVFile(calc_dir)
        self.vc = np.array(xv.vectors)
        # get atomic positions (in Bohr, I assume)
        self.atoms = np.rec.fromarrays([xv.crd, xv.velocities, xv.i_type], names='crd,v,itype', formats='|3f8,|3f8,|i2')
        # now get types
        ityp, ind = np.unique(np.array(xv.i_type), return_index=True)
        iz = np.array(xv.z)[ind]
        ilabel = np.array([const.PeriodicTable[z] for z in iz])
        self.names = np.rec.fromarrays([ityp, iz, ilabel], names='i,z,label', formats='|i1,|i2,|S2')

    def unsupported2geom(self, data):
        """ Raise exception when one wants to read geometry from strange place
        """
        raise errors.UnsupportedError('Now Geom instance supports reading only from fdf, evolstep (es) and xv file')

    def update_with_types(self, types):
        self.types.removeTypes()
        for (typename, condition) in types.iteritems():
            self.types.addType(condition, typename)
        self.types.finalize()

    # Auxiliary routines ---
    
    def fdf_options(self):
        """ Returns a set of fdf options needed for Geom
        """
        return self.keys.keys()
    
    def write(self, calc_dir):
        """ Writes geometry to STRUCT.fdf file

           :param calc_dir: directory where the file will be located
        """
        fn = os.path.join(calc_dir, 'STRUCT.fdf')
        self.opts.write(fn)

    def filter(self, name, f):
        """ Filters geometry atoms by field name & value
        """
        return np.where(f(self.atoms[name]))[0]
    
    def unique(self, name):
        """ Returns a list of unique properties of the model
        """
        return list(np.unique(self.atoms[name]))

    def to_cell(self):
        crd = self.atoms['crd']
        vc = self.vc
        # Get fractional coordinates
        vc_inv = np.linalg.inv(vc)
        crd_vc = np.dot(crd, vc_inv)
        # Fractional coordinates - to cell
        crd_vc -= np.floor(crd_vc)
        crd = np.dot(crd_vc, vc)
        self.atoms['crd'] = crd
        
    # End Auxiliary routines ---

    def distance_to_group(self, **kwds):
        """ Finds distance to the nearest of the atoms belonging to group
        In:
         -> group (list of indexes) - list of atom indexes
        """
        # taking necessary keywords from kwds
        group = kwds['group']
        ngroup = len(group)
        nat = len(self.atoms)
        rij = r(self.atoms['crd'], self.vc, n=(group, range(nat)))
        dist = np.sqrt((rij**2.0).sum(axis=1))
        dist = np.min(dist.reshape(ngroup, nat), axis=0)
        return dist

    # Voronoi tesselation routines ---
    def voronoi(self, pbc, ratio):
        """ Get Voronoi tesselation based on the libraries available:
         -> numpy: QHull library
         -> pyvoro: Python interface to Voro++ library (~30 times faster than Numpy)

        Input:
         -> pbc - whether to use periodic boundary conditions

        """
        vd = dump.dump_shs()
        d = vd.shs_geom(self)
        self.vp = vn.model_voronoi(d)
        self.vp.voronoi(pbc, ratio)

    
    def voronoi_med(self):
        """ Get voronoi tesselation of geometry by pure python Medvedev algorithm
        """
        vd = dump.dump_shs()
        d = vd.shs_geom(self)
        ngbr = NN.model_ngbr(d)
        ngbr.make_ngbr()
        mv = ngbr.toMV()
        mv.make_voronoi(1)
        sq, vol, k_sph, pl_mv = mv.get_voronoi_param()
        self.add_fields('sq', np.array(sq))
        self.add_fields('vol', np.array(vol))
        self.add_fields('k_sph', np.array(k_sph))
        self.nb = pl_mv

    def label(self, **kwds):
        return self.atoms['label']

    def vp_neighbors(self, **kwds):
        """ Finds neighbors of VPs
        """
        # FIXME: Works only with pyvoro
        pbc = kwds.get('pbc', True)
        ratio = kwds.get('ratio', 0.5)
        if not hasattr(self,'vp'):
            self.voronoi(pbc, ratio)
        rm_small = kwds.get('rm_small', True)
        eps = kwds.get('eps', 0.05)
        return self.vp.vp_neighbors(rm_small, eps)
#        fa_np = self.vp_facearea(pbc, ratio, rm_small, eps)
        # If there is a face (with non-zero area) between atoms, then they are neighbors
#        fa_np[fa_np > 0] = 1.
#        return fa_np
    
    def vp_distance(self, pbc=True, ratio=0.5, rm_small=False, eps=0.5):
        """Finds distances between VP neighbors"""

        if self.vp is None:
            self.voronoi(pbc, ratio)
        f = self.vp.vp_faces()
        if rm_small:
            fa = self.vp.vp_face_area(f)
            f = self.vp.remove_small_faces(f, fa, eps)
        dist = self.vp.vp_distance(f)
        # here fa is the list of dictionaries, we make it a 2d numpy array
        # with masked values 
        # WARNING: O(nat^2 * nsteps) memory consumption!
        nat = len(dist)
        dist_np = np.zeros((nat, nat), dtype=np.float)
        for iat, ngbr in enumerate(dist):
            for jat, distance in ngbr.iteritems():
                dist_np[iat, jat] = distance
        dist_np = ma.masked_values(dist_np, 0.)
        return dist_np

    def add_fields(self, name, field):
        """ Add fields to self.atoms

        :param name: (str) name of field
        :param field: data to append. If ndarray, field is added with input name. If recarray,self.atoms is joined with
        field (thus preserving names from field recarray)
        :return:
        """
        import numpy.lib.recfunctions as nlrf
        fcn = field.__class__.__name__
        if fcn == 'ndarray':
            nlrf.append_fields(self.atoms, name, field, asrecarray=True, usemask=False)
        elif fcn == 'recarray':
            for name in field.dtype.names:
                # FIXME: very, very dirty hack!
                if name == 'forces':
                    self.forces = field[name]
                    continue
                self.atoms = nlrf.rec_append_fields(self.atoms, name, field[name])

        else:
            raise TypeError('Geom.add_fields: Only arrays or recarrays can be added to self.atoms as fields!')

    def has_fields(self, *fields):
        """Returns True if fields are present in self.atoms.dtype.names"""
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
        """ Converts geometry (read from anywhere / altered) to the list of values
        """
        data = {'NumberOfSpecies': [1, str(len(self.names))],
                'NumberOfAtoms': [2, str(len(self.atoms))],
                'ChemicalSpeciesLabel': [3, ] + array2block(self.names),
                'LatticeConstant': [4, str(self.alat), self.unit],
                'LatticeVectors': [5, ] + array2block(self.vc),
                'AtomicCoordinatesFormat': [6, 'NotScaledCartesian'+self.unit],
                'AtomicCoordinatesAndAtomicSpecies': ([7, ] +
                                                      np.concatenate([self.atoms['crd'].T.astype('S20'),
                                                                      self.atoms['itype'][np.newaxis, :].astype('S2')
                                                                      ],
                                                                     axis=0).T.tolist())
                }
        print 'Geom.Geom2Opts : Geometry data -> Options'
        self.opts = options.Options(data)

    def initialize(self, lat_type, composition, scell_size, alat, alat_unit='Ang', Basis=None, dist_level=0.):
        """ Initializes geometry for CG run.
        Possible initialization sources:
         - distorted lattice (BCC, FCC, SC)

         :param lat_type: lattice type ('BCC', 'FCC', 'SC', 'OR' - orthorombic)
         :param composition: a dictionary of atomic types {'element' : concentration in fractions}
         :param alat: lattice constant for a cell in the supercell
         :param alat_unit: lattice constant unit ('Ang' or 'Bohr')
         -> SCellSize - supercell size ([3 integers], eg [2,2,2])
         -> DistLevel - distortion level (in % of lattice parameter, default = 0.)
        """

        print 'Geom.Initialize: Initializing geometry from %s lattice' % (lat_type, )
        self.alat = 1.
        self.unit = alat_unit
        if lat_type != 'OR':
            alat = [alat] * 3
        vc = np.array(scell_size) * np.array(alat)
        self.vc = np.diag(vc)
      
        crd = crd_list(lat_type, scell_size, alat, Basis, dist_level)
        nat = len(crd)
        if not (isinstance(composition, (dict, list))):
            raise errors.NotImplementedError('Geom.Initialize : Composition has to be a dict or a list!')
        if isinstance(composition, list):
            c = np.array(composition)
            ntyp = len(np.unique(c))
            i = np.arange(1, ntyp + 1)
            label = np.unique(c)
            z = np.array([const.PeriodicTable[l] for l in label])
            self.names = np.rec.fromarrays([i,z,label], names='i,z,label', formats='|i1,|i2,|S2')
            sc = scell_size[0] * scell_size[1] * scell_size[2]
            ityp = np.concatenate((c, ) * sc)
            self.atoms = np.rec.fromarrays([crd, ityp], names='crd,itype', formats='|3f8,|S2')
            return
        ntyp = len(composition.keys())
        i = np.arange(1, ntyp + 1)
        label = np.array(composition.keys())
        z = np.array([const.PeriodicTable.get(l, 0) for l in label])
        self.names = np.rec.fromarrays([i, z, label], names='i,z,label', formats='|i1,|i2,|S2')
# now calculate number of atoms of each type
# fractions
        f = np.array([composition[x] for x in self.names['label']])
# sum of fractions
        sf = sum(f)
        percask = f / float(sf) * 100.0
# number of atoms of each type = nat * fraction / sum of fractions
        na = (nat * f / float(sf)).round().astype(int)
        perc = na / float(nat) * 100.0
        
        if sum(na) != nat:
            raise errors.Error ('Can not determine the number of atoms of each type!')
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
        ityp = np.ones(nat)
# atomic index (for type)
        ai = 0        
        for i in range(1, ntyp + 1):
            ityp[res[ai:ai + na[i-1]]] = i
            ai += na[i-1]
        self.atoms = np.rec.fromarrays([crd, ityp], names='crd,itype', formats='|3f8,|i2')
        
# METHODS ---


def array2block(arr):
    """ Returns a list of strings from record array
    """
    l = []
    for r in arr:
        l.append([str(x) for x in r])
    return l


# TODO: get rid of all functions
def convert(crd, alat=None, inunit='Bohr', outunit='Ang'):
    """ Converts crd array from inunits to outunits

    :param crd: a matrix of coordinates
    :param alat: lattice constant
    :param inunit: Input units
    :param outunit: Output units
    :return:

    Units could be:
      -> 'Ang'   : Angstroms
      -> 'Bohr'  : Bohr radii
      -> 'scale' : alat units
    """
# conversion matrix
    if inunit != outunit:
        print 'Geom.Convert : Converting geometry coordinates' 
        print '               %s -> %s\n' % (inunit, outunit)
    convm = [[const.Identity, const.Bohr2Ang, const.Unit2Alat],
             [const.Ang2Bohr, const.Identity, const.Unit2Alat],
             [const.Alat2Unit, const.Alat2Unit, const.Identity]]
# units dictionary
    ud = {'Ang':   0,
          'Bohr':  1,
          'scale': 2}
    i = ud[inunit]
    o = ud[outunit]
# conversion factor
    cf = convm[i][o]
    return crd * cf(alat)


def basis(lattice):
    """ Returns basis atom coordinates according to given lattice
    """
    bas = {'BCC': [[0.,  0.,  0.],
                   [0.5, 0.5, 0.5]],
           'FCC': [[0.,  0.,  0.],
                   [0.5, 0.5, 0.],
                   [0.5, 0.,  0.5],
                   [0.,  0.5, 0.5]],
           'SC':  [[0.,  0.,  0.]]
           }
    try:
        return bas[lattice]
    except (KeyError,):
        raise NameError(lattice + " is not in the list of available lattice types")


def crd(a, p, b, d):
    """ Returns atomic coordinate using given alat, place, basis atom coordinate and
    maximum random distortion value
    In:
     -> a - lattice constant
     -> p - cell number in a supercell
     -> b - basis coordinate
     -> d - maximum random distortion (in fractions of lattice constant)
    Out:
     -> crd - an atomic coordinate (float)
    """
    return a*(p+b+random.uniform(-d,d))


def crd_list(lat, sc, alat, bas, dist):
    """ Creates a list of atomic coordinates in a given supercell in ScaledCartesian format
    In:
     -> lat - lattice type (bcc, fcc or sc)
     -> sc - supercell (list of 3 integers)
     -> alat - lattice constant (for a cell in the supercell)
     -> bas - lattice basis
     -> dist - random distortion of atoms in % of lattice parameter

    """
    if bas is None:
        bas = basis(lat)
    atoms = []
    for i in range(sc[0]):
        for j in range(sc[1]):
            for k in range(sc[2]):
                for b in bas:
                    at = [crd(alat[0], i, b[0], dist/100.),
                          crd(alat[1], j, b[1], dist/100.),
                          crd(alat[2], k, b[2], dist/100.)]
                    atoms.append(at)
    return atoms


def r(crd, vc, n=None):
    """ Find distances between atoms based on PBC in a supercell built on vc vectors
    In:
     -> crd - coordinates array
     -> vc - lattice vectors
     -> n - a tuple of 2 crd index lists (or None if we need to find all-to-all distances)
    """
    vc_inv = np.linalg.inv(vc)
    crd_vc = np.dot(crd, vc_inv)
    if n is None:
        crd1 = crd_vc
        crd2 = crd_vc
    else:
        if len(n) != 2:
            raise ValueError('N must be a tuple of 2 elements!')
        crd1 = crd_vc[n[0]]
        crd2 = crd_vc[n[1]]
    n1 = len(crd1)
    n2 = len(crd2)
    sij = crd1[:, None, ...]-crd2[None, ...]
# periodic boundary conditions
    sij[sij > 0.5] -= 1.0
    sij[sij < -0.5] += 1.0
#    print sij.shape
    sij = sij.reshape(n1*n2, 3)
    rij = np.dot(sij, vc)
    return rij
