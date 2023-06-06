#!/bin/bash
cd ../..
IFS=$'\n'
for f in `git status --porcelain`; do 
  if [[ "$f" =~ .*\.py ]]; then
    echo $f
    pipenv run python dev-utils/yapf/convert2.py $f
  fi  
done
