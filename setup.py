"""
Setup script for sona
"""
from distutils.core import setup
setup(name='sona',
      description='A small python noise generator using PyAudio',
      version='0.1',
      packages=['sona', 'sona.generators'],
      package_dir={'': 'src'}
      )
