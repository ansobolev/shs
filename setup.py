#!/opt/epd/bin/python
# -*- coding: utf8 -*-

from distutils.core import setup

long_description = '''
This python module is a set of routines designed to ease the way of making SIESTA calculations, adding them to PBS queue and interpreting the results.
'''

setup(name = 'SHS',
      version = '0.3',
      description = 'Siesta help scripts',
      long_description = long_description,
      author = 'Andrey Sobolev',
      author_email = 'andrey@physics.susu.ac.ru',
      url = 'http://physics.susu.ac.ru/~andrey',
      packages = ['shs', 
                  'shs.vtkxml', 
                  'shs.voronoi', 
                  'shs.voronoi.numpy',
                  'shs.gui',
                  ],
      package_dir = {'shs' : 'src', 
                     'shs.vtkxml' : 'src/vtkxml', 
                     'shs.voronoi' : 'src/voronoi', 
                     'shs.voronoi.numpy' : 'src/voronoi/numpy',
                     'shs.gui' : 'src/gui',
                     },
      package_data = {'shs' : ['PBS/*.pbs', 'slurm/*'],
                      'shs.gui' : ['data-export-icon.png', ],
                      },
      scripts = ['bin/plotmde', 
                 'bin/plotrdf', 
                 'bin/plotmsd', 
                 'src/gui/app.py',
                 ],
      license = 'MIT'
     )

