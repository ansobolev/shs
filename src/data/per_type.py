#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#
import numpy as np
import shs.errors
import plotdata
from abstract import OneTypeData


class VAFData(OneTypeData):
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
