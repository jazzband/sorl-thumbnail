#/bin/bash

for name in pil pgmagick imagemagick graphicsmagick redis wand
do
    ./runtests.py --settings=settings.$name;
done
