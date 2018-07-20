#!/bin/sh
apt-get update
apt-get install -qq git python-software-properties python-pip
apt-get install -qq libjpeg62 libjpeg62-dev zlib1g-dev imagemagick graphicsmagick redis-server
apt-get install -qq libmagickwand-dev libgraphicsmagick++-dev libboost-python-dev libboost-thread-dev
apt-get install -qq libvips-tools

add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install -qq python2.7 python2.7-dev python3.4 python3.4-dev

pip install tox

# Fix locale to allow saving unicoded filenames
echo 'LANG=en_US.UTF-8' > /etc/default/locale

# Start in project dir by default
echo "\n\ncd /vagrant" >> /home/vagrant/.bashrc
