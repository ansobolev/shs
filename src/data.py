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
                 x = None, x_label = None, y = None, y_label = None):
        
        dtypes = ['func', 'per_atom', 'hist'] 
        assert dtype in dtypes
        assert y is not None
        assert y_label is not None
        
        self.dtype = dtype 
        
        if dtype == 'func':
            assert x is not None
            assert x_label is not None

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
       
        assert type(types) == type({})
        self.types = types
        self.y_label = []
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
            for (k,v) in types.iteritems():
                self.y_label.append(k)
                yi = []
                for yj in self.y:
                    yi.append(yj[v])
                y.append(yi)
        self.y = y
    
    def histogram(self, dy, xmin = None, xmax = None, norm = 1.):
        ''' Makes histogram out of data
        '''
        assert (self.dtype == 'per_atom' or self.dtype == 'hist')
        # flattening type lists
        y = [[i for step_y in yi for i in step_y] for yi in self.y]
        # global max and min
        if xmin is not None:
            y_min = xmin
        else:
            y_min = np.ceil(min([i for typ_y in y for i in typ_y])/dy) * dy

        if xmax is not None:
            y_max = xmax
        else:
            y_max = np.ceil(max([i for typ_y in y for i in typ_y])/dy) * dy

        nbins = (y_max - y_min) / dy
        # make recarray out of data
        data = []
        for iy, (y_label, y) in enumerate(zip(self.y_label, y)):
            # norming (ugly hack)
            if type(norm) == type([]): 
                coeff = 1. / norm[iy]
            elif norm == 1.:
                coeff = 1. / float(len(typ_y))
            else:
                coeff = 1. / (norm * len(self.types[y_label[0]]))
            hist, bin_edges = np.histogram(np.array(y), bins = nbins, range = (y_min, y_max))
            data.append(hist[1:] * coeff)
        
        x = (bin_edges[:-1]+dy/2.)[1:]
        return (self.y_label, x, data), None
    
    def evolution(self, steps = [], func = 'avg'):
        ''' Calculates evolution of average value of data over the sequence of steps 
        '''
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
        elif len(self.x) != 0:
            x = self.x
        else:
            x = range(len(data[0]))
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
            