#! /usr/bin/env python
# -*- coding : utf8 -*-

#from shs.calc import SiestaCalc
from calc import SiestaCalc
import plot as Plot 

def mean_distance():
    dir = '../../test'
    c = SiestaCalc(dir, type = 'ani', steps = range(-100, 0))
    n = c.evol.filter('label', 'C')[0]
    md = c.evol.mean_distance(n)
    Plot.plotmd(md)

if __name__== '__main__':
    mean_distance()
      