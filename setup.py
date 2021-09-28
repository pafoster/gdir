import os
import pathlib
from setuptools import setup


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.rst').read_text(encoding='utf-8')
version = '0.3.2'

setup(
    name='gdir',
    version=version,
    description='Command line tool which queries Google Directions. Displays results as human-readable text.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/pafoster/gdir',
    download_url='https://github.com/pafoster/gdir/archive/{}.tar.gz'.format(version),
    author='Peter Foster',
    author_email='pyitlib@gmx.us',
    license='MIT',
    packages=['gdir'],
    zip_safe=True,
    install_requires=[
        'colorama~=0.4.4',
        'googlemaps~=4.4.5',
        'pytz~=2021.1'
    ],
	python_requires='>=3',
    keywords=['Google Directions', 'Google Maps', 'command line', 'terminal', 'public transport', 'transit', 'directions'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities ',
    ],
    entry_points={
        'console_scripts': [
            'gdir=gdir.gdir:main',
        ],
    },
)
