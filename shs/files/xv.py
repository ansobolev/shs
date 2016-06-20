# ---------------------------------------------
#
# The file xv.py is part of the shs project.  
# Copyright (c) 2016 Andrey Sobolev  
# License GNU GPL v.2
# See http://github.com/ansobolev/shs for details
#
# ---------------------------------------------

import os
import glob


class XVFile:

    def __init__(self, calc_dir):
        """
        Class for reading XV file
        :param calc_dir: calculation directory
        """

        xv_files = glob.glob(os.path.join(calc_dir, '*.XV'))
        assert len(xv_files) == 1, 'files.XVFile: Either no or too many XV files in %s' % (calc_dir, )
        self.name = xv_files[0]
        self.file = open(self.name, 'r')
        self.vectors = []
        self.i_type = []
        self.z = []
        self.crd = []
        self.velocities = []
        lines = self.file.readlines()
        for line in lines[0:3]:
            self.vectors.append([float(x) for x in line.split()[0:3]])
        for line in lines[4:]:
            ls = line.split()
            self.i_type.append(int(ls[0]))
            self.z.append(int(ls[1]))
            self.crd.append([float(x) for x in line.split()[2:5]])
            self.velocities.append([float(x) for x in line.split()[5:]])

    def __del__(self):
        self.file.flush()
        self.file.close()
