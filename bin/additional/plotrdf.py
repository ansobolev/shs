#! /usr/bin/env python
# -*- coding : utf8 -*-

import os
# For writing purposes
try:
    from shs.calc import SiestaCalc, LammpsCalc
    import shs.plot as Plot
except (ImportError,):
    from calc import SiestaCalc, LammpsCalc
    import plot as Plot

def plotrdf():
    dir = '/home/andrey/calc/FeH'
    c = LammpsCalc(dir, type = 'ani', steps = range(-300, 0))
#    n1 = c.evol.filter('label', 'C')[0]
    title, r, rdf = c.rdf(partial = True ,n = None)
    Plot.plotrdf(title, r, rdf)

if __name__== '__main__':
    plotrdf()