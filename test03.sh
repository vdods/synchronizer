#!/bin/bash -x

# Test the timeout function of a `wait-for` mode process.  Expect the return code to be 1.
python2 synchronizer.py --wait-for=SPLUNGE --wait-on-port=45954 --debug-spew=true --timeout=5

if [ $? -eq 1 ]; then
    echo "Test passed."
    exit 0
else
    echo "Test failed."
    exit 1
fi
