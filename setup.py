import re
from pathlib import Path

from setuptools import find_packages, setup

ROOT_DIR = Path(__file__).parent

contents = (ROOT_DIR / "aiohttp_debugtoolbar" / "__init__.py").read_text()
version_match = re.search(r'^__version__ = "([^"]+)"$', contents, re.M)
if version_match is None:
    raise RuntimeError("Unable to determine version.")
version = version_match.group(1)


def read(fname):
    return (ROOT_DIR / fname).read_text().strip()


setup(
    name="aiohttp-debugtoolbar",
    version=version,
    description="debugtoolbar for aiohttp",
    long_description="\n\n".join((read("README.rst"), read("CHANGES.rst"))),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Framework :: AsyncIO",
    ],
    author="Nikolay Novik",
    author_email="nickolainovik@gmail.com",
    url="https://github.com/aio-libs/aiohttp_debugtoolbar",
    license="Apache 2",
    packages=find_packages(),
    install_requires=(
        "aiohttp>=3.9",
        "aiohttp_jinja2",
    ),
    include_package_data=True,
)
