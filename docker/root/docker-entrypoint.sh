#!/usr/bin/env bash

set -e

WORKDIR=${WORKDIR:-"/workdir"}

# install the module mounted in $WORKDIR
if [ -e $WORKDIR/setup.py ]; then
    pip install -e $WORKDIR
elif [ -e /home/spendyala/setup.py ]; then
    pip install -e /home/spendyala
elif [ -e /home/spendyala/project/setup.py ]; then
    pip install -e /home/spendyala/project
fi

HOME=/home/spendyala
if [ -d "/home/spendyala/project" ]; then
    exec su -m - spendyala -c "cd /home/spendyala/project; $@"
else
    exec su -m - spendyala -c "cd /home/spendyala; $@"
fi
