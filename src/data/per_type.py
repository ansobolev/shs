#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#
import numpy as np
import shs.errors
import plotdata
from shs.geom import r
from abstract import OneTypeData, InteractingTypesData


class VAFData(OneTypeData):
    ''' Get VAF of evolution (type-wise)
        NB: As it uses only one cell vector set, when calculating VAF for NPT ensemble one should expect getting strange results. 
        In:
         -> atype (int?) - atomic type we need to calculate VAF for 
        '''
    
    _shortDoc = "Velocity autocorrelation"

    def getData(self, calc):
        ''' Calc velocity autocorrelation function (VAF) for the evolution
        In:
         -> n: a list of atoms for which to calculate VAF
        Out:
         -> t: a list of \Delta t differences (in steps)
         -> vaf: a list of average VAFss for every \Delta t
        '''
        # taking coordinates of atoms belonging to the list n
        self.traj, _ = calc.evol.trajectory()
        self.y = []
        self.x_title = "Steps"
        self.y_titles = []
        self.calculate()

    def calculatePartial(self, n):
        coords = self.traj[:,n,:]
        # assuming dt = 1, dx - in distance units!
        v = coords[1:] - coords[:-1] 
        traj_len = len(v)
        # time (in step units!) 
        t = np.arange(traj_len)
        vaf = np.zeros(traj_len)
        num = np.zeros(traj_len, dtype = int)
        for delta_t in t:
            for t_beg in range(traj_len - delta_t):
                # correlation between v(t_beg) and v(t_beg + delta_t)
                v_cor = (v[t_beg] * v[t_beg + delta_t]).sum(axis = 1)
                num[delta_t] += len(v_cor.T)
                vaf[delta_t] += np.sum(v_cor)
        vaf = vaf / num
        return t, vaf

class MSDData(OneTypeData):
    """ Get MSD of evolution (type-wise)
        NB: As it uses only one cell vector set, when calculating MSD for NPT ensemble one should expect getting strange results. 
        In:
         -> atype (int?) - atomic type we need to calculate MSD for""" 

    _shortDoc = "Selfdiffusion (MSD)"
    
    def getData(self, calc):
        ''' Calc mean square displacement for the evolution
        In:
         -> n: a list of atoms for which to calculate MSD
        Out:
         -> t: a list of \Delta t differences (in steps)
         -> vaf: a list of average VAFss for every \Delta t
        '''
        # taking coordinates of atoms belonging to the list n
        self.traj, _ = calc.evol.trajectory()
        self.y = []
        self.x_title = "Steps"
        self.y_titles = []
        self.calculate()

    def calculatePartial(self, n):
        coords = self.traj[:,n,:]
        traj_len = len(coords)
        t = np.arange(traj_len)
        msd = np.zeros(traj_len)
        num = np.zeros(traj_len, dtype = int)
        for delta_t in t:
            for t_beg in range(traj_len - delta_t):
                dx = coords[t_beg + delta_t] - coords[t_beg]
                dr = (dx**2.0).sum(axis = 1)
                num[delta_t] += len(dr.T)
                msd[delta_t] += np.sum(dr)
        msd = msd / num
        return t, msd
    
class RDFData(InteractingTypesData):
    """ Data class for calculating partial RDFs 
    """
    _shortDoc = "Partial RDFs"
    
    def __init__(self, *args, **kwds):
        self.rmax = kwds.get("rmax", None)
        self.dr = kwds.get("dr", 0.05)
        super(RDFData, self).__init__(*args, **kwds)

    def getData(self, calc):
        self.traj, self.vc = calc.evol.trajectory()
        # get rmax
        if self.rmax is None:
            self.rmax = np.max(self.vc)/2.
        self.y = []
        self.x_title = "Distance"
        self.y_titles = []
        self.calculate()
        
    def calculate(self):
        ''' Get RDF of evolution
        In:
         -> partial (bool) - indicates whether we need partial RDF
         -> n (tuple of index lists or None) - if partial, then indicates which atoms we need to find geometry of 
        '''
        if self.partial:
            # get the list of atom types (from the first geometry in evolution)
#            if self.calc.evol.areTypesConsistent():
#                n = self.calc.evol[0].types.toDict()
            # TODO: deal with non-consistent types                
            _, n = self.calc.evol.getAtomsByType()
            labels = sorted(n.keys())
            for i, ityp in enumerate(labels):
                for jtyp in labels[i:]:
                    n1 = n[ityp]
                    n2 = n[jtyp]                    
                    x, y = self.calculatePartial(n1, n2)
                    self.x = x
                    self.y.append(y)
                    self.y_titles.append(ityp+'-'+jtyp)
        else:
            raise NotImplementedError('Calculating RDF from non-partial types is not implemented yet')
#            n = None
#            title.append('Total RDF')
#            r, rdf = self.evol.rdf(n)
#            total_rdf.append(rdf)

    def calculatePartial(self, n1, n2):
#        sij = coords[:,:,None,...] - coords[:,None,...]
# number of bins
        nbins = int((self.rmax-self.dr)/self.dr)
        nsteps = len(self.vc)
        dists = np.zeros(nbins)

        for crd_i, vc_i, n1_i, n2_i in zip(self.traj, self.vc, n1, n2):
# fractional coordinates
            nat1 = len(n1_i)
            nat2 = len(n2_i)
            vol = np.linalg.det(vc_i)
            
            rij = r(crd_i, vc_i, (n1_i, n2_i))
            dist = np.sqrt((rij**2.0).sum(axis = 1))
# found distances, now get histogram
            hist, x = np.histogram(dist, bins = nbins, range = (self.dr, self.rmax)) 
            dists += hist / (nat1 / vol * nat2) 
# find rdf
        rdf = dists / nsteps
# norm rdf
        x = (x + self.dr/2.)[:-1]        
        rdf = rdf / (4.*np.pi*(x**2.)*self.dr)
        return x, rdf
  
