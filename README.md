# Jikken 実験    ![Status][travis-image]

**Jikken** is a lightweight cli experiment manager for scientific experiments written in python.

It makes very few assumptions on the experiment and requires almost zero code changes
to the scripts. In fact the only assumption is that the main function of the script to be run
accepts a positional argument with either a directory with json/yaml config files
or a path to single json/yaml file. That's it. Optionally if the code of the
experiment is in a git repo, the git info will be added as well.

#### Features
- Python 3 code
- Support for TinyDB, MongoDB, and ES (to be implemented)
- tagging of experiments
- CLI to access experiment data
- only requires the script to load the variables from a file or folder
- support for json/yaml configs
- understands git directories

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
- python 3.5 or higher
- pip
- running mongodb version (for use with mongodb)

### Installing

* git clone the library:
```
 git clone https://github.com/outcastofmusic/jikken.git
```
* run the setup install:
```
python3 setup.py install
```
#### Setup the Config

End with an example of getting some data out of the system or using it for a little demo

## Usage

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Contributing

1. Fork it (<https://github.com/yourname/yourproject/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request


## Release History

* 0.1.0
    * Work in progress

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Agis Oikonomou** - *Initial work*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Brian Okken and his great book on python testing: [Python Testing with Pytest](https://pragprog.com/book/bopytest/python-testing-with-pytest)
* Francois Chollet and his book [Deep Learning with Python](https://www.manning.com/books/deep-learning-with-python)

<!-- Markdown link & img dfn's -->
[travis-image]: https://travis-ci.org/outcastofmusic/jikken.svg?branch=master
[wiki]: https://github.com/outcastofmusic/jikken/wiki