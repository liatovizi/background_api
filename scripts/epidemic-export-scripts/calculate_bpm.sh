#!/bin/bash

bpm-tag -fn "$1" 2>&1 | tr -d \:
