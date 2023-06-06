#!/bin/sh
cd ../..; pipenv run pylint -r n -f bgservice natapp tests db-migration dev-utils
