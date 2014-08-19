#! /usr/bin/env python
# -*- coding : utf-8 -*-

''' Container for calculation types (CG, MD, NPR)
'''
import os, copy

import options as Opts

class CalcType():
    ''' Generic class for all calculation types
    '''
    keys = {'MD.TypeOfRun' : ['s', None]}
    ctd = {'CG' : 'CG',
           'MD' : 'Nose',
           'NPR' : 'NoseParrinelloRahman'}

    def __init__(self):
        self.ctype = ''
        self.opts = {}
        
    def read(self, opts):
        self.ctype = opts['MD.TypeOfRun'].value
# calculation types dictionary
        ctd = {'CG' : CG,
               'Nose' : MD,
               'NoseParrinelloRahman': NPR}
        ct = ctd[self.ctype](opts)
        self.keys = ct.keys
        self.opts = ct.opts
        
    def write(self, calcdir):
        ''' Writes calculation type options to CTYPE.fdf file in calcdir 
        Input:
         -> calcdir (string) - new calculation directory
        '''
        fn = os.path.join(calcdir, 'CTYPE.fdf')
        self.opts.write(fn)

    def fdf_options(self, ctype):
        ''' Returns FDF options suitable for a given calc type
        '''
        ctd = {'CG' : CG,
               'Nose' : MD,
               'NoseParrinelloRahman': NPR}
        ct = ctd[ctype]({})
        return ct.keys.keys()
        
    
    def alter(self, ctype, steps = None, temp = None, press = None, optdict = None):
        ''' Alters calculation type with given data
        Input:
         - ctype (CG, MD, NPR) - new calculation type
         - steps (int, default = 50) - number of cg or md steps
         - temp (int) - initial and target temperature in K (MD and NPR)
         - press (float) - target pressure in GPa, for NPR
         - optdict (dict) - dictionary of options, for fine tuning
        '''
# some values dictionary
        print 'CT.Alter: Changing calculation type'
        vd ={'MD.NumCGSteps' : steps,
             'MD.FinalTimeStep' : steps,
             'MD.InitialTemperature' : str(temp) + ' K',
             'MD.TargetTemperature' : str(temp) + ' K',
             'MD.TargetPressure' : str(press) + ' GPa'}
        values = copy.deepcopy(vd)
        for k, v in values.iteritems():
            if v is None or v == 'None K' or v == 'None GPa':
                vd.pop(k)
# new ctype instance
        ctd = {'CG' : CG,
               'Nose' : MD,
               'NoseParrinelloRahman': NPR}        
        ct = ctd[self.ctd[ctype]]({})
# ct.keys - new list of keys, now we get self.opts based on this list
# opts - new dictionary populated with self.opts and defaults from ct.keys 
# pos - MD.TypeOfRun position in CTYPE.fdf (to ensure it's on top of file)
        data = {}
        pos = self.opts['MD.TypeOfRun'].pos + 1
        for key, default in ct.keys.iteritems():
            if key in self.keys.keys():
                data[key] = self.opts[key]
                if key in vd.keys():
                    print '          %s -> %s' % (key, str(vd[key]))
                    data[key].alter(vd[key])
                continue
            data[key] = Opts.MakeOption(key, default, vd.get(key), pos)
            print '          %s -> %s' % (key, data[key].value)
            pos += 1
# now take care of self.ctype and self.opts['MD.TypeOfRun']                
        self.ctype = self.ctd[ctype]
        data['MD.TypeOfRun'].value = self.ctype
        self.opts.opts = data
        print ''

class CG(CalcType):
    keys = {'MD.NumCGSteps' : ['n', 50],
            'MD.MaxForceTol' : ['m', '0.04 eV/Ang'],
            'MD.MaxCGDispl' : ['m', '0.05 Ang']}
    
    def __init__(self, data):
        self.keys.update(CalcType.keys)
        if isinstance(data, Opts.Options):
            self.opts = data
        else:
            self.opts = Opts.Options(data)
        
        
class MD(CalcType):
    keys = {'MD.FinalTimeStep' : ['n', None],
            'MD.LengthTimeStep' : ['m', '1 fs'],
            'MD.InitialTemperature' : ['m', None],
            'MD.TargetTemperature' : ['m', None],
            'MD.NoseMass' : ['m', '500 Ry*fs**2']}

    def __init__(self, data):
        self.keys.update(CalcType.keys)
        if isinstance(data, Opts.Options):
            self.opts = data
        else:
            self.opts = Opts.Options(data)

class NPR(MD):
    keys = {'MD.TargetPressure' : ['m', '0.0 GPa'],
            'MD.ParrinelloRahmanMass' : ['m', '500 Ry*fs**2']}

    def __init__(self, data):
        d = copy.deepcopy(data)
        MD.__init__(self, d)
        self.keys.update(MD.keys)
        if isinstance(data, Opts.Options):
            self.opts = data
        else:
            self.opts = Opts.Options(data)
