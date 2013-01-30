#! /usr/bin/env python
# -*- coding : utf8 -*-


'Plots topological indices of Voronoi polihedra'

import os
import numpy as N

try:
    from shs.calc import SiestaCalc
except (ImportError,):
    from calc import SiestaCalc

def ti():

    calc_dir = '../../test'
    c = SiestaCalc(calc_dir, type = 'ani', steps = [-1,])

# C atoms
    cats = c.evol[0].filter('label','C')
    ncats = len(cats[0]) 
    nsteps = 0
    for ist in range(len(c.evol.steps)):
        c.evol[ist].voronoi_np()
        ti = c.evol[ist].vp.vp_topological_indices(atoms = cats[0])
        for iat, iti in enumerate(ti):
            if tuple(iti) == (0,3,6):
                print cats[0][iat], 'good!'
                c.evol[ist].vp.plot_vp(cats[0][iat])


if __name__== '__main__':
    ti()
      