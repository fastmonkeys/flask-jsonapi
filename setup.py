import os
import re

from setuptools import find_packages, setup

HERE = os.path.dirname(os.path.abspath(__file__))


def get_version():
    filename = os.path.join(HERE, 'flask_jsonapi', '__init__.py')
    contents = open(filename).read()
    pattern = r"^__version__ = '(.*?)'$"
    return re.search(pattern, contents, re.MULTILINE).group(1)


setup(
    name='Flask-JSONAPI',
    version=get_version(),
    description='TODO',
    long_description=(
        open('README.rst').read() + '\n' +
        open('CHANGES.rst').read()
    ),
    author='Janne Vanhala',
    author_email='janne@fastmonkeys.com',
    url='http://github.com/fastmonkeys/flask-jsonapi',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'jsonschema',
        'SQLAlchemy>=1.0',
        'qstring'
    ],
    extras_require={
        'tests': [
            'bunch',
            'psycopg2'
        ],
    },
    package_data={
        '': ['LICENSE']
    },
    license=open('LICENSE').read(),
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
