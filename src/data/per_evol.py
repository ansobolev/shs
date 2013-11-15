#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#
from abstract import PerEvolData
import plotdata

class MDEData(PerEvolData):
    _shortDoc = "MDE evolution"

    def getData(self, calc, title = None):
        nsteps, data = calc.mde()
        self.x_title = data.dtype.names[0]
        self.x = data[self.x_title]
        self.y_titles = data.dtype.names[1:]
        self.y = [data[ty] for ty in self.y_titles]

    def plotData(self):
        return plotdata.FunctionData(self)