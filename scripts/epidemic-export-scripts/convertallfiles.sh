find -type f -name '*.ogg' -exec  echo '/data/scripts/convert_to_ogg_mono.sh {} ../tracks.converted/{}; mv ../tracks.converted/{} {}; /data/scripts/calculate_sha256sum_to_file.sh {} {}.sha256; /data/scripts/calculate_bpm_to_file.sh {} {}.bpm' \; > /tmp/commands
find -type f -name '*.ogg' -exec  echo '/data/scripts/convert_to_ogg_mono.sh {} ../tracks.converted/{}; rm {}; /data/scripts/calculate_sha256sum_to_file.sh ../tracks.converted/{} ../tracks.converted/{}.sha256; /data/scripts/calculate_bpm_to_file.sh ../tracks.converted/{} ../tracks.converted/{}.bpm';  /data/scripts/calculate_duration_to_file.sh ../tracks.converted/{} ../tracks.converted/{}.duration';\; > /tmp/commands