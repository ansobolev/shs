#! /usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
import numpy as np

from shs.calc import SiestaCalc
#from calc import SiestaCalc
import shs.plot as Plot 



def ti_vs_distance():
    steps = range(-300,0,7)
    dir = '/home/andrey/calc/Fe/Spin/MD/BCC/Fe1923'
    c = SiestaCalc(dir, calc_type='ani', steps = steps)
#    nC = c.evol[0].filter('label','C')[0]
    nFe = c.evol[0].filter('label','Fe')[0]
    
    ti_closeFe = []
    for step, g in c.evol:
#        r = g.distance_to_group(nC)
        r = g.distance_to_group(nFe)
        n_closeFe = np.where(r[nFe] < 2.53)[0]
        ti = g.vp_ti()
        ti_Fe = [ti[i] for i in nFe]
        ti_closeFe += [ti_Fe[i] for i in n_closeFe]
# Count number of VP occurrences    
    d = defaultdict(int)
    for elt in ti_closeFe:
        d[tuple(elt)] += 1
# For the sake of beautiful output    
    l = defaultdict(list)
    for key in d.keys():
        l[sum(key)].append(key)
    print len(ti_closeFe) / float(len(steps))
        
    return l, d, len(ti_closeFe), 1

if __name__== '__main__':
    dir = '/home/andrey/Документы/Work/Conference/2013/ISVD-2013/data'
    l, d, ncats, nsteps = ti_vs_distance()
    # Output to file    
    f= open(dir + '/Fe200.dat', 'w')
    for s in sorted(l.keys()):
        for key in sorted(l[s]):
            if d[key] * 100. /(ncats * nsteps) > 1.:
                f.write('%25s\t%6.2f\n' % (str(key), d[key] * 100. /(ncats * nsteps)))
#                print '%25s\t%6.2f' % (str(key), d[key] * 100. /(ncats * nsteps))
        f.write('\n')
#        print ''
    f.close()
    
      