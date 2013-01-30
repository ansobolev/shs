#!/usr/bin/env python 
# __*__ coding: utf8 __*__

import numpy as np

'Class describing Voronoi polyhedra (each as a separate instance)'

def sort_polygons(crd):
    # calculate centroid of the polygon
    n = crd.shape[1] # of corners
    # center of mass
    c = np.sum(crd, axis = 1) / n
    crd_c = (crd.swapaxes(0,1) - c).swapaxes(0,1)
    # angles with respect to CoM position
    ang = (np.arctan2(crd_c[:,:,1], crd_c[:,:,0]) + 2 * np.pi) % (2.0 * np.pi)
    # now sort ang and get indices
    ind = np.argsort(ang, axis = 1)
    # array of static indices (see http://stackoverflow.com/questions/6155649/sort-a-numpy-array-by-another-array-along-a-particular-axis)
    sind = np.ogrid[0:crd.shape[0], 0:crd.shape[1]]
    return ind, crd_c[sind[0],ind]
    
def vp_areas(crd):
    # get areas using the shoelace formula
    x1 = np.concatenate((crd, crd[:,0,np.newaxis]), axis = 1)
    y2 = np.concatenate((np.zeros((crd.shape[0],1,crd.shape[2])), crd), axis = 1)[:,:,::-1]
    y2[:,:,1] *= -1. 
    areas = 0.5 * np.abs(np.sum(np.sum(x1 * y2, axis = 2), axis = 1))
    return areas

class vp():
    
    def __init__(self, center, verts, crd, edges, faces):
        '''Input:
          -> verts - array of vertex numbers
          -> crd - array of vertex coordinates
          -> edges - adjacency list of vertices
          -> faces - dictionary of vertices comprising faces (don't know yet whether we need it)
        '''
        self.c = center
# vertex renumbering goes here (need?)
        e_flat = edges.flatten()
        self.nv = len(verts)
        self.crd = crd
        self.e = np.searchsorted(verts, e_flat).reshape(edges.shape[0], 3)
# max number of vertices per face 
        nvf_max = max([faces[k].shape[0] for k in faces.keys()])
        self.f = []
        vf = [[] for _ in range(nvf_max - 2)]
        for k, val in faces.iteritems():
            nvf = val.shape[0]
            vf[nvf - 3].append(np.searchsorted(verts, val))
        for ivf in vf:
            try:
                self.f.append(np.vstack(ivf))
            except:
                continue
        
    def get_face_area(self):
        areas = []
        for fi in self.f:
            crd_v =self.crd[fi]
            _, crd_v = sort_polygons(crd_v)
            areas.append(vp_areas(crd_v))
        return areas
    
    def remove_small_faces(self, eps = 0.05):
        areas = self.get_face_area()
        nc = self.nv
        f_ind = []
        v_ind = {}
        v_new = []
        for ind, (fi, ai) in enumerate(zip(self.f, areas)):
            n = np.nonzero(ai < eps)[0]
            for ni in n:
# here face is removed
                # centroid vertex
                v_new.append(np.sum(self.crd[fi[ni]], axis = 0) / fi[ni].shape[0])
                # fi[ni] - vertex numbers to be substituted
                # the number of vertex c
                nc += 1
                # indices of objects to be deleted
                v_ind[nc] = fi[ni]
                f_ind.append((ind, ni))
        print v_ind        
        print self.e
        e_flat = self.e.flatten()
        for k, val in v_ind.iteritems():
            e_flat[np.in1d(e_flat, val)] = k
        self.e = e_flat.reshape(self.nv, 3)
        print self.e
                 
    def get_edge_length(self):
        pass
        
        
    
    