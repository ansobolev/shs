#! /usr/bin/env python
# -*- coding : utf8 -*-

import os

from calc import SiestaCalc
import plot as Plot

def plotmsd():
    dir = '../../test'
    c = SiestaCalc(dir, type = 'out', steps = range(-150, 0))
    title, t, msd = c.msd()
    print c.evol[0].atoms[0]
    Plot.plotrdf(title, t, msd, fname = 'MSD')
    


if __name__== '__main__':
    plotmsd()
