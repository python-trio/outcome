from setuptools import find_packages, setup

version = dict()

with open('src/outcome/_version.py') as fp:
    version_mod = fp.read()

exec(version_mod, version)

LONG_DESC = open('README.rst').read()

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
    license='MIT OR Apache-2.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=['attrs>=19.2.0'],
    python_requires='>=3.7',
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
