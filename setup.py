from setuptools import setup, find_packages
import os
import pathlib
import re


with (pathlib.Path(__file__).parent /
      'aiohttp_debugtoolbar' / '__init__.py').open() as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'$", fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


def read(fname):
    with (pathlib.Path(__file__).parent / fname).open() as f:
        return f.read().strip()

install_requires = ['aiohttp>=0.21.1', 'aiohttp_jinja2']
tests_require = install_requires + ['nose']


setup(name='aiohttp_debugtoolbar',
      version=version,
      description=("debugtoolbar for aiohttp"),
      long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Internet :: WWW/HTTP'],
      author="Nikolay Novik",
      author_email="nickolainovik@gmail.com",
      url='https://github.com/aio-libs/aiohttp_debugtoolbar',
      license='Apache 2',
      packages=find_packages(),
      install_requires=install_requires,
      tests_require=tests_require,
      test_suite='nose.collector',
      include_package_data=True)
