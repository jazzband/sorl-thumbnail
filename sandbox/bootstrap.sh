#!/bin/sh
apt-get update
apt-get install -qq python-software-properties python-pip
apt-get install -qq libjpeg62 libjpeg62-dev zlib1g-dev imagemagick graphicsmagick redis-server
apt-get install -qq libmagickwand-dev libgraphicsmagick++-dev libboost-python-dev libboost-thread-dev

add-apt-repository -y ppa:fkrull/deadsnakes
apt-get update
apt-get install -qq python2.7 python2.7-dev python3.3 python3.3-dev

pip install tox

echo 'alias runtests="sh /vagrant/sandbox/tox.sh"' >> /home/vagrant/.bash_aliases
