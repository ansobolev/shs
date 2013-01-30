#!/opt/epd/bin/python
# -*- coding: utf8 -*-

from distutils.core import setup

long_description = '''
This python module is a set of routines designed to ease the way of making SIESTA calculations, adding them to PBS queue and interpreting the results.
'''

setup(name = 'SHS',
      version = '0.1',
      description = 'Siesta help scripts',
      long_description = long_description,
      author = 'Andrey Sobolev',
      author_email = 'andrey@physics.susu.ac.ru',
      url = 'http://physics.susu.ac.ru/~andrey',
      packages = ['shs', 'shs.vtkxml', 'shs.voronoi', 'shs.voronoi.numpy'],
      package_dir = {'shs' : 'src', 'shs.vtkxml' : 'src/vtkxml', 'shs.voronoi' : 'src/voronoi', 'shs.voronoi.numpy' : 'src/voronoi/numpy'},
      package_data = {'shs' : ['PBS/*.pbs', ]},
      scripts = ['bin/plotmde', 'bin/plotrdf', 'bin/animate', 'bin/plotmsd', 'bin/voronoi_calc.py', 'bin/mean_magmom.py', 'bin/partial_cn.py'],
      license = 'GPL'
     )

