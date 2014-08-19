#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import scipy.optimize as SO
import scipy.integrate as SI

'This module contains various fitting procedures'

class Fit():
    '''
    A class for fitting
    '''
    # a number of points needed to fit
    np = {0: 1, # 1-peak Gaussian
          1: 2, # 2-peak Gaussian
          2: 2  # linear fit
          }

    def __init__(self, option, fset):
        self.option = option
        self.fset = fset
        
    def is_enough(self, num):
        return num >= self.np[self.option]
    
    def fit(self, points):
        fit_func = {0: self.fit1peakGauss,
                    1: self.fit2peakGauss,
                    2: self.fitLinear
                   }
        return fit_func[self.option](points)
    
    def fit1peakGauss(self, x_peak):
        # 1-peak Gaussian func
        gauss = lambda p, x: p[0]*(1/np.sqrt(2*np.pi*(p[2]**2)))*np.exp(-(x-p[1])**2/(2*p[2]**2))
        # fit function
        fit = lambda p, x, y: (gauss(p,x) -y)
        # fitting parameters : plot around peaks
        p = [1.,x_peak[0],1.]
        # fitting using least squares
        out, cov_x, infodict, mesg, ier = SO.leastsq(fit, p[:], args=self.fset, maxfev=100000, full_output=1)
        self.p = out
        # resultant fitting parameters    
        return out, self.fset[0], gauss(out, self.fset[0])

    def fit2peakGauss(self, x_peak):
        # 2-peak Gaussian func
        gauss = lambda p, x: p[0]*(1/np.sqrt(2*np.pi*(p[2]**2)))*np.exp(-(x-p[1])**2/(2*p[2]**2))+p[3]*(1/np.sqrt(2*np.pi*(p[5]**2)))*np.exp(-(x-p[4])**2/(2*p[5]**2))
        # fit function
        fit = lambda p, x, y: (gauss(p,x) -y)
        # fitting parameters : plot around peaks
        p = [1.,x_peak[0],1.,1.,x_peak[1],1.]
        # fitting using least squares
        out, cov_x, infodict, mesg, ier = SO.leastsq(fit, p[:], args=self.fset, maxfev=100000, full_output=1)
        self.p = out
        # resultant fitting parameters    
        return out, self.fset[0], gauss(out, self.fset[0])
    
    def fitLinear(self, x_bound):
        # linear func
        line = lambda p, x: p[0] * x + p[1]
        # fit function
        fit = lambda p, x, y: (line(p,x) - y)
        # fitting parameters : a line through boundary points
        i0 = np.where(self.fset[0] > x_bound[0])[0][0]
        i1 = np.where(self.fset[0] > x_bound[1])[0][0] - 1
        x = self.fset[0][[i0,i1]]
        y = self.fset[1][[i0,i1]]
        k = (y[1] - y[0])/(x[1]-x[0])
        b = y[0] - x[0] * k
        p = [k, b]
        # change fit set to use only points inside boundaries 
        fset = (self.fset[0][i0:i1+1], self.fset[1][i0:i1+1])
        # fitting using least squares
        out, cov_x, infodict, mesg, ier = SO.leastsq(fit, p[:], args=fset, maxfev=100000, full_output=1)
        self.p = out
        return out, self.fset[0], line(out, self.fset[0])
    
    def FitInfo(self):
        return self.p
        
def fitGaussian():
    'Fitting with 1-peak Gaussian'
    pass

def intGauss(p, x):
    gauss = lambda x: p[0]*(1/np.sqrt(2*np.pi*(p[2]**2)))*np.exp(-(x-p[1])**2/(2*p[2]**2))
    return SI.quad(gauss, np.min(x), np.max(x))