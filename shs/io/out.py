# ---------------------------------------------
#
# The file out.py is part of the shs project.  
# Copyright (c) 2016 Andrey Sobolev  
# License GNU GPL v.2
# See http://github.com/ansobolev/shs for details
#
# ---------------------------------------------
import numpy as np
import re

from sio import find_files, open_files, cat_files, file_blocks, time_steps


class OUTFile:

    def __init__(self, name_patterns, calc_dir, step_numbers):
        """
        Reading data from stdout siesta file format
        :param name_patterns: a list of output file name patterns
        :param calc_dir: a calc directory
        :param step_numbers: a list of step numbers (int). If negative, then numbers count from the end
        """
        import itertools

        def sign(x):
            return 1 if x < 0 else 0

        if not hasattr(name_patterns, '__iter__'):
            name_patterns = [name_patterns, ]
        file_names = find_files(name_patterns, top=calc_dir)
        print 'SiestaIO.OUTFile: Found OUT files:'
        for fn in file_names:
            print '                  -> %s' % (fn,)

        file_names = find_files(name_patterns, top=calc_dir)
        files = open_files(file_names)
        lines = cat_files(files)
        blocks = file_blocks(lines, 'Begin')
        if any(x < 0 for x in step_numbers):
            s, blocks = itertools.tee(blocks, 2)
            nsteps = sum(1 for _ in s)
            print 'SiestaIO.OUTFile: Number of steps found -> %i' % (nsteps,)
            step_numbers = [i_step + sign(i_step) * nsteps for i_step in step_numbers]
        self.steps = step_numbers
        self.atoms = []
        self.aunit = None
        self.vc = []
        self.vcunit = None
        self.spins = []
        self.forces = []
        for i_step, block in time_steps(blocks, self.steps):
            read_atoms = False
            read_vc = False
            read_spins = False
            read_forces = False
            forces_list = []
            for line in block:
                # getting coordinates block
                if line.find('outcoor: Atomic coordinates') != -1:
                    read_atoms = True
                    at_list = []
                if read_atoms:
                    if line == '\n':
                        read_atoms = False
                        continue
                    at_list.append(line.split())
                # getting cell vectors block
                if line.find('outcell: Unit cell vectors') != -1:
                    read_vc = True
                    vc_list = []
                if read_vc:
                    if line == '\n':
                        read_vc = False
                        continue
                    vc_list.append(line.split())
                # getting spins block
                if line.find('Atomic and Orbital Populations') != -1:
                    read_spins = True
                    spins_list = []
                if read_spins:
                    if line.find('siesta') != -1:
                        read_spins = False
                        continue
                    spins_list.append(line.split())
                # getting forces block
                if line.find('Atomic forces') != -1:
                    read_forces = True
                    forces_list = []
                if read_forces:
                    if line.find('--------') != -1:
                        read_forces = False
                        continue
                    forces_list.append(line.split())
            self.atoms.append(self.list2atoms(at_list))
            self.vc.append(self.list2vc(vc_list))
            self.spins.append(list2spins(spins_list, self.atoms[-1]['label']))
#            self.forces.append(self.list2forces(forces_list))

    def list2atoms(self, at_list):
        # find unit of measurement
        head = at_list.pop(0)
        au = re.search(r'\(.+?\)', str(head))
        self.aunit = au.group(0)[1:-1]
        a = np.array(at_list)
        crd = a[:, 0:3]
        ityp = a[:, 3]
        i = a[:, 4]
        typ = a[:, 5]
        try:
            return np.rec.fromarrays([crd, ityp, i, typ],
                                     formats=['3f8', 'i4', 'i4', 'S2'],
                                     names=['crd', 'itype', 'id', 'label'])
        except (ValueError,):
            return np.rec.fromarrays([crd, ityp, i, typ],
                                     formats=['3f8', 'i4', 'S2', 'i4'],
                                     names=['crd', 'itype', 'label', 'id'])

    def list2vc(self, vc_list):
        # find unit of measurement
        head = vc_list.pop(0)
        vcu = re.search(r'\(.+?\)', str(head))
        self.vcunit = vcu.group(0)[1:-1]
        return np.array(vc_list).astype('float')


def list2forces(forces_list):
    forces = [line[1:] for line in forces_list[1:]]
    return np.rec.fromarrays([np.array(forces).astype('float')],
                             names='forces',
                             formats='3f8')


def list2spins(spins_list, typ):
    """Now supports only collinear spin"""
    # as mulliken charges come in tables by species, let's find how many atoms of each species
    # are there in our model
    from collections import defaultdict
    nat = len(typ)
    ntyp = defaultdict(int)
    for x in typ:
        ntyp[x] += 1
    # now we know the number of atoms (both of each type and total)
    # initializing arrays
    up = np.zeros(nat, dtype='float')
    dn = np.zeros(nat, dtype='float')
    # TODO: read orbital partitioning of charge
    species = []
    orbs = []
    species.append(spins_list[4][1])
    o = 0
    for spins_line in spins_list[6:9]:
        try:
            int(spins_line[0])
            break
        except ValueError:
            o += 1
    orbs.append(o)
    ind = 7
    for i in range(1, len(ntyp)):
        ind += orbs[i-1]*(ntyp[species[i-1]]+1)
        species.append(spins_list[ind][1])
        o = 0
        for spins_line in spins_list[ind+2:ind+5]:
            try:
                int(spins_line[0])
                break
            except ValueError:
                o += 1
        orbs.append(o)
    # found number of species and orb lines, now go get spins (up & dn differently)
    ind = 6 + orbs[0]
    for i in range(len(ntyp)):
        nl = orbs[i]*ntyp[species[i]]
        s = np.array(spins_list[ind:ind+nl:orbs[i]])
        ats = s[:, 0].astype('int')
        spins = s[:, 1].astype('float')
        up[ats-1] = spins
        try:
            ind += nl + 3 + orbs[i+1]
        except IndexError:
            ind += nl + 4
    ind += 3 + orbs[0]
    for i in range(len(ntyp)):
        nl = orbs[i] * ntyp[species[i]]
        s = np.array(spins_list[ind:ind+nl:orbs[i]])
        ats = s[:, 0].astype('int')
        spins = s[:, 1].astype('float')
        dn[ats-1] = spins
        try:
            ind += nl + 3 + orbs[i+1]
        except IndexError:
            pass
    return np.rec.fromarrays([up, dn], formats=['f4', 'f4'], names=['up', 'dn'])
