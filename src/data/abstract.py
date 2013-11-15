#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

from abc import ABCMeta, abstractproperty, abstractmethod

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
    _isFunction = True
    _isTimeEvol = False
    _isHistogram = False
