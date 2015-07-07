# ---------------------------------------------
#
# The file voronoi_test.py is part of the shs project.  
# Copyright (c) 2015 Andrey Sobolev  
# License GNU GPL v.2
# See http://github.com/ansobolev/shs for details
#
# ---------------------------------------------

""" The module runs a (quick) test for voronoi calculations
"""
__author__ = 'andrey'
import matplotlib.pyplot as plt
from shs.calc import SiestaCalc
from shs.data.per_type import *

if __name__ == "__main__":
    # get siesta calc
    calc = SiestaCalc("../../examples/FeCANI", calc_type="ani", steps=range(-50, 0, 1))
    data = VPRDFData(calc)
    # faces = calc.evol.geom[0].vp_facearea(pbc=True, ratio=0.5)
    # print len(faces.flatten().compressed())
    # print faces.flatten().compressed().mean()
    # raw = calc.evol.geom[0].vp.v
    for (y, y_title) in zip(data.y, data.y_titles):
        if y_title == "Fe-Fe":
            plt.plot(data.x, y, label=y_title)
            print y
    plt.legend()
    plt.show()
