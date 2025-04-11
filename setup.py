#!/usr/bin/env python3
"""
Setup script for C0lorNote application.
"""

import os
from setuptools import setup, find_packages

# Get the long description from the README file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="c0lornote",
    version="1.0.0",
    description="A modern note-taking application inspired by macOS Notes and Google Keep",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/c0lornote",
    author="Your Name",
    author_email="your.email@example.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Personal Information Management",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: Gnome",
    ],
    keywords="notes, note-taking, markdown, rich text, tkinter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "ttkthemes>=3.0.0",
        "pillow>=10.0.0",
        "reportlab>=4.0.0",
        "sqlalchemy>=2.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    package_data={
        "c0lornote": [
            "assets/*.png",
            "assets/*.ico",
            "assets/*.svg",
        ],
    },
    data_files=[
        ("share/applications", ["debian/c0lornote.desktop"]),
        ("share/pixmaps", ["assets/c0lornote.png"]),
        ("share/icons/hicolor/48x48/apps", ["assets/c0lornote.png"]),
        ("share/icons/hicolor/256x256/apps", ["assets/c0lornote.png"]),
    ],
    entry_points={
        "console_scripts": [
            "c0lornote=c0lornote.main:main",
        ],
        "gui_scripts": [
            "c0lornote-gui=c0lornote.main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/c0lornote/issues",
        "Source": "https://github.com/yourusername/c0lornote",
    },
)

