#!/bin/bash
set -e

BINDIR="$(dirname "$(readlink -m "$0")")"/..

TEMPDIR="/tmp/conwork"

rm -rf $TEMPDIR

TRACKNUM=0
IMPORTNUM=0
for i in $(find $BINDIR/../epidemic/tracks -type f -name '*.mp3' | sed 's|.*../epidemic/||g'); do 
	i_ogg=$(echo $i | sed 's/\.mp3/.ogg/g'); 
	[ $(( $TRACKNUM % 100 )) == 0 ] && echo processed $TRACKNUM tracks, imported $IMPORTNUM new
	TRACKNUM=$(( $TRACKNUM + 1 ))
	if [ -e $BINDIR/../trackdb/$i_ogg ] && [ -s $BINDIR/../trackdb/$i_ogg ]; then 
		continue; 
	fi; 
	echo starting $i_ogg, imported $IMPORTNUM tracks so far
	IMPORTNUM=$(( $IMPORTNUM + 1 ))
	echo "mkdir -p $TEMPDIR/$i_ogg;
	rm -rf $TEMPDIR/$i_ogg*;
	$BINDIR/convert_to_ogg_mono.sh $BINDIR/../epidemic/$i $TEMPDIR/$i_ogg;
	$BINDIR/calculate_bpm_to_file.sh $TEMPDIR/$i_ogg $TEMPDIR/$i_ogg.bpm;
	$BINDIR/calculate_duration_to_file.sh $TEMPDIR/$i_ogg $TEMPDIR/$i_ogg.duration;
	$BINDIR/calculate_sha256sum_to_file.sh $TEMPDIR/$i_ogg $TEMPDIR/$i_ogg.sha256;
	$BINDIR/calculate_sha256sum_to_file.sh $BINDIR/../epidemic/$i $TEMPDIR/$i_ogg.sha256.original;
	mkdir -p $BINDIR/../trackdb/$i_ogg;
	rm -rf $BINDIR/../trackdb/$i_ogg;
	mv $TEMPDIR/$i_ogg.sha256.original $BINDIR/../trackdb/$(dirname $i_ogg);
	mv $TEMPDIR/$i_ogg.sha256 $BINDIR/../trackdb/$(dirname $i_ogg);
	mv $TEMPDIR/$i_ogg.duration $BINDIR/../trackdb/$(dirname $i_ogg);
	mv $TEMPDIR/$i_ogg.bpm $BINDIR/../trackdb/$(dirname $i_ogg);
	mv $TEMPDIR/$i_ogg $BINDIR/../trackdb/$(dirname $i_ogg);" | bash &
done
echo Waiting for all consersions to finish
wait
