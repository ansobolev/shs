#! /usr/bin/env python
# -*- coding : utf8 -*-

#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

import itertools
import numpy as np


class Data():
    
    ''' A class for obtaining and manipulating data 
    '''    
    
    def __init__(self, dtype, name, partial = False, 
                 x = None, x_label = None, y = None, y_label = None, data = None):
        
        dtypes = ['func', 'per_atom', 'hist'] 
        assert dtype in dtypes
        # data is a numpy record array (if not None)
        assert (y is not None and y_label is not None) or data is not None
        
        self.dtype = dtype 
        
        if dtype == 'func':
            assert x_label is not None
            if data is not None:
                y_label = data.dtype.names[1:]
                # TODO: check if x_label always is the 1st in dtype.names 
                x = data[x_label]
                y = [data[iy] for iy in y_label]
                
        self.name = name
        self.x = x
        self.x_label = x_label
        self.y = y
        self.y_label = y_label
        self.types = None
        
        self.partial = partial
    
    def make_partial(self, types, pairwise = False):
        ''' Makes partial calculation from non-partial 
        '''
        if self.partial:
            return
       
        assert isinstance(types, list)
        
        self.types = types
        self.y_label = []
        self.nat = []
        y = []
        typeind = {}
        if pairwise:
            nat = len(self.y[0])    
            # adding atoms to existing types
            for (t, nt) in types.iteritems():
                self.y_label.append((t,))
                typeind[(t,)] = (nt, np.arange(nat))
            # expanding types by products
            for (t1, t2) in itertools.product(types.keys(), types.keys()):
                self.y_label.append((t1, t2))
                typeind[(t1, t2)] = (types[t1], types[t2])
            # data according to types
            for t in self.y_label:
                (n1, n2) = typeind[t]
                yi = []
                for yj in self.y:
                    yi.append(yj[n1][:,n2].compressed())
                y.append(yi)
             
        else:
            # cycle over geometry steps
            for (ti, yi) in zip(types, self.y):
                # cycle over types in each step 
                for (k,v) in ti.items(): 
                    # if typename is not known yet 
                    if k not in self.y_label:
                        self.y_label.append(k)
                        self.nat.append(len(v))
                        # label index
                        y.append([yi[v]])
                    else:
                        y[self.y_label.index(k)].append(yi[v])
                        self.nat[self.y_label.index(k)] += len(v)
        self.y = y
    
    def function(self):
        ''' Returns function data
        '''
        assert self.dtype == 'func'
        return (self.y_label, self.x, self.y), None
    
    def histogram(self, dx, **kwds):
        ''' Makes histogram out of data
        '''
        assert (self.dtype == 'per_atom' or self.dtype == 'hist')
        xmin = kwds.pop('xmin', None)
        xmax = kwds.pop('xmax', None)
        norm = kwds.pop('norm', 'nat')
        
        # flattening type lists
        y = [[i for step_y in yi for i in step_y] for yi in self.y]
        # global max and min
        if xmin is None:
            xmin = np.ceil(min([i for typ_y in y for i in typ_y])/dx) * dx

        if xmax is None:
            xmax = np.ceil(max([i for typ_y in y for i in typ_y])/dx) * dx

        nbins = (xmax - xmin) / dx
        # make recarray out of data
        data = []
        for iy, (y_label, y) in enumerate(zip(self.y_label, y)):
            # FIXME: norming (ugly hack)
            if type(norm) == type([]): 
                coeff = 1. / norm[iy]
            elif norm == 'unity':
                # norm by unity
                coeff = 1. / (dx * len(y))
            elif norm == 'nat':
                # norm by the number of atoms (for per-atom quantities)
                nat = self.nat[iy]
                coeff = nat / (dx * len(y))
            else:
                coeff = 1. / (norm * len(self.types[y_label[0]]))
            hist, bin_edges = np.histogram(np.array(y), bins = nbins, range = (xmin, xmax))
            data.append(hist[1:] * coeff)
        
        x = (bin_edges[:-1]+dx/2.)[1:]
        if type(self.y_label[0]) == type(()):
            self.y_label = ['-'.join(n) for n in self.y_label]
        return (self.y_label, x, data), None
    
    def evolution(self, **kwds):
        ''' Calculates evolution of average value of data over the sequence of steps 
        '''
        steps = kwds.pop('steps', [])
        func = kwds.pop('func', 'avg')
       
        assert (self.dtype == 'per_atom' or self.dtype == 'hist')
        assert func in ['avg', 'cum_sum', 'part_avg']
        
        if func == 'avg':
            func = average
            # to make it compatible with part_avg
            types = None            
        elif func == 'cum_sum':
            func = cum_sum
            # to make it compatible with part_avg
            types = None
        elif func == 'part_avg':
            func = partial_average
            # a list of numbers of atoms of the 1st types in self.y_label
            types = [len(self.types[y[0]]) for y in self.y_label]
        # calculate average
        data = func(self.y, types)
        if len(steps) != 0:
            x = steps
        else:
            x = range(len(data[0]))
        if type(self.y_label[0]) == type(()):
            self.y_label = ['-'.join(n) for n in self.y_label]
        return (self.y_label, x, data), None        

# Misc functions ---
def average(y, types = None):
    'Computes average of a list or Numpy array l'
    l = y[0][0]
    if type(l) == np.ndarray:
        avg = np.mean
    else: 
        avg = lambda x: sum(x) / float(len(x))
    return [[avg(step_y) for step_y in yi] for yi in y]

def partial_average(y, types):
    'Computes partial averages'
    assert types is not None
    assert len(y) == len(types)
    return [[sum(step_y) / float(nat) for step_y in yi] for (nat, yi) in zip(types, y)]

def cum_sum(y, types = None):
    'Computes cumulative sum of a list or Numpy array l'
    y_summed = [[sum(step_y) for step_y in yi] for yi in y]
    return [np.cumsum(yi) for yi in y_summed]
            