#!/bin/bash
# We can't launch setup.py dist directly because of bug in hard linking
# http://stackoverflow.com/questions/7719380/python-setup-py-sdist-error-operation-not-permitted
SOURCE_DIR="/vagrant/*"
TOX_DIR="/home/vagrant/tox/"
mkdir -p $TOX_DIR
rsync -r $SOURCE_DIR $TOX_DIR
cd $TOX_DIR && tox "$@"
