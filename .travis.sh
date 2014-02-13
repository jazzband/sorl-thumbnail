#!/usr/bin/env bash

REPO_WHEEL=https://raw.github.com/mariocesar/sorl-thumbnail/wheels/wheel

pip install -U pip

pip install Wheel

if python --version 2>&1 >/dev/null | grep -q 'Python 3'; then
    pip install Pillow;
else
    pip install $REPO_WHEEL/Pillow-2.3.0-cp27-none-linux_x86_64.whl;
fi

pip install Pillow

pip install $PIP

pip install Django$DJANGO_VERSION

pip install coveralls