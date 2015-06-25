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
        if box.shape == (3,3):
            self.vc = box
        elif box.shape == (3):
            self.vc = np.diag(box)
        else:
            raise ValueError ('Box should be (3,3) or (3) array')
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

    def voronoi(self, pbc, ratio):
        """ The main function for computing Voronoi tessellation
        """
        vc = [[0., self.vc[0,0]], [0., self.vc[1,1]], [0., self.vc[2,2]]]
        self.v = pyvoro.compute_voronoi(self.atoms['crd'], vc, np.max(self.vc)/4., periodic=[True]*3)
    
    def vp_faces(self):
        return None
    
    def vp_neighbors(self, rm_small = False, eps = 0.05):
        ''' Finds nearest neighbors according to VP tesselation
        '''
        if not hasattr(self, 'v'):
            self.voronoi()
        ngbrs = []
        for iat, vi in enumerate(self.v):
            ngbrs.append(np.array([iat,] + [fi['adjacent_cell'] for fi in vi['faces'] 
                                            if (not rm_small or fi['area']  > eps)]))
        return ngbrs
    
    def vp_volumes(self, f, partial = False):
        ''' Returns volumes and total areas of VPs 
        '''
        
        if not hasattr(self, 'v'):
            self.voronoi()
        self.vp_volume = np.array([vi['volume'] for vi in self.v])
        self.vp_area = np.array([vi['surface'] for vi in self.v])
        return self.vp_volume, self.vp_area
    
    def vp_distance(self, f):
        ''' Returns a dictionary of distances 
        '''
        if not hasattr(self, 'v'):
            self.voronoi()
        dists = [{} for _ in self.v]
        for iat, vi in enumerate(self.v):
            for fi in vi['faces']:
                jat = fi['adjacent_cell']
                dists[iat][jat] = fi['distance']
                dists[jat][iat] = fi['distance']
        return dists
   
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
            sfs = []
            for sf in small_faces:
                verts = np.array(self.v[iat]['vertices'])
                # a small face (with list index)
                sfi, sface = [(fi, face) for (fi,face) in enumerate(self.v[iat]['faces']) if face['adjacent_cell'] == sf][0]
                sfs.append(sfi)
                # small face vertices
                sfv = sface['vertices']
                # small face centroid
                c = np.sum(verts[sfv], axis=0) / len(sfv)
                ic = len(self.v[iat]['vertices'])
                # exchange all vertices belonging to sf to the face centroid
                # remove all small vertices from other faces
                for fi, face in enumerate(self.v[iat]['faces']):
                    self.v[iat]['faces'][fi]['vertices'] = uniquify([ic if i in sfv else i for i in self.v[iat]['faces'][fi]['vertices']])
                # insert small face centroid in VP
                self.v[iat]['vertices'].append(c.tolist())
                # remove all small face vertices from VP
                self.v[iat]['vertices'] = [[None, None, None] if i in sfv else self.v[iat]['vertices'][i] for i in range(len(self.v[iat]['vertices']))]
            #remove small face from faces
            for sfi in sorted(sfs, reverse = True):
                self.v[iat]['faces'].pop(sfi)
        return None

    def vp_topological_indices(self, atoms = None):
        ''' Finds topological indices (N3, N4, N5...) of resulting Voronoi polihedra 
        Here N3 is the number of triangular faces of a given VP,
        N4 - the number of quadrangular faces, N5 - the number of pentagonal faces etc. 
        Input:
         -> atoms - the list of atomic numbers (default: None)
        
        '''
        if not hasattr(self, 'v'):
            self.voronoi()
        ti = []
        nat = len(self.atoms)
        if atoms is None:
            atoms = range(nat)
        for iat in atoms:
            ni = np.array([len(fi['vertices']) for fi in self.v[iat]['faces']])
            ti.append(np.bincount(ni)[3:])
        return ti

# area of polygon poly ((c) http://code.activestate.com/recipes/578276-3d-polygon-area/)
def poly_area(poly):
    if len(poly) < 3: # not a plane - no area
        return 0
    total = [0, 0, 0]
    N = len(poly)
    for i in range(N):
        vi1 = poly[i]
        vi2 = poly[(i+1) % N]
        prod = np.cross(vi1, vi2)
        total[0] += prod[0]
        total[1] += prod[1]
        total[2] += prod[2]
    result = np.dot(total, unit_normal(poly[0], poly[1], poly[2]))
    return abs(result/2)

#unit normal vector of plane defined by points a, b, and c
def unit_normal(a, b, c):
    x = np.linalg.det([[1,a[1],a[2]],
             [1,b[1],b[2]],
             [1,c[1],c[2]]])
    y = np.linalg.det([[a[0],1,a[2]],
             [b[0],1,b[2]],
             [c[0],1,c[2]]])
    z = np.linalg.det([[a[0],a[1],1],
             [b[0],b[1],1],
             [c[0],c[1],1]])
    magnitude = (x**2 + y**2 + z**2)**.5
    return (x/magnitude, y/magnitude, z/magnitude)

# uniquify list [f8 in (c) http://www.peterbe.com/plog/uniqifiers-benchmark] 
def uniquify(seq): # Dave Kirby
    # Order preserving
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]

       