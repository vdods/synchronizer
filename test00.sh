#!/bin/bash -x

# Run `wait-for` mode as a separate process, then wait on the success of a `tell` mode process.
python2 synchronizer.py --wait-for=SPLUNGE --wait-on-port=45954 &
python2 synchronizer.py --tell=localhost:45954/SPLUNGE --debug-spew=true

if [ $? -eq 0 ]; then
    echo "Test passed."
    exit 0
else
    echo "Test failed."
    exit 1
fi
