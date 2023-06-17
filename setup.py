# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 07:14:27 2023

@author: richie bao
"""
from setuptools import setup, find_packages
from pathlib import Path
import usda_dashboard
from typing import List

# this_directory= Path(__file__).parent
# long_description = (this_directory / 'README.md').read_text()
def get_install_requires() -> List[str]:
    """Returns requirements.txt parsed to a list"""
    fname = Path(__file__).parent / 'requirements.txt'
    targets = []
    if fname.exists():
        with open(fname, 'r') as f:
            targets = f.read().splitlines()
    return targets

# print(get_install_requires())

setup(
      name='usda_dashboard',
      version=usda_dashboard.__version__,
      license='GNU',
      author='richie bao',
      author_email='richiebao@outlook.com',
      url='https://github.com/richieBao',
      packages=find_packages(),
      install_requires=get_install_requires(), # ['pandas','sqlalchemy','pyodbc','dash','dash_bootstrap_components','dash_mantine_components','openpyxl'],
      description='dashborad for USDA',
      # long_description=long_description,
      # long_description_content_type='text/markdown',
      include_package_data=True,
      package_data={"usda_dashboard.data":["*.xlsx","*.accdb","*.geojson"]},
      )