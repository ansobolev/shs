#!/usr/bin/env python

''' The module providing interface from SHS to GUI
'''

import os, glob
import numpy as np

import shs.calc

def getcalc(cdir, ctype, steps):
    copts = {'.FDF':'fdf',
             '.ANI':'ani',
             '.output':'out',
             'pdos.xml':'fdf'}
    
    return shs.calc.SiestaCalc(cdir, dtype = copts[ctype], steps = steps)

def getvalue(cdir, label):
    c = shs.calc.SiestaCalc(cdir, dtype = 'fdf')
    return c.opts[label].value
        
def setvalue(cdir, label, value):
    c = shs.calc.SiestaCalc(cdir, dtype = 'fdf')
    c.opts[label].value = value
    return 0

def getdata(ptype, clist):
    """Returns data according to plot type from a list of calcs
    Input:
     -> ptype (int) - plot type 
     -> clist (list) - a list of SiestaCalc instances 
    """
    if clist == []:
        raise ValueError('interface.getdata: No calculations selected!')
# plot options
    pdata = {0: get_mdedata,
             1: get_rdfdata,
             2: get_msddata,
             3: get_vafdata,
             4: get_dos,
             5: get_cn,
             6: get_cnevolution,
             7: get_facearea,
             8: get_totalfacearea,
             9: get_totalvolume,
             10: get_ksph,
             11: get_mmagmom,
             12: get_mabsmagmom,
             13: get_spinflips
             }
    return pdata[ptype](clist)

def get_mdedata(clist):
    'Returns MDE data suitable for plotting'
    return [c.readmde() for c in clist], None

def get_rdfdata(clist):
    'Returns RDF data suitable for plotting'
    rdfdata = []
    for c in clist:
        title, r, rdf = c.rdf(partial = True ,n = None)
        formats = ['f8' for _ in title]
        rdfdata.append(np.rec.fromarrays([r] + rdf, names = title, formats = formats))
    return rdfdata, None

def get_msddata(clist):
    'Returns MSD data suitable for plotting'
    msddata = []
    for c in clist:
        title, t, msd = c.msd()
        formats = ['f8' for _ in title]
        msddata.append(np.rec.fromarrays([t] + msd, names = title, formats = formats))
    return msddata, None

def get_vafdata(clist):
    'Returns velocity autocorrelation function suitable for plotting'
    vafdata = []
    for c in clist:
        title, t, vaf = c.vaf()
        formats = ['f8' for _ in title]
        vafdata.append(np.rec.fromarrays([t] + vaf, names = title, formats = formats))
    return vafdata, None

def get_dos(clist):
    'Returns projected PDOS on orbitals'
    dosdata = []
    dosinfo = []
    for c in clist:
        (title, ev, dos), info = c.dos()
        formats = ['f8' for _ in title]
        dosdata.append(np.rec.fromarrays([ev] + dos, names = title, formats = formats))
        dosinfo.append(info)
    return dosdata, dosinfo

def get_cn(clist):
    'Returns VP RDFs and coordination numbers (full and partial)'
    cndata = []
    cninfo = []
    for c in clist:
        (title, r, cn), info = c.cn()
        formats = ['f8' for _ in title]
        cndata.append(np.rec.fromarrays([r] + cn, names = title, formats = formats))
        cninfo.append(info)
    return cndata, cninfo

def get_cnevolution(clist):
    'Returns time evolution of partial CNs'
    cn_evol = []
    cne_info = []
    for c in clist:
        (title, x, pcne), info = c.pcn_evolution()
        formats = ['f8' for _ in title]        
        cn_evol.append(np.rec.fromarrays([x] + pcne, names = title, formats = formats))
        cne_info.append(info)
    return cn_evol, cne_info

def get_facearea(clist):
    'Returns partial VP face area distribution'
    facedata = []
    faceinfo = []
    for c in clist:
        (title, area, data), info = c.vp_facearea()
        formats = ['f8' for _ in title]
        facedata.append(np.rec.fromarrays([area] + data, names = title, formats = formats))
        faceinfo.append(info)
    return facedata, faceinfo

    
    vp_fa = []
    for c in clist:
        vp_fa.append(c.vp_facearea())
    return vp_fa, None

def get_totalfacearea(clist):
    'Returns partial VP total face area distribution'
    vp_tfa = []
    for c in clist:
        vp_tfa.append(c.vp_totfacearea(da = 0.2))
    return vp_tfa, None

def get_totalvolume(clist):
    'Returns partial VP total volume distribution'
    vp_tv = []
    for c in clist:
        vp_tv.append(c.vp_totvolume())
    return vp_tv, None

def get_ksph(clist):
    'Returns VP sphericity coefficient distribution'
    vp_ksph = []
    for c in clist:
        vp_ksph.append(c.vp_ksph())
    return vp_ksph, None

def get_mmagmom(clist):
    'Returns mean magnetic moment for atoms'
    mmagmom = []
    for c in clist:
        mmagmom.append(c.mmagmom())
    return mmagmom, None

def get_mabsmagmom(clist):
    'Returns mean absolute value of magnetic moment for atoms'
    mmagmom = []
    for c in clist:
        mmagmom.append(c.mabsmagmom())
    return mmagmom, None

def get_spinflips(clist):
    'Returns the number of spin flips for atoms in system'
    sflips = []
    for c in clist:
        sflips.append(c.spinflips())
    return sflips, None

        
def isCalcOfType(ctype, **kwargs):
    if 'fn' in kwargs.keys():
        options = {'.FDF' : [f for f in kwargs['fn'] if f.endswith('.fdf')],
               '.ANI' : [f for f in kwargs['fn'] if f.endswith('.ANI')],
               '.output' : [d for d in kwargs['dn'] if d == 'stdout'],
               'pdos.xml' : [f for f in kwargs['fn'] if f == 'pdos.xml']}
    elif 'dir' in kwargs.keys():
        options = {'.FDF' : [f for f in os.listdir(kwargs['dir']) if f.endswith('.fdf')],
               '.ANI' : [f for f in os.listdir(kwargs['dir']) if f.endswith('.ANI')],
               '.output' : [d for d in os.listdir(kwargs['dir']) if d == 'stdout'],
               'pdos.xml' : [f for f in os.listdir(kwargs['dir']) if f == 'pdos.xml']}
    return options[ctype]

def GetNumMDESteps(cdir):
    mdefn = glob.glob(os.path.join(cdir, '*.MDE'))
    if len(mdefn) == 0:
        return None
    nsteps = sum(1 for line in open(mdefn[0]) if line[0] != '#')
    return nsteps

def GetCalcInfo():
    pass

if __name__ == '__main__':
    pass