#!/bin/bash
set -e
BINDIR="$(dirname "$(readlink -m "$0")")"/..
cd $BINDIR/../trackdb

find ./tracks_by_sha256 -type f -name '*.ogg' -exec echo "if ! [ -e `pwd`/{}.waveform.3.json ] ; then echo echo creating waveform for: {}; '$BINDIR/create_waveform.sh' `pwd`/{}; fi" \; | bash | bash $BINDIR/audiowaveform/run.sh | nl
