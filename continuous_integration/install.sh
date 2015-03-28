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
    pip install Cython
    pip install nibabel
    # Install several packages from source
    CWD=$PWD
    cd /tmp
    wget https://pypi.python.org/packages/source/s/six/six-1.9.0.tar.gz
    tar -xzvf six-1.9.0.tar.gz
    cd six-1.9.0
    python setup.py install
    cd ..
    rm six-1.9.0.tar.gz
    rm -rf six-1.9.0
    wget https://pypi.python.org/packages/source/n/networkx/networkx-1.9.1.tar.gz
    tar -xzvf networkx-1.9.1.tar.gz
    cd networkx-1.9.1
    python setup.py install
    cd ..
    rm networkx-1.9.1.tar.gz
    rm -rf networkx-1.9.1
    git clone http://github.com/scikit-image/scikit-image.git
    cd scikit-image
    pip install .
    cd ..
    rm -rf scikit-image
    pip install nilearn
    cd $CWD
}

create_new_venv() {
    # At the time of writing numpy 1.9.1 is included in the travis
    # virtualenv but we want to be in control of the numpy version
    # we are using for example through apt-get install
    sudo apt-get install python-nose python-numpy python-scipy python-matplotlib python-pandas python-sympy python-sklearn
    deactivate
    virtualenv --system-site-packages testvenv
    source testvenv/bin/activate
    pip install nose
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
