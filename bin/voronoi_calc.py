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


def voronoi_calc():
    calc_dir = '../test'
    c = SiestaCalc(calc_dir, type = 'out', steps = [-2,])
#    c.evol[0].to_cell()
    n = c.evol[0].filter('label','C')
    r = c.evol[0].distance_to_group(n[0])
    spin = N.abs(c.evol[0]['up'] - c.evol[0]['dn'])
    c.evol[0].voronoi()
    SIO.data2file([c.evol[0]['vol'], r, spin], ['Vol', 'R', 'Spin'], 'vol-r-spin.dat')
#    Plot.scatter(c.evol[0]['vol'], N.abs(c.evol[0]['up']-c.evol[0]['dn']))
    Plot.scatter3d(c.evol[0]['vol'], r, spin)
 
if __name__== '__main__':
    voronoi_calc()
      