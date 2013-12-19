#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

import numpy as np

class PlotData(object):
    pass

class FunctionData(PlotData):

    def __init__(self, data, **kwds):
        self.title = data.title
        self.x = data.x
        self.x_title = data.x_title
        self.y = data.y
        self.y_titles = tuple(data.y_titles)

class HistogramData(PlotData):
    
    def __init__(self, data, **kwds):
        self.dx = kwds["dx"]
        self.data = data
        self.title = data.title
        self.y = []
        self.y_titles = []
        # flattening type lists        
        self.prepare(data)
        
    def prepare(self, data):
        dx = self.dx
        y = [np.hstack(y_typ) for y_typ in data.y]        
        print [len(yi) for yi in y], y[0].shape
        xmin = np.ceil(np.min(np.hstack(y))/dx) * dx
        xmax = np.ceil(np.max(np.hstack(y))/dx) * dx
        nbins = (xmax - xmin) / dx
        # make recarray out of data
        for y_typ in y:
            hist, bin_edges = np.histogram(y_typ, bins = nbins, range = (xmin, xmax))
            self.y.append(hist[1:])
        
        self.x = (bin_edges[:-1]+dx/2.)[1:]
        self.x_title = data.x_title
        self.y_titles = tuple(data.y_titles)

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
    pass

class CumSumData(PlotData):
   
    def __init__(self, data, **kwds):
        self.data = data
        self.title = data.title
        self.x_title = data.x_title
        self.y = []
        self.y_titles = tuple(data.y_titles)
        # flattening type lists        
        self.prepare(data)
        
    def prepare(self, data):
        y_summed = [np.sum(yi, axis = 1) for yi in data.y]
        self.x = np.arange(len(data.y[0]))
        self.y = [np.cumsum(yi) for yi in y_summed]