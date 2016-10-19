#!/bin/bash -x

./test00.sh && ./test01.sh && ./test02.sh && ./test03.sh && ./test04.sh && ./test05.sh

if [ $? -eq 0 ]; then
	echo "All tests passed."
	exit 0
else
	echo "Some test failed."
	exit 1
fi
