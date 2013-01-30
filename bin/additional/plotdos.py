#!/usr/bin/env python 


import numpy as np
import xml.dom.minidom as xml

# Reading XML files (c) Inelastica package

def GetPDOSnspin(dom):
    "Returns an integer for the number of spins (variable nspin)"
    node = dom.getElementsByTagName('nspin')[0] # First (and only) entry
    return int(node.childNodes[0].data)

def GetPDOSenergyValues(dom):
    # Read energy values
    node = dom.getElementsByTagName('energy_values')[0] # First (and only) entry
    data = node.childNodes[0].data.split()
    return np.array(data, dtype = np.float)

def GetPDOSfromOrbitals(dom,species,ldict):
    nodes = dom.getElementsByTagName('orbital')
    names = []
    d = []
    orbs = {0:'s', 1:'p', 2:'d', 3:'f'}
    if not species:
        species = set([node.attributes['species'].value for node in nodes])
    if not ldict:
        for sp in species:
            sp_nodes = [node for node in nodes if node.attributes['species'].value == sp]
            sp_l = set([int(node.attributes['l'].value) for node in sp_nodes])
            ldict[sp] = sorted(list(sp_l))
    
    for sp, ls in ldict.iteritems():
        for l in ls:
            data = [node.getElementsByTagName('data')[0].childNodes[0].data.split() for node in nodes \
                    if node.attributes['species'].value == sp and int(node.attributes['l'].value) == l]
            data = np.array(data, dtype = np.float)
            names.append(sp + '-' + orbs[l])
            d.append(data.sum(axis = 0))                
    return names, d

def ReadPDOSFile(filename, species = [], ldict = {}):
    # Reads SIESTA *.PDOS files summing up contributions from orbitals
    # belonging to a subset specified by the keywords
    dom = xml.parse(filename)
    nspin = GetPDOSnspin(dom)
    ev = GetPDOSenergyValues(dom)
    names = ['energy']
    data = [ev]
    formats = ['f8']
    raw_names, raw_data = GetPDOSfromOrbitals(dom,species,ldict)
    if nspin == 2:
         for n, d in zip(raw_names, raw_data):
             names.append(n + '_up')
             data.append(d[::2])
             formats.append('f8')
             names.append(n + '_dn')
             data.append(-1.0 * d[1::2])
             formats.append('f8')
    elif nspin == 1:
        names += raw_names
        data +=raw_data
        formats += (['f8' for _ in names])
    pdos = np.rec.fromarrays(data, formats = formats, names = names)
    return nspin,pdos

if __name__ == '__main__':
    fn = '../../test/pdos.xml'
    print ReadPDOSFile(fn)    