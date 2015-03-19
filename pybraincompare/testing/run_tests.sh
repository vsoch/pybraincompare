#!/bin/sh

TESTDIR=$1
TEST_RUN_FOLDER=$2

cd $TEST_RUN_FOLDER
nosetests --verbosity=3 --with-doctest $TESTDIR/test_correlation.py $TESTDIR/test_masking.py
