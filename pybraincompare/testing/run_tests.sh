#!/bin/sh

TESTDIR=$1
TEST_RUN_FOLDER=$2

# Make sure the user supplied input arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: ./run_tests.sh [directory_run_tests_from] [folder_with_tests]"
    echo "       ./run_tests.sh $PWD $PWD"
    exit
fi

cd $TEST_RUN_FOLDER
nosetests --verbosity=3 --with-doctest --with-coverage --cover-package=pybraincompare $TESTDIR/test_correlation.py $TESTDIR/test_masking.py
ls $TESTDIR/* -1
ls $TEST_RUN_FOLDER/* -1
echo $PWD
ls $PWD -1
