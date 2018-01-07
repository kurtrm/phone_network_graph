# Communication Network Graph

_See the visualization [here](https://kurtrm.github.io/phone_network_graph/)._

---
### Description
[![Build Status](https://travis-ci.org/kurtrm/phone_network_graph.svg?branch=master)](https://travis-ci.org/kurtrm/phone_network_graph) [![Coverage Status](https://coveralls.io/repos/github/kurtrm/phone_network_graph/badge.svg)](https://coveralls.io/github/kurtrm/phone_network_graph)

Version: *1.0*

Module that parses T-Mobile phone bills, cleans the data, and creates a visualization using d3.js.
* Provides a parser that uses PyPDF2 to extract data from T-Mobile phone bills and puts them into a dictionary.
* A crude implementation of a labeled property graph data structure.
* A rudimentary visualization of the network graph using d3.js, as well as jupyter notebooks used for data cleaning and manipulation.

### Authors
---
* [Kurt Maurer](https://github.com/kurtrm/phone_network_graph)

### Dependencies
---
* PyPDF2
* Pandas
* Numpy

### Getting Started
---
##### *Prerequisites*
* [python (3.6+)](https://www.python.org/downloads/)
* [pip](https://pip.pypa.io/en/stable/)
* [git](https://git-scm.com/)

##### *Installation*
First, clone the project repo from Github. Then, change directories into the cloned repository. To accomplish this, execute these commands:

`$ git clone https://github.com/kurtrm/phone_network_graph.git`

`$ cd phone_network_graph`

Now now that you have cloned your repo and changed directories into the project, create a virtual environment named "ENV", and install the project requirements into your VE.

`$ python3 -m venv ENV`

`$ source ENV/bin/activate`

`$ pip install -e .`

`$ pip install -e .[testing]`

### Test Suite
---
##### *Running Tests*
This application uses [pytest](https://docs.pytest.org/en/latest/) as a testing suite. To run tests, run:

``$ pytest``

To view test coverage, run:

``$ pytest --cov``
##### *Test Files*
The testing files for this project are:

| File Name | Description |
|:---:|:---:|
| `./tests/test_labeled_property_graph.py` | Test labeled property graph comprehensively. |
| `./tests/test_parser.py` | Test parser to ensure we are getting expected values. Many tests target assumptions, not necessarily code. |
| `./tests/test_refactored_lpg.py` | Test refactored labeled property graph. |

### Development Tools
---
* *python* - programming language

### License
---
This project is licensed under MIT License - see the LICENSE.md file for details.
### Acknowledgements
---
* Coffee

*This README was generated using [writeme.](https://github.com/chelseadole/write-me)*
