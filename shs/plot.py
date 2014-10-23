#!/usr/bin/env python
# -*- coding : utf8 -*-

import sio as SIO

import math
import numpy as N
import matplotlib.pyplot as plt
import pylab as p
#import mpl_toolkits.mplot3d.axes3d as p3

''' A module for plotting various data
'''

def plotmde(data):
    ''' Plot information from MDE file
         Input:
         -> data : structured array 
    '''
#number of graphs
    ng = len(data.dtype.names[1:])
    ncols = round(ng**0.5)
    nrows = math.ceil(float(ng) / ncols)
    for i, igraph in enumerate(data.dtype.names[1:]):
        plt.subplot(nrows,ncols,i+1)
        plt.title(igraph)
        plt.plot(data['step'], data[igraph])
    plt.show()
    
def plotrdf(title, r, rdf, fname = 'RDF'):
    ''' Plot radial distribution function
         Input:
         -> title (list of str): data title
         -> r (numpy array): array of radii
         -> rdf (list of arrays): data arrays 
    '''
    SIO.data2file([r, N.array(rdf).T], title, fname)
        
    nrows = len(title)
    for i, (ititle, irdf) in enumerate(zip(title[1:], rdf)):
        plt.subplot(nrows,1,i+1)
        plt.title(ititle)
        plt.plot(r, irdf)
    plt.show()
    
def plotmd(md):
    ''' Plots mean distance between atoms as a function of step number
    '''
    dist = []
    nsteps = len(md)
    nat = len(md[0])
    for step in md:
        dist.append(step.sum()/nat/(nat-1))
    plt.plot(range(nsteps), dist)
    plt.show()
    
def plot2d(x, y):
    plt.plot(x, y)
    plt.show()

def scatter(x,y, xlabel = None, ylabel = None):
    ''' Plot dependence of y by x using scatter graph
    '''
    plt.scatter(x, y)
    if xlabel is not None:
        plt.xlabel(xlabel)
    if ylabel is not None:
        plt.ylabel(ylabel)
    plt.show()
    
#def scatter3d(x, y, z):
#    fig=p.figure()
#    ax = p3.Axes3D(fig)
# scatter3D requires a 1D array for x, y, and z
# ravel() converts the 100x100 array into a 1x10000 array
#    ax.scatter3D(x,y,z)

#    p.show()


