# -*- coding: utf8 -*-

from collections import defaultdict
import numpy as N

import geom as G
from data_old import Data


''' Container for working with files in FDF, XV, MDE, OUT format
'''
class EvolStep():
    ''' One evolution step, data is a dictionary
    '''
    def __init__(self, atoms, vc, au, vcu, data):
        self.atoms = atoms
        self.vc = vc
        self.aunit = au
        self.vcunit = vcu
        self.data = data

class Evolution():
    ''' Works with a set of geometries; RDF, diffusion should be calculated here
    '''
    def __init__(self, steps, atoms, vc, au='Ang', vcu='Bohr', data=None):
# check length of each list, should be the same
        self.geom = []
        self.steps = steps
        ns = len(steps)
        if len(atoms) != ns or len(vc) != ns:
            raise ValueError('Evolution.__init__: Lists must have the same length!')
        for i, (at, ivc) in enumerate(zip(atoms,vc)):
            if data is not None:
                ds = datastep(data, i)
            else:
                ds = None
            es = EvolStep(at, ivc, au, vcu, ds)
            self.geom.append(G.Geom('es', es))
            
    def __getitem__(self, item):
        if type(item) == type(''):
            try:
                return [g.atoms[item] for g in self.geom]
            except ValueError:
                if item == 'vc':
                    return [g.vc for g in self.geom]
        elif type(item) == type(0):
            return self.geom[item]
        else:
            raise TypeError('Evolution: Only int or string key is allowed')
    
    def __iter__(self):
        for istep, igeom in zip(self.steps,self.geom):
            yield istep, igeom
    
    def __len__(self):
        return len(self.geom)
    
    def filter(self, name, f):
        ''' Filters evolution by field name & value
        '''
        return [g.filter(name, f) for g in self.geom]

    def trajectory(self):
        return N.array(self['crd']), N.array(self['vc'])
    
    def mean_distance(self, n):
        ''' Calculate mean distance between atoms with indexes in n
        '''
        coords, vc = self.trajectory()
        md = []
        for crd_step, vc_step in zip(coords, vc):
            rij = G.r(crd_step, vc_step, n = (n,n))
            dist = N.sqrt((rij**2.0).sum(axis = 1))
            nat = len(n[0])
            dist = dist.reshape(nat,nat)
            md.append(dist)
        return md

    def getPropNames(self):
        ''' Returns the list of names for per-atom atomic properties
        '''
        props = None
        for g in self.geom:
            if props is None:
                props = g.getPropNames()
            else:
                assert props == g.getPropNames()
        return props

# Functions dealing with types ---

    def updateWithTypes(self, types):
        ''' Updates geometries with given types
        '''
        for ig in range(len(self.geom)):
            self.geom[ig].updateWithTypes(types)

    def getAtomsByType(self):
        labels = []
        types = defaultdict(list)
        for g in self.geom:
            itype = g.types.toDict()
            labels.append(sorted(itype.keys()))
            for l, at in itype.iteritems():
                types[l].append(at)
        return labels, types

    def areTypesConsistent(self):
        """ Checks whether all atoms belong to the same type throughout the evol
        """
        labels, types = self.getAtomsByType()
        # check if labels are the same throughout evol
        if labels.count(labels[0]) != len(labels):
            return False
        # check if atoms belong to the same type
        for _, at in types.iteritems():
            try:
                np_at = N.array(at)
            except:
                # evolsteps contain different number of atoms of a type
                return False
            if not N.all(at == at[0]):
                return False
        return True

    def pcn_evolution(self, ratio, partial, **kwds):
        'Returns time evolution of partial coordination numbers'
        result = []
        for g in self.geom:
            result.append(g.vp_neighbors(ratio = ratio, rm_small = False, eps = 0.5))
        d = Data('hist', 'vp_pcn', y = result, y_label = 'Total')
        # partial calculations
        if partial:
            typs = self.geom[0].types['label'].tolist()
            # atomic numbers by type, atoms do not change their type throughout calculation 
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]           
            d.make_partial(dict(zip(typs, n)), pairwise = True)
        return d
  
    def vp_ti(self, ratio, part):
        nat = len(self.geom[0].atoms)
# full calculations         
        typs = ['Total']
        n = [range(nat)]
        if part:
            typs = self.geom[0].types['label'].tolist()
# atomic numbers by type, atoms do not change their type throughout calculation 
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]
# results storage
        typ_ti = [[] for _ in typs]

        for g in self.geom:
            ti = g.vp_ti(ratio = ratio)
            for it, nt in enumerate(n):
                typ_ti[it] += [ti[jnt] for jnt in nt]
        return typs, typ_ti

    def has_fields(self, *fields):
        'Returns True if all Geoms in  self.geom have these fields'
        return all([g.has_fields(*fields) for g in self.geom])
    
#  METHODS -----        
def datastep(data, step):
    ''' Data is a dictionary like {'key' : [list of values]}, len(list) = number of step
    '''
    dstep = {}
    for key, value in data.iteritems():
        dstep[key] = value[step]
    return dstep
