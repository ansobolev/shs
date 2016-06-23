# ---------------------------------------------
#
# The file fdf.py is part of the shs project.  
# Copyright (c) 2016 Andrey Sobolev  
# License GNU GPL v.2
# See http://github.com/ansobolev/shs for details
#
# ---------------------------------------------
from shs.sio import read_fdf_file, fdf_lines_to_dict


class FDFFile:

    def __init__(self, filename, mode='r'):
        self.name = filename
        self.file = None
        self.fdf_dict = None
        act = {'r': self.read_fdf,
               'w': self.write_fdf}
        act.get(mode)()

    def read_fdf(self):
        lines = read_fdf_file(self.name)
        self.file = open(self.name, 'r')
        self.fdf_dict = fdf_lines_to_dict(lines)

    def write_fdf(self):
        self.file = open(self.name, 'w')

    def __del__(self):
        self.file.flush()
        self.file.close()