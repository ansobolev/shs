# -*- coding: utf8 -*-

""" Container for working with files in FDF, XV, MDE, OUT format
"""

from collections import defaultdict
import numpy as np

from geom import r, Geom

class EvolStep():
    """ One evolution step, data is a dictionary
    """
    def __init__(self, atoms, vc, au, vcu, data):
        self.atoms = atoms
        self.vc = vc
        self.aunit = au
        self.vcunit = vcu
        self.data = data


class Evolution():
    """ Works with a set of geometries; RDF, diffusion should be calculated here
    """
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
            self.geom.append(Geom('es', es))
            
    def __getitem__(self, item):
        if isinstance(item, str):
            try:
                return [g.atoms[item] for g in self.geom]
            except ValueError:
                if item == 'vc':
                    return [g.vc for g in self.geom]
        elif isinstance(item, int):
            return self.geom[item]
        else:
            raise TypeError('Evolution: Only int or string key is allowed')
    
    def __iter__(self):
        for istep, igeom in zip(self.steps,self.geom):
            yield istep, igeom
    
    def __len__(self):
        return len(self.geom)
    
    def filter(self, name, f):
        """ Filters evolution by field name & value
        """
        return [g.filter(name, f) for g in self.geom]

    def trajectory(self):
        return np.array(self['crd']), np.array(self['vc'])
    
    def mean_distance(self, n):
        ''' Calculate mean distance between atoms with indexes in n
        '''
        coords, vc = self.trajectory()
        md = []
        for crd_step, vc_step in zip(coords, vc):
            rij = r(crd_step, vc_step, n = (n,n))
            dist = np.sqrt((rij**2.0).sum(axis = 1))
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
                props = g.get_prop_names()
            else:
                assert props == g.get_prop_names()
        return props

# Functions dealing with types ---

    def updateWithTypes(self, types):
        ''' Updates geometries with given types
        '''
        for ig in range(len(self.geom)):
            self.geom[ig].update_with_types(types)

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
                np.array(at)
            except:
                # evolsteps contain different number of atoms of a type
                return False
            if not np.all(at == at[0]):
                return False
        return True
  
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
