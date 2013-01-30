#! /usr/bin/env python
# -*- coding : utf8 -*-

import os
# For writing purposes
try:
    from shs.calc import SiestaCalc
    import shs.pbs as PBS
except (ImportError,):
    from calc import SiestaCalc
    import pbs as PBS
    
subs = [['$NODES$', '3:ppn=8'], ['$WALLTIME$', '48:00:00']]

def setup():
    template = '../../test'
    newdir = './newdir'
    PBSout = os.path.join(newdir, 'RUN.pbs')
    c = SiestaCalc(template, type='fdf')
    c.geom.initialize('BCC', {'Fe':175, 'C':25}, [5,5,4], 2.885, 'Ang', DistLevel = 0.0)
    c.geom.geom2opts()
#    c.ctype.alter('CG')
    c.write(newdir)
    PBS.MakePBS(None, PBSout, subs, submitJob = False, type='CG')

if __name__== '__main__':
    setup()
      