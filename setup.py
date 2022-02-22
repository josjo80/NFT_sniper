#!/usr/bin/python3
import os
from warnings import warn
from distutils.core import setup
from setuptools import find_packages

REQ_FILE = 'requirements.txt'

if not os.path.exists(REQ_FILE):
      warn("No requirements file found.  Using defaults deps")
      deps = [
            'numpy',
            'pandas',
            'matplotlib',
            'scipy',
            'seaborn',
            'scikit-learn',
            'tensorflow',
            'pyyaml',
            'pynvml']
      warn(', '.join(deps))
else:
      with open(REQ_FILE, 'r') as f:
            deps = f.read().splitlines()


setup(name='NFT_Sniper',
      version='0.0.1',
      description='Identify Mispriced NFTs',
      author='Jason St George',
      author_email='stgeorgejas@gmail.com',
      packages=find_packages(),
      install_requires=deps)

