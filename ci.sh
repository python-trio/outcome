#!/bin/bash

set -ex

CHECK_FILES="setup.py src tests"
YAPF_VERSION=0.20.1

pip install -U pip setuptools wheel

python setup.py sdist --formats=zip
pip install dist/*.zip

if [ "$CHECK_FORMATTING" = "1" ]; then
    pip install yapf==${YAPF_VERSION} "isort>=5"
    if ! yapf -rpd $CHECK_FILES; then
        cat <<EOF
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Formatting problems were found (listed above). To fix them, run

   pip install yapf==${YAPF_VERSION}
   yapf -rpi $CHECK_FILES

in your local checkout.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
EOF
        exit 1
    fi

    # required for isort to order test imports correctly
    pip install -Ur test-requirements.txt

    if ! isort --check-only --diff $CHECK_FILES ; then
        cat <<EOF
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Formatting problems were found (listed above). To fix them, run

   pip install isort
   isort $CHECK_FILES

in your local checkout.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
EOF
        exit 1
    fi
    exit 0
fi

# Actual tests
pip install -Ur test-requirements.txt

pytest -W error -ra -v tests --cov --cov-config=.coveragerc

bash <(curl -s https://codecov.io/bash)
