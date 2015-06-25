# ---------------------------------------------
#
# The file voronoi_test.py is part of the shs project.  
# Copyright (c) 2015 Andrey Sobolev  
# License GNU GPL v.2
# See http://github.com/ansobolev/shs for details
#
# ---------------------------------------------
__author__ = 'andrey'

""" The module runs a (quick) test for voronoi calculations
"""

import matplotlib.pyplot as plt
from shs.calc import SiestaCalc


if __name__ == "__main__":
    # get siesta calc
    calc = SiestaCalc("../examples/FeCANI", calc_type="ani", steps=[-1, ])
    faces = calc.evol.geom[0].vp_facearea(pbc=True, ratio=0.5)
    print len(faces.flatten().compressed())
    print faces.flatten().compressed().mean()
    raw = calc.evol.geom[0].vp.v
    # plt.hist(faces.flatten().compressed(), bins=50)
    #plt.show()
