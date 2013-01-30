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


def rdfvp():
    calc_dir = '../test'
    dr = 0.2
    evol_steps = 20
    c = SiestaCalc(calc_dir, type = 'out', steps = range(-evol_steps,-1))
#    c.evol[0].to_cell()
    rawrdf = []
    for istep, g in c.evol:
        n = g.filter('label','C')
        
        g.voronoi()
#    c_atoms = c.evol[0].atoms[n]
        for i, inb in enumerate(g.nb):
            if N.any(n[0] == i):
#            print inb
                rawrdf += [inb[x][3] for x in inb.keys()]
    nat = len(n[0])
    r_min = N.floor(N.min(rawrdf)/dr) * dr
    r_max = N.ceil(N.max(rawrdf)/dr) * dr
    nbins = (r_max - r_min) / dr
#    print N.min(rawrdf), N.max(rawrdf), r_min, r_max, nbins
    hist, bin_edges = N.histogram(N.array(rawrdf), bins = nbins, range = (r_min, r_max))
#    print bin_edges
    SIO.data2file([bin_edges[:-1]+dr/2., hist/(evol_steps * nat * dr)], ['R','rdfvp'], fname = 'RDFVP.dat')
    Plot.plot2d(bin_edges[:-1]+dr/2., hist/(evol_steps * nat * dr))

if __name__== '__main__':
    rdfvp()
      