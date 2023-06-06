DIRNAME="$(readlink -m $(dirname $0))"

cd $DIRNAME

docker run --rm -i -v "/mnt/data/trackdb/tracks_by_sha256:/mnt/data/trackdb/tracks_by_sha256" audiowaveform $@
