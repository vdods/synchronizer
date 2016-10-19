#!/bin/bash -x

# Run several `wait-for` modes as separate processes, then wait on the success of a `tell` mode process.
python2 synchronizer.py --wait-for=SPLUNGE --wait-on-port=45954 &
python2 synchronizer.py --wait-for="hello Mr. Gumby!" --wait-on-port=45955 &
python2 synchronizer.py --wait-for="FISHY FISH, FISHY, OH." --wait-on-port=45956 &
python2 synchronizer.py --wait-for=pencil-droppers --wait-on-port=45957 &

python2 synchronizer.py --tell=localhost:45954/SPLUNGE \
						--tell="localhost:45955/hello Mr. Gumby!" \
                        --tell="localhost:45956/FISHY FISH, FISHY, OH." \
                        --tell=localhost:45957/pencil-droppers \
                        --debug-spew=true

if [ $? -eq 0 ]; then
    echo "Test passed."
    exit 0
else
    echo "Test failed."
    exit 1
fi
