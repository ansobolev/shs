#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#
import numpy as np
import shs.errors
import plotdata
from abstract import PerTypeData


class VAFData(PerTypeData):
    _shortDoc = "Velocity autocorrelation"

    def __init__(self, *args, **kwds):
        self.partial = kwds.get("partial", True)
        super(VAFData, self).__init__(*args, **kwds)

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

    def calculate(self):
        if self.partial:
            if not self.calc.evol.areTypesConsistent():
                raise shs.errors.AtomTypeError("VAF: " +
                    "Types should be consistent to get partial results")
            # now we know that types are consistent
            n = self.calc.evol[0].types.toDict()
        else:
            n = {"Total": self.calc.evol.natoms}
        for label, nat in n.iteritems():
            x, y = self.calculatePartial(nat)
            self.y.append(y)
            self.y_titles.append(label)
        self.x = x

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

    def plotData(self):
        return plotdata.FunctionData(self)
    