#!/usr/bin/env python
# -*- coding: utf8 -*-

import numpy as np
import scipy.spatial as ss
try:
    from calc import SiestaCalc
except (ImportError,):
    from shs.calc import SiestaCalc

def make_ngbr(mngbr, iat):
    mngbr.make_ngbr()
    vec = [0.,0.,0.]
# Adding zero point to ngbrs     
    crd = np.array([vec,] + mngbr.ngbr.ind[iat]['vec'].tolist())
# Numbers of atoms in crd table
    nums =  np.array([iat,] + mngbr.ngbr.ind[iat]['n'].tolist())
    
    dt = ss.Delaunay(crd)
    num_smplx = np.nonzero((dt.vertices == 0).any(axis=1))[0]
    iat_smplx = dt.vertices[num_smplx]
# Finding VP vertices
    vtcs = []
    for vtx in iat_smplx:
        vtcs.append(vp_vertex(dt.points[vtx]))
# 
    ngbrs = np.unique(iat_smplx.flatten())
# Numbers and types of neighbors
    ngbr_nums = nums[ngbrs]
    ngbr_types = mngbr.atoms[ngbr_nums]['itype']
  
# create a set for edges that are indexes of the points.  
    edges = set()
# for each Delaunay triangle
    for smplx in num_smplx:
        ngbr_smplx = dt.neighbors[smplx]
        at_ngbr_smplx = dt.vertices[ngbr_smplx]
        ngbr_verts = ngbr_smplx[np.nonzero((at_ngbr_smplx == 0).any(axis=1))]
        edges.add((smplx,ngbr_verts[0]))
        edges.add((smplx,ngbr_verts[1]))
        edges.add((smplx,ngbr_verts[2]))
    
    return ngbr_nums, ngbr_types, crd[ngbrs], num_smplx, np.array(vtcs), edges   

def plot_atom(istep, num, typ, crd, ivert, vert, edges, view = None, roll = None):
    import networkx as nx
    from enthought.mayavi import mlab

    dictXI = dict(zip(ivert, xrange(len(ivert))))
    G = nx.Graph()
    for edge in edges:
        G.add_edge(dictXI[edge[0]], dictXI[edge[1]])
    
    colors = typ
#    mlab.options.offscreen = True
    mlab.figure(1, bgcolor = (0., 0., 0.))
    mlab.clf()
    atoms = mlab.points3d(crd[:,0], crd[:,1], crd[:,2],
        colors,
        scale_factor = 1,
        scale_mode = 'none',
        colormap = 'autumn',
        resolution = 20)
    vp_verts = mlab.points3d(vert[:,0], vert[:,1], vert[:,2],
        color=(1.,1.,1.),
        scale_factor = 0.02,
        scale_mode = 'none',
        resolution = 20)
    vp_verts.mlab_source.dataset.lines = np.array(G.edges())
    tube = mlab.pipeline.tube(vp_verts, tube_radius=0.1)
    mlab.pipeline.surface(tube, color = (0.8, 0.8, 0.8))
    if view == None:
        view = mlab.view()
        roll = mlab.roll()
    else:
        mlab.view(*view)
        mlab.roll(roll)

    mlab.show()
    mlab.savefig(str(istep) +'.png')
    return view, roll

if __name__ == '__main__':
# Working directory
    dir = '../../test'
    view = roll = None
    c = SiestaCalc(dir, type = 'ani', steps = [-1])
    
    for ist in range(len(c.evol.steps)):
        c.evol[ist].voronoi_np()


    for istep, es in enumerate(cdictlist):
        view,  roll = plot_atom(c.evol.steps[istep],ngbr_nums, ngbr_types, crd_at, ivert, vert_crd, edges, view, roll)