from os import path

from setuptools import find_packages, setup
from options_scraper import __version__


this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

VERSION = __version__
DISTNAME = 'options_scraper'
LICENSE = 'GNU GPLv3'
AUTHOR = 'Abhishek Singh'
MAINTAINER = 'Abhishek Singh'
MAINTAINER_EMAIL = 'aosingh@asu.edu'
DESCRIPTION = 'NASDAQ Options chain scraper for https://old.nasdaq.com'
URL = 'https://github.com/aosingh/options_scraper'

PACKAGES = ['options_scraper']

DEPENDENCIES = ['lxml', 'requests', 'urllib3']

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Education',
    'Intended Audience :: Developers',
    'Intended Audience :: Financial and Insurance Industry',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Topic :: Office/Business :: Financial',
    'Topic :: Text Processing :: Markup :: HTML',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Unix',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: MacOS'
]
keywords = 'nasdaq options chain scraper'


setup(
    name=DISTNAME,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=MAINTAINER_EMAIL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    url=URL,
    version=VERSION,
    entry_points={
        'console_scripts': [
            'options-scraper= options_scraper.scraper:main'
        ]
    },
    packages=find_packages(exclude=("tests",)),
    package_dir={'options_scraper': 'options_scraper'},
    install_requires=DEPENDENCIES,
    include_package_data=True,
    classifiers=classifiers,
    keywords=keywords,
)