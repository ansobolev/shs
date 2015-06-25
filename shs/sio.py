#!/usr/bin/env python
# -*- coding : utf8 -*-

""" Container for working with files in FDF, XV, MDE, OUT format
"""

import os
import string
import re
import glob

from collections import OrderedDict
import xml.dom.minidom as xml

import numpy as np
import const as C
import errors as Err

# --- Methods ---

def data2file(data, title, fname):
    ''' Writes data to file fname.
    Input:
      -> data (numpy array, list of numpy arrays) - data to be written
      -> title (iterable object) - title corresponding to each column of data
      -> fname (str) - name of file  
    '''
    file = open(fname, 'w')
# names - a list with names
    if type(title) == type([]): 
        names = title
    else:
        raise Err.NotImplementedError('SIO.Data2File : As of now title must be a list!')
   
    fmt = ''
    for i in range(len(names)):    
        fmt += ' {0[%i]:^8} ' % (i, )    

    file.write(fmt.format(names) + '\n')
    d = np.column_stack(tuple(data))
    np.savetxt(file, d, fmt='%-9.5f')
    file.close()


def ReadFDFLines(infile, head = ''):
    '''Returns an FDF file and all the %include files as split strings
       infile = input file
       (c) Inelastica package
    '''
    absfile = os.path.abspath(infile)
    if head == '':                                                                                                                                                                  
        head = os.path.split(absfile)[0]
    else:
        infile = os.path.join(head, infile)                                                                                                                                                                                                                                                                             

    file = open(infile,'r')                           
    lines = []
    tmp = file.readline()                                                                                                                                                           
    while tmp != '':                                                                                                                                                                
        if len(tmp)>3:                                                                                                                                                              
            tmp = string.split(tmp)                                                                                                                                                 
            for ii,s in enumerate(tmp):  # Remove comments                                                                                                                          
                if s[0]=="#":                                                                                                                                                       
                    break                                                                                                                                                           
            if s[0]=='#':                                                                                                                                                           
                tmp = tmp[0:ii]                                                                                                                                                     
            if len(tmp)>0:                                                                                                                                                          
                if tmp[0] == '%include':                                                                                                                                            
                    subfile = tmp[1]                                                                                                                                       
                    tmp2 = ReadFDFLines(subfile, head=head)                                                                                                     
                    lines += tmp2                                                                                                                                                   
                else:                                                                                                                                                               
                    lines.append(tmp)                                                                                                                                               
        tmp = file.readline()                                                                                                                                                       
    file.close()
    return lines

def any2dict(data):
    ''' Converts list of FDF file lines to a dictionary of FDF file options 
    '''  
    fddict = OrderedDict()
    is_block = False                                                                                                                                                                
    for i, fdline in enumerate(data):
        if (is_block):                                                                                                                                                              
            if (fdline[0] == '%endblock'):                                                                                                                                          
                is_block = False                                                                                                                                                    
                continue                                                                                                                                                            
            fddict[key].append(fdline)                                                                                                                                              
            continue                                                                                                                                                                
        key = fdline.pop(0)                                                                                                                                                         
        if (key == '%block'):                                                                                                                                                       
            is_block = True                                                                                                                                                         
            key = fdline.pop(0)                                                                                                                                                     
            fdline = []                                                                                                                                                             
        fddict[key] = [i] + fdline                                                                                                                                                        
    return fddict    

# --- Iterators ---

def findfiles(fileparts,top=None):
    'Iterate on the files found by a list of file parts, (c) A.Vorontsov'
    import fnmatch
    if top == None: top=os.getcwd()

    for path, dirlist, filelist in os.walk(top):
        for filepart in fileparts:
            for name in fnmatch.filter(sorted(filelist),filepart):
                yield os.path.join(path,name)

def openfiles(filenames):       # open files with different types
    'Iterate on the file descriptors of different types, (c) A.Vorontsov'
    import gzip, bz2
    for name in filenames:
        if not os.path.isfile(name):
            yield os.popen(name,'r')
        elif name.endswith(".gz"):
            yield gzip.open(name,'r')
        elif name.endswith(".bz2"):
            yield bz2.BZ2File(name,'r')
        else:
            yield open(name,'r')

def catfiles(sources):   # make union stream
    'Concatenate file contents, make a whole list of strings, (c) A.Vorontsov'
    for s in sources:
        for item in s:
            yield item

def fileblocks(lines,separator):  # cut file with separator
    'Cut file contents in blocks with separator, (c) A.Vorontsov'
    dat=[]
    istep = -1
    for line in lines:
        if line.count(separator)<>0:
            istep += 1
            if dat<>[]:
                yield istep, dat
                dat=[]
        if line<>'': dat+=[line]
#    if dat<>[]:
#        yield istep, dat

def timesteps(blocks,time=None):         # filter of time
    ''' Filters blocks generator by time steps 
    '''
    for istep, b in blocks:
        if time is None:
            yield istep, b
            continue
        if istep in time:
            yield istep, b

# --- Classes ---

class PDOSFile():
    """ Class for reading partial density of electronic states, use code
    """
    def __init__(self, calc):
        # get file name
        if os.path.isfile(os.path.join(calc.dir, 'pdos.xml')):
            self.file_name = os.path.join(calc.dir, 'pdos.xml')
        elif os.path.isfile(os.path.join(calc.dir, calc.sl + '.PDOS')):
            self.file_name = os.path.join(calc.dir, calc.sl + '.PDOS')
        else:
            raise Exception('No possible DOS files found!')
        print 'calc.DOS : Took %s as DOS file' % (self.file_name, )
        self.dom = xml.parse(self.file_name)

    # Reading XML files (c) Inelastica package

    def GetPDOSnspin(self):
        "Returns an integer for the number of spins (variable nspin)"
        node = self.dom.getElementsByTagName('nspin')[0] # First (and only) entry
        return int(node.childNodes[0].data)

    def GetPDOSenergyValues(self):
        # Read energy values
        node = self.dom.getElementsByTagName('energy_values')[0] # First (and only) entry
        data = node.childNodes[0].data.split()
        return np.array(data, dtype = np.float)

    def GetPDOSfromOrbitals(self, species, ldict):
        nodes = self.dom.getElementsByTagName('orbital')
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


class FDFFile():
    
    def __init__(self, filename, mode = 'r'):
        self.fn = filename
        act = {'r' : self.readfdf,
               'w' : self.writefdf}
        act.get(mode)()
    
    def readfdf(self):
        lines = ReadFDFLines(self.fn)
        self.f = open(self.fn, 'r')
        self.d = any2dict(lines)
        
    def writefdf(self):
        self.f = open(self.fn, 'w')
    
    def __del__(self):
        self.f.flush()
        self.f.close()
       

class XVFile():
    ''' Class for reading XV file
    '''
    def __init__(self, xvf):
        self.f = open(xvf, 'r')
        self.vc = []
        self.ityp = []
        self.z = []
        self.crd = []
        self.v = []
        lines = self.f.readlines()
        for line in lines[0:3]:
            self.vc.append([float(x) for x in line.split()[0:3]])
        for line in lines[4:]:
            ls = line.split()
            self.ityp.append(int(ls[0]))
            self.z.append(int(ls[1]))
            self.crd.append([float(x) for x in line.split()[2:5]])
            self.v.append([float(x) for x in line.split()[5:]])        
        
    def __del__(self):
        self.f.flush()
        self.f.close()


class LMPFile():
    
    def __init__(self, lmpf):
        self.f = open(lmpf, 'r')
        self.steps = []
        self.vc = []
        self.atoms = []
        self.aunit = 'Bohr'
        self.vcunit = 'Bohr'

        lines = self.f.readlines()
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
        i = step[:,0]
        ityp = step[:,1]
        label = np.array([C.PeriodicTable[typ] for typ in ityp.astype(np.int)])
        crd = step[:,2:]
        self.atoms.append(np.rec.fromarrays([crd,ityp,i,label], formats=['3f8','i4','i4', 'S2'], names=['crd','itype','id','label']))

    def __del__(self):
        self.f.flush()
        self.f.close()

class MDEFile():
    """ Class for reading MDE files
    """

    def __init__(self, calc):
        """ MDE file data initialization

        :param calc: Siesta calculation
        """
        # get MDE file name
        mde_names = glob.glob(os.path.join(calc.dir, '*.MDE'))
        if len(mde_names) != 1:
            raise ValueError('Calc.ReadMDE: Either no or too many MDE files in %s' % (dir, ))
        dt = {'names': ('step', 'temp', 'e_ks', 'e_tot', 'vol', 'p'),
              'formats': ('i4','f4','f4','f4','f4','f4')
              }
        self.file_name = mde_names[0]
        data = np.loadtxt(self.file_name, dtype=dt)
        self.nsteps = len(data['step'])
        print 'SIO.ReadMDE : Found %i steps' % (self.nsteps,)
        data['step'] = np.arange(self.nsteps)
        self.data = data


class ANIFile():
    ''' Class for reading ANI file
    '''
# ANI-file is in Angstroms

    def __init__(self, anif, stepnums):
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
        xvf = os.path.join(os.path.dirname(anif),self.sl + '.XV')
        xv = XVFile(xvf)
# vc in Bohr
        vc = np.array(xv.vc)
        self.vcunit = 'Bohr'
        nat = len(xv.crd)
        lines = self.f.readlines()
        if nat != int(lines[0]):
            raise Err.FileError('SIO.ANIFile: Number of atoms in XV and ANI files MUST be equal!')
        nsteps  = len(lines)/(nat + 2)
        print 'SIO.ANIFile : Found %i steps' % (nsteps,)
# Steps
        if any(x<0 for x in stepnums):
            stepnums = [istep+sign(istep)*nsteps for istep in stepnums]
        self.steps = stepnums        
# crd in Angstroms
        for istep in stepnums:
# ANI file offset
            offset = istep * (nat + 2)
            step = np.array([line.split() for line in lines[offset+2:offset+nat+2]])
            self.vc.append(vc)
            crd = step[:,1:]
            typ = step[:,0]
            i = np.arange(1, nat+1)
            types = np.unique(typ)
            label2ityp = dict(zip(types,xrange(1, len(types) + 1)))
            ityp = np.array([label2ityp[l] for l in typ])
            self.atoms.append(np.rec.fromarrays([crd,ityp,i,typ], formats=['3f8','i4','i4','S2'], names=['crd','itype','id','label']))
        self.aunit = 'Ang'
        
    def __del__(self):
        self.f.flush()
        self.f.close()



class OUTFile():
    
    def __init__(self, outfns, dir, stepnums):
        ''' Reading data from stdout siesta file format
        Input:
         -> outfns - a list of output file name patterns
         -> dir - a calc directory
         -> stepnums - a list of step numbers (int).
           If negative, then numbers count from the end  
        '''
        import itertools
        def sign(x):
            return 1 if x < 0 else 0
        
        if not hasattr(outfns, '__iter__'):
            outfns = [outfns, ]
        filenames = findfiles(outfns, top = dir)
        print 'SiestaIO.OUTFile: Found OUT files:'
        for fn in filenames:          
            print '                  -> %s' % (fn,)
        
        filenames = findfiles(outfns, top = dir)
        files = openfiles(filenames)
        lines = catfiles(files)
        blocks = fileblocks(lines, 'Begin')
        if any(x<0 for x in stepnums):
            s, blocks = itertools.tee(blocks, 2)
            nsteps = sum(1 for x in s)
            print 'SiestaIO.OUTFile: Number of steps found -> %i' % (nsteps,)
            stepnums = [istep+sign(istep)*nsteps for istep in stepnums]
        self.steps = stepnums
        self.atoms = []
        self.vc = []
        self.spins = []
        self.forces = []
        for istep, block in timesteps(blocks, self.steps):
            read_atoms = False
            read_vc = False
            read_spins = False
            read_forces = False
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
        crd = a[:,0:3]
        ityp = a[:,3]
        i = a[:,4]
        typ = a[:,5]
        try:
            return np.rec.fromarrays([crd,ityp,i,typ], formats=['3f8','i4','i4','S2'], names=['crd','itype','id','label'])
        except (ValueError,):
            return np.rec.fromarrays([crd,ityp,i,typ], formats=['3f8','i4','S2','i4'], names=['crd','itype','label','id'])

    def list2vc(self, vc_list):
# find unit of measurement
        head = vc_list.pop(0)
        vcu = re.search(r'\(.+?\)', str(head))
        self.vcunit = vcu.group(0)[1:-1]
        return np.array(vc_list).astype('float')

    def list2forces(self, forces_list):
        forces = [line[1:] for line in forces_list[1:]]
        return np.rec.fromarrays([np.array(forces).astype('float')], names = 'forces', formats = '3f8' )

    def list2spins(self, spins_list, typ):
        'Now supports only collinear spin'
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
            except:
                o += 1
        orbs.append(o)
        ind = 7
        for i in range(1,len(ntyp)):
            ind += orbs[i-1]*(ntyp[species[i-1]]+1)
            species.append(spins_list[ind][1])
            o = 0
            for spins_line in spins_list[ind+2:ind+5]:
                try:
                    int(spins_line[0])
                    break
                except:
                    o += 1
            orbs.append(o)
# found number of species and orb lines, now go get spins (up & dn differently)
        ind = 6 + orbs[0]
        for i in range(len(ntyp)):
            nl = orbs[i]*ntyp[species[i]]
            s = np.array(spins_list[ind:ind+nl:orbs[i]])
            ats = s[:,0].astype('int')
            spins = s[:,1].astype('float')
            up[ats-1] = spins
            try:
                ind += nl + 3 + orbs[i+1]
            except:
                ind += nl + 4
        ind += 3 + orbs[0]
        for i in range(len(ntyp)):
            nl = orbs[i]*ntyp[species[i]]
            s = np.array(spins_list[ind:ind+nl:orbs[i]])
            ats = s[:,0].astype('int')
            spins = s[:,1].astype('float')
            dn[ats-1] = spins
            try:
                ind += nl + 3 + orbs[i+1]
            except:
                pass
        return np.rec.fromarrays([up, dn], formats=['f4','f4'], names=['up','dn'])
