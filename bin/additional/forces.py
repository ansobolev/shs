#!/usr/bin/env python
# -*- coding : utf-8 -*-

#
#   This file is part of the Siesta help scripts 
#
#   (c) Andrey Sobolev, 2013
#
import numpy as np
import matplotlib.pyplot as plt
from shs.calc import SiestaCalc

if __name__== '__main__':
    calc_dir = '../../examples/FeCANI'
    crd = []
    forces = [] 
    nsteps_beg = 1400
    nsteps_end = 0
    sc = SiestaCalc(calc_dir, dtype='out', steps = range(-nsteps_beg,-nsteps_end,1))
    n = sc.evol[0].filter('label',lambda x: x == 'C')
    for step, g in sc.evol:
        crd.append(g.atoms['crd'][n])
        forces.append(g.forces[n])
    crd = np.array(crd)
    forces = np.array(forces)
    r = crd[:, 1] - crd[:, 0]
    r_mod = np.sum(r * r, axis = 1) ** 0.5
    # indices
    r_near_ind = np.where(r_mod < 3.34)[0]
    r_far_ind = np.where(r_mod > 3.42)[0]
    # force module
    f_mod = np.sum(forces * forces, axis = 2) ** 0.5
#    cos_f1 = np.sum(r * forces[:,0], axis = 1) / r_mod / f_mod[:,0] 
#    cos_f2 = np.sum(r * forces[:,1], axis = 1) / r_mod / f_mod[:,1] 
    # projections
    f1_r = (np.sum(forces[:,0] * r, axis = 1) / np.sum(r * r, axis = 1))[:, np.newaxis] * r
    f1_r_mod = np.sum(f1_r * f1_r, axis = 1) ** 0.5
    f2_r = (np.sum(forces[:,1] * r, axis = 1) / np.sum(r * r, axis = 1))[:, np.newaxis] * r
    f2_r_mod = np.sum(f2_r * f2_r, axis = 1) ** 0.5
    # linear approximation   
    
#    poly = np.polyfit(r_mod, f2_r_mod, 2)
#    poly = np.polyfit(r_mod[r_near_ind], f2_r_mod[r_near_ind], 1)
    poly = np.polyfit(r_mod[r_far_ind], f2_r_mod[r_far_ind], 1)

    print poly
    p = np.poly1d(poly)
    steps = np.arange(-nsteps_beg, -nsteps_end)
    xp = np.linspace(3.1, 3.6, 300)

#    print np.min(p(xp)), (p - np.poly1d(np.min(p(xp)))).r

#    plt.plot(steps, r_mod)
#    plt.plot(steps, f2_r_mod)

#    plt.plot(steps, f_mod[:,0])
#    plt.scatter(r_mod, f_mod[:,0])
    plt.plot(r_mod, f2_r_mod, '.', xp, p(xp), '-')
#    plt.scatter(r_mod, f1_r_mod, color = "blue")
#    plt.scatter(r_mod, f2_r_mod, color = "red")

#    plt.scatter(r_mod, f_mod[:,1], c = 'red')
    plt.show()