#! /usr/bin/env python
# -*- coding : utf8 -*-


'Finds topological indices of Voronoi polihedra'

import os
import numpy as N

try:
    from shs.calc import SiestaCalc
except (ImportError,):
    from calc import SiestaCalc

def fill_c(vp):
    rFe = 1.4
    rC = 0.7
    
    colors = N.zeros(vp.nsimplex)
    colors[N.where(vp.vp_r < rFe + rC)] = -1
    rtmp = vp.vp_r[N.where(colors > -1)[0]]
    print rtmp
    print vp.dt_ngbrs[N.where(colors > -1)[0]]
    print vp.vp_verts[N.where(colors > -1)[0]]

def ti():
    from collections import defaultdict

#    calc_dir = os.getcwd()
    calc_dir = '../../test/lammps/NP'
    c = SiestaCalc(calc_dir, type = 'ani', steps = range(-100,0,5))
    ti = []
#    calc_dir = '../../test/lammps'
#    c = LammpsCalc(calc_dir)

# C atoms
    cats = c.evol[0].filter('label','C')
    ncats = len(cats[0]) 
    nsteps = 0
    for ist in range(len(c.evol.steps)):
        c.evol[ist].voronoi_np()
#        ti += c.evol[ist].vp.vp_topological_indices(atoms = cats[0])
        ti += c.evol[ist].voronoi_params()
        nsteps += 1
# Count number of VP occurrences    
    d = defaultdict(int)
    for elt in ti:
        d[tuple(elt)] += 1
# For the sake of beautiful output    
    l = defaultdict(list)
    for key in d.keys():
        l[sum(key)].append(key)
        
    return l, d   
 
if __name__== '__main__':
    l, d = ti()
    # Output to file    
    f= open('vt.dat', 'w')
    for s in sorted(l.keys()):
        for key in sorted(l[s]):
            f.write('%25s\t%6.2f\n' % (str(key), d[key] * 100. /(ncats * nsteps)))
        f.write('\n')
    f.close()
