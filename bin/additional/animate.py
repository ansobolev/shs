#! /usr/bin/env python
# -*- coding : utf8 -*-

import numpy as np
#from shs.calc import SiestaCalc
from calc import SiestaCalc
from geom import r as dist 


def setup():
#    dir = '/home/andrey/calc/FeC/Fe161C39/NVT/1'
    dir = '/home/andrey/calc/Fe/Spin/MD/FCC/MagMom'

    c = SiestaCalc(dir, type = 'out', steps = range(-1400, 0))
    return c

def full_mag_mom(c):
        
    steps = []
    mm = []
    for step, geom in c.evol:
        spins = geom.atoms['up'] - geom.atoms['dn']
        steps.append(step)
        mm.append(sum(spins))
    return steps, mm

def spin_product(c, r_max = 10., dr = 0.4):
    nat = len(c.evol.geom[0].atoms) 
    nr = int(r_max / dr)
    sp = [[] for _ in range(nr)]

    for es in c.evol.geom:
        n = es.filter('label','Fe')
        spin = es[n]['up'] - es[n]['dn']
        # spin product
        spin2 = np.outer(spin, spin)
        # dist
        r = dist(es['crd'], es.vc, [n,n])
        r2 = np.sum(r*r, axis = 1)
        ri = np.floor(np.sqrt(r2.reshape(len(n[0]), len(n[0]))) / dr)
        for i in range(len(n[0])):
            for j in range(len(n[0])):
                if ri[i,j] < nr:
                    sp[int(ri[i,j])].append(spin2[i,j])
    sp_mean = [0. for _ in sp]
    for i, spi in enumerate(sp):
        if len(spi) != 0:
            sp_mean[i] += sum(spi)/len(spi)
    return np.arange(0., r_max, dr), sp_mean
        
        

if __name__== '__main__':
    c = setup()
#    x, sp = spin_product(c)
    x, sp = full_mag_mom(c)
    f = open('full_mm_Fe.dat', 'a')
    for s, m in zip(x, sp):
        f.write('%f\t\t%f\n' % (s,m))
    
      