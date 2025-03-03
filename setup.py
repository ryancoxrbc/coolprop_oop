from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="coolprop-oop",
    version="1.3.0",
    author="Ryan Cox",
    author_email="ryanbradleycox@gmail.com",
    description="A Pythonic object-oriented wrapper for CoolProp with property validation, state management, and all thermodynamic properties settable",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ryancoxrbc/coolprop_oop",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Development Status :: 5 - Production/Stable",
    ],
    python_requires=">=3.8",
    install_requires=[
        "CoolProp>=6.7.0",
    ],
    include_package_data=True,
    package_data={
        "": ["LICENSE", "README.md"],
    },
) 