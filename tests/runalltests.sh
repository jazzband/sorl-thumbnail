#/bin/bash

for name in pil pgmagick imagemagick graphicsmagick wand redis
do
    ./runtests.py --settings=settings.$name;
done
