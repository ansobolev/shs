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
        self.nsteps = len(calc)
        # default plot options         
        self.plot_options['dx'] = 0.1
        
        self.x_title = "Volume"
        self.data = []
        for _, g in calc.evol:
            self.data.append(self._get_vp_totvolume(g))
        self.calculate()

    def _get_vp_totvolume(self, geom, n=None):
        """ Finds total volumes for resulting Voronoi polihedra

                :param geom: a Geom instance
                :param n: a tuple of arrays containing atomic numbers of corresponding type

        :return:
        """
        if geom.vp is None:
            geom.voronoi(self.pbc, self.ratio)
        if hasattr(geom.vp, 'vp_volume'):
            return geom.vp.vp_volume
        f = geom.vp.vp_faces()
        v, _ = geom.vp.vp_volumes(f)
        if n is not None:
            v = [v[i] for i in n]
        return v


class VPTotalFaceAreaData(PerAtomData):
    _shortDoc = "VP total face area"
    
    def getData(self, calc):
        self.nsteps = len(calc)
        # default plot options         
        self.plot_options['dx'] = 0.2
        
        self.x_title = "Face area"
        self.data = []
        for _, g in calc.evol:
            self.data.append(self._get_vp_totfacearea(g))
        self.calculate()

    def _get_vp_totfacearea(self, geom, n=None):
        """
        Finds total face areas for resulting Voronoi polihedra
        :param geom: a Geom instance
        :param n: a tuple of arrays containing atomic numbers of corresponding type
        :return:
        """

        if geom.vp is None:
            geom.voronoi(self.pbc, self.ratio)
        if hasattr(geom.vp, 'vp_area'):
            return geom.vp.vp_area
        f = geom.vp.vp_faces()
        _, a = geom.vp.vp_volumes(f)
        return a


class VPSphericityCoefficient(PerAtomData):
    _shortDoc = "VP sphericity coefficient"
    
    def getData(self, calc):
        self.nsteps = len(calc)        
        # default plot options         
        self.plot_options['dx'] = 0.01
        
        self.x_title = "Ksph"
        self.data = []
        for _, g in calc.evol:
            self.data.append(self._get_vp_ksph(g))
        self.calculate()

    def _get_vp_ksph(self, geom):
        """ Finds total volumes for resulting Voronoi polyhedra
        """
        if geom.vp is None:
            geom.voronoi(self.pbc, self.ratio)
        if not hasattr(geom.vp, 'vp_volume'):
            f = geom.vp.vp_faces()
            v, a = geom.vp.vp_volumes(f, partial=False)
        else:
            v = geom.vp.vp_volume
            a = geom.vp.vp_area
        ksph = 36. * np.pi * v * v / (a * a * a)
        return ksph


class VPFaceAreaData(PerAtomData):
    _shortDoc = "VP face area"    

    def getData(self, calc):
        self.nsteps = len(calc)        
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
            raise NotImplementedError
# FIXME:            self.y = self.data
    
    def calculatePartial(self, ti, tj = None):
        if tj is None:
            return [self.data[i][t_i].flatten() for (i,t_i) in enumerate(ti)]
        else:
            return  [self.data[i][t_i][:,t_j].flatten() for i,(t_i,t_j) in enumerate(zip(ti,tj))]

class MagneticMoment(PerAtomData):
    _shortDoc = "Magnetic moment"
    
    def getData(self, calc):
        self.nsteps = len(calc)        
        self.plot_options['dx'] = 0.1
        
        self.x_title = "Magnetic moment"
        self.data = []
        for _, g in calc.evol:
            self.data.append(g.magmom())
        self.calculate()

class AbsMagneticMoment(PerAtomData):
    _shortDoc = "Absolute magnetic moment"
    
    def getData(self, calc):
        self.nsteps = len(calc)
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

class TopologicalIndices(PerAtomData):
    _isTimeEvol = False
    _shortDoc = 'Topological indices'
    
    def getData(self, calc):
        self.plot_options['threshold'] = 0.5
        self.x_title = 'VP TIs'
        self.data = []
        for _, g in calc.evol:
            # pbc, ratio, rm_small, eps
            self.data.append(g.vp_ti())
        self.calculate()

    def calculateTotal(self):
        return self.data

    def calculatePartial(self, t):
        result = []
        for d, ti in zip(self.data, t):
            result += [d[tij] for tij in ti]
        return result
    
    def plotData(self, plot_type):
        from plotdata import VarXData
        return VarXData(self, **self.plot_options)
