#!/usr/bin/env python
# -*- coding : utf8 -*-

from collections import OrderedDict
import fdftypes as T
import sio as SIO
import const as Const
''' Calculation options should be stored here
'''


class Options(object):
    """  Options class must be instantiated with a dict of FDF data
    """

    def __init__(self, data):

        self.opts = OrderedDict()
        # nonrecognized options
        self.nr_opts = OrderedDict()
        if data != {}:
        # we are creating non-empty options
            self.read(data)
    
    def read(self, data):
        if isinstance(data.values()[0], list):
            self.readfdf(data)
        elif data.values()[0].__class__.__name__ in ['BlockValue', 'MeasuredValue',
                                                     'BoolOrNumberValue', 'StringValue',
                                                     'NoneType']:
            self.readopts(data)

    def readfdf(self, data):
        # fdf types (a.k.a. actions)
        act = {'b': T.BlockValue,
               'm': T.MeasuredValue,
               'n': T.BoolOrNumberValue,
               's': T.StringValue,
               }
        # iterating over data
        for key, value in data.iteritems():
            # if key is valid
            vkey = isValid(key)
            if vkey is not None:
                # try to get the fdf-type of value
                vtype = T.GetType(value[1:])
                self.opts[vkey] = act.get(vtype)(vkey, value)
            else:
                self.nr_opts[key] = value
        print 'Non-recognized options: ' + str(self.nr_opts)

    def readopts(self, data):
        self.opts = data
    
    def __str__(self):
        keys = [[self.opts[key].pos, key] for key in self.opts.keys()]
        keys.sort()
        keylen = max([len(k[1]) for k in keys])
        s = ''
        for k in keys:
            s += self.opts[k[1]].str2fdf()
        return s
    
    def __getitem__(self, key):
        return self.opts[key]
    
    def divide(self, keys):
        ''' Divides self.opts into 2 dictionaries based on the list of keys provided:
         - self.opts (without key-value pairs from the list)
         - a dictionary of opts (with keys from the list) returned by divide
        '''
        new_opts = {}
        for key in keys:
            new_opts[key] = self.opts.pop(key, None)
        return Options(new_opts)

    def write(self, fn, includes = None):
        ''' Write Options.opts dictionary to FDF file. 
          - fn  -- output FDF file name
          - includes -- a list of FDF files to include (using %%include directive)
            -> Default : None 
        '''
        ofile = SIO.FDFFile(fn, 'w')
        ofile.file.write('%s\n' % (str(self)))
        if includes is not None:
            for ifn in includes:
                ofile.file.write('%%include %s\n' % (ifn,))

    def alter(self, altdata):
        ''' Altering Options.opts dictionary with altdata
        Altdata is a dictionary {'FDFLabel' : altdata, ...} 
        - 'FDFLabel' -- a section label in FDF file
        -  altdata   -- alternative data 
           -> BlockValue        : 2D list of strings
           -> MeasuredValue     : a [value(int or float), measurement unit(str)] list
           -> BoolOrNumberValue : value(bool, int or float)
           -> StringValue       : value(str)
                    
        '''
        for key in altdata.keys():
            self.opts[key].alter(altdata[key])


class Options_old():
    
    def __init__(self, keys, data):
        self.opts = {}
        act = {'b' : T.BlockValue,
               'm' : T.MeasuredValue,
               'n' : T.BoolOrNumberValue,
               's' : T.StringValue,            
               }
        for key, value in keys.iteritems():
            try:
                self.opts[key] = act.get(value[0])(key, data[key])
            except (KeyError,):
                if value[1] is not None:
                    self.opts[key] = act.get(value[0])(key, [pos(),] +  str(value[1]).split())
#                pass

    def __getitem__(self, key):
        return self.opts[key]
    
    def __str__(self):
        keys = [[self.opts[key].pos, key] for key in self.opts.keys()]
        keys.sort()
        s = ''
        for k in keys:
            s += self.opts[k[1]].str2fdf()
        return s

    def write(self, fn, includes = None):
        ''' Write Options.opts dictionary to FDF file. 
          - fn  -- output FDF file name
          - includes -- a list of FDF files to include (using %%include directive)
            -> Default : None 
        '''
        ofile = SIO.FDFFile(fn, 'w')
        ofile.file.write('%s\n' % (str(self)))
        if includes is not None:
            for ifn in includes:
                ofile.file.write('%%include %s\n' % (ifn,))
                
    def alter(self, altdata):
        ''' Altering Options.opts dictionary with altdata
        Altdata is a dictionary {'FDFLabel' : altdata, ...} 
        - 'FDFLabel' -- a section label in FDF file
        -  altdata   -- alternative data 
           -> BlockValue        : 2D list of strings
           -> MeasuredValue     : a [value(int or float), measurement unit(str)] list
           -> BoolOrNumberValue : value(bool, int or float)
           -> StringValue       : value(str)
                    
        '''
        for key in self.opts.keys():
            self.opts[key].alter(altdata[key])
             
def MakeOption(key, default, value, pos):
    ''' Make option from the given data
      Input:
       - key (str) - FDF label for the option
       - default (list) - a list like ['option type', default value]
       - value (int or float or str) - a value instead of default
       - pos (int) - position in FDF file
    '''
    act = {'b': T.BlockValue,
           'm': T.MeasuredValue,
           'n': T.BoolOrNumberValue,
           's': T.StringValue,
               }
    if value is not None:
        data = [pos, ] + str(value).split()
    elif default[1] is not None:
        data = [pos, ] + str(default[1]).split()
    else:
        raise ValueError('%s can not be None' % (key,))
    return act.get(default[0])(key, data)

def isValid(key):
    'checks if fdf key is valid, returns \'canonical\' fdf-key (the one from const) or None '
    # generic keys
    gen_keys = [k.lower().replace('-','').replace('_','').replace('.','') for k in Const.opts]
    if key.lower().replace('-','').replace('_','').replace('.','') in gen_keys:
        return Const.opts[gen_keys.index(key.lower().replace('-','').replace('_','').replace('.',''))]
    else:
        return None
    
# TODO: make some utils module for such stuff
def pos():
    pos = 0
    while 1 == 1:
        pos += 1
        yield pos
    