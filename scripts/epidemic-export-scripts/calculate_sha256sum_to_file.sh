#!/bin/bash

if [ $# -ne 2 ]; then
	echo "Usage: $0 <oggfile> <sha256file>"
	exit 1
fi

sha256sum "$1" | awk '{print $1}' > $2
