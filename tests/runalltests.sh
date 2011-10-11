#/bin/bash

for name in pil pgmagick imagemagick graphicsmagick redis
do
    ./runtests.py --settings=settings.$name
done
