import inspect
from collections import OrderedDict


class FDFOptionList(object):

    def __init__(self,parent,panel):
        self._ol = OrderedDict()
        self._fdf_ol = OrderedDict()
        options = inspect.getmembers(panel, inspect.isclass)
        options.sort(key=lambda option: option[1].priority)
        for (name, option) in options:
            instance = option(parent) 
            self._ol[name] = instance
            # get all fdf texts in fdf option list
            if type(instance.fdf_text) == str:
                self._fdf_ol[instance.fdf_text.lower()] = instance
            elif type(instance.fdf_text) == list:
                for text in instance.fdf_text:
                    self._fdf_ol[text.lower()] = instance

    @property
    def ol(self):
        return self._ol

    @property
    def fdf_ol(self):
        return self._fdf_ol

    def __iter__(self):
        for (name, value) in self._ol.iteritems():
            yield value
