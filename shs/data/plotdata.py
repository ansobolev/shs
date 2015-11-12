#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#
from collections import defaultdict
import numpy as np


class PlotData(object):

    def __init__(self, data, **kwds):
        self.title = data.title
        self.y = []
        self.y_titles = tuple(data.y_titles)


class FunctionData(PlotData):

    def __init__(self, data, **kwds):
        super(FunctionData, self).__init__(data, **kwds)
        self.x = data.x
        self.x_title = data.x_title
        self.y = data.y


class HistogramData(PlotData):
    
    def __init__(self, data, **kwds):
        super(HistogramData, self).__init__(data, **kwds)
        self.dx = kwds["dx"]
        self.x_title = data.x_title
        # flattening type lists        
        self.prepare(data, self.dx)
        
    def prepare(self, data, dx):
        y = [np.hstack(y_typ) for y_typ in data.y]        
        xmin = np.ceil(np.min(np.hstack(y))/dx) * dx
        xmax = np.ceil(np.max(np.hstack(y))/dx) * dx
        nbins = (xmax - xmin) / dx
        bin_edges = []
        # make recarray out of data
        for y_typ in y:
            hist, bin_edges = np.histogram(y_typ, bins = nbins, range = (xmin, xmax))
            self.y.append(hist[1:])
       
        self.x = (bin_edges[:-1]+dx/2.)[1:]

#            # FIXME: norming (ugly hack)
#            if type(norm) == type([]): 
#                coeff = 1. / norm[iy]
#            elif norm == 'unity':
                # norm by unity
#                coeff = 1. / (dx * len(y))
#            elif norm == 'nat':
                # norm by the number of atoms (for per-atom quantities)
#                nat = self.nat[iy]
#                coeff = nat / (dx * len(y) * self.nsteps)
#            else:
#                coeff = 1. / (norm * len(self.types[y_label[0]]))
#        data.append(hist[1:] * coeff)
        
#        if type(self.y_label[0]) == type(()):
#            self.y_label = ['-'.join(n) for n in self.y_label]
        

class TimeEvolData(PlotData):

    def __init__(self, data, **kwds):
        super(TimeEvolData, self).__init__(data, **kwds)
        self.x = np.arange(data.nsteps)
        self.x_title = "Steps"
        # flattening type lists        
        self.prepare(data)
    
    def prepare(self, data):
        for y_t in data.y:
            self.y.append([np.mean(y_i) for y_i in y_t])


class CumSumData(PlotData):
   
    def __init__(self, data, **kwds):
        super(CumSumData, self).__init__(data, **kwds)
        self.x_title = data.x_title
        # flattening type lists        
        self.prepare(data)
        
    def prepare(self, data):
        y_summed = [np.sum(yi, axis = 1) for yi in data.y]
        self.x = np.arange(len(data.y[0]))
        self.y = [np.cumsum(yi) for yi in y_summed]


class VarXData(HistogramData):

    def __init__(self, data, **kwds):
        super(HistogramData, self).__init__(data, **kwds)
        self.threshold = kwds.get('threshold', None)
        self.x_title = data.x_title
        # flattening type lists        
        self.prepare(data)
        self.var_x = True
    
    def prepare(self, data):
        'Returns topological indices for VPs'
        x = []
        d = [defaultdict(int) for _ in self.y_titles]
        for i, yi in enumerate(data.y):
            # Count number of VP occurrences    
            for elt in yi:
                d[i][tuple(elt)] += 1
        # get xs from d based on threshold
        for di in d:
            t = max(di.values()) * self.threshold
            for key_i in di.keys():
                if di[key_i] > t:
                    x.append(key_i)
        # uniquify x
        x = list(set(x))
        # For the sake of beautiful output    
        l = defaultdict(list)
        for key in x:
            l[sum(key)].append(key)
        x = [sorted(l[k]) + ['',] for k in sorted(l.keys())]        
        # flattening list
        self.x = [l for sublist in x for l in sublist][:-1]
        self.y = []
        # cycle over calcs
        for di in d:
            self.y.append([di.get(xi, 0) for xi in self.x])
