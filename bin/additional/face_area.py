#! /usr/bin/env python
# -*- coding : utf8 -*-


'Finds topological indices of Voronoi polihedra'

import os
import numpy as N

try:
    from shs.calc import SiestaCalc
except (ImportError,):
    from calc import SiestaCalc

def face_area():

    calc_dir = '../../test'
    c = SiestaCalc(calc_dir, type = 'ani', steps = [-1])

    for ist in range(len(c.evol.steps)):
        c.evol[ist].voronoi_params()
    
if __name__== '__main__':
    face_area()
      