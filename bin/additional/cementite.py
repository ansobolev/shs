#!/usr/bin/env python
# -*-coding: utf-8 -*-

import os 

from shs.geom import Geom

def init_cementite():
# Lattice constants
    alat = [4.524, 5.088, 6.741]
    bas_crd = [[0.333, 0.175, 0.065],
               [0.333, 0.175, 0.435],
               [0.167, 0.675, 0.065],
               [0.167, 0.675, 0.435],
               [0.667, 0.825, 0.935],
               [0.667, 0.825, 0.565],
               [0.833, 0.325, 0.935],
               [0.833, 0.325, 0.565],
               [0.833, 0.040, 0.250],
               [0.667, 0.540, 0.250],
               [0.167, 0.960, 0.750],
               [0.333, 0.460, 0.750],
# Normal prisms
               [0.430, 0.870, 0.250],
               [0.070, 0.370, 0.250],
               [0.570, 0.130, 0.750],
               [0.930, 0.630, 0.750]]
# Normal octahedrons
#               [0.000, 0.000, 0.000],
#               [0.500, 0.500, 0.000],
#               [0.000, 0.000, 0.500],
#               [0.500, 0.500, 0.500]]

    bas_type = ['Fe','Fe','Fe','Fe',
                'Fe','Fe','Fe','Fe',
                'Fe','Fe','Fe','Fe',
                'C','C','C','C']    
    
    for i in range(300):
        G = Geom()
        G.initialize('OR', bas_type, [3,3,3], alat, 'Ang', Basis = bas_crd, dist_level= 8.)
        write_ani(G, '.', 'FeC')
    write_xv(G, '.', 'FeC')

def write_ani(geom, dir, sl):
    nat = len(geom.atoms)
    fqfn = os.path.join(dir, sl + '.ANI')
    f = open(fqfn, 'a')
    f.write('%i\n\n' % (nat,))
    for at in geom.atoms:
        f.write('%2s\t%10.5f  %10.5f  %10.5f\n' % (at['itype'], at['crd'][0], at['crd'][1], at['crd'][2],))
    f.close()
    
def write_xv(geom, dir, sl):
    nat = len(geom.atoms)
    fqfn = os.path.join(dir, sl + '.XV')
    f = open(fqfn, 'w')
# lookup dict
    ld = {}
    for i, typ in enumerate(geom.types):
        ld[typ['label']] = i
    for vc in geom.vc:
        f.write('%f\t%f\t%f\t0.000\t0.000\t0.000\n' % (vc[0]/0.529, vc[1]/0.529, vc[2]/0.529))
    f.write('   %i\n' % (nat,))
    for at in geom.atoms:
        f.write('%4i\t%4i\t%16.8f\t%16.8f\t%16.8f\t     0.00000\t     0.00000\t     0.00000\n' % (geom.types[ld[at['itype']]]['i'], geom.types[ld[at['itype']]]['z'], at['crd'][0], at['crd'][1], at['crd'][2]))
    f.close()
    
    
    
if __name__ == '__main__':
    init_cementite()