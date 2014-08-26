#!/opt/epd/bin/python
# -*- coding: utf8 -*-

from distutils.core import setup

long_description = '''
This python module is a set of routines designed to ease the way of making SIESTA calculations,
adding them to PBS queue and interpreting the results.
'''

setup(name='SHS',
      version='0.3',
      description='Siesta help scripts',
      long_description=long_description,
      author='Andrey Sobolev',
      author_email='andrey@physics.susu.ac.ru',
      url='http://asobolev.ddns.info',
      packages=['shs',
                'shs.vtkxml',
                'shs.voronoi',
                'shs.voronoi.numpy',
                'shs.gui',
                ],
      package_dir={'shs' : 'shs',
                   'shs.vtkxml': 'shs/vtkxml',
                   'shs.voronoi': 'shs/voronoi',
                   'shs.voronoi.numpy': 'shs/voronoi/numpy',
                   'shs.voronoi.pyvoro': 'shs/voronoi/pyvoro',
                   'shs.gui': 'shs/gui',
                   },
      package_data={'shs' : ['PBS/*.pbs', 'slurm/*'],
                    'shs.gui': ['data-export-icon.png', ],
                    },
      scripts=['bin/plotmde',
               'bin/plotrdf',
               'bin/plotmsd',
               'bin/gui.py',
               'bin/setup_input.py',
               ],
      install_requires=["numpy>=1.8.1",
                        "scipy>=0.14.0",
                        "matplotlib>=1.3.1",
                        "wxPython>=2.8.11.0"],
      license='MIT'
     )

