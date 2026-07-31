#!/usr/bin/env python3
"""
BSG-IDE Complete Build and Deployment Script with Menu Entry Support
Version: 5.7
"""

import os
import sys
import shutil
import subprocess
import argparse
import platform
from pathlib import Path

# Configuration
VERSION = "7.1.2"
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
        self.system = platform.system()

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

        for pattern in ["*.egg-info", "__pycache__", "*.pyc", "*.whl", "*.tar.gz"]:
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
            self.package_dir / "scripts",
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

    def create_launcher_scripts(self):
        """Create platform-specific launcher scripts"""
        print_color("\n🚀 Creating launcher scripts...", Colors.BOLD)

        # Python launcher script (cross-platform)
        launcher_lines = [
            '#!/usr/bin/env python3',
            '"""',
            'BSG-IDE Launcher',
            'This script launches the Beamer Slide Generator IDE',
            '"""',
            '',
            'import sys',
            'import os',
            'from pathlib import Path',
            '',
            'def main():',
            '    """Main entry point for launcher"""',
            '    try:',
            '        # Try to import from installed package',
            '        from bsg_ide.BSG_IDE import launch_ide',
            '        launch_ide()',
            '    except ImportError:',
            '        # Fallback: try local import',
            '        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))',
            '        from BSG_IDE import launch_ide',
            '        launch_ide()',
            '    except Exception as e:',
            '        print(f"Error launching BSG-IDE: {e}")',
            '        import traceback',
            '        traceback.print_exc()',
            '        sys.exit(1)',
            '',
            'if __name__ == "__main__":',
            '    main()',
        ]

        launcher_file = self.package_dir / "scripts" / "bsg-ide-launcher.py"
        launcher_file.write_text("\n".join(launcher_lines))
        print(f"  ✓ Created: {launcher_file}")

        # Windows batch file
        if self.system == "Windows":
            batch_lines = [
                '@echo off',
                'REM BSG-IDE Launcher for Windows',
                'set PYTHONPATH=%PYTHONPATH%;%~dp0..\\..\\',
                'python -c "from bsg_ide.BSG_IDE import launch_ide; launch_ide()" %*',
                'if errorlevel 1 (',
                '    echo Failed to launch BSG-IDE',
                '    pause',
                ')',
            ]
            batch_file = self.package_dir / "scripts" / "bsg-ide.bat"
            batch_file.write_text("\n".join(batch_lines))
            print(f"  ✓ Created: {batch_file}")

        # Unix shell script
        else:
            shell_lines = [
                '#!/bin/sh',
                '# BSG-IDE Launcher for Unix/Linux/macOS',
                'PYTHONPATH="$PYTHONPATH:$(dirname "$0")/../.."',
                'export PYTHONPATH',
                'python3 -c "from bsg_ide.BSG_IDE import launch_ide; launch_ide()" "$@"',
            ]
            shell_file = self.package_dir / "scripts" / "bsg-ide"
            shell_file.write_text("\n".join(shell_lines))
            shell_file.chmod(0o755)
            print(f"  ✓ Created: {shell_file}")

        return True

    def create_desktop_integration(self):
        """Create desktop integration files"""
        print_color("\n🖥️ Creating desktop integration files...", Colors.BOLD)

        # Linux .desktop file
        if self.system == "Linux":
            desktop_lines = [
                "[Desktop Entry]",
                "Version=" + self.version,
                "Type=Application",
                "Name=BSG-IDE",
                "Name[en]=Beamer Slide Generator IDE",
                "GenericName=Presentation Editor",
                "GenericName[en]=LaTeX Presentation Editor",
                "Comment=" + DESCRIPTION,
                "Exec=bsg-ide %F",
                "Icon=bsg-ide",
                "Terminal=false",
                "Categories=Office;Development;Education;TextEditor;",
                "Keywords=latex;beamer;presentation;slides;editor;",
                "MimeType=text/x-tex;application/x-latex;",
                "StartupWMClass=BSG-IDE",
                "StartupNotify=true",
                "Actions=new-window;",
                "",
                "[Desktop Action new-window]",
                "Name=New Window",
                "Name[en]=New Window",
                "Exec=bsg-ide",
            ]
            desktop_file = self.package_dir / "scripts" / "bsg-ide.desktop"
            desktop_file.write_text("\n".join(desktop_lines))
            print(f"  ✓ Created: {desktop_file}")

        # macOS .app bundle structure
        elif self.system == "Darwin":
            app_dir = self.package_dir / "scripts" / "BSG-IDE.app"
            contents_dir = app_dir / "Contents"
            macos_dir = contents_dir / "MacOS"
            resources_dir = contents_dir / "Resources"

            for d in [macos_dir, resources_dir]:
                d.mkdir(parents=True, exist_ok=True)

            # Info.plist
            plist_lines = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
                '<plist version="1.0">',
                '<dict>',
                '    <key>CFBundleDevelopmentRegion</key>',
                '    <string>en</string>',
                '    <key>CFBundleExecutable</key>',
                '    <string>bsg-ide</string>',
                '    <key>CFBundleIconFile</key>',
                '    <string>bsg-ide.icns</string>',
                '    <key>CFBundleIdentifier</key>',
                '    <string>com.airis4d.bsg-ide</string>',
                '    <key>CFBundleInfoDictionaryVersion</key>',
                '    <string>6.0</string>',
                '    <key>CFBundleName</key>',
                '    <string>BSG-IDE</string>',
                '    <key>CFBundlePackageType</key>',
                '    <string>APPL</string>',
                '    <key>CFBundleShortVersionString</key>',
                '    <string>' + self.version + '</string>',
                '    <key>CFBundleVersion</key>',
                '    <string>' + self.version + '</string>',
                '    <key>LSMinimumSystemVersion</key>',
                '    <string>10.13</string>',
                '    <key>NSHighResolutionCapable</key>',
                '    <true/>',
                '</dict>',
                '</plist>',
            ]
            plist_file = contents_dir / "Info.plist"
            plist_file.write_text("\n".join(plist_lines))
            print(f"  ✓ Created: {plist_file}")

            # Launcher script for macOS
            launcher_lines = [
                '#!/bin/bash',
                '# BSG-IDE macOS Launcher',
                'DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"',
                'export PYTHONPATH="$DIR/../../../..:$PYTHONPATH"',
                'exec python3 -c "from bsg_ide.BSG_IDE import launch_ide; launch_ide()"',
            ]
            launcher_file = macos_dir / "bsg-ide"
            launcher_file.write_text("\n".join(launcher_lines))
            launcher_file.chmod(0o755)
            print(f"  ✓ Created: {launcher_file}")

        return True

    def create_post_install_script(self):
        """Create post-installation script for menu entries"""
        print_color("\n📝 Creating post-install script...", Colors.BOLD)

        if self.system == "Windows":
            post_install_lines = [
                '# Windows post-installation script',
                'import os',
                'import sys',
                'import subprocess',
                'from pathlib import Path',
                '',
                'def create_start_menu_shortcut():',
                '    """Create Start Menu shortcut on Windows"""',
                '    try:',
                '        import winshell',
                '        from win32com.client import Dispatch',
                '        ',
                '        # Get paths',
                '        start_menu = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs"',
                '        bsg_folder = start_menu / "BSG-IDE"',
                '        bsg_folder.mkdir(exist_ok=True)',
                '        ',
                '        # Find Python and script',
                '        python_path = sys.executable',
                '        script_path = Path(__file__).parent / "scripts" / "bsg-ide-launcher.py"',
                '        ',
                '        # Create shortcut',
                '        shell = Dispatch("WScript.Shell")',
                '        shortcut = shell.CreateShortCut(str(bsg_folder / "BSG-IDE.lnk"))',
                '        shortcut.Targetpath = python_path',
                '        shortcut.Arguments = f\'"{script_path}"\'',
                '        shortcut.WorkingDirectory = str(Path.home() / "Documents")',
                '        shortcut.IconLocation = str(Path(__file__).parent / "resources" / "bsg-ide.ico")',
                '        shortcut.save()',
                '        ',
                '        print("✓ Start Menu shortcut created")',
                '    except Exception as e:',
                '        print(f"⚠ Could not create Start Menu shortcut: {e}")',
                '',
                'if __name__ == "__main__":',
                '    create_start_menu_shortcut()',
            ]
        else:
            post_install_lines = [
                '# Unix/Linux/macOS post-installation script',
                'import os',
                'import sys',
                'import subprocess',
                'from pathlib import Path',
                '',
                'def create_desktop_entry():',
                '    """Create desktop entry on Linux/Unix"""',
                '    try:',
                '        # Get paths',
                '        home = Path.home()',
                '        desktop_dir = home / ".local" / "share" / "applications"',
                '        desktop_dir.mkdir(parents=True, exist_ok=True)',
                '        ',
                '        icons_dir = home / ".local" / "share" / "icons" / "hicolor" / "256x256" / "apps"',
                '        icons_dir.mkdir(parents=True, exist_ok=True)',
                '        ',
                '        # Copy icon',
                '        icon_src = Path(__file__).parent / "resources" / "bsg-ide.png"',
                '        icon_dst = icons_dir / "bsg-ide.png"',
                '        if icon_src.exists():',
                '            import shutil',
                '            shutil.copy2(icon_src, icon_dst)',
                '        ',
                '        # Create desktop entry',
                '        desktop_content = "[Desktop Entry]\\n"',
                '        desktop_content += "Version=1.0\\n"',
                '        desktop_content += "Type=Application\\n"',
                '        desktop_content += "Name=BSG-IDE\\n"',
                '        desktop_content += "Comment=Beamer Slide Generator IDE\\n"',
                '        desktop_content += "Exec=bsg-ide\\n"',
                '        desktop_content += "Icon=bsg-ide\\n"',
                '        desktop_content += "Terminal=false\\n"',
                '        desktop_content += "Categories=Office;Development;Education;\\n"',
                '        desktop_content += "StartupNotify=true\\n"',
                '        ',
                '        desktop_file = desktop_dir / "bsg-ide.desktop"',
                '        desktop_file.write_text(desktop_content)',
                '        desktop_file.chmod(0o755)',
                '        ',
                '        # Update desktop database',
                '        subprocess.run(["update-desktop-database", str(desktop_dir)],',
                '                      capture_output=True)',
                '        ',
                '        print("✓ Desktop entry created")',
                '    except Exception as e:',
                '        print(f"⚠ Could not create desktop entry: {e}")',
                '',
                'if __name__ == "__main__":',
                '    create_desktop_entry()',
            ]

        post_install_file = self.package_dir / "scripts" / "post_install.py"
        post_install_file.write_text("\n".join(post_install_lines))
        print(f"  ✓ Created: {post_install_file}")

        return True

    def create_init_files(self):
        """Create __init__.py and __main__.py"""
        print_color("\n📝 Creating init files...", Colors.BOLD)

        # __init__.py
        init_lines = [
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
        init_file.write_text("\n".join(init_lines))
        print(f"  ✓ Created: {init_file}")

        # __main__.py
        main_lines = [
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
        main_file.write_text("\n".join(main_lines))
        print(f"  ✓ Created: {main_file}")

        return True

    def create_setup_files(self):
        """Create setup files with menu entry support"""
        print_color("\n🔧 Creating setup files...", Colors.BOLD)

        # Create a proper setup.py
        setup_lines = [
            '#!/usr/bin/env python3',
            '"""Setup script for BSG-IDE"""',
            'from setuptools import setup, find_packages',
            'from pathlib import Path',
            'import sys',
            'import subprocess',
            '',
            '__version__ = "' + self.version + '"',
            '',
            '# Read README',
            'readme_file = Path(__file__).parent / "README.md"',
            'long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else "' + DESCRIPTION + '"',
            '',
            'def post_install():',
            '    """Run post-installation setup"""',
            '    try:',
            '        # Run the post-install script',
            '        post_install_script = Path(__file__).parent / "bsg_ide" / "scripts" / "post_install.py"',
            '        if post_install_script.exists():',
            '            subprocess.run([sys.executable, str(post_install_script)], check=False)',
            '    except Exception:',
            '        pass',
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
            '            "resources/*.ico",',
            '            "resources/*.icns",',
            '            "templates/*.txt",',
            '            "scripts/*.py",',
            '            "scripts/*.sh",',
            '            "scripts/*.bat",',
            '            "scripts/*.desktop",',
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
            '        "windows": ["winshell>=0.6", "pywin32>=300"] if sys.platform == "win32" else [],',
            '    },',
            '    entry_points={',
            '        "console_scripts": [',
            '            "bsg-ide = bsg_ide.BSG_IDE:launch_ide",',
            '            "bsg = bsg_ide.BSG_IDE:launch_ide",',
            '        ],',
            '        "gui_scripts": [',
            '            "bsg-ide-gui = bsg_ide.BSG_IDE:launch_ide",',
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
            '',
            '# Run post-install if installed',
            'if __name__ == "__main__":',
            '    pass  # Let setuptools handle it',
        ]

        setup_file = self.src_dir / "setup.py"
        setup_file.write_text("\n".join(setup_lines))
        print(f"  ✓ Created: {setup_file}")

        # pyproject.toml
        pyproject_lines = [
            '[build-system]',
            'requires = ["setuptools>=61.0", "wheel"]',
            'build-backend = "setuptools.build_meta"',
        ]

        pyproject_file = self.src_dir / "pyproject.toml"
        pyproject_file.write_text("\n".join(pyproject_lines))
        print(f"  ✓ Created: {pyproject_file}")

        # MANIFEST.in
        manifest_lines = [
            'include README.md',
            'include LICENSE',
            'include requirements.txt',
            'recursive-include bsg_ide *.py',
            'recursive-include bsg_ide/resources *',
            'recursive-include bsg_ide/templates *',
            'recursive-include bsg_ide/scripts *',
        ]

        manifest_file = self.src_dir / "MANIFEST.in"
        manifest_file.write_text("\n".join(manifest_lines))
        print(f"  ✓ Created: {manifest_file}")

        return True

    def create_requirements(self):
        """Create requirements.txt"""
        print_color("\n📦 Creating requirements.txt...", Colors.BOLD)

        req_lines = [
            'customtkinter>=5.2.0',
            'Pillow>=9.0.0',
            'requests>=2.25.0',
            'latexcodec>=2.0.0',
        ]

        req_file = self.src_dir / "requirements.txt"
        req_file.write_text("\n".join(req_lines))
        print(f"  ✓ Created: {req_file}")
        return True

    def create_readme(self):
        """Create README.md"""
        print_color("\n📖 Creating README.md...", Colors.BOLD)

        readme_lines = [
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
            '- **Desktop menu integration** (Start Menu on Windows, App Menu on Linux/macOS)',
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
            'After installation, you can launch BSG-IDE in several ways:',
            '',
            '### From command line:',
            '```bash',
            'bsg-ide',
            '```',
            '',
            '### From application menu:',
            '- **Windows**: Start Menu → BSG-IDE',
            '- **Linux**: Applications → Office → BSG-IDE',
            '- **macOS**: Applications → BSG-IDE.app',
            '',
            '### Creating a new presentation:',
            '1. Click "New" or press Ctrl+N',
            '2. Add slides with titles and content',
            '3. Insert media (images, videos)',
            '4. Generate PDF',
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
        readme_file.write_text("\n".join(readme_lines))
        print(f"  ✓ Created: {readme_file}")
        return True

    def create_license(self):
        """Create LICENSE"""
        print_color("\n📜 Creating LICENSE...", Colors.BOLD)

        license_lines = [
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
        license_file.write_text("\n".join(license_lines))
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
        test_code = '''
import sys
sys.path.insert(0, "''' + str(self.dist_dir) + '''")
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
    print(f"✗ Import failed: {e}")
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
            print_color("\nTo launch, run: bsg-ide", Colors.BLUE)
            print_color("Or look for BSG-IDE in your application menu", Colors.BLUE)
            return True
        else:
            print_color(f"Installation failed: {result.stderr}", Colors.RED)
            return False

    def upload_to_pypi(self):
        """Upload to PyPI with improved error handling and version management"""
        print_color("\n📤 Uploading to PyPI...", Colors.BOLD)

        # Check for existing versions on PyPI
        print_color("  Checking existing versions on PyPI...", Colors.BLUE)
        existing_versions = self._check_pypi_versions()

        if existing_versions:
            print_color(f"  Existing versions on PyPI: {', '.join(existing_versions)}", Colors.YELLOW)
            if self.version in existing_versions:
                print_color(f"\n⚠️ Version {self.version} already exists on PyPI!", Colors.RED)
                print_color("  You need to increment the version number before uploading.", Colors.YELLOW)
                response = input("\n  Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    return False

        confirm = input("\n⚠️ Upload to PRODUCTION PyPI? Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            print_color("Upload cancelled.", Colors.YELLOW)
            return False

        # Install/upgrade twine
        print_color("  Upgrading twine...", Colors.BLUE)
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "twine"],
                       capture_output=True)

        # Get API token
        api_token = os.environ.get("TWINE_PASSWORD") or os.environ.get("PYPI_API_TOKEN")

        if api_token:
            print_color("  Using API token from environment", Colors.BLUE)
        else:
            print_color("  You will be prompted for API token", Colors.YELLOW)

        # Build the upload command - ONLY upload the latest version
        upload_cmd = [sys.executable, "-m", "twine", "upload"]

        # Add repository if needed
        repo = os.environ.get("TWINE_REPOSITORY_URL", "https://upload.pypi.org/legacy/")
        upload_cmd.extend(["--repository-url", repo])

        # Only upload the latest version files, not all versions
        dist_files = list(self.dist_dir.glob("*"))
        if not dist_files:
            print_color("✗ No distribution files found in dist/", Colors.RED)
            return False

        # Filter to only upload the latest version
        latest_files = []
        for f in dist_files:
            # Only include files with the current version
            if self.version in f.name:
                latest_files.append(f)
            else:
                print_color(f"  Skipping older version: {f.name}", Colors.YELLOW)

        if not latest_files:
            print_color("✗ No files found for current version", Colors.RED)
            return False

        for f in latest_files:
            upload_cmd.append(str(f))

        print_color(f"\n  Uploading {len(latest_files)} file(s) for version {self.version}...", Colors.BLUE)

        # Run the upload with better output capture
        try:
            # Use subprocess with real-time output for better visibility
            process = subprocess.Popen(
                upload_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Print output in real-time
            stdout_lines = []
            stderr_lines = []

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    stdout_lines.append(output)

            # Get remaining stderr
            stderr_output = process.stderr.read()
            if stderr_output:
                print(stderr_output)
                stderr_lines.append(stderr_output)

            # Wait for process to finish
            return_code = process.wait()

            # Check for success
            if return_code == 0:
                print_color("\n✓ Uploaded to PyPI successfully!", Colors.GREEN)
                print_color(f"\nUsers can now install with:\npip install {self.pypi_name}", Colors.BLUE)
                print_color("\nAfter installation, menu entries will be created automatically!", Colors.GREEN)
                return True
            else:
                # Analyze the error
                combined_output = ''.join(stdout_lines) + ''.join(stderr_lines)

                # Check for specific errors
                if "400" in combined_output and "Bad Request" in combined_output:
                    print_color("\n⚠️ 400 Bad Request - Common causes:", Colors.YELLOW)
                    print_color("  1. Version already exists on PyPI", Colors.WHITE)
                    print_color("  2. Package name already taken", Colors.WHITE)
                    print_color("  3. Invalid metadata (check your setup.py)", Colors.WHITE)
                    print_color("  4. API token expired or invalid", Colors.WHITE)

                    # Try to provide more specific guidance
                    if self.version in existing_versions:
                        print_color(f"\n  ✗ Version {self.version} already exists!", Colors.RED)
                        print_color("  Please increment the version number in your setup files.", Colors.YELLOW)
                    else:
                        print_color("\n  Check your API token and package metadata.", Colors.YELLOW)

                    return False
                elif "ERROR" in combined_output.upper() or "FAIL" in combined_output.upper():
                    print_color(f"\n✗ Upload failed: {combined_output[:500]}", Colors.RED)
                    return False
                else:
                    print_color("\n⚠ Upload completed with warnings but appears successful", Colors.YELLOW)
                    print_color(f"\nCheck your package at: https://pypi.org/project/{self.pypi_name}/", Colors.BLUE)
                    return True

        except Exception as e:
            print_color(f"\n✗ Upload error: {str(e)}", Colors.RED)
            import traceback
            traceback.print_exc()
            return False

    def _check_pypi_versions(self):
        """Check existing versions on PyPI"""
        import urllib.request
        import json

        try:
            url = f"https://pypi.org/pypi/{self.pypi_name}/json"
            req = urllib.request.Request(url, headers={'User-Agent': 'BSG-IDE-Build'})

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                if 'releases' in data:
                    versions = list(data['releases'].keys())
                    return versions
                return []
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return []  # Package not on PyPI yet
            else:
                print_color(f"⚠ Error checking PyPI: {e}", Colors.YELLOW)
                return []
        except Exception as e:
            print_color(f"⚠ Verification error: {e}", Colors.YELLOW)
            return []

    def verify_pypi_upload(self):
        """Verify the package is on PyPI"""
        print_color("\n🔍 Verifying PyPI upload...", Colors.BOLD)

        import urllib.request
        import json

        try:
            # Check PyPI API
            url = f"https://pypi.org/pypi/{self.pypi_name}/json"
            req = urllib.request.Request(url, headers={'User-Agent': 'BSG-IDE-Build'})

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                if 'info' in data and 'version' in data['info']:
                    version = data['info']['version']
                    print_color(f"✓ Package {self.pypi_name} version {version} is on PyPI!", Colors.GREEN)
                    print_color(f"  URL: https://pypi.org/project/{self.pypi_name}/", Colors.BLUE)

                    # Also check if our version is available
                    if self.version in data['releases']:
                        print_color(f"✓ Version {self.version} is available!", Colors.GREEN)
                    else:
                        print_color(f"⚠ Version {self.version} not yet indexed (may take a few minutes)", Colors.YELLOW)

                    return True
                else:
                    print_color("⚠ Package found but version info not available", Colors.YELLOW)
                    return False

        except urllib.error.HTTPError as e:
            if e.code == 404:
                print_color("⚠ Package not yet indexed on PyPI (may take a few minutes)", Colors.YELLOW)
                print_color("  Check manually at: https://pypi.org/project/bsg-ide/", Colors.BLUE)
                return False
            else:
                print_color(f"⚠ Error checking PyPI: {e}", Colors.YELLOW)
                return False
        except Exception as e:
            print_color(f"⚠ Verification error: {e}", Colors.YELLOW)
            return False


def main():
    parser = argparse.ArgumentParser(description="BSG-IDE Build Script with Menu Entry Support")
    parser.add_argument("--clean", action="store_true", help="Clean only")
    parser.add_argument("--build", action="store_true", help="Build package")
    parser.add_argument("--test", action="store_true", help="Test local installation")
    parser.add_argument("--install", action="store_true", help="Install locally")
    parser.add_argument("--upload", action="store_true", help="Upload to PyPI")
    parser.add_argument("--verify", action="store_true", help="Verify PyPI upload")

    args = parser.parse_args()

    build_deploy = BSGIDEBuildDeploy()

    if args.clean:
        build_deploy.clean_up()
        return

    if args.build or (not args.clean and not args.test and not args.install and not args.upload and not args.verify):
        print_color("=" * 60, Colors.BOLD)
        print_color("BSG-IDE Build Script v" + VERSION, Colors.BOLD)
        print_color("=" * 60, Colors.BOLD)

        steps = [
            ("Setting up directories", build_deploy.setup_directories),
            ("Copying source files", build_deploy.copy_source_files),
            ("Creating launcher scripts", build_deploy.create_launcher_scripts),
            ("Creating desktop integration", build_deploy.create_desktop_integration),
            ("Creating post-install script", build_deploy.create_post_install_script),
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
        if build_deploy.upload_to_pypi():
            # Wait a moment for PyPI to index
            import time
            print_color("\n⏳ Waiting 5 seconds for PyPI to index...", Colors.YELLOW)
            time.sleep(5)
            build_deploy.verify_pypi_upload()

    if args.verify:
        build_deploy.verify_pypi_upload()

if __name__ == "__main__":
    main()
