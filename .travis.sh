#!/usr/bin/env bash

set -x

REPO_WHEEL=https://raw.github.com/mariocesar/sorl-thumbnail/wheels/wheel

pip install -U pip

pip install Wheel

if python --version 2>&1 >/dev/null | grep -q 'Python 3'; then

    wget $REPO_WHEEL/PyYAML-3.10-cp32-cp32mu-linux_x86_64.whl

    pip install Pillow;
    pip install PyYAML-3.10-cp32-cp32mu-linux_x86_64.whl

else

    wget $REPO_WHEEL/Pillow-2.3.0-cp27-none-linux_x86_64.whl
    wget $REPO_WHEEL/PyYAML-3.10-cp27-none-linux_x86_64.whl

    pip install Pillow-2.3.0-cp27-none-linux_x86_64.whl
    pip install PyYAML-3.10-cp27-none-linux_x86_64.whl

fi

if [[ -z "$WHEEL" ]]; then
else
    wget $REPO_WHEEL/$WHEEL
    pip install $WHEEL
fi

if [[ -z "$PIP" ]]; then
else
    pip install $PIP
fi

pip install Django$DJANGO_VERSION

pip install coveralls