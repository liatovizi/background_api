#!/bin/bash

set -e

BINDIR="$(dirname "$(readlink -m "$0")")/.."

cd $BINDIR/../trackdb

find ./tracks -type f -name '*.ogg' -exec echo 'if ! [ -e "tracks_by_sha256/$(cat {}.sha256 | head -c1)/$(cat {}.sha256 | head -c2)/$(cat {}.sha256).ogg" ]; then echo copying {}; ' mkdir -p "tracks_by_sha256/\$(cat {}.sha256 | head -c1)/\$(cat {}.sha256 | head -c2)/; cp {} tracks_by_sha256/\$(cat {}.sha256 | head -c1)/\$(cat {}.sha256 | head -c2)/\$(cat {}.sha256).ogg; fi " \;  | parallel | nl
