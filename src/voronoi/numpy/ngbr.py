#!/usr/bin/python 
# __*__ coding: utf8 __*__

#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2012
#


oneline = "Find nearest neighbors table"

#import os
import numpy as np

from base_numpy import model_base
try:
    from voronoi.model_voronoi import model_voronoi as MV
except (ImportError,):
    from shs.voronoi.model_voronoi import model_voronoi as MV

# --------------------------------------------------------------------
class Free_class:
    pass

#=============================================================================
class model_ngbr(model_base):

    def __init__(self,d={}):
        model_base.__init__(self,d)

    def make_verlet(self, r):
        " Make Verlet for the model  "

        print "Verlet go. r=",r

        vc = self.vc
        crd = self.atoms['crd']

        ver = Free_class()

        ver.imax = (vc/r).astype(int) + 1
        ver.dr = vc / ver.imax
        ver.ind = np.mod((crd/ver.dr).astype(int), ver.imax)

        self.verlet=ver
        print "Verlet done"    

    def make_ngbr_short(self,r):
        " makes Short Neighbours table "
    
        print "Short NGBR go. r=",r 

        if not hasattr(self,'verlet'): self.make_verlet(r/2.5)
   
        ng = Free_class()
        ng.r = r

        ind = self.verlet.ind
        dr = self.verlet.dr
        imax = self.verlet.imax

        m = int(r/np.min(dr)) + 1
        print 'm = ', m

        ng.ind=[]

        for vi in ind:
            b0 = (np.abs(ind[:,0]-vi[0]) < m) | ((ind[:,0]-vi[0])%imax[0] < m) | ((vi[0] - ind[:,0])%imax[0] < m)
            b1 = (np.abs(ind[:,1]-vi[1]) < m) | ((ind[:,1]-vi[1])%imax[1] < m) | ((vi[1] - ind[:,1])%imax[1] < m)
            b2 = (np.abs(ind[:,2]-vi[2]) < m) | ((ind[:,2]-vi[2])%imax[2] < m) | ((vi[2] - ind[:,2])%imax[2] < m)
            idn, = np.where(b0 * b1 * b2)
            ng.ind.append(idn)
        self.ngbr_short=ng
        print "Short NGBR done" 

    def make_ngbr(self,r=None,part=''):  
        " makes Neighbours table with distances "

        if r == None: 
            r = np.max(self.vc)/3.
        print "NGBR numpy go. r=",r 
#        if not hasattr(self,'ngbr_short'): self.make_ngbr_short(r)

        ng=Free_class()
        r2=r*r
        ng.r=r

#        ngsh = self.ngbr_short.ind
# crd - to box, vc - orthogonal
        crd, vc = to_orthogonal(self.atoms['crd'], self.vc)

        ng.ind = []

        vn, r2n = distance(crd, vc)

        for iat in range(crd.shape[0]):
            ivn = vn[iat]
            ir2n = r2n[iat]
            idn, = np.nonzero((ir2n < r2) & (ir2n > 0.))
            ng.ind.append(np.rec.fromarrays([idn, ivn[idn], ir2n[idn]], names = 'n, vec, r2', formats = 'i4, 3f4, f4'))
        self.ngbr=ng
        print "NGBR numpy done"
        
    def toMV(self):
        ''' get model_voronoi instance.
        let it be so until we can get voronoi_numpy working somehow
        '''
        mv = MV()
# legend - to list
        legend = list(self.atoms.dtype.names)
        crd_index = legend.index('crd')
        mv.legend = legend[:crd_index] + ['x','y','z'] + legend[crd_index+1:]
        v1 = np.linalg.det(self.vc)
        v2 = self.vc[0,0]*self.vc[1,1]*self.vc[2,2]
        print 'NGBR.toMV: Vcell = %f, Vorth = %f' % (v1, v2)
        mv.vc = [float(self.vc[0,0]),float(self.vc[1,1]),float(self.vc[2,2])]
# self.atoms - to box
        self.atoms['crd'], vc = to_orthogonal(self.atoms['crd'], self.vc)
# atoms - to list of lists        
        mv.atoms = []
        atoms_list = list(self.atoms)
        for iat, line in enumerate(atoms_list):
            mv.atoms.append([])
            for el in flatten(line):
                if type(el).__name__ == 'float64' or type(el).__name__ == 'float32':
                    mv.atoms[iat].append(float(el))
                elif type(el).__name__ == 'int32':
                    mv.atoms[iat].append(int(el))
                elif type(el).__name__ == 'string_':
                    mv.atoms[iat].append(str(el))
# ngbr - to dict
        mv.ngbr = Free_class()        
        mv.ngbr.index = [{} for atom in mv.atoms]
        for i, ind in enumerate(self.ngbr.ind):
            for ng in ind:
                mv.ngbr.index[i][ng['n']] = []
                for el in flatten(list(ng))[1:]:
                    if type(el).__name__ == 'float64' or type(el).__name__ == 'float32':
                        mv.ngbr.index[i][ng['n']].append(float(el))
        return mv

def distance(crd, vc):
    ''' Find distances between atoms based on PBC in a supercell built on vc vectors
    In:
     -> crd - coordinates array
     -> vc - lattice vectors
     -> n - a tuple of 2 crd index lists (or None if we need to find all-to-all distances) 
    ''' 
    vc_inv = np.linalg.inv(vc)
    crd_vc = np.dot(crd, vc_inv)
    n = len(crd_vc)
    sij = crd_vc[None,...]-crd_vc[:, None,...]
# periodic boundary conditions
    sij[sij > 0.5] -= 1.0
    sij[sij < -0.5] += 1.0
#    print sij.shape
    sij = sij.reshape(n*n, 3)
    rij = np.dot(sij, vc)
    r2 = (rij**2.0).sum(axis = 1)
    return rij.reshape(n,n,3), r2.reshape(n,n)

def flatten(x):
    result = []
    for v in x:
        if hasattr(v, '__iter__') and not isinstance(v, basestring):
            result.extend(flatten(v))
        else:
            result.append(v)
    return result

def to_orthogonal(crd, vc):
    vc_inv = np.linalg.inv(vc)
    crd = np.dot(crd, vc_inv)
    crd[crd < 0.] += 1. 
    crd[crd > 1.] -= 1.
    vc_diag = np.diag(vc)
    orth_vc = np.diag(vc_diag)
    crd = np.dot(crd, orth_vc)
    return crd, orth_vc    