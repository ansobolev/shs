#! /usr/bin/env python
# -*- coding : utf8 -*-

#from shs.calc import SiestaCalc
from calc import SiestaCalc
import plot as Plot 

def mm_vs_distance():
    dir = '../../test'
    c = SiestaCalc(dir, mode='out', steps = [-2, -1,])
    n = c.evol[1].filter('label','C')
    r = c.evol[1].distance_to_group(n[0])
    spin = c.evol[0]['up'] - c.evol[0]['dn']
    Plot.scatter(r, N.abs(spin),'Distance to C', 'Absolute magnetic moment')


if __name__== '__main__':
    mm_vs_distance()
      