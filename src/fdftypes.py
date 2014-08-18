#! /usr/bin/env python
# -*- coding : utf-8 -*-

''' Container for types of values in FDF file
'''
# ------------ METHODS ------------

def str2bool(value):
    t = ('yes', 'true', 't', '.true.')
    if (value.lower() in t):
        return True
    else: 
        return False

def get_bif_type(value):
    'Finds whether the value is bool, int or float (for T.BoolOrNumberValue)'
    if (value.lower() in ('yes', 'true', 't', '.true.', 'no', 'false', 'f', '.false.')):
        return 'bool'
    if value.isdigit(): 
        return 'int'
    try:
        value = value.replace('d','e')
        float(value)
        return 'float'
    except ValueError:
        raise ValueError('Strange error... %s is not bool, int nor float' % (value,))
    
def GetType(v):
    'Gets FDF label type'
# not very good switch-case construction
    if len(v) == 0:
        return 'n'
    elif type(v[0]) == type([]):
        return 'b'
    try:

        if (len(v) == 1 and get_bif_type(v[0])):
            return 'n' 
        elif len(v) == 2 and (get_bif_type(v[0]) == 'int' or get_bif_type(v[0]) == 'float'):      
            return 'm'
    except:
        return 's'
    # in any other case return s
    return 's'

def str2type(typ, value):
    s2t = {'bool' : str2bool,
           'int' : int,
           'float': float}
    try:
        return s2t[typ](value)
    except ValueError:
        value = value.replace('d','e')
        return s2t[typ](value)
        

# ------------ CLASSES ------------

class BlockValue():
    ''' FDF blocks - represented as lists of lists or arrays
    '''
    def __init__(self, key, value):
        self.key = key
        self.pos = value.pop(0)
        self.value = value

    def str2fdf(self):
        s = '%%block %s\n' % (self.key)
        ncol = max([len(x) for x in self.value])
        wcol = []
        for l in range(ncol):
            wcol.append(max([len(x[l]) for x in self.value if len(x) >= l]))
        for line in self.value:
            fmt = ''
            for i in range(len(line)):
                fmt += ' {0[%i]:<%i}' % (i, wcol[i] + 2)
            s += (fmt.format(line) + '\n')
        s += '%%endblock %s\n\n' % (self.key)
        return s

    def __str__(self):
        s = ''
        ncol = max([len(x) for x in self.value])
        wcol = []
        for l in range(ncol):
            wcol.append(max([len(x[l]) for x in self.value if len(x) >= l]))
        for line in self.value:
            fmt = ''
            for i in range(len(line)):
                fmt += ' {0[%i]:<%i}' % (i, wcol[i] + 2)
            s += (fmt.format(line) + '\n')
        return s
    
    def alter(self, altblock):
        self.value = altblock

class MeasuredValue():
    ''' Values with units of measurement. Might be conversion?
    '''
    def __init__(self, key, value):
        self.key = key
        self.pos = value.pop(0)
        self.value = str2type(get_bif_type(value[0]), value[0])
        self.unit = value[1]

    def str2fdf(self):
        return '%-35s %s %s\n' % (self.key, str(self.value), self.unit)
    
    def __str__(self):
        return '%s %s' % (str(self.value), self.unit)

    def alter(self,altmv):
        if type(altmv) == type(''):
            altmv = altmv.split()
        self.value = altmv[0]
        self.unit = altmv[1]
       
class BoolOrNumberValue():
    ''' Boolean or number (FP or integer) FDF values
    '''
    def __init__(self, key, value):
        self.key = key
        self.pos = value.pop(0)
        if len(value) == 0:
            self.typ = 'bool'
            self.value = True
        else:
            self.typ = get_bif_type(value[0])
            self.value = str2type(self.typ, value[0])

    def str2fdf(self):
        return '%-35s %s\n' % (self.key, str(self.value))

    def __str__(self):
        return '%s' % (str(self.value))

    def alter(self,altv):
        self.value = altv


class StringValue():
    ''' Values made of strings 
    '''
    def __init__(self, key, value):
        self.key = key
        self.pos = value.pop(0)
        self.value = ' '.join(value)
        
    def __str__(self):
        return '%s' % (self.value)

    def str2fdf(self):
        return '%-35s %s\n' % (self.key, self.value)


    def alter(self,altsv):
        self.value = altsv
    