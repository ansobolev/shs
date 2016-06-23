# ---------------------------------------------
#
# The file out.py is part of the shs project.  
# Copyright (c) 2016 Andrey Sobolev  
# License GNU GPL v.2
# See http://github.com/ansobolev/shs for details
#
# ---------------------------------------------
import re
import os
from datetime import datetime
import numpy as np

from shs.sio import find_files, open_files, cat_files, file_blocks, time_steps, read_fdf_lines, fdf_lines_to_dict


class OUTFile:

    def __init__(self, calc_dir, file_name, step_numbers=None):
        """
        Reading data from stdout siesta file format
        :param file_name: a name of an OUT file
        :param calc_dir: a calc directory
        :param step_numbers: a list of step numbers (int). If negative, then numbers count from the end
        """
        def sign(x):
            return 1 if x < 0 else 0

        file_names = list(find_files(file_name, top=calc_dir))
        if len(file_names) != 1:
            raise ValueError, 'files.OUTFile: Either no or many OUT files found in the current calculation directory'
        self.calc_dir = calc_dir
        self.name = file_names[0]
        print 'files.OUTFile: Found OUT file: %s' % self.name
        files = open_files(file_names)
        lines = cat_files(files)
        blocks = list(file_blocks(lines, 'Begin'))

        self.n_steps = len(blocks) - 1
        print 'files.OUTFile: Number of steps found -> %i' % self.n_steps

        if step_numbers is None:
            step_numbers = range(self.n_steps)
        if any(x < 0 for x in step_numbers):
            step_numbers = [i_step + sign(i_step) * self.n_steps for i_step in step_numbers]
        self.steps = step_numbers
        self.run_info = {}
        self.fdf_dict = None
        self.finished = False
        self.energies = {}
        self.atoms = []
        self.aunit = None
        self.vc = []
        self.vcunit = None
        self.spins = []
        self.forces = []

        # parsing start block
        self._parse_start_block(blocks[0])

        # parsing end block
        self._parse_end_block(blocks[-1])

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

    def _parse_start_block(self, block):
        lines = block[1]
        self.run_info['version'] = lines[0].split(':')[1].strip()
        self.run_info['arch'] = lines[1].split(':')[1].strip()
        self.run_info['fflags'] = lines[2].split(':')[1].strip()
        self.run_info['is_parallel'] = (lines[3].split()[0] == 'PARALLEL')
        self.run_info['nodes'] = int(lines[5].split()[3])
        self.run_info['start_time'] = datetime.strptime(lines[6].split('n:')[1].strip(), '%d-%b-%Y  %H:%M:%S')
        self.run_info['end_time'] = None

        fdf_beg = [i for i, s in enumerate(lines) if 'Dump of input data file' in s][0]
        fdf_end = [i for i, s in enumerate(lines) if 'End of input data file' in s][0]
        self.fdf_dict = fdf_lines_to_dict(read_fdf_lines(lines[fdf_beg + 1:fdf_end], head=self.calc_dir))

    def _parse_end_block(self, block):
        lines = block[1]
        self.finished = ('End of run' in lines[-1])
        if self.finished:
            self.run_info['end_time'] = datetime.strptime(lines[-1].split('n:')[1].strip(), '%d-%b-%Y  %H:%M:%S')
            self.run_info['elapsed'] = self.run_info['end_time'] - self.run_info['start_time']
        else:
            self.run_info['elapsed'] = datetime.fromtimestamp(os.path.getmtime(file)) - self.run_info['start_time']
            return -1
        idx = [i for i, s in enumerate(lines) if 'Maximum dynamic memory allocated' in s][0 if self.n_steps != 1 else 1]
        lines = lines[idx:]
        e_idx = [i for i, s in enumerate(lines) if 'Final energy' in s][0] + 1
        e_labels = ['band', 'kinetic', 'hartree', 'ext_field', 'xc', 'ion-el', 'ion-ion', 'kinion', 'total']
        self.energies = {label: float(lines[e_idx + i].split('=')[1]) for i, label in enumerate(e_labels)}


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
