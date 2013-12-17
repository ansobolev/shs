#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

from numpy import ma
from abstract import PerAtomData

class VPVolumeData(PerAtomData):
    _shortDoc = "Total VP volume"

    def getData(self, calc):
        # default plot options         
        self.plot_options['dx'] = 0.05
        
        self.x_title = "Volume"
        self.y = []
        self.y_titles = []
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
        self.y = []
        self.y_titles = []
        self.data = []
        for _, g in calc.evol:
            self.data.append(ma.getdata(g.vp_totfacearea(self.pbc, self.ratio)))
        self.calculate()

class VPFaceAreaData(PerAtomData):
    _shortDoc = "VP face area"    

    def getData(self, calc):
        # default plot options         
        self.plot_options['dx'] = 0.025
        
        self.x_title = "Face area"
        self.y = []
        self.y_titles = []
        self.data = []
        for _, g in calc.evol:
            self.data.append(ma.getdata(g.vp_facearea(self.pbc, self.ratio)))
        self.calculate()
    
    def calculate(self):
        if self.partial:
            _, types = self.calc.evol.getAtomsByType()
            types_list = sorted(types.keys())
            # pairwise
            for i, ti in enumerate(types_list):
                for tj in types_list[i:]:
                    self.y_titles.append(ti + "-" + tj)
                    self.y.append(self.calculatePartial(types[ti], types[tj]))
            # single
            for ti in types_list:
                self.y_titles.append(ti)
                self.y.append(self.calculatePartial(types[ti]))
        else:
            self.y_titles = ["Total"]
# FIXME:            self.y = self.data
    
    def calculatePartial(self, ti, tj = None):
        if tj is None:
            return [self.data[i][t_i].flatten() for (i,t_i) in enumerate(ti)]
        else:
            return  [self.data[i][t_i][:,t_j].flatten() for i,(t_i,t_j) in enumerate(zip(ti,tj))]


class AbsMagneticMoment(PerAtomData):
    pass

class MagneticMoment(PerAtomData):
    _shortDoc = "Magnetic moment"
     
