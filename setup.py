from setuptools import setup, find_packages
from os import path
from imap_storage import VERSION

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='imap-storage',
    version=VERSION,
    description='Use your Email-account as Storage for data structures and files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/snake-soft/imap-storage',

    author='Snake-Soft',
    author_email='info@snake-soft.com',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: System :: Filesystems',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='imap email storage data files',

    packages=find_packages(exclude=['imap-storage']),

    python_requires='>=3.5.3, <4',

    install_requires=['imapclient', 'lxml'],


    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage', 'pylint'],
    },

#    package_data={'sample': ['package_data.dat'],},
#    data_files=[('my_data', ['data/data_file'])],  # Optional
#    entry_points={'console_scripts': ['sample=sample:main',],},

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/snake-soft/imap-storage/issues/',
#        'Funding': 'https://donate.pypi.org',
#        'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://github.com/snake-soft/imap-storage/',
    },
)
