#!/usr/bin/env python3
from setuptools import setup, find_packages
import os
import sys

# Read the version from the main file
with open('BSG_IDE.py', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('self.__version__'):
            version = line.split('"')[1]
            break
    else:
        version = "4.0.0"

# Read long description from README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="bsg-ide",
    version=version,
    description="Beamer Slide Generator IDE - Integrated development environment for creating LaTeX Beamer presentations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ninan Sajeeth Philip",
    author_email="nsp@airis4d.com",
    url="https://github.com/sajeethphilip/Beamer-Slide-Generator",
    packages=find_packages(),
    py_modules=["BSG_IDE", "BeamerSlideGenerator"],
    include_package_data=True,
    package_data={
        '': ['*.png', '*.txt', '*.md', 'requirements.txt'],
    },
    entry_points={
        'console_scripts': [
            'bsg-ide=BSG_IDE:launch_ide',
        ],
        'gui_scripts': [
            'bsg-ide-gui=BSG_IDE:launch_ide',
        ]
    },
    install_requires=[
        "customtkinter>=5.2.2",
        "Pillow>=10.0.0",
        "requests>=2.31.0",
        "yt-dlp>=2023.11.16",
        "opencv-python>=4.8.0",
        "screeninfo>=0.8.1",
        "numpy>=1.24.0",
        "PyMuPDF>=1.23.7",
        "pyautogui>=0.9.54",
        "pyspellchecker>=0.7.2",
        "latexcodec>=2.0.1",
        "latex>=0.7.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Office/Business",
        "Topic :: Multimedia :: Graphics :: Presentation",
        "Topic :: Text Processing :: Markup :: LaTeX",
    ],
    keywords="latex beamer presentation slides ide editor",
    project_urls={
        "Bug Reports": "https://github.com/sajeethphilip/Beamer-Slide-Generator/issues",
        "Source": "https://github.com/sajeethphilip/Beamer-Slide-Generator",
        "Documentation": "https://github.com/sajeethphilip/Beamer-Slide-Generator/wiki",
    },
)
