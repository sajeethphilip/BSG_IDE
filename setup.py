#!/usr/bin/env python3
"""
Setup script for BSG-IDE (Beamer Slide Generator IDE)
"""

import os
import sys
from setuptools import setup, find_packages
from pathlib import Path

# Read version from package
__version__ = "5.0.1"

# Read README
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "BSG-IDE: Beamer Slide Generator IDE - Create professional LaTeX presentations with ease"

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Platform-specific dependencies
extras_require = {
    'video': ['opencv-python>=4.5.0', 'yt-dlp>=2023.0.0'],
    'spellcheck': ['pyspellchecker>=0.7.0'],
    'pdf': ['PyMuPDF>=1.23.0'],
    'full': [
        'opencv-python>=4.5.0',
        'yt-dlp>=2023.0.0',
        'pyspellchecker>=0.7.0',
        'PyMuPDF>=1.23.0',
        'screeninfo>=0.8.0',
        'numpy>=1.21.0',
        'requests>=2.25.0'
    ],
    'dev': [
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'black>=22.0.0',
        'flake8>=5.0.0',
        'mypy>=1.0.0',
        'build>=0.10.0',
        'twine>=4.0.0'
    ]
}

# Console scripts entry points
entry_points = {
    'console_scripts': [
        'bsg-ide = bsg_ide.BSG_IDE:launch_ide',
        'bsg = bsg_ide.BSG_IDE:launch_ide',
    ],
    'gui_scripts': [
        'bsg-ide-gui = bsg_ide.BSG_IDE:launch_ide',
    ]
}

setup(
    name="bsg-ide",
    version=__version__,
    author="Ninan Sajeeth Philip",
    author_email="nsp@airis4d.com",
    description="Beamer Slide Generator IDE - Create professional LaTeX presentations with ease",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sajeethphilip/Beamer-Slide-Generator",
    project_urls={
        "Bug Reports": "https://github.com/sajeethphilip/Beamer-Slide-Generator/issues",
        "Source": "https://github.com/sajeethphilip/Beamer-Slide-Generator",
        "Documentation": "https://github.com/sajeethphilip/Beamer-Slide-Generator/wiki",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "Topic :: Text Processing :: Markup :: LaTeX",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    packages=find_packages(exclude=["tests", "docs", "scripts"]),
    include_package_data=True,
    package_data={
        'bsg_ide': [
            'resources/*.png',
            'templates/*.txt',
            '*.py',
        ],
    },
    install_requires=[
        "customtkinter>=5.2.0",
        "Pillow>=9.0.0",
        "requests>=2.25.0",
        "latexcodec>=2.0.0",
    ],
    extras_require=extras_require,
    entry_points=entry_points,
    python_requires=">=3.8",
    keywords="latex beamer presentation slides generator ide",
    zip_safe=False,
)
