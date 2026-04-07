#!/usr/bin/env python3
"""
BSG-IDE Complete Build and Deployment Script
Version: 5.1.4
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

# Configuration
VERSION = "5.2.3"
PACKAGE_NAME = "bsg_ide"
PYPI_NAME = "bsg-ide"
AUTHOR = "Ninan Sajeeth Philip"
EMAIL = "nsp@airis4d.com"
DESCRIPTION = "Beamer Slide Generator IDE - Create professional LaTeX presentations with multimedia support"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_color(text: str, color: str = Colors.GREEN):
    print(f"{color}{text}{Colors.ENDC}")

class BSGIDEBuildDeploy:
    def __init__(self, version=VERSION):
        self.version = version
        self.package_name = PACKAGE_NAME
        self.pypi_name = PYPI_NAME
        self.project_root = Path.cwd()

        # Create build directories
        self.build_dir = self.project_root / "build_temp"
        self.dist_dir = self.project_root / "dist"
        self.src_dir = self.build_dir / "src"
        self.package_dir = self.src_dir / self.package_name

    def clean_up(self):
        """Clean build directories"""
        print_color("\n🧹 Cleaning up...", Colors.BOLD)

        dirs_to_remove = [self.build_dir, self.dist_dir]
        for d in dirs_to_remove:
            if d.exists():
                shutil.rmtree(d)
                print(f"  ✓ Removed: {d}")

        for pattern in ["*.egg-info", "__pycache__", "*.pyc"]:
            for p in self.project_root.glob("**/" + pattern):
                if p.exists():
                    if p.is_dir():
                        shutil.rmtree(p)
                    else:
                        p.unlink()

        print("  ✓ Cleanup completed")
        return True

    def setup_directories(self):
        """Create directories"""
        print_color("\n📁 Setting up directories...", Colors.BOLD)

        dirs = [
            self.build_dir,
            self.src_dir,
            self.package_dir,
            self.dist_dir,
            self.package_dir / "resources",
            self.package_dir / "templates",
            self.package_dir / "utils",
        ]

        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created: {d}")
        return True

    def copy_source_files(self):
        """Copy source files"""
        print_color("\n📋 Copying source files...", Colors.BOLD)

        source_files = [
            "BeamerSlideGenerator.py",
            "BSG_IDE.py",
            "InteractiveTerminal.py",
            "Grammarly.py",
            "EnhancedCommandDialog.py",
        ]

        for file in source_files:
            src = self.project_root / file
            dst = self.package_dir / file
            if src.exists():
                shutil.copy2(src, dst)
                print(f"  ✓ Copied: {file}")
            else:
                print_color(f"  ⚠ Warning: {file} not found", Colors.YELLOW)

        # Copy resources
        for res in ["airis4d_logo.png", "bsg-ide.png"]:
            src = self.project_root / res
            dst = self.package_dir / "resources" / res
            if src.exists():
                shutil.copy2(src, dst)
                print(f"  ✓ Copied: {res}")

        return True

    def create_init_files(self):
        """Create __init__.py and __main__.py"""
        print_color("\n📝 Creating init files...", Colors.BOLD)

        # __init__.py
        init_content = [
            '"""',
            f'{PYPI_NAME.upper()} - {DESCRIPTION}',
            f'Version: {self.version}',
            '"""',
            '',
            '__version__ = "' + self.version + '"',
            '__author__ = "' + AUTHOR + '"',
            '__license__ = "MIT"',
            '',
            '# Import main components for easy access',
            'from .BSG_IDE import BeamerSlideEditor, launch_ide',
            'from .BeamerSlideGenerator import (',
            '    get_beamer_preamble,',
            '    process_media,',
            '    process_input_file,',
            '    construct_search_query,',
            '    open_google_image_search,',
            '    download_media,',
            ')',
            '',
            '# For backward compatibility',
            'from .InteractiveTerminal import InteractiveTerminal',
            'from .Grammarly import GrammarlyIntegration',
            '',
            '__all__ = [',
            '    "BeamerSlideEditor",',
            '    "launch_ide",',
            '    "get_beamer_preamble",',
            '    "process_media",',
            '    "process_input_file",',
            '    "construct_search_query",',
            '    "open_google_image_search",',
            '    "download_media",',
            '    "InteractiveTerminal",',
            '    "GrammarlyIntegration",',
            ']',
        ]

        init_file = self.package_dir / "__init__.py"
        init_file.write_text('\n'.join(init_content))
        print(f"  ✓ Created: {init_file}")

        # __main__.py
        main_content = [
            '"""Main entry point for BSG-IDE"""',
            '',
            'import sys',
            'import os',
            'from pathlib import Path',
            '',
            '# Ensure we can find resources',
            'from .BSG_IDE import launch_ide',
            '',
            'if __name__ == "__main__":',
            '    launch_ide()',
        ]

        main_file = self.package_dir / "__main__.py"
        main_file.write_text('\n'.join(main_content))
        print(f"  ✓ Created: {main_file}")

        return True

    def create_setup_files(self):
        """Create setup files"""
        print_color("\n🔧 Creating setup files...", Colors.BOLD)

        # Create a proper setup.py
        setup_content = [
            '#!/usr/bin/env python3',
            '"""Setup script for BSG-IDE"""',
            'from setuptools import setup, find_packages',
            'from pathlib import Path',
            '',
            '__version__ = "' + self.version + '"',
            '',
            '# Read README',
            'readme_file = Path(__file__).parent / "README.md"',
            'long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else "' + DESCRIPTION + '"',
            '',
            'setup(',
            '    name="' + self.pypi_name + '",',
            '    version=__version__,',
            '    author="' + AUTHOR + '",',
            '    author_email="' + EMAIL + '",',
            '    description="' + DESCRIPTION + '",',
            '    long_description=long_description,',
            '    long_description_content_type="text/markdown",',
            '    url="https://github.com/sajeethphilip/Beamer-Slide-Generator",',
            '    license="MIT",',
            '    packages=find_packages(include=["bsg_ide", "bsg_ide.*"]),',
            '    include_package_data=True,',
            '    package_data={',
            '        "bsg_ide": [',
            '            "resources/*.png",',
            '            "templates/*.txt",',
            '            "*.py",',
            '        ],',
            '    },',
            '    install_requires=[',
            '        "customtkinter>=5.2.0",',
            '        "Pillow>=9.0.0",',
            '        "requests>=2.25.0",',
            '        "latexcodec>=2.0.0",',
            '    ],',
            '    extras_require={',
            '        "full": [',
            '            "opencv-python>=4.5.0",',
            '            "yt-dlp>=2023.0.0",',
            '            "pyspellchecker>=0.7.0",',
            '            "PyMuPDF>=1.23.0",',
            '            "screeninfo>=0.8.0",',
            '            "numpy>=1.21.0",',
            '        ],',
            '        "video": ["opencv-python>=4.5.0", "yt-dlp>=2023.0.0"],',
            '        "spellcheck": ["pyspellchecker>=0.7.0"],',
            '        "pdf": ["PyMuPDF>=1.23.0"],',
            '    },',
            '    entry_points={',
            '        "console_scripts": [',
            '            "bsg-ide = bsg_ide.BSG_IDE:launch_ide",',
            '            "bsg = bsg_ide.BSG_IDE:launch_ide",',
            '        ],',
            '    },',
            '    python_requires=">=3.8",',
            '    classifiers=[',
            '        "Development Status :: 4 - Beta",',
            '        "Intended Audience :: Education",',
            '        "Intended Audience :: Science/Research",',
            '        "License :: OSI Approved :: MIT License",',
            '        "Programming Language :: Python :: 3.8",',
            '        "Programming Language :: Python :: 3.9",',
            '        "Programming Language :: Python :: 3.10",',
            '        "Programming Language :: Python :: 3.11",',
            '        "Programming Language :: Python :: 3.12",',
            '        "Programming Language :: Python :: 3.13",',
            '        "Operating System :: OS Independent",',
            '    ],',
            '    keywords="latex beamer presentation slides generator ide",',
            '    zip_safe=False,',
            ')',
        ]

        setup_file = self.src_dir / "setup.py"
        setup_file.write_text('\n'.join(setup_content))
        print(f"  ✓ Created: {setup_file}")

        # pyproject.toml
        pyproject_content = [
            '[build-system]',
            'requires = ["setuptools>=61.0", "wheel"]',
            'build-backend = "setuptools.build_meta"',
        ]

        pyproject_file = self.src_dir / "pyproject.toml"
        pyproject_file.write_text('\n'.join(pyproject_content))
        print(f"  ✓ Created: {pyproject_file}")

        # MANIFEST.in
        manifest_content = [
            'include README.md',
            'include LICENSE',
            'include requirements.txt',
            'recursive-include bsg_ide *.py',
            'recursive-include bsg_ide/resources *.png',
            'recursive-include bsg_ide/templates *',
        ]

        manifest_file = self.src_dir / "MANIFEST.in"
        manifest_file.write_text('\n'.join(manifest_content))
        print(f"  ✓ Created: {manifest_file}")

        return True

    def create_requirements(self):
        """Create requirements.txt"""
        print_color("\n📦 Creating requirements.txt...", Colors.BOLD)

        req_content = [
            'customtkinter>=5.2.0',
            'Pillow>=9.0.0',
            'requests>=2.25.0',
            'latexcodec>=2.0.0',
        ]

        req_file = self.src_dir / "requirements.txt"
        req_file.write_text('\n'.join(req_content))
        print(f"  ✓ Created: {req_file}")
        return True

    def create_readme(self):
        """Create README.md"""
        print_color("\n📖 Creating README.md...", Colors.BOLD)

        readme_content = [
            '# BSG-IDE - Beamer Slide Generator IDE',
            '',
            f'**Version {self.version}**',
            '',
            DESCRIPTION,
            '',
            '## Features',
            '',
            '- Create professional LaTeX presentations with an intuitive GUI',
            '- Support for images, videos, and animations',
            '- Syntax highlighting for LaTeX commands',
            '- Real-time spell checking',
            '- Grammarly integration for grammar checking',
            '- Screen capture and camera integration',
            '- Export to PDF and Overleaf-compatible ZIP',
            '',
            '## Installation',
            '',
            '### Basic installation:',
            '```bash',
            'pip install bsg-ide',
            '```',
            '',
            '### Full installation (with all features):',
            '```bash',
            'pip install bsg-ide[full]',
            '```',
            '',
            '## Quick Start',
            '',
            '1. Launch the application:',
            '   ```bash',
            '   bsg-ide',
            '   ```',
            '',
            '2. Create a new presentation or open an existing one',
            '3. Add slides with titles, content, and media',
            '4. Generate PDF and present with notes',
            '',
            '## Requirements',
            '',
            '- Python 3.8 or higher',
            '- LaTeX distribution (MiKTeX on Windows, TeX Live on Linux/macOS)',
            '',
            '## Documentation',
            '',
            'For detailed documentation, visit:',
            'https://github.com/sajeethphilip/Beamer-Slide-Generator',
            '',
            '## License',
            '',
            'MIT License - See LICENSE file for details',
        ]

        readme_file = self.src_dir / "README.md"
        readme_file.write_text('\n'.join(readme_content))
        print(f"  ✓ Created: {readme_file}")
        return True

    def create_license(self):
        """Create LICENSE"""
        print_color("\n📜 Creating LICENSE...", Colors.BOLD)

        license_content = [
            'MIT License',
            '',
            f'Copyright (c) 2024 {AUTHOR}',
            '',
            'Permission is hereby granted, free of charge, to any person obtaining a copy',
            'of this software and associated documentation files (the "Software"), to deal',
            'in the Software without restriction, including without limitation the rights',
            'to use, copy, modify, merge, publish, distribute, sublicense, and/or sell',
            'copies of the Software, and to permit persons to whom the Software is',
            'furnished to do so, subject to the following conditions:',
            '',
            'The above copyright notice and this permission notice shall be included in all',
            'copies or substantial portions of the Software.',
            '',
            'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR',
            'IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,',
            'FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE',
            'AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER',
            'LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,',
            'OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE',
            'SOFTWARE.',
        ]

        license_file = self.src_dir / "LICENSE"
        license_file.write_text('\n'.join(license_content))
        print(f"  ✓ Created: {license_file}")
        return True

    def build_package(self):
        """Build the package"""
        print_color("\n🔨 Building package...", Colors.BOLD)

        original_dir = os.getcwd()
        os.chdir(self.src_dir)

        try:
            # Clean previous builds
            for pattern in ["build", "dist", "*.egg-info"]:
                for p in Path(".").glob(pattern):
                    if p.exists():
                        if p.is_dir():
                            shutil.rmtree(p)
                        else:
                            p.unlink()

            # Build using setuptools
            result = subprocess.run(
                [sys.executable, "-m", "pip", "wheel", "--no-deps", "-w", "dist", "."],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                src_dist = self.src_dir / "dist"
                if src_dist.exists():
                    # Copy built packages
                    for f in src_dist.glob("*"):
                        shutil.copy2(f, self.dist_dir / f.name)
                        print(f"  ✓ Copied: {f.name}")

                    # Also create source distribution
                    subprocess.run(
                        [sys.executable, "setup.py", "sdist"],
                        capture_output=True,
                        text=True
                    )

                    for f in src_dist.glob("*"):
                        if f.suffix in ['.tar.gz', '.zip']:
                            shutil.copy2(f, self.dist_dir / f.name)
                            print(f"  ✓ Copied: {f.name}")

                    return True
            else:
                print_color(f"Build failed: {result.stderr}", Colors.RED)
                return False

        finally:
            os.chdir(original_dir)

        return False

    def test_local_install(self):
        """Test local installation"""
        print_color("\n🧪 Testing local installation...", Colors.BOLD)

        wheels = list(self.dist_dir.glob("*.whl"))
        if not wheels:
            print_color("✗ No wheel found", Colors.RED)
            return False

        # Test import
        test_code = f'''
import sys
sys.path.insert(0, "{self.dist_dir}")
try:
    import bsg_ide
    print("✓ Import successful - version:", bsg_ide.__version__)

    # Test that we can import all submodules
    from bsg_ide import BSG_IDE
    from bsg_ide import BeamerSlideGenerator
    from bsg_ide import InteractiveTerminal
    from bsg_ide import Grammarly
    from bsg_ide import EnhancedCommandDialog
    print("✓ All submodules imported successfully")

except Exception as e:
    print(f"✗ Import failed: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''

        result = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print_color("✓ Package test passed!", Colors.GREEN)
            print(result.stdout)
            return True
        else:
            print_color("✗ Package test failed", Colors.RED)
            print(result.stderr)
            return False

    def install_local(self):
        """Install locally for testing"""
        print_color("\n💿 Installing locally...", Colors.BOLD)

        wheels = list(self.dist_dir.glob("*.whl"))
        if not wheels:
            print_color("✗ No wheel found", Colors.RED)
            return False

        wheel = wheels[0]

        # Uninstall old version
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", self.pypi_name],
            capture_output=True
        )

        # Install new version
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", str(wheel)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print_color(f"\n✓ {self.pypi_name} {self.version} installed!", Colors.GREEN)
            return True
        else:
            print_color(f"Installation failed: {result.stderr}", Colors.RED)
            return False

    def upload_to_pypi(self):
        """Upload to PyPI"""
        print_color("\n📤 Uploading to PyPI...", Colors.BOLD)

        confirm = input("\n⚠️ Upload to PRODUCTION PyPI? Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            print_color("Upload cancelled.", Colors.YELLOW)
            return False

        # Install/upgrade twine
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "twine"])

        # Upload
        result = subprocess.run(
            [sys.executable, "-m", "twine", "upload", str(self.dist_dir / "*")],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print_color("\n✓ Uploaded to PyPI successfully!", Colors.GREEN)
            print_color(f"\nUsers can now install with:\npip install {self.pypi_name}", Colors.BLUE)
            return True
        else:
            print_color(f"Upload failed: {result.stderr}", Colors.RED)
            return False

def main():
    parser = argparse.ArgumentParser(description="BSG-IDE Build Script")
    parser.add_argument("--clean", action="store_true", help="Clean only")
    parser.add_argument("--build", action="store_true", help="Build package")
    parser.add_argument("--test", action="store_true", help="Test local installation")
    parser.add_argument("--install", action="store_true", help="Install locally")
    parser.add_argument("--upload", action="store_true", help="Upload to PyPI")

    args = parser.parse_args()

    build_deploy = BSGIDEBuildDeploy()

    if args.clean:
        build_deploy.clean_up()
        return

    if args.build or (not args.clean and not args.test and not args.install and not args.upload):
        print_color("=" * 60, Colors.BOLD)
        print_color("BSG-IDE Build Script v" + VERSION, Colors.BOLD)
        print_color("=" * 60, Colors.BOLD)

        steps = [
            ("Setting up directories", build_deploy.setup_directories),
            ("Copying source files", build_deploy.copy_source_files),
            ("Creating init files", build_deploy.create_init_files),
            ("Creating setup files", build_deploy.create_setup_files),
            ("Creating requirements", build_deploy.create_requirements),
            ("Creating README", build_deploy.create_readme),
            ("Creating LICENSE", build_deploy.create_license),
            ("Building package", build_deploy.build_package),
        ]

        for name, step in steps:
            print_color(f"\n▶ Step: {name}", Colors.BOLD)
            if not step():
                print_color(f"\n✗ Failed at: {name}", Colors.RED)
                sys.exit(1)

        print_color("\n" + "=" * 60, Colors.BOLD)
        print_color("✓ Build completed successfully!", Colors.GREEN)
        print_color("=" * 60, Colors.BOLD)

    if args.test:
        build_deploy.test_local_install()

    if args.install:
        build_deploy.install_local()

    if args.upload:
        build_deploy.upload_to_pypi()

if __name__ == "__main__":
    main()
