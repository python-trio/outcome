# coding: utf-8
from __future__ import absolute_import, division, print_function

from io import open

from setuptools import find_packages, setup

version = dict()

# read _version.py as bytes, otherwise exec will complain about
# 'coding: utf-8', which we want there for the normal Python 2 import
with open('src/outcome/_version.py', 'rb') as fp:
    version_mod = fp.read()

exec(version_mod, version)

LONG_DESC = open('README.rst', encoding='utf-8').read()

setup(
    name='outcome',
    version=version['__version__'],
    description='Capture the outcome of Python function calls.',
    url='https://github.com/python-trio/outcome',
    project_urls={
        "Documentation": "https://outcome.readthedocs.io/en/latest/",
        "Chat": "https://gitter.im/python-trio/general",
    },
    long_description=LONG_DESC,
    long_description_content_type='text/x-rst',
    author='Frazer McLean',
    author_email='frazer@frazermclean.co.uk',
    license='MIT -or- Apache License 2.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['attrs'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    keywords='result',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Trio',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
