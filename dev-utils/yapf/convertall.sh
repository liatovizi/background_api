#!/bin/bash
cd ../..; for f in `find . -name '*.py'`; do echo $f; pipenv run python dev-utils/yapf/convert.py $f; done
