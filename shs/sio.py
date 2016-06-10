#!/usr/bin/env python
# -*- coding : utf8 -*-

""" Container for working with files in FDF, XV, MDE, OUT format
"""

from collections import OrderedDict

import numpy as np
import os

import const
import errors
from io.xv import XVFile


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

def find_files(file_parts, top=None):
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
        xv = XVFile(os.path.dirname(anif))
        # vc in Bohr
        vc = np.array(xv.vectors)
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


