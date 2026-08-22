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
    description="A modern PyQt6 note-taking application with rich text, code editing and three themes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MarbleLabs1/C0lornote",
    author="MarbleCeo",
    author_email="",
    license="Proprietary",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Personal Information Management",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Environment :: X11 Applications :: Gnome",
    ],
    keywords="notes, note-taking, markdown, rich text, pyqt6",
    packages=find_packages(include=["src", "src.*"]),
    python_requires=">=3.9",
    install_requires=[
        "PyQt6>=6.5.0",
        "SQLAlchemy>=2.0.0",
        "PyYAML>=6.0",
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
            "c0lornote=src.main:main",
        ],
        "gui_scripts": [
            "c0lornote-gui=src.main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/MarbleLabs1/C0lornote/issues",
        "Source": "https://github.com/MarbleLabs1/C0lornote",
    },
)

