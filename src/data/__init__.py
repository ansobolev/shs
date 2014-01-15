#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

import per_atom
import per_evol
import per_type
import per_step

class Data(object):
    _types = ['Function', 'Histogram', 'Time evolution']

    def __init__(self):
        import inspect
        # dirty hack; I don't know how to populate the list of modules imported within current file
        data_modules = [per_atom, per_evol, per_type, per_step]
    
        data_class_list = []
        for mod in data_modules:
            data_class_list += inspect.getmembers(mod, lambda m: inspect.isclass(m) and not inspect.isabstract(m))
        self._classes = dict(zip(self._types, [{} for _ in self._types]))
        for name, cl in data_class_list:
            if cl.isFunction:
                self._classes['Function'][cl.shortDoc()] = cl
            if cl.isHistogram:
                self._classes['Histogram'][cl.shortDoc()] = cl
            if cl.isTimeEvol:
                self._classes['Time evolution'][cl.shortDoc()] = cl

    def types(self):
        return sorted(self._types)

    def classes(self, t):
        assert t in self._types
        return sorted(self._classes[t].keys())

    def dataClass(self, t, c):
        assert t in self._types
        assert c in self._classes[t].keys()
        return self._classes[t][c]