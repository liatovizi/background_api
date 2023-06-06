#!/bin/bash

set -e

BINDIR="$(dirname "$(readlink -m "$0")")"

cd $BINDIR/../../trackdb


cat es_track_spec.csv | awk -v FS="	" '{if (NR ==  1) print "echo \""$0"	Duration	SHA256Sum	URL	OriginalSHA256Sum\""; else print "echo \""$0"	`cat tracks/"$10"/"$1".ogg.duration`	`cat tracks/"$10"/"$1".ogg.sha256`	https://cdn.tgg.thecloudcasting.com/$(cat tracks/"$10"/"$1".ogg.sha256 | head -c1)/$(cat tracks/"$10"/"$1".ogg.sha256| head -c2)/$(cat tracks/"$10"/"$1".ogg.sha256).ogg	`cat tracks/"$10"/"$1".ogg.sha256.original`\""}' |  bash > /tmp/.es_track_spec.extended.csv

if diff /tmp/.es_track_spec.extended.csv es_track_spec.extended.csv > /dev/null; then
	# 2 files are the same
	exit
fi
mv  es_track_spec.extended.csv  es_track_spec.extended.csv.old
mv /tmp/.es_track_spec.extended.csv es_track_spec.extended.csv
cp es_track_spec.extended.csv tracks_by_sha256/es_track_spec.extended.csv
