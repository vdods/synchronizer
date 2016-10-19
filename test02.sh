#!/bin/bash -x

# Test the timeout function of a `tell` mode process.  Expect the return code to be 1.
python2 synchronizer.py --tell=localhost:45954/SPLUNGE --debug-spew=true --timeout=5

if [ $? -eq 1 ]; then
    echo "Test passed."
    exit 0
else
    echo "Test failed."
    exit 1
fi
