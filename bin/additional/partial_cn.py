#! /usr/bin/env python
# -*- coding : utf8 -*-


import itertools
import numpy as np
#from shs.calc import SiestaCalc
from calc import SiestaCalc


oneline = 'Finds partial coordination numbers according to Voronoi analysis'

def pcns(evol = False): 
    dir = '../../test'
    c = SiestaCalc(dir, type = 'ani', steps = range(-201, -1, 5))
#    c = SiestaCalc(dir, type = 'ani', steps = [-1])
    typs = c.evol[0].unique('label')
    parts = list(itertools.product(typs, typs))
# partial neighbors init
    png = [[] for p in parts]
# full neighbors init
    fng = [[] for t in typs]
# just in case we need time evolution: 
    if evol:
        png_evol = [[] for p in parts]
        fng_evol = [[] for t in typs]        
        
# atomic numbers by type
    n = [c.evol[0].filter('label',typ)[0] for typ in typs]
    for istep, g in c.evol:
        g.voronoi_np()
# ngbrs - neighbors of all atoms 
        ngbrs = g.vp.vp_neighbors()
# partial neighbors
        for ip, part in enumerate(parts):
            for iat in n[typs.index(part[0])]:
                png[ip].append(len(np.nonzero(np.in1d(ngbrs[iat], n[typs.index(part[1])]))[0]) - (part[0] == part[1]))
# full neighbors
        for it, typ in enumerate(typs):
            for iat in n[it]:
                fng[it].append(len(ngbrs[iat]) - 1)      
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
    return dict(zip(parts, [float(sum(pn))/len(pn) for pn in png])), dict(zip(typs, [float(sum(fn))/len(fn) for fn in fng]))


if __name__== '__main__':
    pns, fns = pcns(evol = True)
    print pns
    print fns