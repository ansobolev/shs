#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

from abc import ABCMeta, abstractmethod

import shs.errors
import plotdata


class ClassProperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class AbstractData(object):
    __metaclass__ = ABCMeta
    _isFunction = None
    _isTimeEvol = None
    _isHistogram = None
    _shortDoc = None
    
    def __init__(self, *args, **kwds):
        assert args[0].__class__.__name__ == "SiestaCalc"
        calc = args[0]
        self.calc = calc
        self.title = calc.dir
        self.plot_options = {}
        self.x_title = ""
        self.y = []
        self.y_titles = []
        self.getData(calc)

    @ClassProperty
    def isFunction(self):
        assert self._isFunction is not None
        return self._isFunction

    @ClassProperty
    def isTimeEvol(self):
        assert self._isTimeEvol is not None
        return self._isTimeEvol

    @ClassProperty
    def isHistogram(self):
        assert self._isHistogram is not None
        return self._isHistogram

    @classmethod
    def shortDoc(self):
        assert self._shortDoc is not None
        return self._shortDoc

    @abstractmethod
    def getData(self, calc):
        pass

    @abstractmethod
    def calculate(self):
        pass

    @abstractmethod
    def calculatePartial(self, *args):
        pass
    
    def plotData(self, plot_type, plot_options = None):
        if plot_options is None:
            plot_options = self.plot_options
        choice = {"Function" : (self.isFunction, plotdata.FunctionData),
                  "Histogram": (self.isHistogram, plotdata.HistogramData),
                  "Time evolution": (self.isTimeEvol, plotdata.TimeEvolData)}
        assertion, plot_class = choice[plot_type]
        assert assertion
        return plot_class(self, **plot_options)


class PerAtomData(AbstractData):
    _isFunction = False
    _isTimeEvol = True
    _isHistogram = True

    def __init__(self, *args, **kwds):
        self.partial = kwds.get("partial", True)
        self.pbc = kwds.get("pbc", True)
        self.ratio = kwds.get("ratio", 0.7)
        super(PerAtomData, self).__init__(*args, **kwds)

    def calculate(self):
        if self.partial:
            _, types = self.calc.evol.getAtomsByType()
            self.y_titles = sorted(types.keys())
            for y_title in self.y_titles:
                self.y.append(self.calculatePartial(types[y_title]))
        else:
            self.y_titles = ["Total"]
            self.y = self.calculateTotal()
    
    def calculatePartial(self, n):
        return [self.data[i][n_i] for i, n_i in enumerate(n)]
    
    def calculateTotal(self):
        return self.data


class PerEvolData(AbstractData):
    _isFunction = True
    _isTimeEvol = False
    _isHistogram = False

    def calculate(self):
        pass

    def calculatePartial(self, n):
        pass


class PerTypeData(AbstractData):
    """ Base class for per-type functions
    """
    _isFunction = True
    _isTimeEvol = False
    _isHistogram = False

    def __init__(self, *args, **kwds):
        self.partial = kwds.get("partial", True)
        super(PerTypeData, self).__init__(*args, **kwds)


class PerStepData(AbstractData):
    """ Base class for per-type functions
    """
    _isFunction = False
    _isTimeEvol = True
    _isHistogram = False

    def __init__(self, *args, **kwds):
        self.partial = kwds.get("partial", True)
        self.rm_small = kwds.get("rm_small", True)
        self.eps = kwds.get("eps", True)
        super(PerStepData, self).__init__(*args, **kwds)


class OneTypeData(PerTypeData):
    """ Data with consistent types (VAF, MSD)
    """
    
    def getData(self, calc):
        # taking coordinates of atoms belonging to the list n
        self.traj, _ = calc.evol.trajectory()
        self.x_title = "Steps"
        self.calculate()

    def calculate(self):
        data_type = self.__class__.__name__
        if self.partial:
            if not self.calc.evol.areTypesConsistent():
                raise shs.errors.AtomTypeError(
                    "%s: Types should be consistent to get partial results"
                    % (data_type,))
            # now we know that types are consistent
            n = self.calc.evol[0].types.toDict()
        else:
            n = {"Total": self.calc.evol.natoms}
        for label, nat in n.iteritems():
            x, y = self.calculatePartial(nat)
            self.y.append(y)
            self.y_titles.append(label)
        self.x = x


class InteractingTypesData(PerTypeData):
    """ Data with non-consistent interacting types (RDF)
    """
    
