#!/bin/bash

if [ $# -ne 1 ]; then
	echo "Usage: $0 <infile.ogg> "
	exit 1
fi

OGGNAME="$(basename $1)"
OGGDIRNAME="$(readlink -m $(dirname $1))"

#docker run --rm -v "$OGGDIRNAME:/tmp" -w /tmp realies/audiowaveform -b 8 --pixels-per-second 10 -i "$OGGNAME" -o "$OGGNAME".waveform.10.json >/dev/null
#docker run --rm -v "$OGGDIRNAME:/tmp" -w /tmp realies/audiowaveform -b 8 --pixels-per-second 5 -i "$OGGNAME" -o "$OGGNAME".waveform.5.json >/dev/null
echo audiowaveform -b 8 --pixels-per-second 3 -i "$OGGDIRNAME/$OGGNAME" -o "$OGGDIRNAME/$OGGNAME".waveform.3.json #| bash ./audiowaveform/run.sh
