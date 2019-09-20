# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nasspy",
    version="0.0.1",
    author="Travis Williams",
    author_email="travis.williams@colorado.edu",
    description=("Python wrappers for the U.S. National Agricultural " +
                 "Statistics Service's Quick Stats API."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WilliamsTravis/nasspy",
    packages=['nasspy'],
    package_data={'nasspy': ['data/*.txt']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['pandas', 'requests'],
    python_requires='>=3.6',
)
