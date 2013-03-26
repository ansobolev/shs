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
    
    def rdfvp(self, part = True, dr = 0.2, ratio = 0.5):
        ''' Calc RDF for VP tesselation of the geometries, using geom's voronoi_np() method
        '''        

        nat = len(self.geom[0].atoms)
# full calculations         
        typs = ['Total']
        n = [range(nat)]
# partial calculations
        if part:
            typs = self.geom[0].types['label'].tolist()
# atomic numbers by type
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]            
        parts = list(itertools.product(typs, typs))
        
        typrdf = [[] for _ in typs]
        partrdf = [[] for _ in parts]
# accumulate ngbrs for further use (in partial_cn)
        tot_ngbrs = []
        
        for g in self.geom:
            if not hasattr(g, 'vp'):
                g.voronoi(ratio = ratio)
            ngbrs = g.vp.vp_neighbors(rm_small = True, eps = 0.2)
# all-to-all distance
            r = G.r(g.atoms['crd'], g.vc)
            r2 = ((r*r).sum(axis=1)**0.5).reshape(nat,nat)
# full calculations
            for it, typ in enumerate(typs): 
                for iat in n[it]:
                    r = r2[iat,ngbrs[iat]]
                    typrdf[it] += r.flatten().tolist()
        
# partial calculations
            for ip, part in enumerate(parts):
                n1 = typs.index(part[0])
                n2 = typs.index(part[1])
                for iat in n[n1]:
                    r = r2[iat, ngbrs[iat][N.in1d(ngbrs[iat],n[n2])]]
                    partrdf[ip] += r.flatten().tolist()
            tot_ngbrs.append(ngbrs)
        info = self.partial_cn(typs, parts, n, tot_ngbrs)
        return n, typs, parts, typrdf, partrdf, info
    
    def partial_cn(self, typs, parts, n, ngbrs, evol = False):
        ''' Returns partial coordination numbers based on Voronoi tesselation
        '''
# partial neighbors init
        png = [[] for _ in parts]
# full neighbors init
        fng = [[] for _ in typs]
# just in case we need time evolution: 
        if evol:
            png_evol = [[] for _ in parts]
            fng_evol = [[] for _ in typs]
        for ngbr in ngbrs:
# partial neighbors
            for ip, part in enumerate(parts):
                for iat in n[typs.index(part[0])]:
                    png[ip].append(len(N.nonzero(N.in1d(ngbr[iat], n[typs.index(part[1])]))[0]) - (part[0] == part[1]))
# full neighbors
            for it, _ in enumerate(typs):
                for iat in n[it]:
                    fng[it].append(len(ngbr[iat]) - 1)      
# time evolution
            if evol:
                for ip, pn in enumerate(png):
                    png_evol[ip].append(float(sum(pn))/len(pn))
                    png[ip] = []
                for it,fn in enumerate(fng):
                    fng_evol[it].append(float(sum(fn))/len(fn))
                    fng[it] = []
# returning two dicts - one with partial cns and one with full cns
        if evol:
            return dict(zip(parts, png_evol)), dict(zip(typs, fng_evol))
        return dict(zip(parts, [float(sum(pn))/len(pn) for pn in png]) + zip(typs, [float(sum(fn))/len(fn) for fn in fng]))

    def pcn_evolution(self, ratio, part):
        'Returns time evolution of partial coordination numbers'
        
        nat = len(self.geom[0].atoms)
# full calculations         
        typs = ['Total']
        n = [range(nat)]
# partial calculations
        if part:
            typs = self.geom[0].types['label'].tolist()
# atomic numbers by type
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]            
        parts = list(itertools.product(typs, typs))
        tot_ngbrs = []
        
        for g in self.geom:
            if not hasattr(g, 'vp'):
                g.voronoi(ratio = ratio)
            tot_ngbrs.append(g.vp.vp_neighbors())
        return self.partial_cn(typs, parts, n, tot_ngbrs, evol = True)
    
    def vp_facearea(self, ratio, part):
        'Returns a dictionary of {part: [areas]} for evolution to make a histogram'

        nat = len(self.geom[0].atoms)
# full calculations         
        typs = ['Total']
        n = [range(nat)]
# partial calculations
        if part:
            typs = self.geom[0].types['label'].tolist()
# atomic numbers by type, atoms do not change their type throughout calculation 
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]            
# results storage
        typ_fa = [[] for _ in typs]
                
        for g in self.geom:
            fa = g.voronoi_facearea(ratio = ratio, rm_small = True, eps = 0.5)
            for it, nt in enumerate(n):
                typ_fa[it] += [area for jnt in nt for area in fa[jnt].values()]
        return typs, typ_fa
        
    def vp_totfacearea(self, ratio, part):
        result = []
        for g in self.geom:
            result.append(g.vp_totfacearea(ratio = ratio))
        d = Data('per_atom', 'vp_totfacearea', y = result, y_label = 'Total')
        if part:
            typs = self.geom[0].types['label'].tolist()
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]            
            d.make_partial(dict(zip(typs, n)))
        return d
    
    def vp_totvolume(self, ratio, part):
        result = []
        for g in self.geom:
            result.append(g.vp_totvolume(ratio = ratio))
        d = Data('per_atom', 'vp_totvolume', y = result, y_label = 'Total')
        if part:
            typs = self.geom[0].types['label'].tolist()
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]            
            d.make_partial(dict(zip(typs, n)))
        return d

    def vp_ksph(self, ratio, part):
        result = []
        for g in self.geom:
            result.append(g.vp_ksph(ratio = ratio))
        d = Data('per_atom', 'vp_ksph', y = result, y_label = 'Total')
        if part:
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

    def mmagmom(self, abs_mm = False, part = True):
        assert self.has_fields('up', 'dn')
        result = []
        for g in self.geom:
            result.append(g.mmagmom(abs_mm))
        d = Data('per_atom', 'mmagmom', y = result, y_label = 'Total')
        if part:
            typs = self.geom[0].types['label'].tolist()
            n = [self.geom[0].filter('label',typ)[0] for typ in typs]            
            d.make_partial(dict(zip(typs, n)))
        return d
       
    def spinflips(self, part = True):
        'Get spin flips'
        assert self.has_fields('up', 'dn')
        prevmm = self.geom[0].mmagmom(abs_mm = False)
        result = [N.zeros(len(prevmm))]
        
        for g in self.geom[1:]:
            gmm = g.mmagmom(abs_mm = False)            
            result.append((prevmm * gmm) < 0)
            prevmm = gmm
        d = Data('per_atom', 'spinflips', y = result, y_label = 'Total')
        if part:
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
