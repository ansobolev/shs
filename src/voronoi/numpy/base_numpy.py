#!/usr/bin/python
# __*__ coding: utf8 __*__

oneline = "Read, write and operate with models"

import numpy as N
import numpy.lib.recfunctions as nlrf

class model_base:
# --------------------------------------------------------------------
    def __init__(self,d={}):
# time: timestep number
        self.time=d.get('time',0)
# box: numpy array of lattice vectors
        box = d.get('box',N.zeros((3,3)))
        self.box = box
        if box.shape == (3,3): self.vc = box
        elif box.shape == (3): self.vc = N.diag(box)
        else:                  raise ValueError ('Box should be (3,3) or (3) array')
# atoms: atoms numpy array
        atoms = d.get('atoms',[])
        
        leg_list = atoms.dtype.names

        if not 'id' in leg_list:       # add 'id' column
            atoms = nlrf.append_fields(atoms, 'id', N.arange(len(atoms))+1, asrecarray=True, usemask=False)
   
        if not 'itype' in leg_list:    # add 'itype' column
            if 'label' in leg_list:
                labels = list(N.unique(atoms['label']))
                labels = dict(zip(labels, range(1,len(labels)+1)))
                ityp = N.array([labels[atom['label']] for atom in atoms])
                atoms = nlrf.append_fields(atoms, 'itype', ityp, asrecarray=True, usemask=False)
            else:   
                atoms = nlrf.append_fields(atoms, 'itype', N.ones(len(atoms)), asrecarray=True, usemask=False)

        self.atoms = atoms
