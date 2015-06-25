#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

import os
import glob

from shs import sio
from abstract import PerEvolData


class MDEData(PerEvolData):
    """ Functions describing calculations (E, temp, pressure...) 
    """
    _shortDoc = "MDE evolution"

    def getData(self, calc):

        mde = sio.MDEFile(mdef[0])
        calc.nsteps = mde.nsteps
        self.parseData(mde.data)

    def parseData(self, data):
        self.x_title = data.dtype.names[0]
        self.x = data[self.x_title]
        self.y_titles = data.dtype.names[1:]
        self.y = [data[ty] for ty in self.y_titles]
    

class DOSData(PerEvolData):
    """ Densities of electronic states
    """
    _shortDoc = "Density of states (DOS)"
    
    def getData(self, calc, title=None):
        (names, x, data), info = calc.dos()
        self.x_title = names[0]
        self.x = x
        self.y_titles = names[1:]
        self.y = data
        self.info = info
