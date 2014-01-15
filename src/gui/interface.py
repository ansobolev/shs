#!/usr/bin/env python

''' The module providing interface from SHS to GUI
'''

import os, glob
import numpy as np

from shs.calc import SiestaCalc as Sc
from shs.data import Data
#from shs.atomtype import Comparison

settings = {'func': [{}, {}, {}, {}, {}],
            'per_atom': [{'dx' : 0.2}, {'dx' : 0.05}, {'dx' : 0.005}, {},
                         {}, {'func': 'cum_sum'}, {}],
            'hist_evol' : [{'dx' : 0.05, 'xmin' : 0.}], 
            'hist' : [{'dx' : 0.1, 'xmin' : 0.}],
            'evol' : [{'func' : 'part_avg'}]
            }

def getCalc(cdir, ctype, steps):
    copts = {'.FDF':'fdf',
             '.ANI':'ani',
             '.output':'out',
             'pdos.xml':'fdf'}
    return Sc(cdir, dtype = copts[ctype], steps = steps)

def dataClasses():
    return Data()

#def getCondition(prop, cond, value):
#    return Comparison(prop, cond, value)

#def addAndToCondition(comparison, prop, cond, value):
#    return comparison.addAnd(prop, cond, value)

def get_value(cdir, label):
    c = Sc(cdir, dtype = 'fdf')
    return c.opts[label].value
        
def set_value(cdir, label, value):
    c = Sc(cdir, dtype = 'fdf')
    c.opts[label].value = value
    return 0


def getProperties(clist):
    if clist == []:
        raise ValueError('interface.getProperties: No calculations selected!')
    props = None
    for c in clist:
        if props is None:
            props = c.getPropNames()
        else:
            assert c.getPropNames() == props
    return props


def getData(ptype, data_class, leg, clist):
    """Returns data according to plot type from a list of calcs
    Input:
     -> data_class - a class of data needed
     -> leg - legend describing calcs
     -> clist (list) - a list of SiestaCalc instances 
    """
    if clist == []:
        raise ValueError('interface.getData: No calculations selected!')
    data = []
    for c in clist:
        data.append(data_class(c).plotData(ptype))
    return data

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
    example = '../../examples/FeCANI'

    c = get_calc(example, ".ANI", steps = range(-1,0,1))
    c.evol[0].types.removeTypes()

    comp = get_condition('vp_totvolume', '>', '12')
    comp = add_And_to_condition(comp, 'label', '==', "\'Fe\'")
    c.evol[0].types.addType(comp, 'Fe_big')

    comp2 = Comparison('vp_totvolume', '>', '9')
    comp2 = comp2.addAnd('label', '==', "\'Fe\'")
    c.evol[0].types.addType(comp2, 'Fe_medium')

    comp3 = Comparison('label', '==', "\'C\'")
    c.evol[0].types.addType(comp3, 'C')

    for typ, at in c.evol[0].types:
        print typ
        print at

