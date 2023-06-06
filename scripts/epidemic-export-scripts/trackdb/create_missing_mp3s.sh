#!/bin/bash
set -e
BINDIR="$(dirname "$(readlink -m "$0")")"/..
cd $BINDIR/../trackdb
find ./tracks_by_sha256 -type f -name '*.ogg' -exec echo "if ! [ -e {}.mp3 ]; then echo converting {}; sox {} -C 64 {}.tmp.mp3; mv {}.tmp.mp3 {}.mp3 ; fi" \; | parallel | nl
