#!/bin/bash
# This script is meant to be called by the "install" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behavior of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.
#
# This script is adapted from a similar script from the nilearn repository.
#
# License: 3-clause BSD

set -e

# Fix the compilers to workaround avoid having the Python 3.4 build
# lookup for g++44 unexpectedly.
export CC=gcc
export CXX=g++

install_packages() {
    pip install --upgrade pip
    conda install --yes python=$TRAVIS_PYTHON_VERSION numpy scipy pandas cython six networkx scikit-learn scikit-image matplotlib numexpr
    conda install --yes -c dan_blanchard python-coveralls
}

create_new_venv() {
    wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O miniconda.sh
    chmod +x miniconda.sh
    ./miniconda.sh -b
    export PATH=/home/travis/miniconda/bin:$PATH
    conda update --yes conda
    conda create --yes -n condaenv python=2.7
    conda install --yes -n condaenv pip
    source activate condaenv
}

if [[ "$DISTRIB" == "standard-linux" ]]; then
    create_new_venv
    install_packages

else
    echo "Unrecognized distribution ($DISTRIB); cannot setup travis environment."
    exit 1
fi

if [[ "$COVERAGE" == "true" ]]; then
    pip install coverage coveralls
fi

python setup.py install
