#! /usr/bin/env python
# -*- coding : utf8 -*-

#from shs.calc import SiestaCalc
import os, sys

import numpy as N
from calc import SiestaCalc
import plot as Plot 


def setup():
    template = '../test'
    c = SiestaCalc(template, dtype = 'fdf')
    c.geom.initialize('FCC', {'Fe':3, 'C':6}, [5,4,4], 2.5, 'Ang', DistLevel = 10.0)
    c.geom.geom2opts()
    for temp in range(773, 2773, 200): 
        for et in range(100, 400, 100):
            newdir = os.path.join('../test/new', str(temp), str(et)) 
            str_et = str(et) + ' meV'
            c.alter({'ElectronicTemperature' : str_et})
            c.ctype.alter('MD', temp = temp)
            c.write(newdir)

if __name__== '__main__':
    setup()
