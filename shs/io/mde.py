# ---------------------------------------------
#
# The file mde.py is part of the shs project.  
# Copyright (c) 2016 Andrey Sobolev  
# License GNU GPL v.2
# See http://github.com/ansobolev/shs for details
#
# ---------------------------------------------
import glob

import numpy as np
import os


class MDEFile:

    def __init__(self, calc):
        """
        Class for reading MDE files
        :param calc: Siesta calculation
        """
        # get MDE file name
        mde_names = glob.glob(os.path.join(calc.dir, '*.MDE'))
        if len(mde_names) != 1:
            raise ValueError('Calc.ReadMDE: Either no or too many MDE files in %s' % (dir, ))
        dt = {'names': ('step', 'temp', 'e_ks', 'e_tot', 'vol', 'p'),
              'formats': ('i4', 'f4', 'f4', 'f4', 'f4', 'f4')
              }
        self.file_name = mde_names[0]
        data = np.loadtxt(self.file_name, dtype=dt)
        self.n_steps = len(data['step'])
        print 'SIO.ReadMDE : Found %i steps' % (self.n_steps,)
        data['step'] = np.arange(self.n_steps)
        self.data = data
