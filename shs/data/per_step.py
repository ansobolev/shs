#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

import numpy as np
from abstract import PerStepData

class CoordinationNumbers(PerStepData):
    ''' Data for plotting stepwise evolution of partial coordination 
    numbers of the system
    ''' 
    _shortDoc = "Coordination numbers"
    
    def getData(self, calc):
        self.nsteps = len(calc)
        self.data = [g.vp_neighbors(rm_small=self.rm_small, eps=self.eps) 
                       for _, g in calc.evol]
        self.y = []
        self.y_titles = []
        self.calculate()
    
    def calculate(self):
        if self.partial:
            _, types = self.calc.evol.getAtomsByType()
            labels = sorted(types.keys())
            # single
            for ti in labels:
                self.y_titles.append(ti)
                self.y.append(self.calculatePartial(types[ti]))
        else:
            self.y_titles = ["Total"]
            raise NotImplementedError
    
    def calculatePartial(self, ti):
        return [np.array([len(self.data[i][iat]) - 1 for iat in t_i]) for (i, t_i) in enumerate(ti)] 
        
    