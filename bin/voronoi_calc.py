#! /usr/bin/env python
# -*- coding : utf8 -*-

import os, timeit, time
import numpy as N
import pyvoro

try:
    from shs.calc import SiestaCalc
    import shs.sio as SIO
    import shs.plot as Plot
except (ImportError,):
    from calc import SiestaCalc
    import sio as SIO
    import plot as Plot



def vor_med(c):
    return c.evol[0].voronoi()

def voronoi_calc():
#    print timeit.repeat('vor_pv(c)', setup='from __main__ import vor_pv, c', repeat = 10, number = 10)
    calc_dir = '/home/andrey/calc/FeC/Fe161C39/NVT/1'
    c = SiestaCalc(calc_dir, calc_type= 'out', steps = range(-10,0,1))

    for i in range(10):
        start = time.time()
        pyvoro.compute_voronoi(
        c.evol[i].atoms['crd'], # point positions
        c.evol[i].vc, # limits
         c.evol[i].vc[0,0]/4. # block size
        )
        print time.time() - start

if __name__== '__main__':
    voronoi_calc()
