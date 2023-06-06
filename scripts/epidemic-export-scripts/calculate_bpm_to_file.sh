#!/bin/bash

if [ $# -ne 2 ]; then
	echo "Usage: $0 <oggfile> <bpmfile>"
	exit 1
fi

bpm-tag -fn "$1" 2>&1 | cut -d \: -f 2 | cut -d \  -f2 > $2
