#!/bin/bash
#RSYNC_PASSWORD="iMcsh3ahOAkE7g"
BINDIR=`dirname \`readlink -m "$0"\``
PWFILE="$BINDIR/../config/pwfile"
#RSYNC_SERVER="synclib@213.136.43.18::share"
RSYNC_SERVER="synclib@ec2-54-246-74-78.eu-west-1.compute.amazonaws.com::share"
/usr/bin/rsync -avz --progress --password-file "$PWFILE" $RSYNC_SERVER /mnt/data/epidemic
