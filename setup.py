"""
setup.py for gherkin-objects
"""

from pathlib import Path
from setuptools import setup, find_packages, findall

from pbr.packaging import (
    get_version,
    get_requirements_files,
    parse_requirements
)

readme = Path(".", "README.md").absolute()
with readme.open("r", encoding="utf-8") as file:
    long_description = file.read()

PACKAGE_NAME = 'gherkin-objects'
pkgs = find_packages(exclude=["tests"])
version = get_version(package_name=PACKAGE_NAME)

setup(
    name=PACKAGE_NAME,
    author="Aaron Koch",
    author_email="aaron.koch@siriusxm.com",
    packages=pkgs,
    scripts=findall("scripts/"),
    include_package_data=True,
    version=version,
    install_requires=parse_requirements(get_requirements_files()),
    description="Programmatically read, create, and modify Gherkin",
    python_requires=">=3.8",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    platforms=["any"],
    keywords=[
        "gherkin",
        "gherkin-objects",
        "objects",
        "gherkin-formatter",
        "formatter"
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PandoraMedia/gherkin-objects"
)