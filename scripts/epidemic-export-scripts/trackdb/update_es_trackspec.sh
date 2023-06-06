#!/bin/bash

set -e

BINDIR="$(dirname "$(readlink -m "$0")")"

cd $BINDIR/../../trackdb

if [ -e ../epidemic/es_track_spec.csv ] && [ -s ../epidemic/es_track_spec.csv ] && ! diff es_track_spec.csv ../epidemic/es_track_spec.csv >/dev/null; then
	mv es_track_spec.csv es_track_spec.csv.old
	cp ../epidemic/es_track_spec.csv es_track_spec.csv
fi
