#!/usr/bin/env python

''' The module providing interface from SHS to GUI
'''

import os, glob
import numpy as np

from shs.calc import SiestaCalc as Sc

propChoice = {'func': ['mde', 'rdf', 'msd', 'vaf', 'dos'],
            'per_atom': ['vp_totfacearea', 'vp_totvolume', 'vp_ksph', 'mmagmom',
                         'mabsmagmom', 'spinflips', 'vp_ti'],
            'hist_evol' : ['vp_facearea',],
            'hist' : ['rdfvp',],
            'evol' : ['vp_pcn',]
            }
settings = {'func': [{}, {}, {}, {}, {}],
            'per_atom': [{'dx' : 0.2}, {'dx' : 0.05}, {'dx' : 0.005}, {},
                         {}, {'func': 'cum_sum'}, {}],
            'hist_evol' : [{'dx' : 0.05, 'xmin' : 0.}], 
            'hist' : [{'dx' : 0.1, 'xmin' : 0.}],
            'evol' : [{'func' : 'part_avg'}]
            }

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

def get_data(ptype, pchoice, clist):
    """Returns data according to plot type from a list of calcs
    Input:
     -> ptype (int, int) - plot type 
     -> clist (list) - a list of SiestaCalc instances 
    """
    if clist == []:
        raise ValueError('interface.get_data: No calculations selected!')
# plot interfaces
    pIface = {0: function, 
              1: histogram, 
              2: time_evolution
             }
    
    return pIface[ptype](pchoice, clist)

def get_corr(xchoice, ychoice, clist):
    ''' Gets data for correlation plotting
    Input:
     -> xchoice (int) - x axis data
     -> ychoice (int) - y axis data 
     -> clist (list) - a list of SiestaCalc instances 

    '''
    if clist == []:
        raise ValueError('interface.get_data: No calculations selected!')

    data = []
    xc = propChoice['per_atom'][xchoice]
    yc = propChoice['per_atom'][ychoice]
    for c in clist:
        xd = c.get_data(xc)
        yd = c.get_data(yc)
        assert (xd.y_label == yd.y_label)
        # flattening type lists
        # TODO: check everything
        x = [np.hstack([i for step_y in yi for i in step_y]) for yi in xd.y]
        y = [np.hstack([i for step_y in yi for i in step_y]) for yi in yd.y]
        data.append([np.array((xi, yi)) for (xi, yi) in zip(x, y)])
    return data, xd.y_label

# interfaces per se
def function(pchoice, clist):
    data = []
    # data kinds
    kinds = ['func']
    choices = [ci for k in kinds for ci in propChoice[k]]
    choice = choices[pchoice]
    for c in clist:
        d = c.get_data(choice)
        (names, x, calc_data), info = d.function()
        data.append((x, np.rec.fromarrays(calc_data, names = names)))
    return data, info

def histogram(pchoice, clist):
    data = []
    # data kinds
    kinds = ['hist', 'hist_evol', 'per_atom']
    choices = [ci for k in kinds for ci in propChoice[k]]
    # data settings
    dsettings = [si for k in kinds for si in settings[k]]
    choice = choices[pchoice]
    setting = dsettings[pchoice]
    # get histogram
    dx = setting.pop('dx', 0.05)
    for c in clist:
        # get Data instance 
        d = c.get_data(choice)
        (names, x, calc_data), info = d.histogram(dx, **setting) 
        data.append((x, np.rec.fromarrays(calc_data, names = names)))
    return data, info


def time_evolution(pchoice, clist):
    data = []
    kinds = ['evol', 'hist_evol', 'per_atom']
    choices = [ci for k in kinds for ci in propChoice[k]]
    # data settings
    dsettings = [si for k in kinds for si in settings[k]]
    choice = choices[pchoice]
    setting = dsettings[pchoice]
    
    for c in clist:
        setting['steps'] = c.steps
        d = c.get_data(choice)
        (names, x, calc_data), info = d.evolution(**setting)
        data.append((x, np.rec.fromarrays(calc_data, names = names)))
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