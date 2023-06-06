#!/bin/bash

sha256sum "$1" | awk '{print $2, $1}'
