#!/bin/bash

if [ $# -ne 2 ]; then
	echo "Usage: $0 <oggfile> <durationfile>"
	exit 1
fi

soxi -D  "$1"  > $2
