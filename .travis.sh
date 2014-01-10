#!/usr/bin/env bash

REPO_WHEEL=https://github.com/mariocesar/sorl-thumbnail/raw/wheels/wheel

pip install Wheel

if python --version 2>&1 >/dev/null | grep -q 'Python 3'; then
    pip install Pillow;
else
    pip install $REPO_WHEEL/Pillow-2.3.0-cp27-none-linux_x86_64.whl;
fi

pip install $PIP

pip install django==$DJANGO_VERSION

pip install coveralls