#!/usr/bin/env python3
import functools
import pathlib
import re
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

try:
    from pip.req import parse_requirements
except ImportError:  # pip >= 10.0.0
    from pip._internal.req import parse_requirements

WORK_DIR = pathlib.Path(__file__).parent

# Check python version
MINIMAL_PY_VERSION = (3, 6)
if sys.version_info < MINIMAL_PY_VERSION:
    raise RuntimeError('aiograph works only with Python {}+'.format('.'.join(map(str, MINIMAL_PY_VERSION))))


def get_version():
    """
    Read version

    :return: str
    """
    txt = (WORK_DIR / 'aiograph' / '__init__.py').read_text('utf-8')
    try:
        return re.findall(r"^__version__ = '([^']+)'\r?$", txt, re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


def get_description():
    """
    Read full description from 'README.rst'

    :return: description
    :rtype: str
    """
    with open('README.rst', 'r', encoding='utf-8') as f:
        return f.read()


@functools.lru_cache()
def get_requirements(filename=None):
    """
    Read requirements from 'requirements txt'

    :return: requirements
    :rtype: list
    """
    if filename is None:
        filename = 'requirements.txt'

    file = WORK_DIR / filename

    install_reqs = parse_requirements(str(file), session='hack')
    return [str(ir.req) for ir in install_reqs]


class PyTest(TestCommand):
    user_options = []

    def run(self):
        import subprocess
        errno = subprocess.call([sys.executable, '-m', 'pytest', '--cov=aiograph', 'tests'])
        raise SystemExit(errno)


setup(
    name='aiograph',
    version=get_version(),
    packages=find_packages(exclude=('tests', 'tests.*', 'examples.*', 'docs',)),
    url='https://github.com/aiogram/aiograph',
    license='MIT',
    requires_python='>=3.6',
    author='Alex Root Junior',
    author_email='aiogram@illemius.xyz',
    maintainer=', '.join((
        'Alex Root Junior <jroot.junior@gmail.com>',
    )),
    maintainer_email='aiogram@illemius.xyz',
    description='Python asynchronous Telegra.ph API wrapper',
    long_description=get_description(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    install_requires=get_requirements(),
    tests_require=get_requirements('dev_requirements.txt'),
    extras_require={
        'dev': get_requirements('dev_requirements.txt')
    },
    cmdclass={
        'test': PyTest
    }
)
