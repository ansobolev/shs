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

def getcorr(x, y, clist):
    if clist == []:
        raise ValueError('interface.getcorr: No calculations selected!')
    # correlation plot options
    pdata = {"X": Sc.x,
             "Y": Sc.y, 
             "Z": Sc.z, 
             "Magnetic moment": Sc.mmagmom,
             "Coordination number": Sc.cn,
             "VP volume": Sc.vp_totvolume,
             "VP area": Sc.vp_totfacearea
             }
    data = []
    info = []
    for c in clist:
        (title, _, data_x), info_i = pdata[x](c)
        (title, _, data_y), info_i = pdata[y](c)
        info.append(info_i)
        data.append([title, data_x, data_y])
    return data, info


def getdata(ptype, clist):
    """Returns data according to plot type from a list of calcs
    Input:
     -> ptype (int) - plot type 
     -> clist (list) - a list of SiestaCalc instances 
    """
    if clist == []:
        raise ValueError('interface.getdata: No calculations selected!')
# plot options
    iface = {0: simple,   # MDE
             1: per_calc, # RDF
             2: per_calc, # MSD
             3: per_calc, # Velocity autocorrelation
             4: per_calc, # DOS
             5: per_calc, # Coordination numbers
             6: per_calc, # CN time evolution
             7: per_calc, # VP facearea
             8: per_calc, # Total VP facearea
             9: per_calc, # Total VP volume
             10: per_calc, # VP sphericity coefficient
             11: per_calc, # Mean magnetic moment
             12: per_calc, # Mean absolute magnetic moment
             13: per_calc, # Number of spin flips
             14: var_x  # Topological indices
             }
    
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
    return iface[ptype](pdata[ptype], clist)
        
# interfaces per se
def simple(fn, clist):
    data = []
    info = []
    for c in clist:
        data_i, info_i = fn(c)
        data.append(data_i)
        info.append(info_i)
    return data, info
 
def per_calc(fn, clist):
    data = []
    info = []
    for c in clist:
        (title, x, data_i), info_i = fn(c)
        info.append(info_i)
        formats = ['f8' for _ in title]
        data.append(np.rec.fromarrays([x] + data_i, names = title, formats = formats))
    return data, info

def var_x(fn, clist, threshold = 0.5):
    from collections import defaultdict
    x = []
    d = []
    data = [[] for _ in clist]
    info = [{} for _ in clist]
    for c in clist:
        title, data_i = fn(c)
        d.append(data_i)

        for data_ij in data_i:
            for key_ij in data_ij.keys():
                t = max(data_ij.values()) * threshold
                if data_ij[key_ij] > t:
                    x.append(key_ij)
    x = list(set(x))
    # For the sake of beautiful output    
    l = defaultdict(list)
    for key in x:
        l[sum(key)].append(key)
    x = [sorted(l[k]) + ['',] for k in sorted(l.keys())]
    # flattening list
    x = [l for sublist in x for l in sublist][:-1]
    # cycle over calcs
    for i, di in enumerate(d):
        for dij in di:
            data[i].append([dij[xi] for xi in x])
        formats = ['f8' for _ in title]
        data[i] = np.rec.fromarrays([range(len(x))] + data[i], names = title, formats = formats)
        info[i]['x'] = x
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