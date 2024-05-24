#!/bin/bash

set -ex -o pipefail

CHECK_FILES="src tests"
YAPF_VERSION=0.20.1

# Log some general info about the environment
echo "::group::Environment"
uname -a
env | sort
echo "::endgroup::"

################################################################
# We have a Python environment!
################################################################

echo "::group::Versions"
python -c "import sys, struct; print('python:', sys.version); print('version_info:', sys.version_info); print('bits:', struct.calcsize('P') * 8)"
echo "::endgroup::"

echo "::group::Install dependencies"
python -m pip install -U pip build
python -m pip --version

python -m build
python -m pip install dist/*.whl
echo "::endgroup::"

echo "::group::Setup for tests"
# Install dependencies.
pip install -Ur test-requirements.txt
echo "::endgroup::"

if [ "$CHECK_FORMATTING" = "1" ]; then
    echo "::group::Yapf"
    pip install yapf==${YAPF_VERSION} "isort>=5" mypy pyright
    if ! yapf -rpd $CHECK_FILES; then
        echo "::endgroup::"
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
        echo "::error:: yapf found issues"
        exit 1
    else
        echo "::endgroup::"
    fi

    echo "::group::isort"
    if ! isort --check-only --diff $CHECK_FILES ; then
        echo "::endgroup::"
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
        echo "::error:: isort found issues"
        exit 1
    else
        echo "::endgroup::"
    fi

    echo "::group::Mypy"
    if ! mypy src/ tests/type_tests.py ; then
        echo "::endgroup::"
        cat <<EOF
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Type checking errors were found (listed above). To get more detail, run

   pip install mypy
   mypy src/ tests/type_tests.py

in your local checkout.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
EOF
        echo "::error:: Mypy found issues"
        exit 1
    else
        echo "::endgroup::"
    fi

    echo "::group::Pyright"
    if ! pyright --verifytypes outcome src/outcome/ ; then
        cat <<EOF
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Types are not complete (listed above). To get more detail, run

   pip install pyright
   pyright --verifytypes outcome src/outcome/

in your local checkout.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
EOF
        echo "::error:: Pyright found issues"
        exit 1
    else
        echo "::endgroup::"
    fi

    exit 0
fi

echo "::group:: Run Tests"
pytest -W error -ra -v tests --cov --cov-config=.coveragerc
echo "::endgroup::"

echo "::group:: Code Coverage"
bash <(curl -s https://codecov.io/bash)
echo "::endgroup::"