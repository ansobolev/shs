#! /usr/bin/env python
# -*- coding : utf8 -*-

#
# This file is a part of Siesta Help Scripts
#
# (c) Andrey Sobolev, 2013
#

import numpy as np

class AtomType():
    ''' Class dealing with atom types
    
    Input:
     -> geom : Geometry
    
    Default: 
     Return types based on geom.atoms[typ]
    '''    
    
    def __init__(self, geom):
        
        self.geom = geom
        # default
        self.labels = geom.names['label'].tolist()
        self.atoms = [np.where(geom.atoms['label'] == i)[0] for i in self.labels] 
        self.isFinalized = True

    def getAtoms(self, label):
        assert label in self.labels
        return self.atoms[self.labels.index(label)]

    def removeTypes(self):
        self.labels = []
        self.atoms = []
        self._untyped = self.geom.atoms['id'] - 1
        self.isFinalized = False
    
    def addType(self, condition, typeLabel):
        '''
        '''
        if len(self._untyped) == 0:
            self.finalize()
            raise Exception("No untyped atoms exist")
        atomProp = [self.geom.property(propLabel) for propLabel in condition.getLabels()]
        nat = np.where(condition.getCondition()(*[iProp[self._untyped] for iProp in atomProp]))[0]
        if len(nat) == 0:
            raise Exception("No untyped atoms satisfy given condition")
        self.labels.append(typeLabel)
        self.atoms.append(self._untyped[nat])
        self._untyped = np.delete(self._untyped, nat)
    
    def finalize(self):
        if len(self._untyped) != 0:
            self.atoms.append(self._untyped)
            self.labels.append('Other')
            self._untyped = np.array([])
        self.isFinalized = True

    def toDict(self):
        if not self.isFinalized:
            self.finalize() 
        return dict(zip(self.labels, self.atoms))
    
    def __iter__(self):
        if not self.isFinalized:
            self.finalize() 
        for (label, nat) in zip(self.labels, self.atoms):
            yield label, nat 


class Condition():
    ''' Class for filtering atoms based on condition
    Input:
     -> label : the label of atomic property the filter is based on
     -> condition : the array -> boolean lambda function
     -> parent, connector -> internal use variables  
    '''
    def __init__(self, label, condition, parent = None, connector = None):
        if parent is None:
            self.propLabels = [label]
            self.cond = condition
        else:
            self.propLabels = parent.propLabels + [label,]
            if connector == 'and':
                self.cond = lambda *x: parent.cond(*x[:-1]) * condition(x[-1])
            else:
                self.cond = lambda *x: parent.cond(*x[:-1]) + condition(x[-1])
    
    def addAnd(self, condition):
        return Condition(condition, self, 'and')
    
    def addOr(self, condition):
        return Condition(condition, self, 'or')
    
    def getLabels(self):
        return self.propLabels
    
    def getCondition(self):
        return self.cond
    
class Comparison(Condition):
    
    def __init__(self, label, compare, value, parent = None, connector = None):
        condition = eval('lambda x: x ' + compare + ' ' + value)
        Condition.__init__(self, label, condition, parent, connector)
        if parent is None:
            self.str = label + ' ' + compare + ' ' + value
        else:
            if connector == 'and':
                self.str = parent.str + ' AND ' + label + ' ' + compare + ' ' + value
            else:
                self.str = parent.str + ' OR ' + label + ' ' + compare + ' ' + value

    def addAnd(self, label, compare, value):
        return Comparison(label, compare, value, self, 'and')
    
    def addOr(self, label, compare, value):
        return Comparison(label, compare, value, self, 'or')
    
    def __str__(self):
        return self.str
    
if __name__ == "__main__":
# some tests
    from calc import SiestaCalc
    example = '../examples/FeCANI'
    c = SiestaCalc(example, dtype = "ani", steps = range(-3,0,1))
    c.evol[0].types.removeTypes()
    comp = Comparison('vp_totvolume', '>', '12')
    comp = comp.addAnd('label', '==', "\'Fe\'")
    c.evol[0].types.addType(comp, 'Fe_big')
    comp2 = Comparison('vp_totvolume', '>', '9')
    comp2 = comp2.addAnd('label', '==', "\'Fe\'")
    c.evol[0].types.addType(comp2, 'Fe_medium')
    comp3 = Comparison('label', '==', "\'C\'")
    c.evol[0].types.addType(comp3, 'C')
    for typ, at in c.evol[0].types:
        print typ
        print at
