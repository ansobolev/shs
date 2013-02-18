#!/usr/bin/env python
# -*- coding : utf8 -*-

#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

import numpy as np
import numpy.lib.recfunctions as nlrf
import pyvoro

class model_voronoi():
    
    def __init__(self, d = {}):
# time: timestep number
        self.time=d.get('time',0)
# box: numpy array of lattice vectors
        box = d.get('box',np.zeros((3,3)))
        self.box = box
        if box.shape == (3,3): self.vc = box
        elif box.shape == (3): self.vc = np.diag(box)
        else:                  raise ValueError ('Box should be (3,3) or (3) array')
# atoms: atoms numpy array
        atoms = d.get('atoms',[])
        
        leg_list = atoms.dtype.names

        if not 'id' in leg_list:       # add 'id' column
            atoms = nlrf.append_fields(atoms, 'id', np.arange(len(atoms))+1, asrecarray=True, usemask=False)
   
        if not 'itype' in leg_list:    # add 'itype' column
            if 'label' in leg_list:
                labels = list(np.unique(atoms['label']))
                labels = dict(zip(labels, range(1,len(labels)+1)))
                ityp = np.array([labels[atom['label']] for atom in atoms])
                atoms = nlrf.append_fields(atoms, 'itype', ityp, asrecarray=True, usemask=False)
            else:   
                atoms = nlrf.append_fields(atoms, 'itype', np.ones(len(atoms)), asrecarray=True, usemask=False)

        self.atoms = atoms
        
    def voronoi(self, pbc = True, ratio = 0.5):
        ''' The main function for computing Voronoi tesselation 
        '''
        self.v = pyvoro.compute_voronoi(self.atoms['crd'], self.vc, np.max(self.vc)/4.)
    
    def vp_faces(self):
        return None
    
    def vp_neighbors(self, rm_small = False, eps = 0.05):
        ''' Finds nearest neighbors according to VP tesselation
        '''
        if not hasattr(self, 'v'):
            self.voronoi()
        ngbrs = []
        for iat, vi in enumerate(self.v):
            ngbrs.append([iat,] + [fi['adjacent_cell'] for fi in vi['faces']])
        return ngbrs
    
    def vp_volumes(self, f, partial = False):
        ''' Returns volumes and total areas of VPs 
        '''
        
        if not hasattr(self, 'v'):
            self.voronoi()
        self.vp_volume = np.array([vi['volume'] for vi in self.v])
        self.vp_area = np.array([vi['surface'] for vi in self.v])
        return self.vp_volume, self.vp_area
    
    def vp_face_area(self, f):
        ''' Returns a dictionary of face areas 
        '''
        if not hasattr(self, 'v'):
            self.voronoi()
        areas = [{} for _ in self.v]
        for iat, vi in enumerate(self.v):
            for fi in vi['faces']:
                jat = fi['adjacent_cell']
                areas[iat][jat] = fi['area']
                areas[jat][iat] = fi['area']
        return areas

    def remove_small_faces(self, faces, areas, eps = 0.5):
        ''' Removes all faces from self.v, area of which is less than eps 
        '''
        nat = len(self.v)
        for iat in range(nat):
            # Small faces
            small_faces = [ngbr for ngbr in areas[iat].keys() if areas[iat][ngbr] < eps]
            for sf in small_faces:
                pass        