from setuptools import setup, find_packages
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


setup(name='aiohttp-debugtoolbar',
      version=version,
      description='debugtoolbar for aiohttp',
      long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: AsyncIO',
      ],
      author='Nikolay Novik',
      author_email='nickolainovik@gmail.com',
      url='https://github.com/aio-libs/aiohttp_debugtoolbar',
      license='Apache 2',
      packages=find_packages(),
      install_requires=[
          'aiohttp>=3.3.0',
          'aiohttp_jinja2'
      ],
      include_package_data=True)
