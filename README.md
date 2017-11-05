# Jikken no Heitangaku     ![Status](https://travis-ci.org/outcastofmusic/jikken.svg?branch=master)

___Lightweight experiment manager___
**Jikken** is a cli experiment manager for scientific experiments written in python. It
captures the configuration variables and the stdout, stderr of a python script.
It makes very few assumptions on the experiment and requires almost zero code changes
to the scripts. In fact the only assumption is that the main function of the script to be run
accepts a positional argument with either a directory with json/yaml config files
or a path to single json/yaml file. That's it. Optionally if the code of the
experiment is in a git repo, the git info will be added as well.

### Features
- Python 3 code 
- Support for TinyDB, MongoDB, and ES (to be implemented)
- tagging of experiments
- CLI to access experiment data
- only requires the script to load the variables from a file or folder
- support for json/yaml configs
- understands git directories

## Installation

* git clone the library: `git clone https://github.com/outcastofmusic/jikken.git`
* run `python3 setup.py install`


## USAGE

