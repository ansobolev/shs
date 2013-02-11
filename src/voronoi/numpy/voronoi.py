#!/usr/bin/env python 
# __*__ coding: utf8 __*__

#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2012
#

import numpy as np
import scipy.spatial as ss

from ngbr import model_ngbr
from vp import vp

# Functions:
def vp_vertex(pt, pbc, vc, vc_inv):
    ''' Finds Voronoi polihedon vertex as the circumsphere center of  
 Delaunay simplex
     Input:
      -> pt - array containing coordinates of Delaunay simplex vertices
     Output:
      -> r - circumsphere radius
      -> a+u - coordinates of VP vertex
    ''' 
    a = pt[0]
    pt_vc = np.dot(pt, vc_inv)
    pt_vc = pt_vc - pt_vc[0]
    if pbc:
# periodic boundary conditions
        pt_vc[pt_vc > 0.5] -= 1.0
        pt_vc[pt_vc < -0.5] += 1.0
    pt = np.dot(pt_vc, vc)        
    dum,b,c,d = pt
    u = np.dot(d,d)*np.cross(b,c) + np.dot(c,c)*np.cross(d,b) + np.dot(b,b)*np.cross(c,d)
    u = u / (2*np.linalg.det([b,c,d]))
    r = np.dot(u,u)**0.5
    return r, a + u

def vp_vertices(dt, vc, pbc):
    ''' Finds Voronoi polihedra vertices as the circumsphere centers of  
 Delaunay simplices
     Input:
      -> dt - array containing coordinates of Delaunay simplices
      -> vc - lattice vectors
      -> pbc - whether use (or not) periodic boundary conditions 
     Output:
      -> r - circumsphere radius
      -> a+u - coordinates of VP vertex

    ''' 
    a = dt[:,0]
    vc_inv = np.linalg.inv(vc)
    dt_vc = np.dot(dt, vc_inv)
    dt_vc = (dt_vc.swapaxes(0,1) - dt_vc[:,0]).swapaxes(0,1)
    if pbc:
# periodic boundary conditions
        dt_vc[dt_vc > 0.5] -= 1.0
        dt_vc[dt_vc < -0.5] += 1.0
    dt = np.dot(dt_vc, vc)
    b = dt[:,1]
    c = dt[:,2]
    d = dt[:,3]
    bb = (b*b).sum(axis=1)
    cc = (c*c).sum(axis=1)
    dd = (d*d).sum(axis=1)
    bc = np.cross(b, c)
    db = np.cross(d, b)
    cd = np.cross(c, d)
    u = (dd*bc.T).T + (cc*db.T).T + (bb*cd.T).T
    det = (b*cd).sum(axis=1)
    u = (u.T / (2 * det)).T
    r = (u*u).sum(axis=1)**0.5
    return r, a + u
    


def border_plane(at, nbat):
    ''' Finds atoms on the model border (needed for proper account of PBC)
    '''
# Find number of occurrences of atoms from at in nbat (if 3 - interior atom)
    th_num = []
    for iat in at:
        th_num.append(len(np.nonzero(nbat == iat)[0]))
    th_num = np.array(th_num)
# Renumerate atoms in tetrahedron according to tetrahedron number 
    inds = np.argsort(th_num)
    th_num = th_num[inds]
    at = at[inds]
    bp = []
# Find border planes of a tetrahedron
    while not np.all(th_num == 3):      
        ibp = []
        for i, a in enumerate(at):
            if th_num[i] < 3:
                th_num[i] += 1
                ibp.append(a)
            if len(ibp) == 3:
                break
        bp.append(ibp)
    return bp

def tetrahedron_volume(pt):
    a,b,c,d = pt
    b = b - a
    c = c - a
    d = d - a
    return 1/6.*np.abs(np.linalg.det(np.vstack((b,c,d)).T))

def crd22d(pt, vc, pbc, h_out = False, at_crd = None):
    ''' Finds VP coordinates in 2d space
    Input:
     -> pt - a 2d coordinate array 
    '''
    vc_inv = np.linalg.inv(vc)
    pt_vc = np.dot(pt, vc_inv)
    origin = pt_vc[:,0]
    pt_vc = (pt_vc.swapaxes(0,1) - origin).swapaxes(0,1)
    if pbc:
# periodic boundary conditions
        pt_vc[pt_vc > 0.5] -= 1.0
        pt_vc[pt_vc < -0.5] += 1.0
    pt = np.dot(pt_vc, vc)
    norm = np.cross(pt[:,1], pt[:,2])
# atomic coordinates to face CS 
    if h_out:
        at_vc = np.dot(at_crd, vc_inv)
        at_vc = (at_vc.swapaxes(0,1) - origin).swapaxes(0,1)
        if pbc:
# periodic boundary conditions
            at_vc[at_vc > 0.5] -= 1.0
            at_vc[at_vc < -0.5] += 1.0
        at_crd = np.dot(at_vc, vc)
        onorm = (norm.T / np.sum(norm * norm, axis = 1)**0.5).T
        h = np.sum((at_crd.swapaxes(0,1)* onorm).swapaxes(0,1), axis = 2)
# orts
    o1 = np.vstack([norm[:,2], np.zeros(len(norm)), -norm[:,0]]).T
    o2 = np.cross(o1, norm)
# norming orts
    o1 = (o1.T / np.sum(o1 * o1, axis = 1)**0.5).T    
    o2 = (o2.T / np.sum(o2 * o2, axis = 1)**0.5).T    
    x = np.sum((pt.swapaxes(0,1)* o1).swapaxes(0,1), axis = 2)
    y = np.sum((pt.swapaxes(0,1)* o2).swapaxes(0,1), axis = 2)
    crd = np.array((x, y)).swapaxes(0,1).swapaxes(1,2)
    if h_out:
        return crd, h
    return crd

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
#=====================================================================

class model_voronoi(model_ngbr):

    def __init__(self,d = {}):
        model_ngbr.__init__(self,d)

    def make_pbcmodel(self, ratio):
        crd = self.atoms['crd'] 
        vc = self.vc
        vc_inv = np.linalg.inv(vc) 
        crd_vc = np.dot(crd, vc_inv)
        xpl = crd_vc[...,0] > 1 - ratio
        xmin = crd_vc[...,0] < ratio
        ypl = crd_vc[...,1] > 1 - ratio
        ymin = crd_vc[...,1] < ratio
        zpl = crd_vc[...,2] > 1 - ratio
        zmin = crd_vc[...,2] < ratio
        model = np.vstack((crd, crd[xmin] + vc[0], crd[xpl] - vc[0],
                           crd[ymin] + vc[1], crd[ypl] - vc[1],
                           crd[zmin] + vc[2], crd[zpl] - vc[2],
                           crd[xmin * ymin] + vc[0] + vc[1], crd[xmin * ypl] + vc[0] - vc[1],
                           crd[xmin * zmin] + vc[0] + vc[2], crd[xmin * zpl] + vc[0] - vc[2],
                           crd[ymin * zmin] + vc[1] + vc[2], crd[ymin * zpl] + vc[1] - vc[2],
                           crd[xpl * ymin] - vc[0] + vc[1], crd[xpl * ypl] - vc[0] - vc[1],
                           crd[xpl * zmin] - vc[0] + vc[2], crd[xpl * zpl] - vc[0] - vc[2],
                           crd[ypl * zmin] - vc[1] + vc[2], crd[ypl * zpl] - vc[1] - vc[2],
                           crd[xmin * ymin * zmin] + vc[0] + vc[1] + vc[2], crd[xmin * ymin * zpl] + vc[0] + vc[1] - vc[2],
                           crd[xmin * ypl * zmin] + vc[0] - vc[1] + vc[2], crd[xmin * ypl * zpl] + vc[0] - vc[1] - vc[2],
                           crd[xpl * ymin * zmin] - vc[0] + vc[1] + vc[2], crd[xpl * ymin * zpl] - vc[0] + vc[1] - vc[2],
                           crd[xpl * ypl * zmin] - vc[0] - vc[1] + vc[2], crd[xpl * ypl * zpl] - vc[0] - vc[1] - vc[2]
                           ))
        atind = np.hstack((np.arange(len(crd)), np.where(xmin)[0], np.where(xpl)[0], np.where(ymin)[0], 
                         np.where(ypl)[0], np.where(zmin)[0], np.where(zpl)[0],
                         np.where(xmin * ymin)[0], np.where(xmin * ypl)[0],
                         np.where(xmin * zmin)[0], np.where(xmin * zpl)[0],   
                         np.where(ymin * zmin)[0], np.where(ymin * zpl)[0],   
                         np.where(xpl * ymin)[0], np.where(xpl * ypl)[0],
                         np.where(xpl * zmin)[0], np.where(xpl * zpl)[0],   
                         np.where(ypl * zmin)[0], np.where(ypl * zpl)[0],   
                         np.where(xmin * ymin * zmin)[0], np.where(xmin * ymin * zpl)[0],
                         np.where(xmin * ypl * zmin)[0], np.where(xmin * ypl * zpl)[0],
                         np.where(xpl * ymin * zmin)[0], np.where(xpl * ymin * zpl)[0],
                         np.where(xpl * ypl * zmin)[0], np.where(xpl * ypl * zpl)[0]
                         )) 
        return model, atind

    def delaunay(self, pbc = True, ratio = 0.5):
        ''' Finds Delaunay triangulation of geometry
        Uses QHull library
        Input:
         -> pbc - whether to use periodic boundary conditions 
        '''
        model = self.atoms['crd']
        nat = len(self.atoms)
        if pbc:
            model, orind = self.make_pbcmodel(ratio)
        dt = ss.Delaunay(model)
# Indices of delaynay tetrahedrons in the center of the model (DT simplex center indices)        
        dtsci = np.nonzero(np.all(dt.vertices < nat, axis = 1))[0] 
        dtsc = dt.vertices[dtsci]
# DT simplex border indices
        dtsbi = np.nonzero(np.any(dt.vertices < nat, axis = 1) * np.any(dt.vertices >= nat, axis = 1))[0]        
# Return back to the original atomic numbers (to be changed if translation algorithm changes)
        c = np.sort(orind[dt.vertices[dtsbi]])
# DT simplices unique border        
        u, ri = np.unique(c.view([('',c.dtype)]*c.shape[1]), return_index = True)
        dtsub = u.view(c.dtype).reshape(-1,c.shape[1])
# dt.vertices with PBC
        self.dt_simplexes = np.sort(np.vstack((dtsc, dtsub)))
        self.nsimplex = len(self.dt_simplexes)
# Now let's find dtsub indices in dt.vertices
        dtsubi = dtsbi[ri]
# So, indices of every needed simplex are dtsci + dtsubi
        dtsi = np.hstack((dtsci, dtsubi))
# Now let's find connectivity matrix
# Build lookup array
        la = -1 * np.ones(np.max(dt.neighbors[dtsi]) + 1, dtype = np.int)
# Every simplex in connectivity matrix (CM simplex indices)
        cmsi = np.unique(dt.neighbors[dtsi])
# Atoms in connectivity matrix (with original atomic numbers, to be changed if transition algorithm changes) 
        cmati = np.sort(orind[dt.vertices[cmsi]])
# Not so long cycle 
        verts = {}
        for i, row in enumerate(self.dt_simplexes):
            verts[tuple(row)] = i
        for i, row in enumerate(cmati):
            la[cmsi[i]] = verts.get(tuple(row), -1)        
        
        self.dt_ngbrs = la[dt.neighbors[dtsi]]
        if np.any(self.dt_ngbrs == -1):
            print 'Delaunay_np WARNING: Didn\'t find some neighboring simplices, increase ratio for PBC!'

    
    def voronoi(self, pbc = True, ratio = 0.5):
        ''' Finds Voronoi tesselation of geometry
        Uses QHull library
        Input:
         -> pbc - whether to use periodic boundary conditions (default: True)
         -> ratio - the part of original model to be translated for PBC calculation (default: 0.5) 
        '''
# Delaunay triangulation        
        self.delaunay(pbc, ratio)
        model = self.atoms['crd'][self.dt_simplexes]        
        vc = self.vc
        self.vp_r, self.vp_verts = vp_vertices(model, vc, pbc)

# VP parameters ---
    
    def vp_neighbors(self, rm_small = False, eps = 0.05):
        ''' Finds nearest neighbors to the given atom according to VP tesselation 
    ATTENTION: Atom # iat is considered to be its own neighbor! 
        '''
        ngbrs = []
        nat = len(self.atoms)
        atoms = np.arange(nat)
        if rm_small:
            if not hasattr(self,'vp_face'): self.vp_faces()
            a = self.vp_face_area(self.vp_face)
            f = self.remove_small_faces(self.vp_face, a, eps)
            ngbrs = [np.array(d.keys()) for d in f]
            return ngbrs 
        for iat in atoms:
            ing = self.dt_simplexes[np.any(self.dt_simplexes == iat, axis = 1)]
            ngbrs.append(np.unique(ing))
        return ngbrs
    
    def vp_topological_indices(self, atoms = None):
        ''' Finds topological indices (n3,n4,n5...) of VPs. 
        Here n3 is the number of triangular faces of a given VP,
        n4 - the number of quadrangular faces, n5 - the number of pentagonal faces etc. 
        Input:
         -> atoms - the list of atomic numbers (default: None)
        '''
        
        from collections import defaultdict

        ti = []
        nat = len(self.atoms)
        if atoms is None:
            atoms = np.arange(nat)
        for iat in atoms:
            ngbrs = self.dt_simplexes[np.any(self.dt_simplexes == iat, axis = 1)]
            d = defaultdict(int)
            for elt in ngbrs.flatten():
                d[elt] += 1
# as of now we don't need info about the vertex number of VP
            d.pop(iat)
            ti.append(np.bincount(np.array(d.values()))[3:])      
        return ti

    def vp_faces(self, atoms = None):
        ''' Finds faces of VPs 
        '''
        nat = len(self.atoms)
        if atoms is None:
            atoms = np.arange(nat)
        faces = [{} for i in atoms] 
        for i, iat in enumerate(atoms):
            n1 = np.any(self.dt_simplexes == iat, axis = 1)
            ngbrs = self.dt_simplexes[n1]
            for ngbr in np.unique(ngbrs.flatten()):
                n2 = np.any(self.dt_simplexes == ngbr, axis = 1)
                faces[i][ngbr] = np.where(n1 * n2)[0]
            faces[i].pop(iat)
        self.vp_face = faces 
        return faces

    def vp_face_area(self, faces):
        ''' Finds face areas of VPs
        Input:
         -> atoms - the list of atomic numbers (default: None)
        Output:
         -> a list of dictionaries (or arrays?)
        '''
        vpf_max = max([len(a) for at_face in faces for a in at_face.values()])
        vpf = [[] for _ in range(vpf_max - 2)]
        areas = [{} for _ in faces]
        for iat, f in enumerate(faces):
        # TODO: we can do better here
            for ing, face in f.iteritems():
                vpf[len(face) - 3].append(tuple(sorted([iat, ing]) + sorted(face.tolist())))
        for vpfi in vpf:
        # VP faces (two first numbers - atomic numbers, then - vertices numbers)
            if not vpfi:
                continue
            vpf = np.array(list(set(vpfi)))
        # VP vertex coordinates
            vpcrd = self.vp_verts[vpf[:,2:]]
        # VP coords in 2D space
            vp2d = crd22d(vpcrd, self.box, pbc = True)
        # indexes and coordinates sorted counter-clockwise
            _, vp_s = sort_polygons(vp2d)
        # get vp areas
            vpa = vp_areas(vp_s)
            for i, (iat, ing) in enumerate(vpf[:,:2]):
                areas[iat][ing] = vpa[i]
                areas[ing][iat] = vpa[i]
        return areas

    def vp_volumes(self, faces, partial = True):
        ''' Get volumes AND areas of VP
        '''
        vpf_max = max([len(a) for at_face in faces for a in at_face.values()])
        vpf = [[] for _ in range(vpf_max - 2)]
# areas, partial
        areas = [{} for _ in faces]
# areas and volumes, total
        av = [{} for _ in faces]
        vol_tot = []
        ar_tot = []
        for iat, f in enumerate(faces):
        # TODO: and here!
            for ing, face in f.iteritems():
                vpf[len(face) - 3].append(tuple(sorted([iat, ing]) + sorted(face.tolist())))
        for vpfi in vpf:
        # VP faces (two first numbers - atomic numbers, then - vertices numbers)
            vpf = np.array(list(set(vpfi)))
        # VP vertex coordinates
            if vpf.shape[0] == 0:
                continue
            vpcrd = self.vp_verts[vpf[:,2:]]
        # unit normal vector to faces as well as coords in 2d
            vp2d, h = crd22d(vpcrd, self.box, pbc = True, h_out = True, at_crd = self.atoms['crd'][vpf[:,:2]])
            _, vp_s = sort_polygons(vp2d)
            vpa = vp_areas(vp_s)
            for i, (iat, ing) in enumerate(vpf[:,:2]):
                if partial:
                    areas[iat][ing] = vpa[i]
                    areas[ing][iat] = vpa[i]

                av[iat][ing] = [vpa[i], abs(h[i,0])]
                av[ing][iat] = [vpa[i], abs(h[i,1])]
        for avi in av:
            vol_tot.append(sum([1./3.*avi[k][0]*avi[k][1] for k in avi.keys()]))
            ar_tot.append(sum([avi[k][0] for k in avi.keys()]))

        self.vp_area = np.array(ar_tot)
        self.vp_volume = np.array(vol_tot)
        if partial:
            return self.vp_volume, self.vp_area, areas
        return self.vp_volume, self.vp_area

    def separate_vp(self):
        'Make VP separate class instances (might be pretty slow)'
        nat = self.atoms['crd'].shape[0]
        # get faces
        if not hasattr(self,'vp_face'): self.vp_faces()
        # get separate vp
        self.vp = []
#        for iat in range(nat):
        for iat in range(2):
            # center (atom number)
            c = iat
            # verts
            v = np.nonzero(np.any(self.dt_simplexes == iat, axis = 1))[0]
            # vert crds
            crd_v = self.vp_verts[v]
            # bring crds to atomic center
            crd_c = self.atoms['crd'][iat]
            crd_v -= crd_c 
            vc_inv = np.linalg.inv(self.box)
            crd_vc = np.dot(crd_v, vc_inv)
# periodic boundary conditions
            crd_vc[crd_vc > 0.5] -= 1.0
            crd_vc[crd_vc < -0.5] += 1.0
            crd_v = np.dot(crd_vc, self.box)
            edges = self.dt_ngbrs[v]
            edges = np.ravel(edges)[np.in1d(np.ravel(edges), v)].reshape(edges.shape[0], 3)
            self.vp.append(vp(c,v,crd_v,edges,self.vp_face[c]))
        return self.vp
            
            

    
# TODO: doubling functions (plot_vp and plot_vps)  
    def plot_vp(self, atom):
        import networkx as nx
        try:
            from enthought.mayavi import mlab
        except (ImportError,):
            from mayavi import mlab
        crd = self.atoms['crd'][atom]
        faces = self.vp_faces([atom,])[0]
# Neighboring atoms
        ngbrs = faces.keys() + [atom,]
# Coordinates
        crd_ng = self.atoms['crd'][ngbrs]
        crd_ng -= crd
        vc_inv = np.linalg.inv(self.box)
        crd_vc = np.dot(crd_ng, vc_inv)
# periodic boundary conditions
        crd_vc[crd_vc > 0.5] -= 1.0
        crd_vc[crd_vc < -0.5] += 1.0
        crd_ng = np.dot(crd_vc, self.box)
        np.vstack((crd_ng, np.zeros(3)))

        types = self.atoms['itype'][ngbrs]
# vp vertices
        n = np.nonzero(np.any(self.dt_simplexes == atom, axis = 1))[0]
        crd_vp = self.vp_verts[n]
        crd_vp -= crd
        crd_vc = np.dot(crd_vp, vc_inv)
# periodic boundary conditions
        crd_vc[crd_vc > 0.5] -= 1.0
        crd_vc[crd_vc < -0.5] += 1.0
        crd_vp = np.dot(crd_vc, self.box)
        
# lookup dict
        ld = dict(zip(n, xrange(len(n))))
        edges = set()
        for ngbr in faces.keys():
            nv = len(faces[ngbr])
            s_face = self.sort_face_verts(faces[ngbr]) 
            for iv in range(nv):
                edges.add((ld[s_face[iv]],ld[s_face[(iv+1)%nv]]))
        
        G = nx.Graph()
        for edge in edges:
            G.add_edge(edge[0],edge[1])

        mlab.figure(1, bgcolor = (1., 1., 1.))
        mlab.clf()
        atoms = mlab.points3d(crd_ng[:,0], crd_ng[:,1], crd_ng[:,2],
                              types,
#                              color=(0.5,0.5,0.5),
                              scale_factor = 0.8,
                              scale_mode = 'none',
                              colormap = 'autumn',
                              resolution = 20)
        vp_verts = mlab.points3d(crd_vp[:,0], crd_vp[:,1], crd_vp[:,2],
                                 color=(0.4,0.4,0.4),
                                 scale_factor = 0.02,
                                 scale_mode = 'none',
                                 resolution = 20)
        vp_verts.mlab_source.dataset.lines = np.array(G.edges())
        tube = mlab.pipeline.tube(vp_verts, tube_radius=0.1)
        mlab.pipeline.surface(tube, color = (0.4, 0.4, 0.4))     
        mlab.show()

    def plot_vps(self, atoms):
        import networkx as nx
        try:
            from enthought.mayavi import mlab
        except (ImportError,):
            from mayavi import mlab
        crd = self.atoms['crd'][atoms]
        faces = self.vp_faces(atoms)
# Neighboring atoms
#        ngbrs = atoms.tolist()
        ngbrs =  atoms
        for at_face in faces:
            ngbrs += at_face.keys()
# Coordinates
        crd_ng = self.atoms['crd'][ngbrs]
# find centroid
#        crd_c = np.sum(crd_ng, axis = 0) / crd.shape[0]
        crd_ng -= crd[0]
        vc_inv = np.linalg.inv(self.box)
        crd_vc = np.dot(crd_ng, vc_inv)
# periodic boundary conditions
        crd_vc[crd_vc > 0.5] -= 1.0
        crd_vc[crd_vc < -0.5] += 1.0
        crd_ng = np.dot(crd_vc, self.box)
#        np.vstack((crd_ng, np.zeros(3)))

        types = self.atoms['itype'][ngbrs]
# vp vertices
        n = []
        for atom in atoms:
            n += np.nonzero(np.any(self.dt_simplexes == atom, axis = 1))[0].tolist()
        crd_vp = self.vp_verts[n]
        crd_vp -= crd[0]
        crd_vc = np.dot(crd_vp, vc_inv)
# periodic boundary conditions
        crd_vc[crd_vc > 0.5] -= 1.0
        crd_vc[crd_vc < -0.5] += 1.0
        crd_vp = np.dot(crd_vc, self.box)
        
# lookup dict
        ld = dict(zip(n, xrange(len(n))))
        edges = set()
        for face in faces:
            for ngbr in face.keys():
                nv = len(face[ngbr])
                s_face = self.sort_face_verts(face[ngbr]) 
                for iv in range(nv):
                    edges.add((ld[s_face[iv]],ld[s_face[(iv+1)%nv]]))
        
        G = nx.Graph()
        for edge in edges:
            G.add_edge(edge[0],edge[1])

        mlab.figure(1, bgcolor = (1., 1., 1.))
        mlab.clf()
        atoms = mlab.points3d(crd_ng[:,0], crd_ng[:,1], crd_ng[:,2],
                              types,
#                              color=(0.5,0.5,0.5),
                              scale_factor = 0.8,
                              scale_mode = 'none',
                              colormap = 'autumn',
                              resolution = 20)
        vp_verts = mlab.points3d(crd_vp[:,0], crd_vp[:,1], crd_vp[:,2],
                                 color=(0.4,0.4,0.4),
                                 scale_factor = 0.02,
                                 scale_mode = 'none',
                                 resolution = 20)
        vp_verts.mlab_source.dataset.lines = np.array(G.edges())
        tube = mlab.pipeline.tube(vp_verts, tube_radius=0.1)
        mlab.pipeline.surface(tube, color = (0.4, 0.4, 0.4))     
        mlab.show()
        
# Auxiliary ---

    def sort_face_verts(self, verts): 
        ''' Sorts VP face vertices in the circumvention order
        Input:
        -> verts - array of vert numbers to sort 
        '''
# how much verts to sort
        nv = len(verts)
        if nv == 3:
# nothing to sort
            return verts
# coordinates
        crd = self.vp_verts[verts][np.newaxis,:]
# coordinates in 2d
        crd2d = crd22d(crd, self.box, pbc = True)
# circumvention indices
        ind, _ = sort_polygons(crd2d)
        return verts[ind[0]]        
    
    def remove_small_faces(self, faces, areas, eps = 0.05):
        nat = len(faces)
        for iat in range(nat):
# Small faces
            small_faces = [ngbr for ngbr in areas[iat].keys() if areas[iat][ngbr] < eps]
            for sf in small_faces:
# Face vertices
                fvs = faces[iat][sf]
                faces[iat].pop(sf)
# VERY long cycle!!!
#                for fv in fvs[1:]:                       
#                    for jat in range(nat):
#                        for ngbr in faces[jat].keys():
#                            ind = np.nonzero(faces[jat][ngbr] == fv)
#                            faces[jat][ngbr][ind] = fvs[0]
#        for iat in range(nat):
#            for ngbr in faces[iat].keys():
#                faces[iat][ngbr] = np.unique(faces[iat][ngbr])
        return faces
    
    def ti(self, faces):
        ti = []
        nat = len(faces)
        for iat in range(nat):
            d = [len(faces[iat][ngbr]) for ngbr in faces[iat].keys()]
            ti.append(np.bincount(np.array(d))[3:])
        return ti