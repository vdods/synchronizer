#!/bin/bash -x

# Run `tell` mode as a separate process, then wait on the success of a `wait-for` mode process.
python2 synchronizer.py --tell=localhost:45954/SPLUNGE &
python2 synchronizer.py --wait-for=SPLUNGE --wait-on-port=45954 --debug-spew=true

if [ $? -eq 0 ]; then
    echo "Test passed."
    exit 0
else
    echo "Test failed."
    exit 1
fi
