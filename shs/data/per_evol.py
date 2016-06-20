#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

from shs.files.mde import MDEFile
from shs.files.pdos import PDOSFile
from abstract import PerEvolData


class MDEData(PerEvolData):
    """ Functions describing calculations (E, temp, pressure...) 
    """
    _shortDoc = "MDE evolution"

    def getData(self, calc):
        mde = MDEFile(calc)
        calc.nsteps = mde.n_steps
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

    def getData(self, calc):
        dos = PDOSFile(calc)
        nspin = dos.get_n_spin()
        ev = dos.get_energy_values()
        names = ['energy']
        data = []
        raw_names, raw_data = dos.get_partial_dos(species=[], ldict={})
        if nspin == 2:
            for n, d in zip(raw_names, raw_data):
                names.append(n + '_up')
                data.append(d[::2])
                names.append(n + '_dn')
                data.append(-1.0 * d[1::2])
        elif nspin == 1:
            names += raw_names
            data += raw_data
        self.parseData(names, ev, data, {'nspin': nspin})

    def parseData(self, names, x, data, info):
        self.x_title = names[0]
        self.x = x
        self.y_titles = names[1:]
        self.y = data
        self.info = info
