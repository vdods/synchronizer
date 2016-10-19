#!/bin/bash -x

# Run several `tell` modes as separate processes, then wait on the success of a `wait-for` mode process.
python2 synchronizer.py --tell=localhost:45954/SPLUNGE &
python2 synchronizer.py --tell="localhost:45954/hello Mr. Gumby!" &
python2 synchronizer.py --tell="localhost:45954/FISHY FISH, FISHY, OH." --wait-on-port=45956 &
python2 synchronizer.py --tell=localhost:45954/pencil-droppers --wait-on-port=45957 &

python2 synchronizer.py --wait-for=SPLUNGE \
                        --wait-for="hello Mr. Gumby!" \
                        --wait-for="FISHY FISH, FISHY, OH." \
                        --wait-for=pencil-droppers \
                        --wait-on-port=45954 \
                        --debug-spew=true

if [ $? -eq 0 ]; then
    echo "Test passed."
    exit 0
else
    echo "Test failed."
    exit 1
fi
