#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

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
    
    def calculate(self):
        if self.partial:
            _, types = self.calc.evol.getAtomsByType()
            self.y_titles = sorted(types.keys())
            for y_title in self.y_titles:
                self.y.append(self.calculatePartial(types[y_title]))
        else:
            self.y_titles = ["Total"]
            self.y = self.data
    
    def calculatePartial(self, n):
        return [self.data[i][n_i] for i, n_i in enumerate(n)]
   
class VPTotalFaceAreaData(PerAtomData):
    _shortDoc = "VP total face area"

class AbsMagneticMoment(PerAtomData):
    pass

class MagneticMoment(PerAtomData):
    _shortDoc = "Magnetic moment"
     
    def getData(self):
        pass

