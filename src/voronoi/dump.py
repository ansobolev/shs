#!/usr/bin/python 
#1/usr/bin/env python
# __*__ coding: utf8 __*__

oneline = "Read different types of models"

import os
#=======================================================================
def dump2crd(file_in,file_out):
    
    f=open(file_in,'r')
    while f.readline().count('TIMESTEP')==0:
        pass
    ln=[i.strip() for i in f.readlines()]
    l=[i.split() for i in ln]
    f.close()

    ntypes=max(int(i[1]) for i in l[8:])

    dat  = 'LAMMPS Description. time=0 \n \n'
    dat += '%11s  atoms \n' %ln[2]
    dat +='%11i  atom types \n \n' % ntypes
    dat +='%s xlo xhi \n' %ln[4]
    dat +='%s ylo yhi \n' %ln[5]
    dat +='%s zlo zhi \n \n' %ln[6]

    dat +='Atoms \n \n'
    for i in l[8:]:
        dat+='%s %s %s %s %s \n' % tuple(i[0:5])
    dat +='\n Velocities \n \n'
    for i in l[8:]:
        dat+='%s %s %s %s \n' % (i[0],i[5],i[6],i[7])

    f = open(file_out,"w")
    f.write(dat)
    f.close()
    return
#=========================================================================
def dump2pdb(file_in,file_out):

    f=open(file_in,'r')
    while f.readline().count('TIMESTEP')==0:
        pass
    ln=[i.strip() for i in f.readlines()]
    l=[i.split() for i in ln]
    f.close()

    dat  ="""REMARK  atoms as in 
REMARK
REMARK< i5><  > X     <  >    <x f8.3><y f8.3><z f8.3><f6.2><f6.2> \n"""

    s= 'ATOM  %5i  IS %c     %4i    %8.3f%8.3f%8.3f%6.2f%6.2f \n'
    j=33

    for i in l[8:]:
        j += 1
        if j==240: j=33
        dat+= s%(int(i[0]),chr(j),int(i[1]),float(i[2]),float(i[3]),float(i[4]),0.0,float(i[1]))

    f = open(file_out,"w")
    f.write(dat)
    f.close()
    return
#=========================================================================
def gen_find(fileparts,top=None):
    'Iterate on the files found by a list of file parts, (c) A.Vorontsov'
    import fnmatch
    if top == None: top=os.getcwd()

    for path, dirlist, filelist in os.walk(top):
        for filepart in fileparts:
            for name in fnmatch.filter(filelist,filepart):
                yield os.path.join(path,name)

def gen_open(filenames):       # open files with different types
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

def gen_cat(sources):   # make union stream
    'Concatenate file contents, make a whole list of strings, (c) A.Vorontsov'
    for s in sources:
        for item in s:
            yield item

def gen_blocks(lines,separator='TIMESTEP'):  # cut file with separator
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

def time_filter(gn_block,time=None):         # filter of time
    ''' Filters blocks generator by time steps 
    '''
    for istep, b in gn_block:
        if time is None:
            yield istep, b
            continue
        if istep in time:
            yield istep, b
#-----------------------------------------------------------------
def format_default(s):
    dd='x f,y f,z f,id i,type s,vx f,vy f,vz f,kl i,nkl i,nel i'.split(',')
    ddd= dict([i.split() for i in dd])
    return [ddd.get(i,'s') for i in s]
#---------------------------------------------------------------
def format_data(dl,format='i s f f f f f f'.split()):
    def intt(x): return int(float(x))
    d={'i': intt,'f': float,'s': str}
    for li in dl:
        ll=[i for i in li.split() if i not in '(){}[]']
        yield [d[j](i) for i,j in zip(ll,format)] 
 
#-----------------------------------------------------
def sst_ani_block(file):
    dat=[]
    for i in file:
        if len(i.split())==1:
            if dat<>[]:
                yield dat
                dat=[]
            if i<>'': dat+=[i]
    if dat<>[]:
        yield dat 
#-------------------------------------------------
def sst_ani(file):
    istep = -1
    for i in sst_ani_block(file):
        istep += 1
        nat = int(i[0])
        yield istep, i[2:]

#======================================================
class dump_shs():
    ''' Class making dump of SHS Geometry and Evolution instances 
    '''
    def __init__(self):
        pass
    
    def shs_geom(self, geom):
        'Make dump out of Geom class instance'
        ddd = {'atoms' : geom.atoms,
               'box' : geom.vc}
        return ddd
    
    def shs_evol(self, evol):
        '''Make dump out of Evol class instance
    Returns list of dictionaries
        '''
        dddlist = []
        for es in evol.geom:
            dddlist.append(self.shs_geom(es))
        return dddlist

#======================================================
class dump_sst:
    def __init__(self, files=[], legend='type x y z'):
        if not hasattr(files,'__iter__'):
            files = [files]

        self.files = files
        self.legend = legend
        self.format =  ''
        self.vc = [0,0,0]

    def sst_xv(self,file):
        it = open(file)
        a = [float(k)*0.529 for k in it.next().split()][:3]
        b = [float(k)*0.529 for k in it.next().split()][:3]
        c = [float(k)*0.529 for k in it.next().split()][:3]
        self.vc = [a, b, c]
        return {'box': self.vc}

    def sst_sph(self,file,leg_st='id type x y z rad charge spin'):
        it=open(file)
        self.data=it

    def sst_ani(self, anif, xvf, step = None, leg_st='type x y z'):
        ofiles=gen_open([anif])
        f = gen_cat(ofiles)
        itt = (i for istep, i in sst_ani(f) if istep == step)
        box = self.sst_xv(xvf)

        for it in itt:
            leg_list=leg_st.split()
            ft_list=format_default(leg_list) 

            atoms=[i for i in format_data(it,ft_list)]
            ll=len(atoms[0])
            ddd = {'atoms':atoms,'legend':leg_list[:ll],'format':ft_list[:ll],'time':step}
            ddd.update(box)
        return ddd

# TO DO: Dump from out files
    def sst_out(self, outf, step = None, leg_st='type x y z'):
        ofiles=gen_open([outf])
        f = gen_cat(ofiles)
        itt = (i for istep, i in sst_ani(f) if istep == step)
        box = self.sst_xv(outf)

        for it in itt:
            leg_list=leg_st.split()
            ft_list=format_default(leg_list) 

            atoms=[i for i in format_data(it,ft_list)]
            ll=len(atoms[0])
            ddd = {'atoms':atoms,'legend':leg_list[:ll],'format':ft_list[:ll],'time':step}
            ddd.update(box)
        return ddd

    def __iter__(self):
        ddd = {'format':self.format}

        for file in self.files:
            it=open(file)
            n=int(it.next())
            a=[float(k) for k in it.next().split()]
            b=[float(k) for k in it.next().split()]
            c=[float(k) for k in it.next().split()]
            leg_list=self.legend.split()
            ft_list=format_default(leg_list) 
#{'atoms':atoms,'legend':leg_list[:ll],'format':ft_list[:ll],'box':[a,b,c]} 
            yield ddd