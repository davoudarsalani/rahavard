from os import path
from setuptools import setup, find_packages

import codecs


here = path.abspath(path.dirname(__file__))
with codecs.open(path.join(here, 'README.md'), encoding='utf-8') as opened:
    long_description = '\n' + opened.read()


VERSION = '0.0.31'
DESCRIPTION = 'Re-Usable Utils'
LONG_DESCRIPTION = 'Re-Usable Utils to Be Used on Our Django Projects'

setup(
    name='rahavard',
    version=VERSION,
    author='Davoud Arsalani',
    author_email='d_arsalani@yahoo.com',
    description=DESCRIPTION,
    long_description_content_type='text/markdown',
    long_description=long_description,
    keywords=['python',],
    url='https://github.com/davoudarsalani/rahavard',
    packages=find_packages(),
    install_requires=[
        'convert_numbers',
        'django',
        'jdatetime',
        'natsort',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
    ],
)
