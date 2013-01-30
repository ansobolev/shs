#! /usr/bin/env python
# -*- coding : utf8 -*-

#from shs.calc import SiestaCalc
import numpy as N
from calc import SiestaCalc
import plot as Plot 


def setup():
    template = '../template'
    c = SiestaCalc(template, mode='out', steps = [-2, -1,])
    n = c.evol[1].filter('label','C')
    r = c.evol[1].distance_to_group(n[0])
    spin = c.evol[0]['up'] - c.evol[0]['dn']
    Plot.scatter(r, N.abs(spin),'Distance to C', 'Absolute magnetic moment')
    
#    c.geom.initialize('FCC', {'Fe':3, 'C':6}, [5,4,4], 2.5, 'Ang', DistLevel = 10.0)
#    c.geom.geom2opts()
#    c.ctype.alter('MD', temp = 200)
#    c.write(newdir)

if __name__== '__main__':
    setup()
      