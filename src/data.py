#! /usr/bin/env python
# -*- coding : utf8 -*-

#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

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
        
        self.partial = partial
    
    def make_partial(self, types):
        ''' Makes partial calculation from non-partial 
        '''
        if self.partial:
            return
        
        assert type(types) == type({})
        self.y_label = []
        y = []
        
        for (k,v) in types.iteritems():
            self.y_label.append(k)
            yi = []
            for yj in self.y:
                yi.append(yj[v])
            y.append(yi)
        self.y = y
    
    def histogram(self, dy):
        ''' Makes histogram out of data
        '''
        assert (self.dtype == 'per_atom' or self.dtype == 'hist')
        # flattening type lists
        y = [[i for step_y in yi for i in step_y] for yi in self.y]
        # global max and min
        y_max = np.ceil(max([i for typ_y in y for i in typ_y])/dy) * dy
        y_min = np.ceil(min([i for typ_y in y for i in typ_y])/dy) * dy
        nbins = (y_max - y_min) / dy
        # make recarray out of data
        data = []
        for typ_y in y:
            hist, bin_edges = np.histogram(np.array(typ_y), bins = nbins, range = (y_min, y_max))
            data.append(hist[1:]/float(len(typ_y)))
        
        x = (bin_edges[:-1]+dy/2.)[1:]
        return (self.y_label, x, data), None
    
    def evolution(self, steps = [], func = 'avg'):
        ''' Calculates evolution of average value of data over the sequence of steps 
        '''
        assert (self.dtype == 'per_atom')
        assert func in ['avg', 'cum_sum']
        if func == 'avg':
            func = avg
        elif func == 'cum_sum':
            func = cum_sum
        # calculate average
        data = func(self.y)
        if len(steps) != 0:
            x = steps
        elif len(self.x) != 0:
            x = self.x
        else:
            x = range(len(data[0]))
        return (self.y_label, x, data), None        

# Misc functions ---
def avg(y):
    'Computes average of a list or Numpy array l'
    l = y[0][0]
    if type(l) == np.ndarray:
        avg = np.mean
    else: 
        avg = lambda x: sum(x) / float(len(x))
    return [[avg(step_y) for step_y in yi] for yi in y]

def cum_sum(y):
    'Computes cumulative sum of a list or Numpy array l'
    y_summed = [[sum(step_y) for step_y in yi] for yi in y]
    return [np.cumsum(yi) for yi in y_summed]
            