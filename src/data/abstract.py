#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

from abc import ABCMeta, abstractproperty, abstractmethod

import shs.errors

import plotdata

class classproperty(object):
    def __init__(self, getter):
        self.getter= getter
    def __get__(self, instance, owner):
        return self.getter(owner)

class AbstractData(object):
    __metaclass__ = ABCMeta
    _isFunction = None
    _isTimeEvol = None
    _isHistogram = None
    _shortDoc = "Abstract class for data"

    def __init__(self, *args, **kwds):
        assert args[0].__class__.__name__ == "SiestaCalc"
        calc = args[0]
        self.calc = calc
        self.title = calc.dir
        self.getData(calc)

    @classproperty
    def isFunction(self):
        assert self._isFunction is not None
        return self._isFunction

    @classproperty
    def isTimeEvol(self):
        assert self._isTimeEvol is not None
        return self._isTimeEvol

    @classproperty
    def isHistogram(self):
        assert self._isHistogram is not None
        return self._isHistogram

    @classmethod
    def shortDoc(self):
        return self._shortDoc

    @abstractmethod
    def getData(self, calc):
        pass
    
    def plotData(self, plot_type):
        pass

class PerAtomData(AbstractData):
    _isFunction = False
    _isTimeEvol = True
    _isHistogram = True

class PerEvolData(AbstractData):
    _isFunction = True
    _isTimeEvol = False
    _isHistogram = False

class PerTypeData(AbstractData):
    """ Base class for per-type functions
    """
    
    _isFunction = True
    _isTimeEvol = False
    _isHistogram = False

    def __init__(self, *args, **kwds):
        self.partial = kwds.get("partial", True)
        super(PerTypeData, self).__init__(*args, **kwds)

    def plotData(self):
        return plotdata.FunctionData(self)

class OneTypeData(PerTypeData):
    """ Data with consistent types (VAF, MSD)
    """
    
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