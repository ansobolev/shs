# ---------------------------------------------
#
# The file pdos.py is part of the shs project.  
# Copyright (c) 2016 Andrey Sobolev  
# License GNU GPL v.2
# See http://github.com/ansobolev/shs for details
#
# ---------------------------------------------
from xml.dom import minidom as xml

import numpy as np
import os


class PDOSFile:
    """ Class for reading partial density of electronic states, use code
    """
    def __init__(self, calc):
        # get file name
        if os.path.isfile(os.path.join(calc.dir, 'pdos.xml')):
            self.file_name = os.path.join(calc.dir, 'pdos.xml')
        elif os.path.isfile(os.path.join(calc.dir, calc.label + '.PDOS')):
            self.file_name = os.path.join(calc.dir, calc.label + '.PDOS')
        else:
            raise Exception('No possible DOS files found!')
        print 'calc.DOS : Took %s as DOS file' % (self.file_name, )
        self.dom = xml.parse(self.file_name)

    # Reading XML files (c) Inelastica package

    def get_nspin(self):
        """Returns an integer for the number of spins (variable nspin)"""
        node = self.dom.getElementsByTagName('nspin')[0]  # First (and only) entry
        return int(node.childNodes[0].data)

    def get_energy_values(self):
        # Read energy values
        node = self.dom.getElementsByTagName('energy_values')[0]  # First (and only) entry
        data = node.childNodes[0].data.split()
        return np.array(data, dtype=np.float)

    def get_PDOS_from_orbitals(self, species, ldict):
        nodes = self.dom.getElementsByTagName('orbital')
        names = []
        d = []
        orbs = {0: 's',
                1: 'p',
                2: 'd',
                3: 'f'}
        if not species:
            species = set([node.attributes['species'].value for node in nodes])
        if not ldict:
            for sp in species:
                sp_nodes = [node for node in nodes if node.attributes['species'].value == sp]
                sp_l = set([int(node.attributes['l'].value) for node in sp_nodes])
                ldict[sp] = sorted(list(sp_l))

        for sp, ls in ldict.iteritems():
            for l in ls:
                data = [node.getElementsByTagName('data')[0].childNodes[0].data.split() for node in nodes
                        if node.attributes['species'].value == sp and int(node.attributes['l'].value) == l]
                data = np.array(data, dtype=np.float)
                names.append(sp + '-' + orbs[l])
                d.append(data.sum(axis=0))
        return names, d