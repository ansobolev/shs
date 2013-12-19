#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

import numpy as np
from abstract import PerAtomData

class VPVolumeData(PerAtomData):
    _shortDoc = "Total VP volume"

    def getData(self, calc):
        # default plot options         
        self.plot_options['dx'] = 0.05
        
        self.x_title = "Volume"
        self.data = []
        for _, g in calc.evol:
            self.data.append(g.vp_totvolume(self.pbc, self.ratio))
        self.calculate()
   
class VPTotalFaceAreaData(PerAtomData):
    _shortDoc = "VP total face area"
    
    def getData(self, calc):
        # default plot options         
        self.plot_options['dx'] = 0.1
        
        self.x_title = "Face area"
        self.data = []
        for _, g in calc.evol:
            self.data.append(g.vp_totfacearea(self.pbc, self.ratio))
        self.calculate()

class VPSphericityCoefficient(PerAtomData):
    _shortDoc = "VP sphericity coefficient"
    
    def getData(self, calc):
        # default plot options         
        self.plot_options['dx'] = 0.02
        
        self.x_title = "Ksph"
        self.data = []
        for _, g in calc.evol:
            self.data.append(g.vp_ksph(self.pbc, self.ratio))
        self.calculate()
    

class VPFaceAreaData(PerAtomData):
    _shortDoc = "VP face area"    

    def getData(self, calc):
        # default plot options         
        self.plot_options['dx'] = 0.04
        
        self.x_title = "Face area"
        self.data = []
        for _, g in calc.evol:
            self.data.append(np.ma.getdata(g.vp_facearea(self.pbc, self.ratio)))
        self.calculate()
    
    def calculate(self):
        if self.partial:
            _, types = self.calc.evol.getAtomsByType()
            types_list = sorted(types.keys())
            # single
            for ti in types_list:
                self.y_titles.append(ti)
                self.y.append(self.calculatePartial(types[ti]))
            # pairwise
            for i, ti in enumerate(types_list):
                for tj in types_list[i:]:
                    self.y_titles.append(ti + "-" + tj)
                    self.y.append(self.calculatePartial(types[ti], types[tj]))
        else:
            self.y_titles = ["Total"]
# FIXME:            self.y = self.data
    
    def calculatePartial(self, ti, tj = None):
        if tj is None:
            return [self.data[i][t_i].flatten() for (i,t_i) in enumerate(ti)]
        else:
            return  [self.data[i][t_i][:,t_j].flatten() for i,(t_i,t_j) in enumerate(zip(ti,tj))]

class MagneticMoment(PerAtomData):
    _shortDoc = "Magnetic moment"
    
    def getData(self, calc):
        self.plot_options['dx'] = 0.1
        
        self.x_title = "Magnetic moment"
        self.data = []
        for _, g in calc.evol:
            self.data.append(g.magmom())
        self.calculate()

class AbsMagneticMoment(PerAtomData):
    _shortDoc = "Absolute magnetic moment"
    
    def getData(self, calc):
        self.plot_options['dx'] = 0.1
        
        self.x_title = "Absolute magnetic moment"
        self.data = []
        for _, g in calc.evol:
            self.data.append(g.magmom(abs_mm = True))
        self.calculate()

class SpinFlipsData(PerAtomData):
    _isHistogram = False
    _shortDoc = 'Number of spin flips'

    def getData(self, calc):
        self.x_title = "Spin flips"
        self.data = []
        for _, g in calc.evol:
            self.data.append(g.magmom())
        self.calculate()
    
    def calculateTotal(self):
        prev = self.data[0]
        result = [np.zeros(len(prev))]
        for cur in self.data[1:]:
            result.append((prev * cur) < 0)
            prev = cur
#        print len(result), len(result[0])
        return result        
        
    def calculatePartial(self, t):
        data = self.calculateTotal()
        result = [d[ti] for d, ti in zip(data,t)]
        return result
    
    def plotData(self, plot_type):
        from plotdata import CumSumData
        return CumSumData(self)
        
