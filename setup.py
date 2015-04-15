#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from setuptools import setup, find_packages

def load_requirements(fname):
    is_comment = re.compile("^\s*(#|--).*").match
    with open(fname) as fo:
        return [line.strip() for line in fo if not is_comment(line) and line.strip()]

with open("README.rst", "rt") as f: readme = f.read()
with open("HISTORY.rst", "rt") as f: history = f.read().replace(".. :changelog:", "")
with open("arff_utils/__init__.py") as f: version_file_contents = f.read()

requirements = load_requirements("requirements.txt")
requirements_tests = load_requirements("requirements_tests.txt")

ver_dic = {}
exec(compile(version_file_contents, "arff_utils/__init__.py", "exec"), ver_dic)

setup(
    name="arff_utils",
    version=ver_dic["VERSION"],
    description="Library for reading and writing ARFF files and converting from ARFF to Pandas or Numpy data structures",
    long_description=readme + "\n\n" + history,
    author="Ralph Brecheisen",
    author_email="ralph.brecheisen@gmail.com",
    url="https://github.com/rbrecheisen/arff_utils",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    license="LGPL v3",
    zip_safe=False,
    keywords="arff_utils",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Scientific/Engineering"
    ],
    test_suite="tests",
    tests_require=requirements_tests
)
