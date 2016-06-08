#!/usr/bin/env python
# -*- coding : utf8 -*-

""" Container for working with files in FDF, XV, MDE, OUT format
"""

from collections import OrderedDict

import numpy as np
import os
import re

import const
import errors


# --- Methods ---


def data2file(data, title, file_name):
    """
    Writes data to file.
    :param data: (numpy array, list of numpy arrays) - data to be written
    :param title: (iterable object) - title corresponding to each column of data
    :param file_name: (str) - name of file for datato be written to
    :return:
    """
    f = open(file_name, 'w')
# names - a list with names
    if isinstance(title, list):
        names = title
    else:
        raise errors.NotImplementedError('SIO.Data2File : As of now title must be a list!')
   
    fmt = ''
    for i in range(len(names)):    
        fmt += ' {0[%i]:^8} ' % (i, )    

    f.write(fmt.format(names) + '\n')
    d = np.column_stack(tuple(data))
    np.savetxt(f, d, fmt='%-9.5f')
    f.close()


def read_fdf_lines(infile, head=''):
    """
    Returns an FDF file and all the %include files as split strings
       (c) Inelastica package

    :param infile: input file
    :param head: a top-level directory
    :return: a list of fdf file lines
    """
    if head == '':
        head = os.path.split(os.path.abspath(infile))[0]
    else:
        infile = os.path.join(head, infile)                                                                                                                                                                                                                                                                             

    f = open(infile, 'r')
    lines = []
    line = f.readline()
    # till the end of file
    while line != '':
        if len(line) > 3:
            # throw away comments
            comment_idx = line.find('#')
            if comment_idx != -1:
                line = line[:comment_idx]

            line = line.split()

            if len(line) > 0:
                if line[0] == '%include':
                    sub_file = line[1]
                    sub_lines = read_fdf_lines(sub_file, head=head)
                    lines += sub_lines
                else:                                                                                                                                                               
                    lines.append(line)
        line = f.readline()
    f.close()
    return lines


def fdf_lines_to_dict(lines):
    """
    Converts list of FDF file lines to a dictionary of FDF file options
    :param lines: a list of FDF file lines
    :return: a dictionary of file options
    """
    fdf_dict = OrderedDict()
    is_block = False
    block_key = None
    for i, fdf_line in enumerate(lines):
        key = fdf_line[0]
        if key == '%block':
            is_block = True
            block_key = fdf_line[1]
            fdf_dict[block_key] = [i, ]
            continue
        if is_block:
            if fdf_line[0] != '%endblock':
                fdf_dict[block_key].append(fdf_line)
            else:
                is_block = False
                block_key = None
                continue
        fdf_dict[key] = [i, ] + fdf_line[1:]
    return fdf_dict


# --- Iterators ---

def findfiles(file_parts, top=None):
    """Iterate on the files found by a list of file parts, (c) A.Vorontsov"""
    import fnmatch
    if top is None:
        top = os.getcwd()

    for path, dir_list, file_list in os.walk(top):
        for file_part in file_parts:
            for name in fnmatch.filter(sorted(file_list), file_part):
                yield os.path.join(path, name)


def open_files(file_names):       # open files with different types
    """Iterate on the file descriptors of different types, (c) A.Vorontsov"""
    import gzip
    import bz2

    for name in file_names:
        if not os.path.isfile(name):
            yield os.popen(name, 'r')
        elif name.endswith(".gz"):
            yield gzip.open(name, 'r')
        elif name.endswith(".bz2"):
            yield bz2.BZ2File(name, 'r')
        else:
            yield open(name, 'r')


def cat_files(sources):   # make union stream
    """Concatenate file contents, make a whole list of strings, (c) A.Vorontsov"""
    for s in sources:
        for item in s:
            yield item


def file_blocks(lines, separator):  # cut file with separator
    """Cut file contents in blocks with separator, (c) A.Vorontsov"""
    dat = []
    i_step = -1
    for line in lines:
        if line.count(separator) != 0:
            i_step += 1
            if dat:
                yield i_step, dat
                dat = []
        if line != '':
            dat += [line]
#    if dat<>[]:
#        yield istep, dat


def time_steps(blocks, time=None):         # filter of time
    """ Filters blocks generator by time steps
    """
    for i_step, b in blocks:
        if time is None:
            yield i_step, b
            continue
        if i_step in time:
            yield i_step, b


# --- Classes ---


class FDFFile:
    
    def __init__(self, filename, mode='r'):
        self.name = filename
        self.file = None
        self.fdf_dict = None
        act = {'r': self.read_fdf,
               'w': self.write_fdf}
        act.get(mode)()
    
    def read_fdf(self):
        lines = read_fdf_lines(self.name)
        self.file = open(self.name, 'r')
        self.fdf_dict = fdf_lines_to_dict(lines)
        
    def write_fdf(self):
        self.file = open(self.name, 'w')
    
    def __del__(self):
        self.file.flush()
        self.file.close()
       

class XVFile:
    """ Class for reading XV file
    """
    def __init__(self, xvf):
        self.f = open(xvf, 'r')
        self.vc = []
        self.i_type = []
        self.z = []
        self.crd = []
        self.v = []
        lines = self.f.readlines()
        for line in lines[0:3]:
            self.vc.append([float(x) for x in line.split()[0:3]])
        for line in lines[4:]:
            ls = line.split()
            self.i_type.append(int(ls[0]))
            self.z.append(int(ls[1]))
            self.crd.append([float(x) for x in line.split()[2:5]])
            self.v.append([float(x) for x in line.split()[5:]])        
        
    def __del__(self):
        self.f.flush()
        self.f.close()


class LMPFile:
    
    def __init__(self, file_name):
        self.file = open(file_name, 'r')
        self.steps = []
        self.vc = []
        self.atoms = []
        self.aunit = 'Bohr'
        self.vcunit = 'Bohr'

        lines = self.file.readlines()
# steps
        self.steps.append(int(lines[0].split('=')[1]))
# number of atoms
        nat = int(lines[2].split()[0])
# lattice vectors 
        x = float(lines[5].split()[1])
        y = float(lines[6].split()[1])
        z = float(lines[7].split()[1])        
        self.vc.append(np.diag([x, y, z]))
        step = np.array([line.split() for line in lines[11:nat+11]])
        i = step[:, 0]
        ityp = step[:, 1]
        label = np.array([const.PeriodicTable[typ] for typ in ityp.astype(np.int)])
        crd = step[:, 2:]
        self.atoms.append(np.rec.fromarrays([crd, ityp, i, label],
                                            formats=['3f8', 'i4', 'i4', 'S2'],
                                            names=['crd', 'itype', 'id', 'label']))

    def __del__(self):
        self.file.flush()
        self.file.close()


class ANIFile:
    # ANI-file is in Angstroms

    def __init__(self, anif, stepnums):
        """ Class for reading ANI file
        """
        def sign(x):
            return 1 if x < 0 else 0
        
        print 'SIO.ANIFile : Beware that ANI file stores only coordinates but not lattice vectors!'
        print '              It\'s OK if we do NVT calculations, as we can read vectors from XV file,'
        print '              but for NPT calculations we\'d better use OUT file for reading geometry.'
        self.label = []
        self.atoms = []
        self.vc = []
        self.f = open(anif, 'r')
        # anif - the name of ANI file, we can get system label from here and use it for reading vc from XV
        self.sl = os.path.basename(anif).split('.')[0]
        xvf = os.path.join(os.path.dirname(anif), self.sl + '.XV')
        xv = XVFile(xvf)
        # vc in Bohr
        vc = np.array(xv.vc)
        self.vcunit = 'Bohr'
        nat = len(xv.crd)
        lines = self.f.readlines()
        if nat != int(lines[0]):
            raise errors.FileError('SIO.ANIFile: Number of atoms in XV and ANI files MUST be equal!')
        nsteps = len(lines) / (nat + 2)
        print 'SIO.ANIFile : Found %i steps' % (nsteps,)
        # Steps
        if any(x < 0 for x in stepnums):
            stepnums = [istep+sign(istep)*nsteps for istep in stepnums]
        self.steps = stepnums        
        # crd in Angstroms
        for istep in stepnums:
            # ANI file offset
            offset = istep * (nat + 2)
            step = np.array([line.split() for line in lines[offset+2:offset+nat+2]])
            self.vc.append(vc)
            crd = step[:, 1:]
            typ = step[:, 0]
            i = np.arange(1, nat+1)
            types = np.unique(typ)
            label2ityp = dict(zip(types, xrange(1, len(types) + 1)))
            ityp = np.array([label2ityp[l] for l in typ])
            self.atoms.append(np.rec.fromarrays([crd, ityp, i, typ],
                                                formats=['3f8', 'i4', 'i4', 'S2'],
                                                names=['crd', 'itype', 'id', 'label']))
        self.aunit = 'Ang'
        
    def __del__(self):
        self.f.flush()
        self.f.close()


class OUTFile:
    
    def __init__(self, outfns, calc_dir, stepnums):
        """
        Reading data from stdout siesta file format
        :param outfns: a list of output file name patterns
        :param calc_dir: a calc directory
        :param stepnums: a list of step numbers (int). If negative, then numbers count from the end
        """
        import itertools

        def sign(x):
            return 1 if x < 0 else 0
        
        if not hasattr(outfns, '__iter__'):
            outfns = [outfns, ]
        filenames = findfiles(outfns, top=calc_dir)
        print 'SiestaIO.OUTFile: Found OUT files:'
        for fn in filenames:          
            print '                  -> %s' % (fn,)
        
        filenames = findfiles(outfns, top=calc_dir)
        files = open_files(filenames)
        lines = cat_files(files)
        blocks = file_blocks(lines, 'Begin')
        if any(x < 0 for x in stepnums):
            s, blocks = itertools.tee(blocks, 2)
            nsteps = sum(1 for _ in s)
            print 'SiestaIO.OUTFile: Number of steps found -> %i' % (nsteps,)
            stepnums = [istep+sign(istep)*nsteps for istep in stepnums]
        self.steps = stepnums
        self.atoms = []
        self.vc = []
        self.spins = []
        self.forces = []
        for istep, block in time_steps(blocks, self.steps):
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
            self.spins.append(self.list2spins(spins_list, self.atoms[-1]['label']))
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

    def list2forces(self, forces_list):
        forces = [line[1:] for line in forces_list[1:]]
        return np.rec.fromarrays([np.array(forces).astype('float')],
                                 names='forces',
                                 formats='3f8')

    def list2spins(self, spins_list, typ):
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
