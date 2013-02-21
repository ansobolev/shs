#!/usr/bin/env python

''' The module providing interface from SHS to GUI
'''

import os, glob
import numpy as np

from shs.calc import SiestaCalc as Sc

def getcalc(cdir, ctype, steps):
    copts = {'.FDF':'fdf',
             '.ANI':'ani',
             '.output':'out',
             'pdos.xml':'fdf'}
    
    return Sc(cdir, dtype = copts[ctype], steps = steps)

def getvalue(cdir, label):
    c = Sc(cdir, dtype = 'fdf')
    return c.opts[label].value
        
def setvalue(cdir, label, value):
    c = Sc(cdir, dtype = 'fdf')
    c.opts[label].value = value
    return 0

def getdata(ptype, clist):
    """Returns data according to plot type from a list of calcs
    Input:
     -> ptype (int) - plot type 
     -> clist (list) - a list of SiestaCalc instances 
    """
    if clist == []:
        raise ValueError('interface.getdata: No calculations selected!')
# plot options
    pdata = {0: Sc.mde,
             1: Sc.rdf,
             2: Sc.msd,
             3: Sc.vaf,
             4: Sc.dos,
             5: Sc.cn,
             6: Sc.pcn_evolution,
             7: Sc.vp_facearea,
             8: Sc.vp_totfacearea,
             9: Sc.vp_totvolume,
             10: Sc.vp_ksph,
             11: Sc.mmagmom,
             12: Sc.mabsmagmom,
             13: Sc.spinflips,
             14: Sc.vp_ti
             }
    data = []
    info = []
    for c in clist:
        (title, x, data_i), info_i = pdata[ptype](c)
        info.append(info_i)
        if title is None:
            data.append(data_i)
            continue
        formats = ['f8' for _ in title]
        data.append(np.rec.fromarrays([x] + data_i, names = title, formats = formats))
    return data, info
        
def isCalcOfType(ctype, **kwargs):
    if 'fn' in kwargs.keys():
        options = {'.FDF' : [f for f in kwargs['fn'] if f.endswith('.fdf')],
               '.ANI' : [f for f in kwargs['fn'] if f.endswith('.ANI')],
               '.output' : [d for d in kwargs['dn'] if d == 'stdout'],
               'pdos.xml' : [f for f in kwargs['fn'] if f == 'pdos.xml']}
    elif 'dir' in kwargs.keys():
        options = {'.FDF' : [f for f in os.listdir(kwargs['dir']) if f.endswith('.fdf')],
               '.ANI' : [f for f in os.listdir(kwargs['dir']) if f.endswith('.ANI')],
               '.output' : [d for d in os.listdir(kwargs['dir']) if d == 'stdout'],
               'pdos.xml' : [f for f in os.listdir(kwargs['dir']) if f == 'pdos.xml']}
    return options[ctype]

def GetNumMDESteps(cdir):
    mdefn = glob.glob(os.path.join(cdir, '*.MDE'))
    if len(mdefn) == 0:
        return None
    nsteps = sum(1 for line in open(mdefn[0]) if line[0] != '#')
    return nsteps

def GetCalcInfo():
    pass

if __name__ == '__main__':
    pass