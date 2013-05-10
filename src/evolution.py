#!/usr/bin/env python
# -*- coding : utf8 -*-

import itertools
import numpy as N

import geom as G
from data import Data


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
    
    def filter(self, name, value, cmprsn = 'eq'):
        ''' Filters evolution by field name & value
        '''
        return [g.filter(name, value, cmprsn) for g in self.geom]

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


    def rdf(self, n = None, rmax = 7., dr = 0.05):
        coords, vc = self.trajectory()
#        sij = coords[:,:,None,...] - coords[:,None,...]
# number of bins
        nbins = int((rmax-dr)/dr)
        nsteps = len(vc)
        dists = N.zeros(nbins)

        for crd_step, vc_step in zip(coords, vc):
# fractional coordinates
            if n is None:
                nat1 = len(crd_step)
                nat2 = len(crd_step)
            else:
                nat1 = len(n[0][0])
                nat2 = len(n[1][0])
            vol = N.linalg.det(vc_step)
            
            rij = G.r(crd_step, vc_step, n)
            dist = N.sqrt((rij**2.0).sum(axis = 1))
# found distances, now get histogram
            hist, r = N.histogram(dist, bins = nbins, range = (dr, rmax)) 
            dists += hist / (nat1 / vol * nat2) 
# find rdf
        rdf = dists / nsteps
# norm rdf
        r = (r+dr/2.)[:-1]        
        rdf = rdf / (4.*N.pi*(r**2.)*dr)
        return r, rdf

    def msd(self, n):
        ''' Calc mean square displacement (MSD) for the evolution
        In:
         -> n: a list of atoms for which to calculate MSD
        Out:
         -> t: a list of \Delta t differences (in steps)
         -> msd: a list of average MSDs for every \Delta t
        '''
        all_coords, _ = self.trajectory()
        coords = all_coords[:,n,:]
        traj_len = len(coords)
        t = N.arange(traj_len)
        msd = N.zeros(traj_len)
        num = N.zeros(traj_len, dtype = int)
        for delta_t in t:
            for t_beg in range(traj_len - delta_t):
                dx = coords[t_beg + delta_t] - coords[t_beg]
                dr = (dx**2.0).sum(axis = 2)
                num[delta_t] += len(dr.T)
                msd[delta_t] += N.sum(dr)
        msd = msd / num
        return t, msd
    
    def vaf(self, n):
        ''' Calc velocity autocorrelation function (VAF) for the evolution
        In:
         -> n: a list of atoms for which to calculate VAF
        Out:
         -> t: a list of \Delta t differences (in steps)
         -> vaf: a list of average VAFss for every \Delta t
        '''
        # taking coordinates of atoms belonging to the list n
        all_coords, _ = self.trajectory()
        coords = all_coords[:,n[0],:]
        # assuming dt = 1, dx - in distance units!
        v = coords[1:] - coords[:-1] 
        traj_len = len(v)
        # time (in step units!) 
        t = N.arange(traj_len)
        vaf = N.zeros(traj_len)
        num = N.zeros(traj_len, dtype = int)
        for delta_t in t:
            for t_beg in range(traj_len - delta_t):
                # correlation between v(t_beg) and v(t_beg + delta_t)
                v_cor = (v[t_beg] * v[t_beg + delta_t]).sum(axis = 1)
                num[delta_t] += len(v_cor.T)
                vaf[delta_t] += N.sum(v_cor)
        vaf = vaf / num
        return t, vaf
                
# Evolution VP methods --- 

    def rdfvp(self, ratio, partial, **kwds):
        result = []
        for g in self.geom:
            result.append(g.vp_distance(ratio = ratio, rm_small = False, eps = 0.5))
        d = Data('hist', 'rdfvp', y = result, y_label = 'Total')
        # partial calculations
        if partial:
            typs = self.geom[0].types['label'].tolist()
            # atomic numbers by type, atoms do not change their type throughout calculation 
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]           
            d.make_partial(dict(zip(typs, n)), pairwise = True)
        return d

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
    
    def vp_facearea(self, ratio, partial, **kwds):
        result = []
        for g in self.geom:
            result.append(g.vp_facearea(ratio = ratio, rm_small = True, eps = 0.5))
        d = Data('hist', 'vp_facearea', y = result, y_label = 'Total')
        # partial calculations
        if partial:
            typs = self.geom[0].types['label'].tolist()
            # atomic numbers by type, atoms do not change their type throughout calculation 
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]           
            d.make_partial(dict(zip(typs, n)), pairwise = True)
        return d
       
    def vp_totfacearea(self, ratio, partial, **kwds):
        result = []
        for g in self.geom:
            result.append(g.vp_totfacearea(ratio = ratio))
        d = Data('per_atom', 'vp_totfacearea', y = result, y_label = 'Total')
        if partial:
            typs = self.geom[0].types['label'].tolist()
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]            
            d.make_partial(dict(zip(typs, n)))
        return d
    
    def vp_totvolume(self, ratio, partial, **kwds):
        result = []
        for g in self.geom:
            result.append(g.vp_totvolume(ratio = ratio))
        d = Data('per_atom', 'vp_totvolume', y = result, y_label = 'Total')
        if partial:
            typs = self.geom[0].types['label'].tolist()
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]            
            d.make_partial(dict(zip(typs, n)))
        return d

    def vp_ksph(self, ratio, partial, **kwds):
        result = []
        for g in self.geom:
            result.append(g.vp_ksph(ratio = ratio))
        d = Data('per_atom', 'vp_ksph', y = result, y_label = 'Total')
        if partial:
            typs = self.geom[0].types['label'].tolist()
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]            
            d.make_partial(dict(zip(typs, n)))
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

    def mmagmom(self, ratio, partial, **kwds):
        abs_mm = kwds.pop('abs_mm', False)
        assert self.has_fields('up', 'dn')
        result = []
        for g in self.geom:
            result.append(g.mmagmom(abs_mm))
        d = Data('per_atom', 'mmagmom', y = result, y_label = 'Total')
        if partial:
            typs = self.geom[0].types['label'].tolist()
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]            
            d.make_partial(dict(zip(typs, n)))
        return d
       
    def spinflips(self, ratio, partial, **kwds):
        'Get spin flips'
        assert self.has_fields('up', 'dn')

        prevmm = self.geom[0].mmagmom(abs_mm = False)
        result = [N.zeros(len(prevmm))]
        for g in self.geom[1:]:
            gmm = g.mmagmom(abs_mm = False)            
            result.append((prevmm * gmm) < 0)
            prevmm = gmm
        d = Data('per_atom', 'spinflips', y = result, y_label = 'Total')
        if partial:
            typs = self.geom[0].types['label'].tolist()
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]            
            d.make_partial(dict(zip(typs, n)))
        return d

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
