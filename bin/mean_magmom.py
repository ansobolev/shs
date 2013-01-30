#! /usr/bin/env python
# -*- coding : utf8 -*-

import os
import numpy as N

try:
    from shs.calc import SiestaCalc
    import shs.sio as SIO
    import shs.plot as Plot
except (ImportError,):
    from calc import SiestaCalc
    import sio as SIO
    import plot as Plot


def mean_magmom():
    calc_dir = '../test'
    c = SiestaCalc(calc_dir, type = 'out', steps = range(-20,-1))
#    c.evol[0].to_cell()
    mmagmom = []
    for es in c.evol.geom:
        n = es.filter('label','Fe')
        spin = N.abs(es[n]['up'] - es[n]['dn'])
        mmagmom.append(N.mean(spin))
    print N.mean(N.array(mmagmom))
#    c.evol[0].voronoi()
#    SIO.data2file([c.evol[0]['vol'], r, spin], ['Vol', 'R', 'Spin'], 'vol-r-spin.dat')
#    Plot.scatter(c.evol[0]['vol'], N.abs(c.evol[0]['up']-c.evol[0]['dn']))
#    Plot.scatter3d(c.evol[0]['vol'], r, spin)
 
if __name__== '__main__':
    mean_magmom()
      