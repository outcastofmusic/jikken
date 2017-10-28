from setuptools import setup, find_packages

setup(name='jikken',
      version='0.1.0',
      license='BSD',
      description='Minimal Python3 CLI Experiment Manager',
      author='Agis Oikonomou',
      url='https://github.com/outcastofmusic/jikken',
      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      install_requires=['Click', 'tinydb'],
      tests_require=['pytest', 'pytest-mock'],
      extras_require={'mongo': 'pymongo'},
      entry_points={
          'console_scripts': [
              'jikken = jikken.cli:jikken_cli',
          ]
      },
      )