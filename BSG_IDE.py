#!/usr/bin/env python3
"""
BSG_Integrated_Development_Environment.py
An integrated development environment for BeamerSlideGenerator
Combines GUI editing, syntax highlighting, and presentation generation.

"""
import os
import sys
from pathlib import Path

def setup_package_paths():
    """Setup Python paths for both source and installed runs"""
    try:
        # Get the directory where this file is located
        current_file = Path(__file__).resolve()
        current_dir = current_file.parent

        # Check if we're in source directory (look for key files)
        is_source = (current_dir / 'BeamerSlideGenerator.py').exists()

        if is_source:
            # Running from source - add current directory to path
            if str(current_dir) not in sys.path:
                sys.path.insert(0, str(current_dir))
            print(f"Running from source: {current_dir}")
            return current_dir, current_dir / 'resources'

        # Check if we're in a pip installed package
        try:
            import bsg_ide
            package_dir = Path(bsg_ide.__file__).parent
            if str(package_dir) not in sys.path:
                sys.path.insert(0, str(package_dir))
            resources_dir = package_dir / 'resources'
            if not resources_dir.exists():
                resources_dir = package_dir
            print(f"Running from installed package: {package_dir}")
            return package_dir, resources_dir
        except ImportError:
            pass

        # Check common installation locations
        common_locations = [
            Path.home() / '.local/lib/bsg-ide',
            Path.home() / '.local/share/bsg-ide',
            Path('/usr/local/share/bsg-ide'),
            Path(sys.prefix) / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages' / 'bsg_ide',
        ]

        for loc in common_locations:
            if (loc / 'BeamerSlideGenerator.py').exists():
                if str(loc) not in sys.path:
                    sys.path.insert(0, str(loc))
                resources_dir = loc / 'resources'
                if not resources_dir.exists():
                    resources_dir = loc
                print(f"Found installation at: {loc}")
                return loc, resources_dir

        # Fallback to current directory
        print(f"Using current directory as fallback: {current_dir}")
        return current_dir, current_dir / 'resources'

    except Exception as e:
        print(f"Warning: Error setting up paths: {e}")
        return Path.cwd(), Path.cwd() / 'resources'

# Run path setup immediately
PACKAGE_ROOT, RESOURCES_DIR = setup_package_paths()

# Now try to import BeamerSlideGenerator
try:
    from BeamerSlideGenerator import (
        get_beamer_preamble,
        process_media,
        generate_latex_code,
        download_youtube_video,
        construct_search_query,
        open_google_image_search,
        process_input_file,
        set_terminal_io,
        convert_media,
        download_media
    )
    print("✓ Successfully imported BeamerSlideGenerator")
except ImportError as e:
    print(f"Error importing BeamerSlideGenerator: {e}")
    print(f"Python path: {sys.path}")
    print(f"Looking for BeamerSlideGenerator.py in: {PACKAGE_ROOT}")

    # Try alternative import
    try:
        from bsg_ide.BeamerSlideGenerator import (
            get_beamer_preamble,
            process_media,
            generate_latex_code,
            download_youtube_video,
            construct_search_query,
            open_google_image_search,
            process_input_file,
            set_terminal_io,
            convert_media,
            download_media
        )
        print("✓ Successfully imported BeamerSlideGenerator via bsg_ide")
    except ImportError as e2:
        print(f"Alternative import also failed: {e2}")
        print("\n" + "="*60)
        print("ERROR: BeamerSlideGenerator module not found!")
        print("="*60)
        print("\nPlease ensure one of the following:")
        print("1. BeamerSlideGenerator.py is in the same directory as BSG_IDE.py")
        print("2. The package is properly installed via: pip install bsg-ide")
        print("3. Reinstall the package: pip install --force-reinstall bsg-ide")
        print("\nCurrent Python path:")
        for p in sys.path:
            print(f"  {p}")
        sys.exit(1)

#------------------------------Check and install ----------------------------------------------
import os,re
import sys
import tempfile
import shutil
import subprocess
#------------------------------------------------------------------------------------------------------
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
import venv
import platform
from pathlib import Path
import site
import socket
from importlib import util
global working_folder
working_folder=os.path.expanduser("~")
global original_dir
original_dir = os.path.expanduser("~")
from tkinter import messagebox
try:
    from EnhancedCommandDialog import LatexCommandHelper, CommandTooltip
    ENHANCED_FEATURES_AVAILABLE = True
except ImportError:
    from Grammarly import LatexCommandHelper
    CommandTooltip = None
    ENHANCED_FEATURES_AVAILABLE = False
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bsg_ide_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_xor_text_color(background_color):
    """
    Calculate optimal text color (black or white) for TikZ backgrounds using XOR rule.
    Uses perceived luminance and contrast ratio for better readability.

    Args:
        background_color: Tuple (R, G, B) or string color name

    Returns:
        'black' or 'white' based on background brightness
    """
    try:
        # Handle string color names by converting to RGB
        if isinstance(background_color, str):
            # Common color name mappings
            color_map = {
                'red': (255, 0, 0),
                'green': (0, 255, 0),
                'blue': (0, 0, 255),
                'yellow': (255, 255, 0),
                'cyan': (0, 255, 255),
                'magenta': (255, 0, 255),
                'white': (255, 255, 255),
                'black': (0, 0, 0),
                'gray': (128, 128, 128),
                'orange': (255, 165, 0),
                'purple': (128, 0, 128),
                'brown': (165, 42, 42),
                'pink': (255, 192, 203),
                'lightblue': (173, 216, 230),
                'lightgreen': (144, 238, 144),
                'lightgray': (211, 211, 211),
                'darkgray': (169, 169, 169),
                'darkblue': (0, 0, 139),
                'darkgreen': (0, 100, 0),
                'darkred': (139, 0, 0),
            }

            # Try to get from map, or parse hex/rgb string
            if background_color.lower() in color_map:
                r, g, b = color_map[background_color.lower()]
            elif background_color.startswith('#'):
                # Hex color
                hex_color = background_color.lstrip('#')
                r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            elif background_color.startswith('rgb'):
                # rgb(r, g, b) format
                import re
                match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', background_color)
                if match:
                    r, g, b = map(int, match.groups())
                else:
                    # Default to medium gray if can't parse
                    r, g, b = 128, 128, 128
            else:
                # Unknown color, default to medium gray
                r, g, b = 128, 128, 128
        else:
            # Assume it's already an RGB tuple
            r, g, b = background_color

        # Ensure values are in 0-255 range
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))

        # Calculate perceived luminance using WCAG formula
        # Convert to linear RGB
        def to_linear(channel):
            c = channel / 255.0
            if c <= 0.04045:
                return c / 12.92
            else:
                return ((c + 0.055) / 1.055) ** 2.4

        r_linear = to_linear(r)
        g_linear = to_linear(g)
        b_linear = to_linear(b)

        # Calculate luminance
        luminance = 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

        # XOR Rule: Use white text on dark backgrounds, black text on light backgrounds
        # Threshold can be adjusted (0.5 is middle gray)
        if luminance > 0.179:  # Adjusted threshold for better readability
            return 'black'
        else:
            return 'white'

    except Exception as e:
        print(f"Warning: Error calculating text color: {e}")
        # Fallback to black text
        return 'black'

def generate_default_requirements():
    """Generate a default requirements.txt if none found"""
    try:
        default_requirements = """# Core GUI dependencies
customtkinter==5.2.2
Pillow
tk

# Media and web dependencies
requests
yt_dlp
opencv-python
screeninfo
numpy

# PDF and document processing
PyMuPDF==1.23.7

# System utilities
pyautogui
pyspellchecker

# File type detection (not for Windows)
python-magic>=0.4.27; platform_system != "Windows"
"""
        # Try to write to user's local directory first
        save_paths = [
            Path.home() / '.local' / 'lib' / 'bsg-ide',
            Path.cwd(),
            Path(os.getenv('APPDATA', '')) / 'BSG-IDE'
        ]

        for path in save_paths:
            try:
                os.makedirs(path, exist_ok=True)
                req_file = path / 'requirements.txt'
                req_file.write_text(default_requirements)
                print(f"\nCreated default requirements.txt at: {req_file}")
                return req_file
            except:
                continue

        # If all save attempts fail, create in current directory
        print("\nWarning: Could not save to preferred locations")
        with open('requirements.txt', 'w') as f:
            f.write(default_requirements)
        return Path('requirements.txt')

    except Exception as e:
        print(f"Error generating requirements.txt: {str(e)}")
        return None
generate_default_requirements()

def launch_ide():
    """Entry point for command-line launcher"""
    try:
        # Ensure working directory is script directory
        import os
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # Import required modules
        import sys
        from pathlib import Path

        # Add current directory to Python path
        current_dir = Path(__file__).parent.resolve()
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))



        # Create and run the IDE
        app = BeamerSlideEditor()
        app.mainloop()

    except Exception as e:
        print(f"Error launching BSG-IDE: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def check_internet_connection():
    """Check internet connection without external dependencies"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def setup_virtual_env():
    """Setup and activate virtual environment with improved error handling"""
    try:
        home_dir = Path.home()
        venv_path = home_dir / 'my_python'

        # Create venv if it doesn't exist
        if not venv_path.exists():
            print(f"Creating virtual environment at {venv_path}")
            venv.create(venv_path, with_pip=True, clear=True)

        # Get paths based on platform
        if platform.system() == "Windows":
            venv_python = venv_path / "Scripts" / "python.exe"
            venv_pip = venv_path / "Scripts" / "pip.exe"
        else:
            venv_python = venv_path / "bin" / "python"
            venv_pip = venv_path / "bin" / "pip"

        # Verify the virtual environment is working
        if not venv_python.exists() or not venv_pip.exists():
            print("Virtual environment files not found, recreating...")
            shutil.rmtree(venv_path, ignore_errors=True)
            venv.create(venv_path, with_pip=True, clear=True)

        # Test virtual environment
        try:
            subprocess.run(
                [str(venv_python), "-c", "import sys; print(sys.prefix)"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except subprocess.CalledProcessError:
            print("Virtual environment test failed, falling back to system Python")
            return sys.executable, "pip", False

        return str(venv_python), str(venv_pip), True

    except Exception as e:
        print(f"Error setting up virtual environment: {str(e)}")
        return sys.executable, "pip", False

def install_base_packages(pip_path):
    """Install essential packages without GUI dependencies"""
    base_packages = [
        "customtkinter",
        "Pillow",
        "tk",  # Basic tkinter
        "latexcodec",    # For LaTeX code handling
        "latex",         # Python LaTeX tools

    ]

    for package in base_packages:
        try:
            subprocess.run(
                [pip_path, "install", "--no-cache-dir", package],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except subprocess.CalledProcessError:
            continue


def get_requirements_path():
    """Get path to requirements.txt with exhaustive search"""
    possible_paths = [
        # Current directory
        Path.cwd() / 'requirements.txt',
        # Script directory
        Path(__file__).parent / 'requirements.txt',
        # User local installation
        Path.home() / '.local' / 'lib' / 'bsg-ide' / 'requirements.txt',
        # Windows AppData
        Path(os.getenv('APPDATA', '')) / 'BSG-IDE' / 'requirements.txt',
        # System-wide installation
        Path('/usr/local/share/bsg-ide/requirements.txt'),
        # Virtual environment
        Path(os.getenv('VIRTUAL_ENV', '')) / 'requirements.txt',
    ]

    # Add additional search paths for macOS
    if sys.platform == 'darwin':
        possible_paths.extend([
            Path.home() / 'Library' / 'Application Support' / 'BSG-IDE' / 'requirements.txt',
            Path('/Applications/BSG-IDE.app/Contents/Resources/requirements.txt')
        ])

    print("\nSearching for requirements.txt in:")
    for path in possible_paths:
        print(f"Checking {path}...")
        if path.exists():
            print(f"✓ Found requirements.txt at: {path}")
            return path

    print("Could not find requirements.txt in standard locations")
    return generate_default_requirements()


def install_system_dependencies():
    """Install system dependencies based on detected OS and package manager"""
    try:
        # Detect operating system
        if sys.platform.startswith('linux'):
            # Detect Linux distribution and package manager
            if shutil.which('apt'):  # Debian/Ubuntu
                mgr = 'apt'
                cmd = ['sudo', 'apt', 'install', '-y']
                deps = [
                    'python3-gi',
                    'python3-gi-cairo',
                    'gir1.2-gtk-3.0',
                    'python3-cairo',
                    'libgtk-3-0',
                    'librsvg2-common',
                    'poppler-utils',
                    'libgirepository1.0-dev',
                    'gcc',
                    'python3-dev',
                    'pkg-config',
                    'libcairo2-dev',
                    'pyautogui',
                    'gobject-introspection'
                ]
            elif shutil.which('dnf'):  # Fedora/RHEL
                mgr = 'dnf'
                cmd = ['sudo', 'dnf', 'install', '-y']
                deps = [
                    'python3-gobject',
                    'python3-cairo',
                    'gtk3',
                    'python3-devel',
                    'gcc',
                    'pkg-config',
                    'cairo-devel',
                    'pyautogui',
                    'gobject-introspection-devel',
                    'cairo-gobject-devel'
                ]
            elif shutil.which('pacman'):  # Arch Linux
                mgr = 'pacman'
                cmd = ['sudo', 'pacman', '-S', '--noconfirm']
                deps = [
                    'python-gobject',
                    'python-cairo',
                    'gtk3',
                    'python-pip',
                    'gcc',
                    'pkg-config',
                    'cairo',
                    'pyautogui',
                    'gobject-introspection'
                ]
            elif shutil.which('zypper'):  # openSUSE
                mgr = 'zypper'
                cmd = ['sudo', 'zypper', 'install', '-y']
                deps = [
                    'python3-gobject',
                    'python3-cairo',
                    'gtk3',
                    'python3-devel',
                    'gcc',
                    'pkg-config',
                    'cairo-devel',
                    'pyautogui',
                    'gobject-introspection-devel'
                ]
            else:
                print("Could not detect package manager. Please install dependencies manually:")
                print("Required: GTK3, Python-GObject, Cairo, and development tools")
                return False

            print(f"\nInstalling system dependencies using {mgr}...")
            try:
                subprocess.check_call(cmd + deps)
                print("✓ System dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"✗ Error installing system dependencies: {e}")
                return False

        elif sys.platform.startswith('darwin'):  # macOS
            try:
                # Check if Homebrew is installed
                if not shutil.which('brew'):
                    print("Homebrew not found. Installing...")
                    brew_install = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                    subprocess.check_call(brew_install, shell=True)

                # Install dependencies using Homebrew
                deps = [
                    'gtk+3',
                    'pygobject3',
                    'cairo',
                    'py3cairo',
                    'pyautogui',
                    'gobject-introspection'
                ]

                for dep in deps:
                    subprocess.check_call(['brew', 'install', dep])
                print("✓ System dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"✗ Error installing macOS dependencies: {e}")
                return False

        elif sys.platform.startswith('win'):  # Windows
            try:
                # For Windows, we'll use MSYS2 to install GTK and dependencies
                if not os.path.exists(r'C:\msys64'):
                    print("MSYS2 not found. Please install MSYS2 from: https://www.msys2.org/")
                    print("After installing, run: pacman -S mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python-gobject")
                    return False

                # Update MSYS2 and install dependencies
                msys2_path = r'C:\msys64\usr\bin\bash.exe'
                deps = [
                    'mingw-w64-x86_64-gtk3',
                    'mingw-w64-x86_64-python-gobject',
                    'mingw-w64-x86_64-python-cairo',
                    'mingw-w64-x86_64-gcc'
                ]

                for dep in deps:
                    subprocess.check_call([msys2_path, '-lc', f'pacman -S --noconfirm {dep}'])
                print("✓ System dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"✗ Error installing Windows dependencies: {e}")
                return False

        return True

    except Exception as e:
        print(f"Error installing system dependencies: {str(e)}")
        return False
#------------------------------------------------------------
def install_bsg_ide(fix_mode=False):
    """Main installation function"""
    try:
        # Create a temporary root window if no parent is available
        temp_root = None
        try:
            # Try to get existing Tk root
            temp_root = tk.Tk()
            temp_root.withdraw()  # Hide the window
        except:
            pass

        installer = InstallationManager(temp_root)
        install_type = "system-wide" if installer.is_admin else "user"

        print(f"\nStarting BSG-IDE {'fix' if fix_mode else 'installation'} ({install_type})")
        print(f"Detected OS: {installer.system}")

        # Create directory structure
        installer.create_directory_structure()

        # Copy resources with enhanced PNG handling
        package_root = Path(__file__).resolve().parent
        required_files = {
            'BSG_IDE.py': ['base', 'python_site'],
            'BeamerSlideGenerator.py': ['base', 'python_site'],
            'requirements.txt': ['base'],
            'airis4d_logo.png': ['base/resources', 'resources', 'share', 'icons'],
            'bsg-ide.png': ['base/resources', 'resources', 'share', 'icons']
        }

        # Copy each file to its destinations
        for filename, destinations in required_files.items():
            source_file = package_root / filename
            if source_file.exists():
                for dest_type in destinations:
                    try:
                        # Handle nested paths
                        if '/' in dest_type:
                            base_type, subdir = dest_type.split('/')
                            if base_type in installer.install_paths:
                                dest_dir = installer.install_paths[base_type] / subdir
                        else:
                            dest_dir = installer.install_paths[dest_type]

                        dest_dir.mkdir(parents=True, exist_ok=True)
                        dest_path = dest_dir / filename
                        shutil.copy2(source_file, dest_path)
                        print(f"✓ Copied {filename} to {dest_path}")
                    except Exception as e:
                        print(f"! Warning: Could not copy {filename} to {dest_type}: {e}")

        # Create launcher
        installer.create_launcher()

        # Setup OS integration
        installer.setup_os_integration()

        print(f"\nBSG-IDE {'fix' if fix_mode else 'installation'} completed successfully!")
        print("\nYou can now run BSG-IDE by:")
        if installer.system == "Windows":
            print("1. Using the Start Menu shortcut")
            print("2. Running 'bsg-ide' from Command Prompt")
        elif installer.system == "Darwin":
            print("1. Opening BSG-IDE from Applications")
            print("2. Running 'bsg-ide' from Terminal")
        else:
            print("1. Using the application menu")
            print("2. Running 'bsg-ide' from terminal")

        return True

    except Exception as e:
        print(f"\n✗ Error during {'fix' if fix_mode else 'installation'}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up temporary root window if we created one
        if temp_root is not None:
            try:
                temp_root.destroy()
            except:
                pass

def verify_installation():
    import site
    import sys
    from pathlib import Path

    """Verify BSG-IDE whether running from source or installed"""
    try:
        package_root, resources_dir = setup_paths()
        all_ok = True

        print("\nChecking installation...")
        print(f"Package root: {package_root}")
        print(f"Resources directory: {resources_dir}")

        # 1. Check core files
        required_files = {
            'BSG_IDE.py': package_root,
            'BeamerSlideGenerator.py': package_root,
            'requirements.txt': package_root,
            'airis4d_logo.png': resources_dir,
            'bsg-ide.png': resources_dir
        }

        print("\nChecking required files:")
        for filename, directory in required_files.items():
            path = directory / filename
            if path.exists():
                print(f"✓ Found {filename} in {directory}")
            else:
                print(f"✗ Missing {filename}")
                all_ok = False

        # 2. Check Python paths
        print("\nChecking Python paths:")
        if str(package_root) in sys.path:
            print("✓ Package root in Python path")
        else:
            print("✗ Package root not in Python path")
            all_ok = False

        try:

            # Get all possible site-packages locations
            site_packages_paths = {
                'user': Path(site.getusersitepackages()),
                'venv': Path(sys.prefix) / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages',
                'system': Path(site.getsitepackages()[0]) if site.getsitepackages() else None
            }

            found = False
            for location, path in site_packages_paths.items():
                if path and str(path) in sys.path:
                    print(f"✓ Found {location} site-packages in Python path: {path}")
                    found = True

            if not found:
                print("✗ No site-packages directories found in Python path")
                all_ok = False

            # Also check if BSG-IDE is importable
            try:
                import BeamerSlideGenerator
                print("✓ BSG-IDE package is importable")
            except ImportError as e:
                print(f"✗ Cannot import BSG-IDE package: {e}")
                all_ok = False

        except Exception as e:
            print(f"! Warning: Could not check site-packages: {e}")

        # 3. Check launcher script
        print("\nChecking launcher script:")
        if sys.platform == "win32":
            launcher_name = 'bsg-ide.bat'
        else:
            launcher_name = 'bsg-ide'

        launcher_locations = [
            Path.home() / '.local/bin',
            Path('/usr/local/bin'),
            package_root / 'bin'
        ]

        launcher_found = False
        for loc in launcher_locations:
            launcher_path = loc / launcher_name
            if launcher_path.exists():
                print(f"✓ Found launcher at: {launcher_path}")
                launcher_found = True
                # Check permissions on Unix-like systems
                if sys.platform != "win32":
                    if os.access(launcher_path, os.X_OK):
                        print("✓ Launcher has correct permissions")
                    else:
                        print("✗ Launcher missing executable permission")
                        all_ok = False
                break

        if not launcher_found:
            print("✗ Launcher script not found")
            all_ok = False

        # 4. Check desktop integration
        print("\nChecking desktop integration:")
        if sys.platform.startswith('linux'):
            # Check desktop entry
            desktop_locations = [
                Path.home() / '.local/share/applications',
                Path('/usr/share/applications')
            ]
            desktop_found = False
            for loc in desktop_locations:
                desktop_path = loc / 'bsg-ide.desktop'
                if desktop_path.exists():
                    print(f"✓ Found desktop entry at: {desktop_path}")
                    desktop_found = True
                    break

            if not desktop_found:
                print("✗ Desktop entry not found")
                all_ok = False

            # Check icons
            icon_found = False
            icon_sizes = ['16x16', '32x32', '48x48', '64x64', '128x128', '256x256']
            for size in icon_sizes:
                icon_locations = [
                    Path.home() / f'.local/share/icons/hicolor/{size}/apps',
                    Path(f'/usr/share/icons/hicolor/{size}/apps')
                ]
                for loc in icon_locations:
                    icon_path = loc / 'bsg-ide.png'
                    if icon_path.exists():
                        if not icon_found:  # Only print first found
                            print(f"✓ Found application icon at: {icon_path.parent.parent.parent}")
                        icon_found = True

            if not icon_found:
                print("✗ Application icon not found")
                all_ok = False

        elif sys.platform == "darwin":  # macOS
            app_locations = [
                Path.home() / 'Applications/BSG-IDE.app',
                Path('/Applications/BSG-IDE.app')
            ]
            app_found = False
            for loc in app_locations:
                if loc.exists():
                    print(f"✓ Found application bundle at: {loc}")
                    app_found = True
                    # Check Info.plist
                    if (loc / 'Contents/Info.plist').exists():
                        print("✓ Found Info.plist")
                    else:
                        print("✗ Missing Info.plist")
                        all_ok = False
                    break

            if not app_found:
                print("✗ Application bundle not found")
                all_ok = False

        elif sys.platform == "win32":  # Windows
            # Check Start Menu shortcut
            start_menu_locations = [
                Path(os.environ['APPDATA']) / 'Microsoft/Windows/Start Menu/Programs',
                Path(os.environ['PROGRAMDATA']) / 'Microsoft/Windows/Start Menu/Programs'
            ]
            shortcut_found = False
            for loc in start_menu_locations:
                shortcut_path = loc / 'BSG-IDE/BSG-IDE.lnk'
                if shortcut_path.exists():
                    print(f"✓ Found Start Menu shortcut at: {shortcut_path}")
                    shortcut_found = True
                    break

            if not shortcut_found:
                print("✗ Start Menu shortcut not found")
                all_ok = False

        # 5. Check imports
        print("\nChecking imports:")
        try:
            import BeamerSlideGenerator
            print("✓ Can import BeamerSlideGenerator")
        except ImportError as e:
            print(f"✗ Cannot import BeamerSlideGenerator: {e}")
            all_ok = False



        # Final status
        print("\nVerification result:")
        if all_ok:
            print("✓ All checks passed successfully!")
        else:
            print("✗ Some checks failed. Please run 'bsg-ide --fix' to repair the installation")

        return all_ok

    except Exception as e:
        print(f"\n✗ Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

"""
Path utilities for BSG-IDE to properly locate resources when installed via pip
"""

import os
import sys
from pathlib import Path
from importlib import resources

def get_package_root():
    """Get the root directory of the installed package"""
    try:
        # Try to get from module
        import bsg_ide
        return Path(bsg_ide.__file__).parent
    except ImportError:
        # Fallback to current file location
        return Path(__file__).parent.parent

def get_resource_path(filename):
    """Get path to a resource file in the package"""
    package_root = get_package_root()

    # Check various possible locations
    possible_paths = [
        package_root / filename,
        package_root / "resources" / filename,
        package_root.parent / filename,
        Path.cwd() / filename,
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    # If not found, return the package path as default
    return str(package_root / filename)

def ensure_bsg_file():
    """
    Ensure BeamerSlideGenerator.py is available by adding the package
    directory to Python path if needed
    """
    package_root = get_package_root()

    # Add package root to Python path if not already there
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))

    # Also add the parent directory
    parent_dir = package_root.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

    # Check if we can import BeamerSlideGenerator
    try:
        import BeamerSlideGenerator
        return True
    except ImportError:
        # Try direct import from package
        try:
            from bsg_ide import BeamerSlideGenerator
            return True
        except ImportError:
            return False


def get_package_root():
    """Get the package root directory whether installed or running from source"""
    try:
        # First check if we're running from source
        current_file = Path(__file__).resolve()
        current_dir = current_file.parent

        # Check if we're in source directory (look for key files)
        if all((current_dir / f).exists() for f in ['BeamerSlideGenerator.py', 'BSG_IDE.py']):
            return current_dir

        # If not in source, check if we're pip installed
        try:
            import bsg_ide
            return Path(bsg_ide.__file__).parent
        except ImportError:
            pass

        # Finally check standard installation locations
        standard_locations = [
            Path.home() / '.local/lib/bsg-ide',
            Path.home() / '.local/share/bsg-ide',
            Path('/usr/local/share/bsg-ide')
        ]

        for loc in standard_locations:
            if (loc / 'BSG_IDE.py').exists():
                return loc

        # If we get here, return current directory as fallback
        return current_dir

    except Exception as e:
        print(f"Warning: Could not determine package root: {e}")
        return Path(__file__).parent

def setup_paths():
    """Setup Python paths for both source and installed runs"""
    package_root = get_package_root()

    # Add package root to Python path if not already there
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))

    # Find resources directory
    resources_dir = package_root / 'resources'
    if not resources_dir.exists():
        resources_dir = package_root  # Fallback to package root

    return package_root, resources_dir
#-----------------------------------------------------------


def create_desktop_entry():
    """Create desktop entry for pympress launcher"""
    if sys.platform.startswith('linux'):
        desktop_entry = """[Desktop Entry]
Type=Application
Name=pympress
Comment=PDF Presentation Tool
Exec=pympress %f
Icon=pympress
Terminal=false
Categories=Office;Presentation;
MimeType=application/pdf;
"""
        desktop_path = Path.home() / '.local' / 'share' / 'applications' / 'pympress.desktop'
        os.makedirs(desktop_path.parent, exist_ok=True)
        desktop_path.write_text(desktop_entry)
        desktop_path.chmod(0o755)
        print("✓ Desktop entry created")



def verify_existing_packages():
    """Verify existing packages when offline"""
    try:
        import customtkinter
        import PIL
        import tkinter
        print("✓ Required packages found in existing installation")
        return True
    except ImportError:
        print("Error: Required packages not found and cannot install offline")
        return False
#-----------------------------------------Check dependencies -------------------

def check_and_install_dependencies():
    """
    Two-phase dependency installation with improved virtual environment handling
    """
    # Suppress standard output during initial installation
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

    try:
        # Check internet connection
        if not check_internet_connection():
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            print("No internet connection. Continuing with available packages.")
            return True

        # Get requirements.txt path
        requirements_path = get_requirements_path()
        if not requirements_path:
            print("Error: Could not locate or create requirements.txt")
            return False

        # Setup virtual environment
        #python_path, pip_path, venv_created = setup_virtual_env()

        # Phase 1: Install base packages (no GUI feedback)
        base_packages = {
            "customtkinter": "5.2.2",
            "Pillow": None,
            "tk": None
        }

        # First, upgrade pip in the virtual environment
        try:
            subprocess.run(
                [pip_path, "install", "--upgrade", "pip"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except Exception as e:
            print(f"Error upgrading pip: {e}")

        # Install base packages in virtual environment
        for package, version in base_packages.items():
            try:
                package_spec = f"{package}=={version}" if version else package
                # Do not use --user flag in virtual environment
                subprocess.run(
                    [pip_path, "install", "--no-cache-dir", package_spec],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
                print(f"✓ Installed {package_spec}")
            except subprocess.CalledProcessError as e:
                print(f"Error installing {package}: {e}")
                # Try alternative installation without version constraint
                try:
                    subprocess.run(
                        [pip_path, "install", "--no-cache-dir", package.split('==')[0]],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=True
                    )
                    print(f"✓ Installed {package} (latest version)")
                except subprocess.CalledProcessError as e2:
                    print(f"Alternative installation failed for {package}: {e2}")
                    continue

        # Create media_files directory
        os.makedirs('media_files', exist_ok=True)

        # Restore output for verification
        sys.stdout = original_stdout
        sys.stderr = original_stderr

        # Verify customtkinter installation
        try:
            # Add virtual environment site-packages to Python path
            if venv_created:
                import site
                venv_site_packages = os.path.join(os.path.dirname(pip_path), '..', 'lib',
                                                f'python{sys.version_info.major}.{sys.version_info.minor}',
                                                'site-packages')
                sys.path.insert(0, venv_site_packages)

            import customtkinter
            print("✓ customtkinter installed successfully")

            # Phase 2: Install remaining packages with GUI feedback
            try:
                import tkinter as tk
                from tkinter import ttk
                install_remaining_packages(pip_path)
            except ImportError as e:
                print(f"Error importing GUI packages for phase 2: {e}")
                # Fall back to silent installation of remaining packages
                packages = {
                    'requests': 'requests',
                    'yt_dlp': 'yt-dlp',
                    'cv2': 'opencv-python',
                    'screeninfo': 'screeninfo',
                    'numpy': 'numpy',
                    'pyautogui':'pyautogui',
                    'fitz': 'PyMuPDF==1.23.7'

                }

                for import_name, install_name in packages.items():
                    try:
                        if not util.find_spec(import_name):
                            subprocess.run(
                                [pip_path, "install", "--no-cache-dir", install_name],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=True
                            )
                            print(f"✓ Installed {install_name}")
                    except:
                        continue

            return verify_installation()

        except ImportError:
            print("! Warning: customtkinter not found after installation")
            # Print the current sys.path for debugging
            print("\nCurrent Python path:")
            for p in sys.path:
                print(f"  {p}")
            return False

        return True

    except Exception as e:
        # Restore output
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        print(f"Warning: Some dependencies may be missing. Continuing with available packages.")
        print(f"Error details: {str(e)}")
        return True

    finally:
        # Ensure output is restored
        sys.stdout = original_stdout
        sys.stderr = original_stderr

def install_remaining_packages(pip_path):
    """Install all remaining packages from requirements.txt with progress feedback"""
    try:
        # Now we can safely import GUI packages
        import tkinter as tk
        from tkinter import ttk
        import customtkinter as ctk

        class ProgressDialog:
            def __init__(self):
                self.root = ctk.CTk()
                self.root.title("Installing Dependencies")
                self.root.geometry("300x150")

                # Center window
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                x = (screen_width - 300) // 2
                y = (screen_height - 150) // 2
                self.root.geometry(f"+{x}+{y}")

                self.label = ctk.CTkLabel(
                    self.root,
                    text="Installing dependencies...",
                    font=("Arial", 12)
                )
                self.label.pack(pady=20)

                self.progress = ctk.CTkProgressBar(self.root)
                self.progress.pack(pady=10, padx=20, fill="x")
                self.progress.set(0)

                self.status = ctk.CTkLabel(
                    self.root,
                    text="",
                    font=("Arial", 10)
                )
                self.status.pack(pady=5)

                self.root.update()

            def update(self, progress, text=None):
                self.progress.set(progress)
                if text:
                    self.label.configure(text=text)
                    # Also update status with package name
                    if "Installing" in text:
                        package = text.split("Installing ")[-1].strip('...')
                        self.status.configure(text=f"Package: {package}")
                self.root.update()

            def close(self):
                self.root.destroy()

        try:
            # Get requirements.txt path
            requirements_path = get_requirements_path()

            # Read requirements.txt
            with open(requirements_path, 'r') as f:
                requirements = [line.strip() for line in f
                              if line.strip() and not line.startswith('#')]

            # Create progress dialog
            dialog = ProgressDialog()

            # Install packages with progress updates
            total = len(requirements)
            successful = 0
            failed = []

            for i, requirement in enumerate(requirements, 1):
                progress = i / total
                package_name = requirement.split('>=')[0].split('==')[0].strip()
                dialog.update(progress, f"Installing {package_name}...")

                try:
                    # First try to import to check if already installed
                    try:
                        if ';' in requirement:  # Skip platform-specific requirements check
                            raise ImportError
                        module_name = package_name.replace('-', '_')
                        __import__(module_name)
                        successful += 1
                        dialog.status.configure(text=f"✓ {package_name} already installed")
                        dialog.root.update()
                        continue
                    except ImportError:
                        pass

                    # If not installed, install it
                    result = subprocess.run(
                        [pip_path, "install", "--no-cache-dir", requirement],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=True
                    )
                    successful += 1
                    dialog.status.configure(text=f"✓ {package_name} installed successfully")
                except Exception as e:
                    print(f"Warning: Failed to install {requirement}: {str(e)}")
                    failed.append(package_name)
                    dialog.status.configure(text=f"✗ Failed to install {package_name}")

                dialog.root.update()

            # Show completion status
            dialog.update(1.0, "Installation complete!")
            final_status = f"Installed {successful} of {total} packages"
            if failed:
                final_status += f"\nFailed: {', '.join(failed)}"
            dialog.status.configure(text=final_status)
            dialog.root.after(2000, dialog.close)  # Close after 2 seconds
            dialog.root.mainloop()

        except Exception as e:
            if 'dialog' in locals():
                dialog.close()
            print(f"Error in GUI installation: {str(e)}")
            # Fall back to silent installation
            subprocess.run(
                [pip_path, "install", "-r", str(requirements_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

    except ImportError as e:
        print(f"GUI packages not available for progress dialog: {str(e)}")
        print("Falling back to silent installation...")
        # Fall back to silent installation
        subprocess.run(
            [pip_path, "install", "-r", str(requirements_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        print(f"Error installing packages: {str(e)}")



#check_and_install_dependencies()


import atexit
import shutil
import threading
import queue
import socket
import json
import time
import zipfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import customtkinter as ctk
from typing import Optional, Dict, List, Tuple,Any
from pathlib import Path
from PIL import Image
import traceback
import webbrowser
#from BSE import BeamerSlideEditor,BeamerSyntaxHighlighter

#-------------------------------------BSE-----------------------------------------------

import customtkinter as ctk
import tkinter as tk
import os,sys
import threading
from pathlib import Path
from PIL import Image
#from BSE_ITR import InteractiveTerminal
ENHANCED_FEATURES_AVAILABLE = False
try:
    from .EnhancedCommandDialog import EnhancedCommandIndexDialog, IntelligentAutocomplete, LatexCommandHelper, CommandTooltip
    ENHANCED_FEATURES_AVAILABLE = True
    from .Grammarly import  GrammarlyIntegration,GrammarlySetupDialog,AutomatedGrammarlyIntegration
    from .InteractiveTerminal import InteractiveTerminal
    print("✓ Enhanced command features loaded")
except ImportError as e:
    print(f"Enhanced features not available: {e}")
    from EnhancedCommandDialog import EnhancedCommandIndexDialog, IntelligentAutocomplete, LatexCommandHelper, CommandTooltip
    ENHANCED_FEATURES_AVAILABLE = True
    from Grammarly import  GrammarlyIntegration,GrammarlySetupDialog,AutomatedGrammarlyIntegration
    from InteractiveTerminal import InteractiveTerminal

class DynamicToolbar:
    """Manages dynamic toolbar with overflow handling"""

    def __init__(self, parent):
        self.parent = parent
        self.all_buttons = []  # Store all button references (widget, priority, pack_info)
        self.more_menu = None
        self.more_button = None
        self.last_width = 0
        self.is_dynamic = True

    def add_button(self, button, priority=0, pack_kwargs=None):
        """Add a button with priority (higher priority = stays visible longer)"""
        if pack_kwargs is None:
            pack_kwargs = {'side': 'left', 'padx': 2}
        self.all_buttons.append({
            'widget': button,
            'priority': priority,
            'visible': True,
            'pack_kwargs': pack_kwargs
        })

    def add_frame(self, frame, priority=0, pack_kwargs=None):
        """Add a frame containing multiple widgets"""
        if pack_kwargs is None:
            pack_kwargs = {'side': 'left', 'padx': 2}
        self.all_buttons.append({
            'widget': frame,
            'priority': priority,
            'visible': True,
            'pack_kwargs': pack_kwargs,
            'is_frame': True
        })

    def setup_more_menu(self):
        """Create the 'More' dropdown menu button"""
        if self.more_button is None or not self.more_button.winfo_exists():
            self.more_button = ctk.CTkButton(
                self.parent,
                text="▼ More",
                width=60,
                command=self.show_more_menu,
                fg_color="#2F3542",
                hover_color="#404859"
            )

    def show_more_menu(self):
        """Show the dropdown menu with hidden buttons"""
        if self.more_menu:
            self.more_menu.destroy()

        self.more_menu = tk.Menu(self.parent, tearoff=0)

        # Add hidden items to menu
        for btn_info in self.all_buttons:
            if not btn_info['visible']:
                widget = btn_info['widget']
                if widget.winfo_exists():
                    # Try to get button text
                    try:
                        text = widget.cget('text')
                        if text:
                            self.more_menu.add_command(
                                label=text,
                                command=widget.cget('command')
                            )
                    except:
                        # For frames or complex widgets, add separator with label
                        if btn_info.get('is_frame'):
                            self.more_menu.add_separator()
                            self.more_menu.add_command(
                                label="Additional Controls",
                                state="disabled"
                            )

        # Show menu below the More button
        if self.more_button and self.more_button.winfo_exists():
            x = self.more_button.winfo_rootx()
            y = self.more_button.winfo_rooty() + self.more_button.winfo_height()
            self.more_menu.tk_popup(x, y)

    def update_layout(self, event=None):
        """Update button visibility based on available width"""
        if not self.parent.winfo_exists() or not self.is_dynamic:
            return

        # Get available width
        available_width = self.parent.winfo_width() - 30  # Account for padding

        # Don't update if width hasn't changed significantly
        if abs(available_width - self.last_width) < 50 and self.last_width > 0:
            return
        self.last_width = available_width

        # Sort buttons by priority (higher first)
        sorted_buttons = sorted(
            self.all_buttons,
            key=lambda x: x['priority'],
            reverse=True
        )

        # Calculate current total width
        total_width = 0
        visible_buttons = []

        for btn_info in sorted_buttons:
            if btn_info['visible'] and btn_info['widget'].winfo_exists():
                btn_info['widget'].update_idletasks()
                width = btn_info['widget'].winfo_width()
                if width <= 1:  # Not yet sized properly
                    width = 80  # Default width estimate
                total_width += width + 10
                visible_buttons.append(btn_info)

        # Determine which buttons to hide
        more_button_width = 70  # Approximate width of More button

        if total_width > available_width:
            # Hide lowest priority buttons until we fit
            hide_count = 0
            temp_total = total_width

            for btn_info in reversed(sorted_buttons):
                if btn_info['visible'] and btn_info['widget'].winfo_exists():
                    btn_width = btn_info['widget'].winfo_width()
                    if btn_width <= 1:
                        btn_width = 80

                    if temp_total > available_width - more_button_width:
                        # Hide this button
                        btn_info['widget'].pack_forget()
                        btn_info['visible'] = False
                        temp_total -= (btn_width + 10)
                        hide_count += 1
                    else:
                        break

            # Show More button if we hid anything
            if hide_count > 0:
                self.setup_more_menu()
                if not self.more_button.winfo_ismapped():
                    self.more_button.pack(side="right", padx=5)
            else:
                if self.more_button and self.more_button.winfo_ismapped():
                    self.more_button.pack_forget()

        else:
            # Show hidden buttons if space permits
            for btn_info in sorted_buttons:
                if not btn_info['visible'] and btn_info['widget'].winfo_exists():
                    btn_width = btn_info['widget'].winfo_width()
                    if btn_width <= 1:
                        btn_width = 80

                    if total_width + btn_width + 10 <= available_width:
                        # Repack the button
                        btn_info['widget'].pack(**btn_info['pack_kwargs'])
                        btn_info['visible'] = True
                        total_width += btn_width + 10
                    else:
                        break

            # Hide More button if all buttons are visible
            if all(btn['visible'] for btn in self.all_buttons if btn['widget'].winfo_exists()):
                if self.more_button and self.more_button.winfo_ismapped():
                    self.more_button.pack_forget()

    def pack_all(self):
        """Pack all buttons initially"""
        for btn_info in self.all_buttons:
            if btn_info['widget'].winfo_exists():
                btn_info['widget'].pack(**btn_info['pack_kwargs'])
                btn_info['visible'] = True

        # Bind resize event
        self.parent.bind('<Configure>', self.update_layout)
        self.parent.after(100, self.update_layout)  # Initial layout

    def unbind_events(self):
        """Unbind resize events for cleanup"""
        try:
            self.parent.unbind('<Configure>')
        except:
            pass

    def set_dynamic(self, enabled):
        """Enable or disable dynamic behavior"""
        self.is_dynamic = enabled
        if not enabled:
            # Show all buttons when disabled
            for btn_info in self.all_buttons:
                if not btn_info['visible'] and btn_info['widget'].winfo_exists():
                    btn_info['widget'].pack(**btn_info['pack_kwargs'])
                    btn_info['visible'] = True
            if self.more_button and self.more_button.winfo_ismapped():
                self.more_button.pack_forget()

class LocalPackageInstaller:
    """Install packages locally without requiring sudo/root permissions"""

    def __init__(self, parent=None, verbose=True):
        self.parent = parent
        self.verbose = verbose
        self.local_texmf = Path.home() / 'texmf'
        self.local_texmf.mkdir(parents=True, exist_ok=True)

    def write(self, text, color="white"):
        """Write message to terminal or parent"""
        if self.parent and hasattr(self.parent, 'write'):
            self.parent.write(text, color)
        elif self.verbose:
            print(text)

    def install_latex_package_local(self, package_name: str) -> bool:
        """Install LaTeX package locally (no sudo required) - with multiple methods"""
        try:
            self.write(f"\n📦 Installing {package_name} locally...", "cyan")

            # Method 1: Try tlmgr with --user option (TeX Live)
            if shutil.which('tlmgr'):
                success = self._install_with_tlmgr_user(package_name)
                if success:
                    return True

            # Method 2: Try manual download from CTAN
            success = self._install_from_ctan_local(package_name)
            if success:
                return True

            # Method 3: Try to find and copy from system texmf
            success = self._copy_from_system_texmf(package_name)
            if success:
                return True

            # Method 4: Try using wget/curl to download manually
            success = self._install_with_wget_curl(package_name)
            if success:
                return True

            self.write(f"✗ Could not install {package_name} locally", "red")
            return False

        except Exception as e:
            self.write(f"✗ Local installation error: {str(e)}", "red")
            return False

    def _install_with_tlmgr_user(self, package_name: str) -> bool:
        """Install using tlmgr with --user option (no sudo)"""
        try:
            # Check if tlmgr supports --user
            result = subprocess.run(
                ['tlmgr', '--help'],
                capture_output=True, text=True, timeout=10
            )

            if '--user' in result.stdout:
                self.write("  Using tlmgr --user...", "cyan")
                result = subprocess.run(
                    ['tlmgr', '--user', 'install', package_name],
                    capture_output=True, text=True, timeout=120
                )

                if result.returncode == 0:
                    self.write(" ✓ Installed with tlmgr --user", "green")
                    self._refresh_texmf_local()
                    return True
                else:
                    self.write(f"  tlmgr --user failed: {result.stderr[:100]}", "yellow")

            return False

        except Exception as e:
            self.write(f"  tlmgr user install failed: {str(e)}", "yellow")
            return False

    def _install_from_ctan_local(self, package_name: str) -> bool:
        """Download and install from CTAN to local texmf directory - FIXED for Manjaro Linux"""
        import urllib.request
        import urllib.error
        import tarfile
        import zipfile
        import tempfile
        import glob

        try:
            # Map common package names to CTAN paths
            ctan_map = {
                'siunitx': 'siunitx',
                'textcomp': 'textcomp',
                'amsmath': 'amsmath',
                'amssymb': 'amsfonts',
                'xcolor': 'xcolor',
                'booktabs': 'booktabs',
                'pgfplots': 'pgfplots',
                'pgf': 'pgf',
                'tikz': 'pgf',
                'soul': 'soul',
                'hyperref': 'hyperref',
                'geometry': 'geometry',
                'beamer': 'beamer',
                'tcolorbox': 'tcolorbox',
                'listings': 'listings',
                'fancyvrb': 'fancyvrb',
                'caption': 'caption',
                'subcaption': 'subcaption',
            }

            ctan_name = ctan_map.get(package_name, package_name)

            # Create temporary directory for download
            temp_dir = tempfile.mkdtemp()

            # Try multiple CTAN mirrors with correct URL patterns
            mirrors = [
                # Primary CTAN mirror (Germany)
                f"https://mirror.ctan.org/systems/texlive/tlnet/archive/{ctan_name}.tar.xz",
                f"https://mirror.ctan.org/macros/latex/contrib/{ctan_name}.zip",
                f"https://mirror.ctan.org/macros/latex/contrib/{ctan_name}.tar.xz",
                # Czech mirror
                f"https://ftp.cvut.cz/tex-archive/macros/latex/contrib/{ctan_name}.zip",
                # USA mirror
                f"https://mirrors.ibiblio.org/CTAN/macros/latex/contrib/{ctan_name}.zip",
                # UK mirror
                f"https://www.texlive.info/CTAN/macros/latex/contrib/{ctan_name}.zip",
            ]

            downloaded_file = None
            file_type = None

            for url in mirrors:
                try:
                    self.write(f"  Trying {url[:80]}...", "cyan")

                    # Create request with proper headers
                    req = urllib.request.Request(
                        url,
                        headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
                    )

                    # Download with timeout
                    with urllib.request.urlopen(req, timeout=30) as response:
                        if response.status == 200:
                            # Determine file extension from URL
                            if url.endswith('.tar.xz'):
                                downloaded_file = os.path.join(temp_dir, f"{ctan_name}.tar.xz")
                                file_type = 'tar.xz'
                            elif url.endswith('.zip'):
                                downloaded_file = os.path.join(temp_dir, f"{ctan_name}.zip")
                                file_type = 'zip'
                            else:
                                continue

                            # Save file
                            with open(downloaded_file, 'wb') as f:
                                f.write(response.read())

                            self.write(" ✓ Downloaded", "green")
                            break
                        else:
                            self.write(f" HTTP {response.status}", "yellow")

                except urllib.error.HTTPError as e:
                    self.write(f" HTTP {e.code}", "yellow")
                    continue
                except urllib.error.URLError as e:
                    self.write(f" Connection error", "yellow")
                    continue
                except Exception as e:
                    self.write(f" Error: {str(e)[:30]}", "yellow")
                    continue

            if not downloaded_file or not os.path.exists(downloaded_file):
                self.write("  ✗ Could not download from any mirror", "red")
                return False

            # Extract based on file type
            self.write(f"  Extracting to {self.local_texmf}...", "cyan")

            # Determine correct destination directory
            if package_name in ['siunitx', 'xcolor', 'booktabs', 'soul', 'tcolorbox']:
                dest = self.local_texmf / 'tex' / 'latex' / package_name
            else:
                dest = self.local_texmf / 'tex' / 'latex' / ctan_name

            dest.mkdir(parents=True, exist_ok=True)

            try:
                if file_type == 'zip':
                    with zipfile.ZipFile(downloaded_file, 'r') as zip_ref:
                        # Extract only .sty, .cls, .def, .fd, .cfg, .tex files
                        extracted_count = 0
                        for file in zip_ref.namelist():
                            if file.endswith(('.sty', '.cls', '.def', '.fd', '.cfg', '.tex', '.dtx', '.ins')):
                                # Get just the filename (strip directories)
                                filename = os.path.basename(file)
                                if filename and not filename.startswith('.'):
                                    try:
                                        source = zip_ref.open(file)
                                        target = dest / filename
                                        with open(target, 'wb') as f:
                                            f.write(source.read())
                                        extracted_count += 1
                                    except Exception as e:
                                        self.write(f"\n    Warning: Could not extract {filename}: {e}", "yellow")

                        self.write(f" Extracted {extracted_count} files", "green")

                elif file_type == 'tar.xz':
                    with tarfile.open(downloaded_file, 'r:xz') as tar_ref:
                        extracted_count = 0
                        for member in tar_ref.getmembers():
                            if member.name.endswith(('.sty', '.cls', '.def', '.fd', '.cfg', '.tex', '.dtx', '.ins')):
                                # Get just the filename
                                filename = os.path.basename(member.name)
                                if filename and not filename.startswith('.'):
                                    try:
                                        # Extract to destination
                                        source = tar_ref.extractfile(member)
                                        if source:
                                            target = dest / filename
                                            with open(target, 'wb') as f:
                                                f.write(source.read())
                                            extracted_count += 1
                                    except Exception as e:
                                        self.write(f"\n    Warning: Could not extract {filename}: {e}", "yellow")

                        self.write(f" Extracted {extracted_count} files", "green")

                # If we extracted files, also try to run if the package needs generation
                if extracted_count > 0:
                    # Check if we need to generate .sty from .dtx
                    dtx_files = list(dest.glob('*.dtx'))
                    if dtx_files:
                        self.write("\n  Generating package files from .dtx...", "cyan")
                        for dtx in dtx_files:
                            try:
                                # Run pdflatex on dtx file to generate .sty
                                subprocess.run(
                                    ['pdflatex', '-interaction=nonstopmode', str(dtx)],
                                    cwd=dest,
                                    capture_output=True,
                                    timeout=60
                                )
                                self.write(f" ✓ Generated from {dtx.name}", "green")
                            except Exception as e:
                                self.write(f" ⚠ Could not generate from {dtx.name}: {e}", "yellow")

                # Clean up
                os.remove(downloaded_file)
                shutil.rmtree(temp_dir, ignore_errors=True)

                # Refresh TeX database
                self._refresh_texmf_local()

                if extracted_count > 0:
                    self.write(f"  ✓ Successfully installed {package_name} to local texmf", "green")
                    return True
                else:
                    self.write(f"  ✗ No files extracted for {package_name}", "red")
                    return False

            except Exception as e:
                self.write(f"\n  ✗ Extraction error: {str(e)}", "red")
                return False

        except Exception as e:
            self.write(f"\n  ✗ CTAN install error: {str(e)}", "red")
            import traceback
            traceback.print_exc()
            return False

    def _copy_from_system_texmf(self, package_name: str) -> bool:
        """Try to copy package from system texmf to local texmf"""
        try:
            # Common system texmf paths
            system_paths = [
                Path('/usr/share/texmf-dist/tex/latex'),
                Path('/usr/local/share/texmf-dist/tex/latex'),
                Path('/var/lib/texmf/tex/latex'),
            ]

            for system_path in system_paths:
                pkg_dir = system_path / package_name
                if pkg_dir.exists():
                    self.write(f"  Found {package_name} in system, copying locally...", "cyan")

                    # Copy to local texmf
                    dest = self.local_texmf / 'tex' / 'latex' / package_name
                    shutil.copytree(pkg_dir, dest, dirs_exist_ok=True)

                    self._refresh_texmf_local()
                    self.write(f"  ✓ Copied {package_name} from system", "green")
                    return True

                # Also check for .sty files directly
                sty_file = system_path / f"{package_name}.sty"
                if sty_file.exists():
                    dest = self.local_texmf / 'tex' / 'latex' / package_name
                    dest.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(sty_file, dest / f"{package_name}.sty")

                    self._refresh_texmf_local()
                    self.write(f"  ✓ Copied {package_name}.sty from system", "green")
                    return True

            return False

        except Exception as e:
            self.write(f"  Copy from system failed: {str(e)}", "yellow")
            return False

    def _refresh_texmf_local(self):
        """Refresh local TeX database"""
        try:
            # Try different commands to refresh
            if shutil.which('texhash'):
                subprocess.run(['texhash', str(self.local_texmf)],
                             capture_output=True, timeout=30)
                self.write("  ✓ Refreshed local texmf database", "green")
            elif shutil.which('mktexlsr'):
                subprocess.run(['mktexlsr', str(self.local_texmf)],
                             capture_output=True, timeout=30)
                self.write("  ✓ Refreshed local texmf database", "green")
            else:
                # Create ls-R file manually
                lsr_file = self.local_texmf / 'ls-R'
                if not lsr_file.exists():
                    lsr_file.touch()
                self.write("  ✓ Created local texmf database marker", "green")
        except Exception as e:
            self.write(f"  Warning: Could not refresh database: {e}", "yellow")

    def install_python_package_local(self, package_name: str) -> bool:
        """Install Python package locally (--user flag)"""
        try:
            self.write(f"\n🐍 Installing Python package {package_name} locally...", "cyan")

            # Try with --user flag first
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--user', package_name],
                capture_output=True, text=True, timeout=120
            )

            if result.returncode == 0:
                self.write(f"  ✓ Installed {package_name} with --user", "green")
                return True

            # Try without --user as fallback (might still work without sudo)
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', package_name],
                capture_output=True, text=True, timeout=120
            )

            if result.returncode == 0:
                self.write(f"  ✓ Installed {package_name}", "green")
                return True

            self.write(f"  ✗ Failed to install {package_name}", "red")
            return False

        except Exception as e:
            self.write(f"  ✗ Python install error: {str(e)}", "red")
            return False

    def ensure_package_available(self, package_name: str, pkg_type: str = 'latex') -> bool:
        """Ensure a package is available, installing locally if needed"""

        # First check if already available
        if self._is_package_available(package_name, pkg_type):
            self.write(f"✓ {package_name} is already available", "green")
            return True

        self.write(f"⚠ {package_name} not found, attempting local installation...", "yellow")

        # Try local installation
        if pkg_type == 'latex':
            success = self.install_latex_package_local(package_name)
        elif pkg_type == 'python':
            success = self.install_python_package_local(package_name)
        else:
            success = False

        if success:
            # Verify installation
            if self._is_package_available(package_name, pkg_type):
                self.write(f"✓ {package_name} successfully installed locally", "green")
                return True
            else:
                self.write(f"⚠ {package_name} installed but not yet available", "yellow")
                # Provide manual instructions
                self._show_manual_instructions(package_name, pkg_type)
                return False
        else:
            self.write(f"✗ Could not install {package_name} locally", "red")
            self._show_manual_instructions(package_name, pkg_type)
            return False

    def _is_package_available(self, package_name: str, pkg_type: str) -> bool:
        """Check if package is available (including local texmf)"""
        try:
            if pkg_type == 'latex':
                # Check in local texmf first
                local_sty = self.local_texmf / 'tex' / 'latex' / package_name / f"{package_name}.sty"
                if local_sty.exists():
                    return True

                # Check system with kpsewhich
                result = subprocess.run(
                    ['kpsewhich', f'{package_name}.sty'],
                    capture_output=True, text=True, timeout=10
                )
                return result.returncode == 0 and result.stdout.strip()

            elif pkg_type == 'python':
                import importlib
                module_name = package_name.replace('-', '_')
                if module_name == 'opencv_python':
                    module_name = 'cv2'
                elif module_name == 'Pillow':
                    module_name = 'PIL'
                importlib.import_module(module_name)
                return True

            return False

        except Exception:
            return False

    def _show_manual_instructions(self, package_name: str, pkg_type: str):
        """Show manual installation instructions"""
        self.write(f"\n📝 Manual installation instructions:", "cyan")

        if pkg_type == 'latex':
            self.write(f"  For LaTeX package '{package_name}':", "yellow")
            self.write(f"    1. Download from: https://ctan.org/pkg/{package_name}", "white")
            self.write(f"    2. Extract to: {self.local_texmf}/tex/latex/{package_name}/", "white")
            self.write(f"    3. Run: texhash ~/texmf", "white")
        else:
            self.write(f"  For Python package '{package_name}':", "yellow")
            self.write(f"    pip install --user {package_name}", "white")

        self.write(f"\n  Or ask your system administrator to install it system-wide.\n", "yellow")

    def _install_with_tlmgr_user(self, package_name: str) -> bool:
        """Install using tlmgr with user mode (no sudo)"""
        try:
            # Check if tlmgr is available
            if not shutil.which('tlmgr'):
                return False

            # Try with --user option (TeX Live 2019+)
            self.write("  Trying tlmgr --user...", "cyan")
            result = subprocess.run(
                ['tlmgr', '--user', 'install', package_name],
                capture_output=True, text=True, timeout=120
            )

            if result.returncode == 0:
                self.write(" ✓ Installed with tlmgr --user", "green")
                self._refresh_texmf_local()
                return True

            # Try without --user but with custom TEXMFHOME
            self.write("  Trying tlmgr with custom TEXMFHOME...", "cyan")

            env = os.environ.copy()
            env['TEXMFHOME'] = str(self.local_texmf)

            result = subprocess.run(
                ['tlmgr', 'install', '--force', package_name],
                capture_output=True, text=True, timeout=120,
                env=env
            )

            if result.returncode == 0:
                self.write(" ✓ Installed with custom TEXMFHOME", "green")
                self._refresh_texmf_local()
                return True

            return False

        except Exception as e:
            self.write(f"  tlmgr user install failed: {str(e)}", "yellow")
            return False

    def _install_with_wget_curl(self, package_name: str) -> bool:
        """Try using wget or curl as fallback"""
        try:
            import urllib.request

            # Try to download just the .sty file directly
            sty_url = f"https://raw.githubusercontent.com/latex3/siunitx/master/siunitx.sty"
            if package_name == 'siunitx':
                sty_url = "https://raw.githubusercontent.com/latex3/siunitx/master/siunitx.sty"
            elif package_name == 'soul':
                sty_url = "http://mirrors.ctan.org/macros/latex/contrib/soul/soul.sty"
            else:
                sty_url = f"https://mirrors.ctan.org/macros/latex/contrib/{package_name}/{package_name}.sty"

            self.write(f"  Trying direct .sty download...", "cyan")

            dest = self.local_texmf / 'tex' / 'latex' / package_name
            dest.mkdir(parents=True, exist_ok=True)

            req = urllib.request.Request(
                sty_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    sty_file = dest / f"{package_name}.sty"
                    with open(sty_file, 'wb') as f:
                        f.write(response.read())
                    self.write(f" ✓ Downloaded {package_name}.sty", "green")
                    self._refresh_texmf_local()
                    return True

            return False

        except Exception as e:
            self.write(f"  Direct download failed: {str(e)}", "yellow")
            return False

#---------------Helper Utils ------------------------------
class SessionManager:
    """Manages persistence of session data between IDE launches"""

    def __init__(self):
        try:
            # Get user's home directory
            self.home_dir = Path.home()
            # Create .bsg-ide directory in user's home if it doesn't exist
            self.config_dir = self.home_dir / '.bsg-ide'
            self.config_dir.mkdir(exist_ok=True)
            self.session_file = self.config_dir / 'session.json'

            # Try to find Documents folder
            documents_dir = None
            possible_docs = [
                self.home_dir / 'Documents',  # Linux/macOS
                self.home_dir / 'documents',  # Alternative spelling
                Path(os.path.expandvars('%USERPROFILE%\\Documents'))  # Windows
            ]

            for doc_path in possible_docs:
                if doc_path.exists() and doc_path.is_dir():
                    documents_dir = doc_path
                    break

            # Fall back to home directory if Documents not found
            default_dir = str(documents_dir) if documents_dir else str(self.home_dir)

            self.default_session = {
                'last_file': None,
                'working_directory': default_dir,
                'recent_files': [],
                'window_size': {'width': 1200, 'height': 800},
                'window_position': {'x': None, 'y': None}
            }
        except Exception as e:
            print(f"Warning: Could not initialize session manager: {str(e)}")
            # Still allow the program to run with defaults
            self.session_file = None
            self.default_session = {
                'last_file': None,
                'working_directory': str(Path.home()),
                'recent_files': [],
                'window_size': {'width': 1200, 'height': 800},
                'window_position': {'x': None, 'y': None}
            }

    def load_session(self):
        """Load session data from file with Documents folder preference"""
        try:
            if self.session_file and self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    data = json.load(f)

                # Validate loaded data
                session_data = self.default_session.copy()

                # Only update working directory if it exists and there's a last file or recent files
                if data.get('last_file') or data.get('recent_files'):
                    if os.path.exists(data.get('working_directory', '')):
                        session_data.update({k: v for k, v in data.items() if k in self.default_session})

                # Filter out non-existent recent files
                session_data['recent_files'] = [
                    f for f in session_data['recent_files']
                    if os.path.exists(f)
                ]

                return session_data

            return self.default_session.copy()

        except Exception as e:
            print(f"Warning: Could not load session data: {str(e)}")
            return self.default_session.copy()

    def save_session(self, data):
        """Save session data to file"""
        if not self.session_file:
            return  # Skip saving if no session file available

        try:
            # Ensure all paths are strings
            session_data = {
                'last_file': str(data.get('last_file')) if data.get('last_file') else None,
                'working_directory': str(data.get('working_directory', self.default_session['working_directory'])),
                'recent_files': [str(f) for f in data.get('recent_files', [])[-10:]],  # Keep last 10 files
                'window_size': data.get('window_size', self.default_session['window_size']),
                'window_position': data.get('window_position', self.default_session['window_position'])
            }

            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not save session data: {str(e)}")

class SearchReplacePanel(ctk.CTkToplevel):
    """Search and replace panel for the Error Editor"""

    def __init__(self, parent, editor_widget):
        super().__init__(parent)
        self.editor = editor_widget
        self.title("Search and Replace")
        self.geometry("500x200")
        self.transient(parent)
        self.grab_set()

        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 200) // 2
        self.geometry(f"+{x}+{y}")

        self.create_widgets()
        self.create_app_menu()

    def create_widgets(self):
        """Create search and replace widgets"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Search section
        search_frame = ctk.CTkFrame(main_frame)
        search_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(search_frame, text="Search:", width=60).pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, width=300)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)

        # Search options frame
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", pady=5)

        self.case_sensitive = ctk.BooleanVar(value=False)
        case_check = ctk.CTkCheckBox(
            options_frame,
            text="Case sensitive",
            variable=self.case_sensitive,
            command=self.on_search_change
        )
        case_check.pack(side="left", padx=10)

        self.whole_word = ctk.BooleanVar(value=False)
        word_check = ctk.CTkCheckBox(
            options_frame,
            text="Whole word",
            variable=self.whole_word,
            command=self.on_search_change
        )
        word_check.pack(side="left", padx=10)

        self.use_regex = ctk.BooleanVar(value=False)
        regex_check = ctk.CTkCheckBox(
            options_frame,
            text="Regular expression",
            variable=self.use_regex,
            command=self.on_search_change
        )
        regex_check.pack(side="left", padx=10)

        # Replace section
        replace_frame = ctk.CTkFrame(main_frame)
        replace_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(replace_frame, text="Replace:", width=60).pack(side="left", padx=5)
        self.replace_entry = ctk.CTkEntry(replace_frame, width=300)
        self.replace_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Status label
        self.status_label = ctk.CTkLabel(main_frame, text="", font=("Arial", 10))
        self.status_label.pack(fill="x", pady=5)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=10)

        ctk.CTkButton(
            button_frame,
            text="Find Next",
            command=self.find_next,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Replace",
            command=self.replace_current,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Replace All",
            command=self.replace_all,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.destroy,
            width=80
        ).pack(side="right", padx=5)

        # Bind Escape key to close
        self.bind('<Escape>', lambda e: self.destroy())

    def get_search_pattern(self):
        """Get the search pattern based on options"""
        search_text = self.search_entry.get()
        if not search_text:
            return None

        if self.use_regex.get():
            try:
                flags = 0 if self.case_sensitive.get() else re.IGNORECASE
                return re.compile(search_text, flags)
            except re.error:
                self.status_label.configure(text="Invalid regular expression", text_color="red")
                return None
        else:
            return search_text

    def on_search_change(self, event=None):
        """Handle search text change - clear highlights and update status"""
        self.editor.tag_remove('search_highlight', '1.0', 'end')
        self.status_label.configure(text="", text_color="white")

    def find_next(self):
        """Find the next occurrence of search text"""
        pattern = self.get_search_pattern()
        if not pattern:
            return

        # Get current cursor position
        cursor_pos = self.editor.index('insert')

        # Search from cursor position
        if isinstance(pattern, str):
            # Plain text search
            start_pos = cursor_pos
            while True:
                start_pos = self.editor.search(pattern, start_pos, stopindex="end",
                                               nocase=not self.case_sensitive.get(),
                                               exact=not self.use_regex.get())
                if not start_pos:
                    # Wrap around to beginning
                    start_pos = self.editor.search(pattern, "1.0", stopindex=cursor_pos,
                                                   nocase=not self.case_sensitive.get(),
                                                   exact=not self.use_regex.get())
                    if not start_pos:
                        self.status_label.configure(text="No more matches found", text_color="yellow")
                        return
                    else:
                        self.status_label.configure(text="Search wrapped to beginning", text_color="cyan")
                        break
                else:
                    break
        else:
            # Regex search
            content = self.editor.get("1.0", "end-1c")
            matches = list(pattern.finditer(content))
            if not matches:
                self.status_label.configure(text="No matches found", text_color="yellow")
                return

            # Find match after cursor
            cursor_index = int(self.editor.index(cursor_pos).split('.')[0])
            for match in matches:
                match_start_line = content[:match.start()].count('\n') + 1
                if match_start_line >= cursor_index:
                    start_pos = f"{match_start_line}.{match.start() - content[:match.start()].rfind('\n') - 1}"
                    break
            else:
                # Wrap to first match
                match = matches[0]
                start_pos = f"{content[:match.start()].count('\n') + 1}.{match.start() - content[:match.start()].rfind('\n') - 1}"
                self.status_label.configure(text="Search wrapped to beginning", text_color="cyan")

        # Highlight the match
        end_pos = f"{start_pos}+{len(pattern) if isinstance(pattern, str) else len(match.group(0))}c"
        self.editor.tag_remove('search_highlight', '1.0', 'end')
        self.editor.tag_add('search_highlight', start_pos, end_pos)
        self.editor.tag_config('search_highlight', background='#FFB86C', foreground='black')
        self.editor.see(start_pos)
        self.editor.mark_set('insert', start_pos)

        match_text = self.editor.get(start_pos, end_pos)
        self.status_label.configure(text=f"Found: '{match_text}'", text_color="green")

    def replace_current(self):
        """Replace the current match"""
        # Get the current selection
        try:
            sel_start = self.editor.index('sel.first')
            sel_end = self.editor.index('sel.last')

            # Check if selection is a search highlight
            tags = self.editor.tag_names(sel_start)
            if 'search_highlight' in tags:
                replace_text = self.replace_entry.get()
                self.editor.delete(sel_start, sel_end)
                self.editor.insert(sel_start, replace_text)
                self.status_label.configure(text="Replaced", text_color="green")
                self.find_next()
            else:
                self.find_next()
        except tk.TclError:
            self.find_next()

    def replace_all(self):
        """Replace all occurrences"""
        pattern = self.get_search_pattern()
        if not pattern:
            return

        content = self.editor.get("1.0", "end-1c")
        replace_text = self.replace_entry.get()

        if isinstance(pattern, str):
            # Plain text replacement
            if self.case_sensitive.get():
                new_content = content.replace(pattern, replace_text)
            else:
                # Case-insensitive replacement
                import re
                new_content = re.compile(re.escape(pattern), re.IGNORECASE).sub(replace_text, content)
        else:
            # Regex replacement
            new_content = pattern.sub(replace_text, content)

        # Count replacements
        count = content.count(pattern) if isinstance(pattern, str) else len(pattern.findall(content))

        if count > 0:
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", new_content)
            self.status_label.configure(text=f"Replaced {count} occurrence(s)", text_color="green")
            # Mark as modified
            if hasattr(self.master, 'modified'):
                self.master.modified = True
        else:
            self.status_label.configure(text="No matches found", text_color="yellow")

class CrossPlatformPackageManager:
    """
    Unified package manager for installing missing dependencies across platforms.
    Handles Python packages (PyPI), R packages (CRAN), LaTeX packages (MiKTeX/TeX Live/CTAN),
    and system packages (apt, brew, chocolatey, etc.)
    """

    def __init__(self, parent=None, verbose=True):
        self.parent = parent
        self.verbose = verbose
        self.system = platform.system()
        self.install_history = []

        # Package source mappings
        self.package_sources = {
            # Python packages
            'python': {
                'primary': 'pypi',
                'fallback': ['conda', 'system'],
                'manager': self._install_python_package
            },
            # R packages
            'r': {
                'primary': 'cran',
                'fallback': [],
                'manager': self._install_r_package
            },
            # LaTeX packages
            'latex': {
                'primary': 'auto',
                'fallback': ['ctan', 'miktex', 'texlive'],
                'manager': self._install_latex_package
            },
            # System packages
            'system': {
                'primary': 'auto',
                'fallback': [],
                'manager': self._install_system_package
            }
        }

        # Known package mappings (what to install for what error)
        self.package_mappings = {
            # LaTeX packages
            'siunitx': {'type': 'latex', 'name': 'siunitx', 'alternatives': ['siunitx']},
            'textcomp': {'type': 'latex', 'name': 'textcomp', 'alternatives': ['textcomp']},
            'amsmath': {'type': 'latex', 'name': 'amsmath', 'alternatives': ['amsmath']},
            'amssymb': {'type': 'latex', 'name': 'amssymb', 'alternatives': ['amssymb', 'amsfonts']},
            'graphicx': {'type': 'latex', 'name': 'graphicx', 'alternatives': ['graphics']},
            'xcolor': {'type': 'latex', 'name': 'xcolor', 'alternatives': ['xcolor']},
            'tikz': {'type': 'latex', 'name': 'pgf', 'alternatives': ['pgf', 'tikz']},
            'pgfplots': {'type': 'latex', 'name': 'pgfplots', 'alternatives': ['pgfplots']},
            'booktabs': {'type': 'latex', 'name': 'booktabs', 'alternatives': ['booktabs']},
            'hyperref': {'type': 'latex', 'name': 'hyperref', 'alternatives': ['hyperref']},
            'geometry': {'type': 'latex', 'name': 'geometry', 'alternatives': ['geometry']},
            'beamer': {'type': 'latex', 'name': 'beamer', 'alternatives': ['beamer']},

            # Python packages (keep existing)
            'customtkinter': {'type': 'python', 'name': 'customtkinter', 'alternatives': []},
            'Pillow': {'type': 'python', 'name': 'Pillow', 'alternatives': ['PIL']},
            # ... rest of existing mappings ...
        }


        # System package managers per platform
        self.system_managers = {
            'Linux': {
                'apt': {'cmd': 'apt', 'install': 'install', 'sudo': True, 'packages': {}},
                'dnf': {'cmd': 'dnf', 'install': 'install', 'sudo': True, 'packages': {}},
                'yum': {'cmd': 'yum', 'install': 'install', 'sudo': True, 'packages': {}},
                'pacman': {'cmd': 'pacman', 'install': '-S', 'sudo': True, 'packages': {}},
                'zypper': {'cmd': 'zypper', 'install': 'install', 'sudo': True, 'packages': {}}
            },
            'Windows': {
                'choco': {'cmd': 'choco', 'install': 'install', 'sudo': False, 'packages': {}},
                'winget': {'cmd': 'winget', 'install': 'install', 'sudo': False, 'packages': {}},
                'scoop': {'cmd': 'scoop', 'install': 'install', 'sudo': False, 'packages': {}}
            },
            'Darwin': {  # macOS
                'brew': {'cmd': 'brew', 'install': 'install', 'sudo': False, 'packages': {}},
                'port': {'cmd': 'port', 'install': 'install', 'sudo': True, 'packages': {}}
            }
        }

        # Initialize system package mappings
        self._init_system_package_mappings()

        # Initialize local installer
        self.local_installer = LocalPackageInstaller(parent, verbose)

    def install_package(self, package_info: dict, auto_confirm: bool = False) -> bool:
        """Install a package using local installation first, fallback to system"""
        if not package_info:
            return False

        pkg_type = package_info.get('type', 'python')
        pkg_name = package_info.get('name', '')

        if not pkg_name:
            return False

        # Check if already installed
        if self.is_package_installed(pkg_name, pkg_type):
            self.write(f"✓ {pkg_name} is already installed", "green")
            return True

        # Ask for confirmation
        if not auto_confirm and self.parent:
            response = messagebox.askyesno(
                "Install Package Locally",
                f"The {pkg_type} package '{pkg_name}' is required.\n\n"
                f"Would you like to install it locally (no admin privileges required)?\n\n"
                f"This will install to your home directory only."
            )
            if not response:
                return False

        # Try local installation first (no sudo required)
        self.write(f"\n📦 Attempting local installation of {pkg_name}...", "cyan")
        success = self.local_installer.ensure_package_available(pkg_name, pkg_type)

        if success:
            self.install_history.append({
                'package': pkg_name,
                'type': pkg_type,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'success': True,
                'method': 'local'
            })
            return True

        # Fallback to system installation (may require sudo)
        self.write(f"\n⚠ Local installation failed, trying system installation...", "yellow")

        if not auto_confirm and self.parent:
            response = messagebox.askyesno(
                "System Installation Required",
                f"Local installation of '{pkg_name}' failed.\n\n"
                f"Would you like to try system-wide installation?\n"
                f"This may require administrator (sudo) privileges."
            )
            if not response:
                return False

        # Use existing system installation methods
        manager = self.package_sources[pkg_type]['manager']
        success = manager(pkg_name, package_info)

        self.install_history.append({
            'package': pkg_name,
            'type': pkg_type,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'success': success,
            'method': 'system' if success else 'failed'
        })

        return success

    def _install_latex_package(self, package_name: str, package_info: dict) -> bool:
        """Modified to use local installation first"""
        # First try local installation (handled by install_package)
        # This method is called as fallback
        system = self.system

        # Try system installation as fallback
        if system == "Windows":
            return self._install_miktex_package(package_name)
        elif system == "Linux":
            return self._install_texlive_package(package_name)
        elif system == "Darwin":
            return self._install_mactex_package(package_name)
        else:
            return self._install_from_ctan(package_name)

    def _init_system_package_mappings(self):
        """Initialize system package name mappings for different distributions"""
        # Linux package mappings
        self.system_managers['Linux']['apt']['packages'] = {
            'pdflatex': 'texlive-latex-base',
            'latex': 'texlive-full',
            'python3-pip': 'python3-pip',
            'python3-venv': 'python3-venv',
            'git': 'git',
            'ffmpeg': 'ffmpeg',
            'portaudio': 'portaudio19-dev',
            'opencv': 'python3-opencv'
        }

        self.system_managers['Linux']['dnf']['packages'] = {
            'pdflatex': 'texlive-scheme-basic',
            'latex': 'texlive-scheme-full',
            'python3-pip': 'python3-pip',
            'git': 'git'
        }

        self.system_managers['Linux']['pacman']['packages'] = {
            'pdflatex': 'texlive-basic',
            'latex': 'texlive-most',
            'python-pip': 'python-pip',
            'git': 'git'
        }

        # Windows package mappings (Chocolatey)
        self.system_managers['Windows']['choco']['packages'] = {
            'miktex': 'miktex',
            'python': 'python',
            'git': 'git',
            'ffmpeg': 'ffmpeg',
            'opencv': 'opencv'
        }

        # macOS package mappings (Homebrew)
        self.system_managers['Darwin']['brew']['packages'] = {
            'pdflatex': 'mactex',
            'latex': 'mactex',
            'python': 'python',
            'git': 'git',
            'ffmpeg': 'ffmpeg',
            'opencv': 'opencv'
        }

    def write(self, text: str, color: str = "white"):
        """Write message to terminal or parent"""
        if self.parent and hasattr(self.parent, 'write'):
            self.parent.write(text, color)
        elif self.verbose:
            print(text)

    def detect_missing_package(self, error_message: str, context: str = "") -> dict:
        """
        Detect missing package from error message
        Returns: dict with 'type', 'name', 'confidence'
        """
        error_lower = error_message.lower()
        context_lower = context.lower()

        # LaTeX missing package patterns
        latex_patterns = [
            (r"file `([^']+)\.sty' not found", 0.95),
            (r"! latex error: missing `([^']+)' package", 0.90),
            (r"! i can't find file `([^']+)'", 0.85),
            (r"package ([^\s]+) not found", 0.80),
            (r"undefined control sequence.*\\usepackage\{([^}]+)\}", 0.75),
        ]

        # Python missing module patterns
        python_patterns = [
            (r"modulenotfounderror: no module named '([^']+)'", 0.95),
            (r"importerror: no module named '([^']+)'", 0.95),
            (r"cannot import name '([^']+)'", 0.70),
        ]

        # R missing package patterns
        r_patterns = [
            (r"there is no package called '([^']+)'", 0.95),
            (r"error in library\(([^)]+)\) : there is no package called", 0.90),
        ]

        # Try to match patterns
        for pattern, confidence in latex_patterns:
            match = re.search(pattern, error_lower)
            if match:
                pkg_name = match.group(1)
                if pkg_name in self.package_mappings:
                    return self.package_mappings[pkg_name]
                return {'type': 'latex', 'name': pkg_name, 'confidence': confidence}

        for pattern, confidence in python_patterns:
            match = re.search(pattern, error_lower)
            if match:
                pkg_name = match.group(1)
                # Handle common import name vs package name differences
                if pkg_name == 'cv2':
                    pkg_name = 'opencv-python'
                elif pkg_name == 'PIL':
                    pkg_name = 'Pillow'
                elif pkg_name == 'fitz':
                    pkg_name = 'PyMuPDF'

                if pkg_name in self.package_mappings:
                    return self.package_mappings[pkg_name]
                return {'type': 'python', 'name': pkg_name, 'confidence': confidence}

        for pattern, confidence in r_patterns:
            match = re.search(pattern, error_lower)
            if match:
                pkg_name = match.group(1)
                if pkg_name in self.package_mappings:
                    return self.package_mappings[pkg_name]
                return {'type': 'r', 'name': pkg_name, 'confidence': confidence}

        return None

    def is_package_installed(self, name: str, pkg_type: str) -> bool:
        """Check if a package is already installed"""
        try:
            if pkg_type == 'python':
                # Try to import the package
                import importlib
                # Handle special cases
                if name == 'opencv-python':
                    module_name = 'cv2'
                elif name == 'Pillow':
                    module_name = 'PIL'
                elif name == 'PyMuPDF':
                    module_name = 'fitz'
                else:
                    module_name = name.replace('-', '_')

                importlib.import_module(module_name)
                return True

            elif pkg_type == 'latex':
                # Check if LaTeX package exists
                result = subprocess.run(
                    ['kpsewhich', f'{name}.sty'],
                    capture_output=True, text=True
                )
                return result.returncode == 0 and result.stdout.strip()

            elif pkg_type == 'r':
                # Check if R package is installed
                result = subprocess.run(
                    ['R', '--vanilla', '-e', f'library({name}, character.only=TRUE)'],
                    capture_output=True, text=True
                )
                return result.returncode == 0

            elif pkg_type == 'system':
                # Check if system command exists
                return shutil.which(name) is not None

        except Exception:
            return False

        return False

    def _install_python_package(self, package_name: str, package_info: dict) -> bool:
        """Install Python package from PyPI or conda"""
        methods = [
            ('pip', self._install_with_pip),
            ('pip3', self._install_with_pip),
            ('conda', self._install_with_conda),
            ('python -m pip', self._install_with_pip)
        ]

        for method_name, method_func in methods:
            if method_name == 'pip' or method_name == 'pip3' or method_name == 'python -m pip':
                if method_func(package_name):
                    return True

        return False

    def _install_with_pip(self, package_name: str) -> bool:
        """Install using pip"""
        try:
            # Try user installation first (no admin required)
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--user', package_name],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                return True

            # Try without --user (may need admin)
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', package_name],
                capture_output=True,
                text=True,
                timeout=120
            )

            return result.returncode == 0

        except Exception as e:
            self.write(f"Pip install error: {e}", "red")
            return False

    def _install_with_conda(self, package_name: str) -> bool:
        """Install using conda if available"""
        if not shutil.which('conda'):
            return False

        try:
            result = subprocess.run(
                ['conda', 'install', '-y', package_name],
                capture_output=True,
                text=True,
                timeout=180
            )
            return result.returncode == 0
        except Exception:
            return False

    def _install_r_package(self, package_name: str, package_info: dict) -> bool:
        """Install R package from CRAN"""
        if not shutil.which('R'):
            self.write("R is not installed. Please install R from https://cran.r-project.org/", "red")
            return False

        try:
            # Install from CRAN
            r_script = f'install.packages("{package_name}", repos="https://cran.r-project.org")'
            result = subprocess.run(
                ['R', '--vanilla', '-e', r_script],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0
        except Exception as e:
            self.write(f"R package install error: {e}", "red")
            return False

    def _install_miktex_package(self, package_name: str) -> bool:
        """Install using MiKTeX package manager - IMPROVED VERSION"""
        try:
            # Find MiKTeX executable
            miktex_paths = [
                r'C:\Program Files\MiKTeX\miktex\bin\x64\mpm.exe',
                r'C:\Program Files\MiKTeX\miktex\bin\mpm.exe',
                r'C:\Program Files (x86)\MiKTeX\miktex\bin\mpm.exe'
            ]

            mpm_path = None
            for path in miktex_paths:
                if os.path.exists(path):
                    mpm_path = path
                    break

            if not mpm_path:
                # Try to find via registry
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\MiKTeX\Current") as key:
                        miktex_root = winreg.QueryValueEx(key, "InstallRoot")[0]
                        mpm_path = os.path.join(miktex_root, "miktex", "bin", "x64", "mpm.exe")
                except:
                    pass

            if not mpm_path or not os.path.exists(mpm_path):
                self.write("MiKTeX package manager not found", "red")
                return False

            # Try without admin first
            self.write(f"  Installing {package_name}...", "cyan")
            result = subprocess.run(
                [mpm_path, "--install", package_name],
                capture_output=True, text=True, timeout=120
            )

            if result.returncode == 0:
                self.write(f" ✓ Success\n", "green")
                return True

            # Try with admin
            self.write("  Trying with admin...", "yellow")
            result = subprocess.run(
                [mpm_path, "--admin", "--install", package_name],
                capture_output=True, text=True, timeout=120
            )

            if result.returncode == 0:
                self.write(f" ✓ Success with admin\n", "green")
                return True

            self.write(f" ✗ Failed\n", "red")
            return False

        except Exception as e:
            self.write(f" ✗ MiKTeX install error: {e}\n", "red")
            return False

    def _install_mactex_package(self, package_name: str) -> bool:
        """Install using MacTeX's tlmgr"""
        return self._install_texlive_package(package_name)

    def _install_texlive_package(self, package_name: str) -> bool:
        """Install using TeX Live's tlmgr - IMPROVED VERSION"""
        if not shutil.which('tlmgr'):
            self.write("tlmgr not found. Please install TeX Live first.", "red")
            return False

        try:
            # First check if already installed
            check_result = subprocess.run(
                ['tlmgr', 'info', package_name],
                capture_output=True, text=True, timeout=30
            )

            if 'installed: Yes' in check_result.stdout:
                self.write(f"  ✓ {package_name} is already installed\n", "green")
                return True

            # Try without sudo first
            self.write(f"  Installing {package_name}...", "cyan")
            result = subprocess.run(
                ['tlmgr', 'install', package_name],
                capture_output=True, text=True, timeout=120
            )

            if result.returncode == 0:
                self.write(f" ✓ Success\n", "green")
                # Refresh filename database
                subprocess.run(['texhash'], capture_output=True, timeout=60)
                return True

            # Try with sudo if permission denied
            if 'permission' in result.stderr.lower() or 'cannot' in result.stderr.lower():
                self.write("  Need permissions, trying with sudo...", "yellow")
                result = subprocess.run(
                    ['sudo', 'tlmgr', 'install', package_name],
                    capture_output=True, text=True, timeout=120
                )
                if result.returncode == 0:
                    self.write(f" ✓ Success with sudo\n", "green")
                    subprocess.run(['sudo', 'texhash'], capture_output=True, timeout=60)
                    return True

            self.write(f" ✗ Failed\n", "red")
            return False

        except subprocess.TimeoutExpired:
            self.write(f" ✗ Installation timed out\n", "red")
            return False
        except Exception as e:
            self.write(f" ✗ Error: {str(e)}\n", "red")
            return False

    def _install_from_ctan(self, package_name: str) -> bool:
        """Download and install from CTAN as fallback - IMPROVED VERSION"""
        import urllib.request
        import zipfile
        import tempfile

        try:
            # Map to CTAN package names
            ctan_map = {
                'siunitx': 'siunitx',
                'textcomp': 'textcomp',
                'amsmath': 'amsmath',
                'amssymb': 'amsfonts',
                'xcolor': 'xcolor',
                'booktabs': 'booktabs',
                'pgfplots': 'pgfplots',
                'pgf': 'pgf',
            }

            ctan_name = ctan_map.get(package_name, package_name)

            # Try multiple CTAN mirrors
            mirrors = [
                f"https://mirrors.ctan.org/macros/latex/contrib/{ctan_name}.zip",
                f"https://www.ctan.org/tex-archive/macros/latex/contrib/{ctan_name}.zip",
                f"https://mirror.ctan.org/systems/texlive/tlnet/archive/{ctan_name}.tar.xz",
            ]

            zip_path = os.path.join(tempfile.gettempdir(), f"{ctan_name}.zip")

            for url in mirrors:
                try:
                    self.write(f"  Trying {url[:60]}...", "cyan")
                    urllib.request.urlretrieve(url, zip_path, timeout=30)
                    self.write(" Downloaded\n", "green")
                    break
                except:
                    continue
            else:
                self.write(" ✗ Could not download from any mirror\n", "red")
                return False

            # Extract to texmf directory
            texmf_home = os.path.expanduser("~/texmf")
            os.makedirs(texmf_home, exist_ok=True)

            self.write(f"  Extracting to {texmf_home}...", "cyan")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(texmf_home)
            self.write(" Done\n", "green")

            # Refresh TeX database
            if shutil.which('texhash'):
                subprocess.run(['texhash'], capture_output=True, timeout=60)
            elif shutil.which('mktexlsr'):
                subprocess.run(['mktexlsr'], capture_output=True, timeout=60)

            os.remove(zip_path)
            self.write(f"  ✓ Successfully installed {package_name} from CTAN\n", "green")
            return True

        except Exception as e:
            self.write(f" ✗ CTAN install error: {e}\n", "red")
            return False

    def _install_system_package(self, package_name: str, package_info: dict) -> bool:
        """Install system package using native package manager"""
        manager = self._detect_system_package_manager()
        if not manager:
            self.write("No supported package manager found", "red")
            return False

        manager_info = self.system_managers[self.system][manager]

        # Get the actual package name for this manager
        pkg_mappings = manager_info['packages']
        actual_pkg = pkg_mappings.get(package_name, package_name)

        # Build command
        cmd = [manager_info['cmd']]
        if manager_info.get('sudo', False) and self.system != "Windows":
            cmd = ['sudo'] + cmd
        cmd.append(manager_info['install'])
        cmd.append(actual_pkg)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0
        except Exception as e:
            self.write(f"System package install error: {e}", "red")
            return False

    def _detect_system_package_manager(self) -> str:
        """Detect which system package manager is available"""
        for manager in self.system_managers[self.system]:
            if shutil.which(manager):
                return manager
        return None

    def install_from_error(self, error_message: str, context: str = "", auto_confirm: bool = False) -> bool:
        """
        Detect missing package from error and install it
        """
        package_info = self.detect_missing_package(error_message, context)
        if package_info:
            return self.install_package(package_info, auto_confirm)
        return False

    def ensure_latex_preamble_packages(self, tex_content: str) -> list:
        """
        Parse LaTeX preamble and ensure all required packages are installed.
        Returns list of missing packages that were installed.
        """
        import re

        # Find all \usepackage commands
        usepackage_pattern = r'\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}'
        matches = re.findall(usepackage_pattern, tex_content)

        packages_needed = set()
        for match in matches:
            # Handle multiple packages in one command
            for pkg in match.split(','):
                pkg = pkg.strip()
                packages_needed.add(pkg)

        # Also check for \RequirePackage
        require_pattern = r'\\RequirePackage(?:\[[^\]]*\])?\{([^}]+)\}'
        matches = re.findall(require_pattern, tex_content)
        for match in matches:
            for pkg in match.split(','):
                pkg = pkg.strip()
                packages_needed.add(pkg)

        # Special check for siunitx (often used for units)
        if 'siunitx' not in packages_needed and ('Ω' in tex_content or '\\Omega' in tex_content):
            packages_needed.add('siunitx')
            self.write("  ℹ Detected Ohm symbol (Ω) - adding siunitx package\n", "cyan")

        installed_packages = []
        for pkg in packages_needed:
            # Normalize package name
            pkg_normalized = pkg.lower()

            if not self.is_package_installed(pkg_normalized, 'latex'):
                self.write(f"  Missing LaTeX package: {pkg_normalized}\n", "yellow")
                if self.install_package({'type': 'latex', 'name': pkg_normalized}, auto_confirm=False):
                    installed_packages.append(pkg_normalized)
                    self.write(f"  ✓ Installed {pkg_normalized}\n", "green")
                else:
                    self.write(f"  ✗ Failed to install {pkg_normalized}\n", "red")

        return installed_packages

class LaTeXErrorAnalyzer:
    """Analyze LaTeX errors and suggest corrections - ENHANCED VERSION"""

    # Add more patterns to the existing PACKAGE_MAP
    PACKAGE_MAP = {
        # Existing mappings...
        'toprule': 'booktabs',
        'midrule': 'booktabs',
        'bottomrule': 'booktabs',
        'cmidrule': 'booktabs',
        'multirow': 'multirow',
        'makecell': 'makecell',
        'thead': 'makecell',
        'SI': 'siunitx',
        'num': 'siunitx',
        'qty': 'physics',
        'dv': 'physics',
        'pdv': 'physics',
        'grad': 'physics',
        'div': 'physics',
        'curl': 'physics',
    }

    @staticmethod
    def analyze_error(error_msg: str, context_lines: list, tex_content: str = "",
                      line_num: int = None, tex_lines: list = None) -> dict:
        """Analyze a LaTeX error and return suggested fixes - ENHANCED"""

        # Check for Extra } or forgotten $ (NEW)
        if 'Extra }' in error_msg or 'forgotten $' in error_msg:
            return LaTeXErrorAnalyzer._analyze_extra_brace_error(error_msg, tex_lines, line_num)

        # Check for unclosed math mode in title (NEW)
        if 'Missing $ inserted' in error_msg and line_num and tex_lines:
            # Look at the line before the error
            prev_line = tex_lines[line_num - 2] if line_num >= 2 else ""
            if '\\title' in prev_line and prev_line.count('$') % 2 != 0:
                return {
                    'error_type': 'unclosed_math_in_title',
                    'suggestion': 'Missing closing $ in title. Add $ at the end of the title line.',
                    'auto_fixable': True,
                    'fix_type': 'fix_title_math',
                    'line': line_num - 1
                }

        # Check for runaway argument / missing brace
        if 'Runaway argument' in error_msg or 'File ended while scanning' in error_msg:
            return LaTeXErrorAnalyzer._analyze_runaway_error(error_msg, tex_lines, line_num)

        # Check for misplaced alignment tab (&) error
        if any(phrase in error_msg for phrase in [
            'Misplaced alignment tab character &',
            'Misplaced &',
            'alignment tab character &'
        ]):
            return LaTeXErrorAnalyzer._analyze_ampersand_error(error_msg, tex_lines, line_num)

        # Check for missing \item error
        elif 'missing \\item' in error_msg.lower() or "perhaps a missing \\item" in error_msg:
            return LaTeXErrorAnalyzer._analyze_missing_item_error(error_msg, line_num)

        # Check for undefined control sequence (missing package)
        elif 'Undefined control sequence' in error_msg:
            return LaTeXErrorAnalyzer._analyze_undefined_command(error_msg, line_num)

        # Check for missing $ (math mode)
        elif 'Missing $ inserted' in error_msg:
            return {
                'error_type': 'missing_math_mode',
                'suggestion': 'Math mode may be missing. Add $ around math expressions like $...$ or $$...$$.',
                'auto_fixable': True,
                'fix_type': 'fix_math_delimiters',
                'line': line_num
            }

        # Check for missing closing brace
        elif 'Missing } inserted' in error_msg:
            return {
                'error_type': 'missing_brace',
                'suggestion': 'Missing closing brace. Check for unmatched { characters.',
                'auto_fixable': True,
                'fix_type': 'fix_braces',
                'line': line_num
            }

        return {
            'error_type': 'unknown',
            'suggestion': 'Unknown error. Please check the log file.',
            'auto_fixable': False,
            'fix_type': 'editor',
            'line': line_num
        }

    @staticmethod
    def _analyze_extra_brace_error(error_msg: str, tex_lines: list, line_num: int) -> dict:
        """Analyze Extra } or forgotten $ errors"""
        result = {
            'error_type': 'extra_brace_or_forgotten_dollar',
            'suggestion': 'Extra } or forgotten $. Check for unbalanced braces or unclosed math mode.',
            'auto_fixable': True,
            'fix_type': 'fix_extra_brace',
            'line': line_num
        }

        # Look at the line before the error (often where the actual issue is)
        if tex_lines and line_num and line_num > 1:
            prev_line = tex_lines[line_num - 2] if line_num <= len(tex_lines) else ""

            # Check for unclosed math mode
            if '$' in prev_line and prev_line.count('$') % 2 != 0:
                result['suggestion'] = 'Unclosed math mode in previous line. Add missing $.'
                result['fix_data'] = {'type': 'unclosed_math', 'line': line_num - 1}

            # Check for unclosed braces
            elif prev_line.count('{') != prev_line.count('}'):
                result['suggestion'] = 'Unclosed brace in previous line. Add missing }.'
                result['fix_data'] = {'type': 'unclosed_brace', 'line': line_num - 1}

            # Check for title with unclosed math
            elif '\\title' in prev_line and prev_line.count('$') % 2 != 0:
                result['suggestion'] = 'Missing $ in title. Add $ at the end of the title.'
                result['fix_data'] = {'type': 'title_math', 'line': line_num - 1}

        return result

    @staticmethod
    def apply_fix(tex_lines: list, analysis: dict, error_line: int = None) -> tuple:
        """Apply the suggested fix to the TeX lines - ENHANCED"""
        fix_type = analysis.get('fix_type')
        fixed_lines = tex_lines.copy()
        fix_description = ""
        fix_count = 0

        if fix_type == 'fix_title_math':
            fixed_lines, fix_count, fix_description = LaTeXErrorAnalyzer._fix_title_math(
                fixed_lines, analysis.get('line', error_line)
            )

        elif fix_type == 'fix_extra_brace':
            fixed_lines, fix_count, fix_description = LaTeXErrorAnalyzer._fix_extra_brace(
                fixed_lines, analysis, error_line
            )

        elif fix_type == 'escape_ampersand':
            fixed_lines, fix_count = LaTeXErrorAnalyzer._fix_ampersands(fixed_lines, error_line)
            fix_description = f"Escaped {fix_count} ampersand(s)"

        elif fix_type == 'add_item' and error_line:
            fixed_lines, fix_count = LaTeXErrorAnalyzer._fix_missing_item(fixed_lines, error_line)
            fix_description = f"Added {fix_count} \\item command(s)"

        elif fix_type == 'add_package':
            package = analysis.get('fix_data')
            if package:
                fixed_lines, fix_count = LaTeXErrorAnalyzer._add_package(fixed_lines, package)
                fix_description = f"Added \\usepackage{{{package}}}"

        elif fix_type in ['fix_runaway', 'fix_math_delimiters', 'fix_braces']:
            fixed_lines, fix_count, fix_description = LaTeXErrorAnalyzer._fix_runaway_error(
                fixed_lines, analysis, error_line
            )

        return fixed_lines, fix_description, fix_count

    @staticmethod
    def _fix_title_math(tex_lines: list, line_num: int) -> tuple:
        """Fix unclosed math in title"""
        fixed_lines = tex_lines.copy()
        fix_count = 0
        fix_description = ""

        if line_num and 1 <= line_num <= len(fixed_lines):
            line = fixed_lines[line_num - 1]
            if '\\title' in line:
                # Add missing $ at the end of the line
                if line.count('$') % 2 != 0:
                    fixed_lines[line_num - 1] = line.rstrip() + '$'
                    fix_count = 1
                    fix_description = "Added missing $ to close math mode in title"

        return fixed_lines, fix_count, fix_description

    @staticmethod
    def _fix_extra_brace(tex_lines: list, analysis: dict, error_line: int = None) -> tuple:
        """Fix Extra } or forgotten $ errors"""
        fixed_lines = tex_lines.copy()
        fix_count = 0
        fix_description = ""

        fix_data = analysis.get('fix_data', {})
        error_type = fix_data.get('type', '')
        target_line = fix_data.get('line', error_line)

        if target_line and 1 <= target_line <= len(fixed_lines):
            line = fixed_lines[target_line - 1]
            original_line = line

            if error_type == 'unclosed_math':
                # Add missing $ at the end of the line
                fixed_lines[target_line - 1] = line.rstrip() + ' $'
                fix_count = 1
                fix_description = "Added missing $ to close math mode"

            elif error_type == 'unclosed_brace':
                # Add missing }
                open_count = line.count('{')
                close_count = line.count('}')
                if open_count > close_count:
                    fixed_lines[target_line - 1] = line.rstrip() + ' ' + '}' * (open_count - close_count)
                    fix_count = 1
                    fix_description = f"Added {open_count - close_count} missing closing brace(s)"

            elif error_type == 'title_math':
                # Add missing $ at the end of title line
                if line.count('$') % 2 != 0:
                    fixed_lines[target_line - 1] = line.rstrip() + '$'
                    fix_count = 1
                    fix_description = "Added missing $ to close math mode in title"

        return fixed_lines, fix_count, fix_description

class MediaURLDialog(ctk.CTkToplevel):
    def __init__(self, parent, slide_index, media_entry):
        super().__init__(parent)
        self.title("Update Media Location")
        self.geometry("500x150")
        self.media_entry = media_entry

        # Center dialog
        self.transient(parent)
        self.grab_set()

        # Create widgets
        ctk.CTkLabel(self, text=f"Enter media URL for slide {slide_index + 1}:").pack(pady=10)

        self.url_entry = ctk.CTkEntry(self, width=400)
        self.url_entry.pack(pady=10)
        self.url_entry.insert(0, media_entry.get())

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Play URL",
                     command=self.use_play_url).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Static URL",
                     command=self.use_static_url).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel",
                     command=self.cancel).pack(side="left", padx=5)

    def use_play_url(self):
        url = self.url_entry.get().strip()
        if url:
            self.media_entry.delete(0, 'end')
            self.media_entry.insert(0, f"\\play \\url {url}")
        self.destroy()

    def use_static_url(self):
        url = self.url_entry.get().strip()
        if url:
            self.media_entry.delete(0, 'end')
            self.media_entry.insert(0, f"\\url {url}")
        self.destroy()

    def cancel(self):
        self.destroy()

# ============================================================================
# Bibliography Configuration
# ============================================================================

class BibliographyConfig:
    """Configuration settings for bibliography handling."""

    def __init__(self):
        self.items_per_page = 12  # References per page (adjustable)
        self.enable_back_references = True
        self.enable_navigation = True
        self.preserve_original_numbering = True
        self.use_allowframebreaks_fallback = True
        self.back_reference_format = "Cited on slides: {slides}"
        self.max_back_references_display = 10  # Show first 10, then "+X more"

    def get_back_reference_text(self, slide_numbers: list) -> str:
        """Generate formatted back-reference text."""
        if not slide_numbers:
            return ""

        if len(slide_numbers) > self.max_back_references_display:
            display_slides = slide_numbers[:self.max_back_references_display]
            remaining = len(slide_numbers) - self.max_back_references_display
            slides_text = ', '.join(map(str, display_slides))
            back_ref = f"{slides_text} +{remaining} more"
        else:
            back_ref = ', '.join(map(str, slide_numbers))

        return self.back_reference_format.format(slides=back_ref)


class BibliographyItem:
    """Represents a single bibliography item."""

    def __init__(self, citation_key: str, content: str, raw_text: str):
        self.citation_key = citation_key
        self.content = content.strip()
        self.raw_text = raw_text
        self.slide_references = []  # List of slide numbers where cited

    def add_slide_reference(self, slide_num: int):
        """Add a slide reference if not already present."""
        if slide_num not in self.slide_references:
            self.slide_references.append(slide_num)


    def to_latex(self, config) -> str:
        """Convert to LaTeX with clickable back-references."""
        if self.slide_references and config.enable_back_references:
            # Create clickable hyperlinks
            clickable_links = [f"\\hyperlink{{page.{num}}}{{{num}}}" for num in self.slide_references]

            if len(clickable_links) > config.max_back_references_display:
                display_links = clickable_links[:config.max_back_references_display]
                remaining = len(clickable_links) - config.max_back_references_display
                links_text = ', '.join(display_links)
                back_ref = f"{links_text} +{remaining} more"
            else:
                back_ref = ', '.join(clickable_links)

            back_ref_text = f" \\hfill\\textcolor{{gray}}{{\\tiny [Cited on slides: {back_ref}]}}"

            if self.raw_text.endswith('\n'):
                return self.raw_text.rstrip() + back_ref_text + '\n'
            else:
                return self.raw_text.rstrip() + back_ref_text
        return self.raw_text


class BibliographyParser:
    """Parser for extracting bibliography items from LaTeX content."""

    @staticmethod
    def parse_bibliography(content_lines: list) -> dict:
        """
        Parse bibliography content into structured items.

        Args:
            content_lines: List of LaTeX content lines

        Returns:
            Dictionary with keys: 'header', 'items', 'footer'
        """
        import re

        result = {
            'header': None,
            'items': [],
            'footer': None,
            'raw_content': '\n'.join(content_lines)
        }

        full_content = '\n'.join(content_lines)

        # Extract header
        header_match = re.search(
            r'(\\begin\{thebibliography\}(?:\[[^\]]*\])?\{[^}]+\})',
            full_content
        )
        if header_match:
            result['header'] = header_match.group(1)
        else:
            result['header'] = "\\begin{thebibliography}{99}"

        # Extract footer
        footer_match = re.search(r'(\\end\{thebibliography\})', full_content)
        if footer_match:
            result['footer'] = footer_match.group(1)
        else:
            result['footer'] = "\\end{thebibliography}"

        # Extract individual bibitems
        # Pattern: \bibitem{key} content until next \bibitem or \end{thebibliography}
        pattern = r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem\{|\\end\{thebibliography\})'
        matches = re.findall(pattern, full_content, re.DOTALL)

        for key, content in matches:
            # Clean up the content
            content = content.strip()
            # Construct raw text
            raw_text = f"\\bibitem{{{key}}} {content}"

            item = BibliographyItem(key, content, raw_text)
            result['items'].append(item)

        return result

#--------------------------------------------------Dialogs -------------------------
class InstitutionNameDialog(ctk.CTkToplevel):
    """Dialog for handling long institution names"""
    def __init__(self, parent, institution_name):
        super().__init__(parent)
        self.title("Institution Name Warning")
        self.geometry("500x250")
        self.short_name = None

        # Center dialog
        self.transient(parent)
        self.grab_set()

        # Create widgets
        ctk.CTkLabel(self, text="Long Institution Name Detected",
                    font=("Arial", 14, "bold")).pack(pady=10)

        ctk.CTkLabel(self, text=f"Current name:\n{institution_name}",
                    wraplength=450).pack(pady=10)

        ctk.CTkLabel(self, text="Please provide a shorter version for slide footers:").pack(pady=5)

        self.entry = ctk.CTkEntry(self, width=300)
        self.entry.pack(pady=10)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="Use Short Name",
                     command=self.use_short_name).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Keep Original",
                     command=self.keep_original).pack(side="left", padx=10)

    def use_short_name(self):
        self.short_name = self.entry.get()
        self.destroy()

    def keep_original(self):
        self.destroy()

class MediaSelectionDialog(ctk.CTkToplevel):
    """Dialog for selecting media when URL fails"""
    def __init__(self, parent, title, content):
        super().__init__(parent)
        self.title("Media Selection")
        self.geometry("600x400")
        self.result = None

        # Center dialog
        self.transient(parent)
        self.grab_set()

        # Create widgets
        ctk.CTkLabel(self, text="Media Selection Required",
                    font=("Arial", 14, "bold")).pack(pady=10)

        # Show search query
        search_query = construct_search_query(title, content)
        query_frame = ctk.CTkFrame(self)
        query_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(query_frame, text=f"Search query: {search_query}",
                    wraplength=550).pack(side="left", pady=5)

        ctk.CTkButton(query_frame, text="Open Search",
                     command=lambda: open_google_image_search(search_query)).pack(side="right", padx=5)

        # Options
        options_frame = ctk.CTkFrame(self)
        options_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # URL Entry
        url_frame = ctk.CTkFrame(options_frame)
        url_frame.pack(fill="x", pady=5)
        self.url_entry = ctk.CTkEntry(url_frame, width=400)
        self.url_entry.pack(side="left", padx=5)
        ctk.CTkButton(url_frame, text="Use URL",
                     command=self.use_url).pack(side="left", padx=5)

        # File Selection
        file_frame = ctk.CTkFrame(options_frame)
        file_frame.pack(fill="x", pady=5)
        self.file_listbox = ctk.CTkTextbox(file_frame, height=150)
        self.file_listbox.pack(fill="x", pady=5)

        # Populate file list
        try:
            files = os.listdir('media_files')
            for i, file in enumerate(files, 1):
                self.file_listbox.insert('end', f"{i}. {file}\n")
        except Exception as e:
            self.file_listbox.insert('end', f"Error accessing media_files: {str(e)}")

        ctk.CTkButton(file_frame, text="Use Selected File",
                     command=self.use_file).pack(pady=5)

        # No Media Option
        ctk.CTkButton(options_frame, text="Create Slide Without Media",
                     command=self.use_none).pack(pady=10)

    def use_url(self):
        url = self.url_entry.get().strip()
        if url:
            self.result = url
            self.destroy()

    def use_file(self):
        # Get selected line
        try:
            selection = self.file_listbox.get("sel.first", "sel.last")
            if selection:
                file_name = selection.split('.', 1)[1].strip()
                self.result = f"\\file media_files/{file_name}"
                self.destroy()
        except:
            messagebox.showwarning("Selection Required",
                                 "Please select a file from the list")

    def use_none(self):
        self.result = "\\None"
        self.destroy()

#------------------------------------------------------------------------------------------
class NotesToolbar(ctk.CTkFrame):
    """Toolbar for notes formatting and templates"""
    def __init__(self, parent, notes_editor, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.notes_editor = notes_editor

        # Initialize dynamic toolbar
        self.dynamic_toolbar = None

        # Templates (PRESERVED)
        self.templates = {
            "Key Points": "• Key points:\n  - \n  - \n  - \n",
            "Time Markers": "• Timing guide:\n  0:00 - Introduction\n  0:00 - Main points\n  0:00 - Conclusion",
            "Questions": "• Potential questions:\nQ1: \nA1: \n\nQ2: \nA2: ",
            "References": "• Additional references:\n  - Title:\n    Author:\n    Page: ",
            "Technical Details": "• Technical details:\n  - Specifications:\n  - Parameters:\n  - Requirements:",
        }

        self.create_toolbar()

    def create_toolbar(self):
        """Create the notes toolbar with dynamic layout - ALL FEATURES PRESERVED"""

        # Initialize dynamic toolbar for this frame
        self.dynamic_toolbar = DynamicToolbar(self)

        # ========== TEMPLATE DROPDOWN (Priority: 100 - Highest) ==========
        template_frame = ctk.CTkFrame(self)

        ctk.CTkLabel(template_frame, text="Template:").pack(side="left", padx=2)

        self.template_var = tk.StringVar(value="Select Template")
        template_menu = ctk.CTkOptionMenu(
            template_frame,
            values=list(self.templates.keys()),
            variable=self.template_var,
            command=self.insert_template,
            width=150
        )
        template_menu.pack(side="left", padx=2)

        # Add template frame to dynamic toolbar
        self.dynamic_toolbar.add_frame(template_frame, priority=100, pack_kwargs={'side': 'left', 'padx': 5, 'pady': 2})

        # ========== SEPARATOR (Priority: 90) ==========
        separator = ttk.Separator(self, orient="vertical")
        self.dynamic_toolbar.add_button(separator, priority=90, pack_kwargs={'side': 'left', 'padx': 5, 'fill': 'y', 'pady': 2})

        # ========== FORMATTING BUTTONS (Priority: 80) ==========
        formatting_frame = ctk.CTkFrame(self)

        # ALL formatting buttons preserved exactly as in original
        formatting_buttons = [
            ("B", self.add_bold, "Bold"),
            ("I", self.add_italic, "Italic"),
            ("C", self.add_color, "Color"),
            ("⚡", self.add_highlight, "Highlight"),
            ("•", self.add_bullet, "Bullet point"),
            ("⏱", self.add_timestamp, "Timestamp"),
            ("⚠", self.add_alert, "Alert"),
            ("💡", self.add_tip, "Tip")
        ]

        for text, command, tooltip in formatting_buttons:
            btn = ctk.CTkButton(
                formatting_frame,
                text=text,
                command=command,
                width=30,
                height=30
            )
            btn.pack(side="left", padx=2)
            self.create_tooltip(btn, tooltip)  # Tooltips preserved

        # Add formatting frame to dynamic toolbar
        self.dynamic_toolbar.add_frame(formatting_frame, priority=80, pack_kwargs={'side': 'left', 'padx': 5, 'pady': 2})

        # ========== PACK ALL ITEMS DYNAMICALLY ==========
        self.dynamic_toolbar.pack_all()

        # Add resize handling for the parent window
        def on_parent_resize(event=None):
            if self.dynamic_toolbar and self.winfo_exists():
                self.dynamic_toolbar.update_layout()

        # Bind to parent's configure event
        if hasattr(self, 'master'):
            self.master.bind('<Configure>', on_parent_resize)

        # Also bind to this frame's configure event
        self.bind('<Configure>', on_parent_resize)

    # ========== ALL ORIGINAL METHODS PRESERVED BELOW ==========

    def create_tooltip(self, widget, text):
        """Create tooltip for buttons - PRESERVED"""
        def show_tooltip(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20

            # Create tooltip window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")

            label = tk.Label(self.tooltip, text=text,
                           justify='left',
                           background="#ffffe0", relief='solid', borderwidth=1)
            label.pack()

        def hide_tooltip(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()

        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    def insert_template(self, choice):
        """Insert selected template - PRESERVED"""
        if choice in self.templates:
            self.notes_editor.insert('insert', self.templates[choice])
            self.template_var.set("Select Template")  # Reset dropdown

    def add_bold(self):
        """Add bold text - PRESERVED"""
        self.wrap_selection(r'\textbf{', '}')

    def add_italic(self):
        """Add italic text - PRESERVED"""
        self.wrap_selection(r'\textit{', '}')

    def add_color(self):
        """Add colored text - PRESERVED"""
        colors = ['red', 'blue', 'green', 'orange', 'purple']
        color = simpledialog.askstring(
            "Color",
            "Enter color name or RGB values:",
            initialvalue=colors[0]
        )
        if color:
            self.wrap_selection(f'\\textcolor{{{color}}}{{', '}')

    def add_highlight(self):
        """Add highlighted text - PRESERVED"""
        self.wrap_selection('\\hl{', '}')

    def add_bullet(self):
        """Add bullet point - PRESERVED"""
        self.notes_editor.insert('insert', '\n• ')

    def add_timestamp(self):
        """Add timestamp - PRESERVED"""
        timestamp = simpledialog.askstring(
            "Timestamp",
            "Enter timestamp (MM:SS):",
            initialvalue="00:00"
        )
        if timestamp:
            self.notes_editor.insert('insert', f'[{timestamp}] ')

    def add_alert(self):
        """Add alert note - PRESERVED"""
        self.notes_editor.insert('insert', '⚠ Important: ')

    def add_tip(self):
        """Add tip - PRESERVED"""
        self.notes_editor.insert('insert', '💡 Tip: ')

    def wrap_selection(self, prefix, suffix):
        """Wrap selected text with prefix and suffix - PRESERVED"""
        try:
            selection = self.notes_editor.get('sel.first', 'sel.last')
            self.notes_editor.delete('sel.first', 'sel.last')
            self.notes_editor.insert('insert', f'{prefix}{selection}{suffix}')
        except tk.TclError:  # No selection
            self.notes_editor.insert('insert', f'{prefix}{suffix}')
            # Move cursor inside braces
            current_pos = self.notes_editor.index('insert')
            self.notes_editor.mark_set('insert', f'{current_pos}-{len(suffix)}c')

class EnhancedNotesEditor(ctk.CTkFrame):
    """Enhanced notes editor with toolbar and templates"""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Create toolbar
        self.toolbar = NotesToolbar(self, self.notes_editor)
        self.toolbar.pack(fill="x", padx=2, pady=2)

        # Create editor
        self.notes_editor = ctk.CTkTextbox(self)
        self.notes_editor.pack(fill="both", expand=True, padx=2, pady=2)

        # Enhanced syntax highlighting
        self.setup_syntax_highlighting()

    def setup_syntax_highlighting(self):
        """Setup enhanced syntax highlighting for notes"""
        self.highlighter = BeamerSyntaxHighlighter(self.notes_editor)

        # Add additional patterns for notes
        additional_patterns = [
            (r'⚠.*$', 'alert'),
            (r'💡.*$', 'tip'),
            (r'\[[\d:]+\]', 'timestamp'),
            (r'•.*$', 'bullet'),
            (r'\\hl\{.*?\}', 'highlight'),
        ]

        # Add additional colors
        additional_colors = {
            'alert': '#FF6B6B',
            'tip': '#4ECDC4',
            'timestamp': '#FFB86C',
            'highlight': '#BD93F9',
        }

        # Update highlighter
        self.highlighter.patterns.extend(additional_patterns)
        self.highlighter.colors.update(additional_colors)

#------------------------------------------------------------------------------------------
class FileThumbnailBrowser(ctk.CTkToplevel):
    def __init__(self, parent, initial_dir="media_files", callback=None):
        super().__init__(parent)

        # Import required modules
        try:
            from PIL import Image, ImageDraw, ImageFont
            self.Image = Image
            self.ImageDraw = ImageDraw
            self.ImageFont = ImageFont
            self.has_pil = True
        except ImportError as e:
            print(f"Error importing PIL modules: {e}")
            self.has_pil = False
            messagebox.showwarning("Warning",
                                 "Image processing libraries not available.\nThumbnails will be limited.")

        self.title("Media Browser")
        self.geometry("800x600")

        # Store initial directory and callback
        self.current_dir = os.path.abspath(initial_dir)
        self.callback = callback
        self.thumbnails = []
        self.current_row = 0
        self.current_col = 0
        self.max_cols = 4

        # Create media_files directory if it doesn't exist
        os.makedirs(initial_dir, exist_ok=True)

        # File categories with extended video types
        self.file_categories = {
            'image': ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'),
            'video': ('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.gif'),
            'audio': ('.mp3', '.wav', '.ogg', '.m4a', '.flac'),
            'document': ('.pdf', '.doc', '.docx', '.txt', '.tex'),
            'data': ('.csv', '.xlsx', '.json', '.xml')
        }

        # Create UI components
        self.create_navigation_bar()
        self.create_toolbar()
        self.create_content_area()
        self.load_files()
        # Add destruction handler
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Destroy>", self._on_destroy)

    def _on_close(self):
        """Handle window closing"""
        self._cleanup_bindings()
        self.destroy()

    def _on_destroy(self, event):
        """Handle widget destruction"""
        if event.widget == self:
            self._cleanup_bindings()

    def _cleanup_bindings(self):
        """Clean up all global bindings"""
        try:
            # Unbind all global mouse wheel events
            self.unbind_all("<MouseWheel>")
            if sys.platform.startswith('linux'):
                self.unbind_all("<Button-4>")
                self.unbind_all("<Button-5>")
        except:
            pass  # Ignore errors during cleanup

    def _bind_mousewheel(self, event):
        """Bind mousewheel when mouse enters canvas - with safety check"""
        if not self.winfo_exists():  # Check if widget still exists
            return

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        if sys.platform.startswith('linux'):
            self.canvas.bind_all("<Button-4>", self._on_mousewheel)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """Handle mouse wheel and touchpad scrolling with safety check"""
        if not self.winfo_exists() or not self.canvas.winfo_exists():
            return  # Don't process if widgets are destroyed


    def create_thumbnail(self, file_path):
        """Create thumbnail with proper error handling"""
        if not self.has_pil:
            return self.create_fallback_thumbnail()

        try:
            category = self.get_file_category(file_path)
            thumb_size = (150, 150)

            if category == 'image':
                try:
                    with self.Image.open(file_path) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')

                        # Create thumbnail
                        img.thumbnail(thumb_size, self.Image.Resampling.LANCZOS)

                        # Create background
                        thumb_bg = self.Image.new('RGB', thumb_size, 'black')

                        # Center image on background
                        offset = ((thumb_size[0] - img.size[0]) // 2,
                                (thumb_size[1] - img.size[1]) // 2)
                        thumb_bg.paste(img, offset)

                        return ctk.CTkImage(light_image=thumb_bg,
                                          dark_image=thumb_bg,
                                          size=thumb_size)
                except Exception as e:
                    print(f"Error creating image thumbnail: {str(e)}")
                    return self.create_generic_thumbnail("Image\nError", "#8B0000")

            else:
                # Create appropriate generic thumbnail based on category
                colors = {
                    'video': "#4a90e2",
                    'audio': "#e24a90",
                    'document': "#90e24a",
                    'data': "#4ae290"
                }
                color = colors.get(category, "#808080")
                text = category.upper() if category else "FILE"
                return self.create_generic_thumbnail(text, color)

        except Exception as e:
            print(f"Error creating thumbnail for {file_path}: {str(e)}")
            return self.create_fallback_thumbnail()

    def create_generic_thumbnail(self, text, color):
        """Create generic thumbnail with text"""
        if not self.has_pil:
            return self.create_fallback_thumbnail()

        try:
            thumb_size = (150, 150)
            img = self.Image.new('RGB', thumb_size, 'black')
            draw = self.ImageDraw.Draw(img)

            # Draw colored rectangle
            margin = 20
            draw.rectangle(
                [margin, margin, thumb_size[0]-margin, thumb_size[1]-margin],
                fill=color
            )

            # Draw text
            text_bbox = draw.textbbox((0, 0), text)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            text_x = (thumb_size[0] - text_width) // 2
            text_y = (thumb_size[1] - text_height) // 2

            draw.text((text_x, text_y), text, fill="white")

            return ctk.CTkImage(light_image=img,
                              dark_image=img,
                              size=thumb_size)
        except Exception as e:
            print(f"Error creating generic thumbnail: {str(e)}")
            return self.create_fallback_thumbnail()

    def create_fallback_thumbnail(self):
        """Create a basic fallback thumbnail when PIL is not available or errors occur"""
        try:
            img = self.Image.new('RGB', (150, 150), color='gray')
            return ctk.CTkImage(light_image=img,
                              dark_image=img,
                              size=(150, 150))
        except:
            # Create an empty CTkImage if all else fails
            return ctk.CTkImage(light_image=None,
                              dark_image=None,
                              size=(150, 150))

#-------------------------------------------------------------------------------------------
    def create_file_item(self, file_name):
        """Create file display item with proper error handling"""
        try:
            frame = ctk.CTkFrame(self.scrollable_frame)
            frame.grid(row=self.current_row, column=self.current_col,
                      padx=10, pady=10, sticky="nsew")

            file_path = os.path.join(self.current_dir, file_name)

            # Create thumbnail
            try:
                thumbnail = self.create_thumbnail(file_path)
            except Exception as e:
                print(f"Error creating thumbnail: {e}")
                thumbnail = self.create_generic_thumbnail("Error", "#8B0000")

            if thumbnail:
                # Create thumbnail button
                thumb_button = ctk.CTkButton(
                    frame,
                    image=thumbnail,
                    text="",
                    command=lambda path=file_path: self.on_file_click(path),
                    width=150,
                    height=150
                )
                thumb_button.pack(pady=(5, 0))

                # Add filename label
                label = ctk.CTkLabel(
                    frame,
                    text=file_name,
                    wraplength=140
                )
                label.pack(pady=(5, 5))

                # Store reference to thumbnail
                self.thumbnails.append(thumbnail)

            # Update grid position
            self.current_col += 1
            if self.current_col >= self.max_cols:
                self.current_col = 0
                self.current_row += 1

        except Exception as e:
            print(f"Error creating file item: {str(e)}")

    def on_file_click(self, file_path: str) -> None:
        """Handle file selection with proper path handling"""
        if self.callback:
            # Create relative path if file is in media_files directory
            try:
                relative_to_media = os.path.relpath(file_path, 'media_files')
                if relative_to_media.startswith('..'):
                    # File is outside media_files - use absolute path
                    final_path = file_path
                else:
                    # File is inside media_files - use relative path
                    final_path = os.path.join('media_files', relative_to_media)

                # Determine if file should be played
                ext = os.path.splitext(file_path)[1].lower()
                is_video = ext in self.file_categories['video']

                if is_video and hasattr(self, 'play_vars') and self.play_vars.get(file_path, tk.BooleanVar(value=True)).get():
                    self.callback(f"\\play \\file {final_path}")
                else:
                    self.callback(f"\\file {final_path}")

            except Exception as e:
                print(f"Error handling file selection: {str(e)}")
                return

        self.destroy()

    def create_navigation_bar(self):
        """Create navigation bar with path and controls"""
        nav_frame = ctk.CTkFrame(self)
        nav_frame.pack(fill="x", padx=5, pady=5)

        # Back button
        self.back_button = ctk.CTkButton(
            nav_frame,
            text="⬅ Back",
            command=self.navigate_up,
            width=60
        )
        self.back_button.pack(side="left", padx=5)

        # Path display and navigation
        self.path_var = tk.StringVar()
        self.path_entry = ctk.CTkEntry(
            nav_frame,
            textvariable=self.path_var,
            width=400
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.path_entry.bind('<Return>', self.navigate_to_path)

        # Update current path
        self.update_path_display()

    def create_toolbar(self):
        """Create toolbar with sorting and view options"""
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=5, pady=5)

        # Sorting options
        sort_label = ctk.CTkLabel(toolbar, text="Sort by:")
        sort_label.pack(side="left", padx=5)

        self.sort_var = tk.StringVar(value="name")
        sort_options = ["name", "date", "size", "type"]

        for option in sort_options:
            rb = ctk.CTkRadioButton(
                toolbar,
                text=option.capitalize(),
                variable=self.sort_var,
                value=option,
                command=self.refresh_files
            )
            rb.pack(side="left", padx=10)

        # Sort direction
        self.reverse_var = tk.BooleanVar(value=False)
        reverse_cb = ctk.CTkCheckBox(
            toolbar,
            text="Reverse",
            variable=self.reverse_var,
            command=self.refresh_files
        )
        reverse_cb.pack(side="left", padx=10)

    def create_content_area(self):
        """Create scrollable content area with enhanced navigation"""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create canvas with scrollbars
        self.canvas = tk.Canvas(self.main_frame, bg='black')
        self.v_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical")
        self.h_scrollbar = ttk.Scrollbar(self.main_frame, orient="horizontal")

        # Configure scrollbars
        self.v_scrollbar.config(command=self.canvas.yview)
        self.h_scrollbar.config(command=self.canvas.xview)
        self.canvas.config(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )

        # Pack scrollbars
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create frame for content
        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            tags="self.scrollable_frame"
        )

        # Configure scroll bindings
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Bind scroll events
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        # Touch pad/track pad scrolling
        if sys.platform == 'darwin':
            self.canvas.bind("<TouchpadScroll>", self._on_touchpad_scroll)
        else:
            self.canvas.bind("<Shift-MouseWheel>", self._on_touchpad_scroll)

    def _on_mousewheel(self, event):
        """Handle mouse wheel and touchpad scrolling"""
        if event.num == 4:  # Linux up
            delta = 120
        elif event.num == 5:  # Linux down
            delta = -120
        else:  # Windows/MacOS
            delta = event.delta

        shift_pressed = event.state & 0x1  # Check if Shift is pressed
        if shift_pressed:
            self.canvas.xview_scroll(int(-1 * delta/120), "units")
        else:
            self.canvas.yview_scroll(int(-1 * delta/120), "units")

    def _on_touchpad_scroll(self, event):
        """Handle touchpad scrolling"""
        if event.state & 0x1:  # Shift pressed - horizontal scroll
            self.canvas.xview_scroll(int(-1 * event.delta/30), "units")
        else:  # Vertical scroll
            self.canvas.yview_scroll(int(-1 * event.delta/30), "units")

    def _bind_mousewheel(self, event):
        """Bind mousewheel when mouse enters canvas"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        if sys.platform.startswith('linux'):
            self.canvas.bind_all("<Button-4>", self._on_mousewheel)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel when mouse leaves canvas"""
        self.canvas.unbind_all("<MouseWheel>")
        if sys.platform.startswith('linux'):
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")

    def get_file_category(self, filename):
        """Determine file category and appropriate thumbnail style"""
        ext = os.path.splitext(filename)[1].lower()

        for category, extensions in self.file_categories.items():
            if ext in extensions:
                return category

        return 'other'


    def navigate_up(self):
        """Navigate to parent directory"""
        parent = os.path.dirname(self.current_dir)
        if os.path.exists(parent):
            self.current_dir = parent
            self.update_path_display()
            self.load_files()

    def navigate_to_path(self, event=None):
        """Navigate to entered path"""
        new_path = self.path_var.get()
        if os.path.exists(new_path):
            self.current_dir = os.path.abspath(new_path)
            self.update_path_display()
            self.load_files()
        else:
            messagebox.showerror("Error", "Invalid path")
            self.update_path_display()

    def update_path_display(self):
        """Update path display"""
        self.path_var.set(self.current_dir)

    def load_files(self):
        """Load files and folders with enhanced display"""
        # Clear existing display
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.thumbnails.clear()
        self.current_row = 0
        self.current_col = 0

        try:
            # Get directories and files
            entries = os.listdir(self.current_dir)
            folders = []
            files = []

            for entry in entries:
                full_path = os.path.join(self.current_dir, entry)
                if os.path.isdir(full_path):
                    folders.append(entry)
                else:
                    files.append(entry)

            # Sort folders and files separately
            folders.sort()
            files = self.sort_files(files)

            # Display folders first
            for folder in folders:
                self.create_folder_item(folder)

            # Then display files
            for file in files:
                self.create_file_item(file)

        except Exception as e:
            messagebox.showerror("Error", f"Error loading directory: {str(e)}")

    def create_folder_item(self, folder_name):
        """Create folder display item"""
        frame = ctk.CTkFrame(self.scrollable_frame)
        frame.grid(row=self.current_row, column=self.current_col,
                  padx=10, pady=10, sticky="nsew")

        # Create folder button with icon
        folder_button = ctk.CTkButton(
            frame,
            text="📁",
            command=lambda f=folder_name: self.enter_folder(f),
            width=150,
            height=150
        )
        folder_button.pack(pady=(5, 0))

        # Add folder name label
        label = ctk.CTkLabel(
            frame,
            text=folder_name,
            wraplength=140
        )
        label.pack(pady=(5, 5))

        # Update grid position
        self.current_col += 1
        if self.current_col >= self.max_cols:
            self.current_col = 0
            self.current_row += 1


    def enter_folder(self, folder_name):
        """Enter selected folder"""
        new_path = os.path.join(self.current_dir, folder_name)
        if os.path.exists(new_path):
            self.current_dir = new_path
            self.update_path_display()
            self.load_files()

    def sort_files(self, files):
        """Sort files based on current criteria"""
        sort_key = self.sort_var.get()
        reverse = self.reverse_var.get()

        return sorted(
            files,
            key=lambda f: self.get_file_info(os.path.join(self.current_dir, f))[sort_key],
            reverse=reverse
        )

    def get_file_info(self, file_path):
        """Get file information for sorting"""
        stat = os.stat(file_path)
        return {
            'name': os.path.basename(file_path).lower(),
            'date': stat.st_mtime,
            'size': stat.st_size,
            'type': os.path.splitext(file_path)[1].lower()
        }

    def refresh_files(self):
        """Refresh file display with current sort settings"""
        self.load_files()

    def format_file_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

class TikZColorHelper:
    """Helper class for managing TikZ colors with automatic text color selection"""

    def __init__(self):
        self.color_definitions = {}
        self.default_colors = {
            'airis4d_blue': (41, 128, 185),
            'airis4d_green': (39, 174, 96),
            'airis4d_orange': (243, 156, 18),
            'airis4d_red': (231, 76, 60),
            'airis4d_purple': (155, 89, 182),
            'airis4d_teal': (26, 188, 156),
            'airis4d_gray': (149, 165, 166)
        }

    def define_color(self, name, color_value):
        """Define a custom color for TikZ"""
        self.color_definitions[name] = color_value

    def get_text_color(self, background_color_name):
        """Get optimal text color for a given background color"""
        if background_color_name in self.color_definitions:
            color_value = self.color_definitions[background_color_name]
        elif background_color_name in self.default_colors:
            color_value = self.default_colors[background_color_name]
        else:
            # Try to parse the color
            color_value = background_color_name

        return get_xor_text_color(color_value)

    def generate_tikz_color_definitions(self):
        """Generate TikZ color definition commands"""
        definitions = []

        # Add default colors
        for name, rgb in self.default_colors.items():
            definitions.append(f"\\definecolor{{{name}}}{{RGB}}{{{rgb[0]},{rgb[1]},{rgb[2]}}}")

        # Add custom colors
        for name, color_value in self.color_definitions.items():
            if isinstance(color_value, tuple) and len(color_value) == 3:
                # RGB tuple
                definitions.append(f"\\definecolor{{{name}}}{{RGB}}{{{color_value[0]},{color_value[1]},{color_value[2]}}}")
            elif isinstance(color_value, str):
                # Color name or hex
                definitions.append(f"\\definecolor{{{name}}}{{HTML}}{{{color_value.lstrip('#')}}}")

        return "\n".join(definitions)

    def create_colored_node(self, text, background_color, node_options=""):
        """Create a TikZ node with automatic text color"""
        text_color = self.get_text_color(background_color)

        tikz_code = f"""
\\node[{node_options}, fill={background_color}, text={text_color}] {{{text}}};
"""
        return tikz_code.strip()

class ColorPickerDialog(ctk.CTkToplevel):
    """Dialog for selecting colors with preview and XOR text color feedback"""

    def __init__(self, parent, current_color=None):
        super().__init__(parent)
        self.title("TikZ Color Picker")
        self.geometry("500x400")
        self.result = None

        # Initialize color helper
        self.color_helper = TikZColorHelper()

        # Center dialog
        self.transient(parent)
        self.grab_set()

        # Create UI
        self.create_widgets(current_color)

    def create_widgets(self, current_color):
        """Create color picker widgets"""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Color selection frame
        color_frame = ctk.CTkFrame(main_frame)
        color_frame.pack(fill="x", padx=5, pady=5)

        # Color name entry
        ctk.CTkLabel(color_frame, text="Color Name:").pack(side="left", padx=5)
        self.color_name_entry = ctk.CTkEntry(color_frame, width=150)
        self.color_name_entry.pack(side="left", padx=5)
        self.color_name_entry.insert(0, "custom_color")

        # RGB inputs
        rgb_frame = ctk.CTkFrame(main_frame)
        rgb_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(rgb_frame, text="R:").pack(side="left", padx=5)
        self.r_entry = ctk.CTkEntry(rgb_frame, width=50)
        self.r_entry.pack(side="left", padx=5)
        self.r_entry.insert(0, "128")

        ctk.CTkLabel(rgb_frame, text="G:").pack(side="left", padx=5)
        self.g_entry = ctk.CTkEntry(rgb_frame, width=50)
        self.g_entry.pack(side="left", padx=5)
        self.g_entry.insert(0, "128")

        ctk.CTkLabel(rgb_frame, text="B:").pack(side="left", padx=5)
        self.b_entry = ctk.CTkEntry(rgb_frame, width=50)
        self.b_entry.pack(side="left", padx=5)
        self.b_entry.insert(0, "128")

        # Preview frame
        preview_frame = ctk.CTkFrame(main_frame, height=100)
        preview_frame.pack(fill="x", padx=5, pady=10)
        preview_frame.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="Sample Text",
            font=("Arial", 16, "bold"),
            width=400,
            height=80,
            corner_radius=10
        )
        self.preview_label.pack(pady=10)

        # Text color feedback
        feedback_frame = ctk.CTkFrame(main_frame)
        feedback_frame.pack(fill="x", padx=5, pady=5)

        self.feedback_label = ctk.CTkLabel(
            feedback_frame,
            text="Recommended text color: ",
            font=("Arial", 12)
        )
        self.feedback_label.pack()

        # Color buttons for quick selection
        colors_frame = ctk.CTkFrame(main_frame)
        colors_frame.pack(fill="x", padx=5, pady=10)

        ctk.CTkLabel(colors_frame, text="Quick Colors:").pack(anchor="w", padx=5, pady=5)

        quick_colors = [
            ("Blue", "airis4d_blue", "#2980b9"),
            ("Green", "airis4d_green", "#27ae60"),
            ("Orange", "airis4d_orange", "#f39c12"),
            ("Red", "airis4d_red", "#e74c3c"),
            ("Purple", "airis4d_purple", "#9b59b6"),
            ("Teal", "airis4d_teal", "#1abc9c"),
            ("Gray", "airis4d_gray", "#95a5a6")
        ]

        buttons_frame = ctk.CTkFrame(colors_frame)
        buttons_frame.pack(fill="x", padx=5, pady=5)

        for color_name, color_id, hex_color in quick_colors:
            btn = ctk.CTkButton(
                buttons_frame,
                text=color_name,
                command=lambda c=color_id, h=hex_color: self.select_quick_color(c, h),
                width=80,
                fg_color=hex_color,
                hover_color=hex_color
            )
            btn.pack(side="left", padx=2, pady=2)

        # Action buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=5, pady=10)

        ctk.CTkButton(
            button_frame,
            text="Update Preview",
            command=self.update_preview
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Apply",
            command=self.apply_color
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel
        ).pack(side="right", padx=5)

        # Set initial color if provided
        if current_color:
            self.update_preview()

    def select_quick_color(self, color_id, hex_color):
        """Select a quick color"""
        self.color_name_entry.delete(0, 'end')
        self.color_name_entry.insert(0, color_id)

        # Parse hex to RGB
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        self.r_entry.delete(0, 'end')
        self.r_entry.insert(0, str(r))

        self.g_entry.delete(0, 'end')
        self.g_entry.insert(0, str(g))

        self.b_entry.delete(0, 'end')
        self.b_entry.insert(0, str(b))

        self.update_preview()

    def update_preview(self):
        """Update color preview"""
        try:
            r = int(self.r_entry.get())
            g = int(self.g_entry.get())
            b = int(self.b_entry.get())

            # Ensure values are in range
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            hex_color = f"#{r:02x}{g:02x}{b:02x}"

            # Update preview label
            self.preview_label.configure(fg_color=hex_color)

            # Calculate and show recommended text color
            text_color = get_xor_text_color((r, g, b))
            self.feedback_label.configure(
                text=f"Recommended text color: {text_color.upper()} (XOR rule)",
                text_color="white" if text_color == "white" else "black"
            )

        except ValueError:
            # Invalid input, use default
            self.preview_label.configure(fg_color="gray")
            self.feedback_label.configure(
                text="Invalid RGB values",
                text_color="red"
            )

    def apply_color(self):
        """Apply selected color"""
        try:
            color_name = self.color_name_entry.get().strip()
            r = int(self.r_entry.get())
            g = int(self.g_entry.get())
            b = int(self.b_entry.get())

            self.result = {
                'name': color_name,
                'rgb': (r, g, b),
                'hex': f"#{r:02x}{g:02x}{b:02x}",
                'text_color': get_xor_text_color((r, g, b))
            }
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid color values")

    def cancel(self):
        """Cancel color selection"""
        self.result = None
        self.destroy()

    @staticmethod
    def pick_color(parent, current_color=None):
        """Static method to pick color"""
        dialog = ColorPickerDialog(parent, current_color)
        dialog.wait_window()
        return dialog.result

#------------------------------------------------------------------------------------------
class PreambleEditor(ctk.CTkToplevel):
    def __init__(self, parent, current_preamble=None):
        super().__init__(parent)
        self.title("Preamble Editor")
        self.geometry("800x600")

        # Store the default preamble
        self.default_preamble = get_beamer_preamble(
            "Title", "Subtitle", "Author", "Institution", "Short Inst", "\\today"
        )

        # Create UI
        self.create_editor()
        self.create_toolbar()

        # Load current preamble if provided, else load default
        if current_preamble:
            self.editor.delete('1.0', 'end')
            self.editor.insert('1.0', current_preamble)
        else:
            self.reset_to_default()

    def create_editor(self):
        """Create the preamble text editor"""
        # Editor frame
        editor_frame = ctk.CTkFrame(self)
        editor_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Editor with syntax highlighting
        self.editor = ctk.CTkTextbox(
            editor_frame,
            wrap="none",
            font=("Courier", 12)
        )
        self.editor.pack(fill="both", expand=True, padx=5, pady=5)

        # Add syntax highlighting
        self.syntax_highlighter = BeamerSyntaxHighlighter(self.editor)

    def create_toolbar(self):
        """Create toolbar with editor controls"""
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=10, pady=5)

        # Create buttons
        buttons = [
            ("Reset to Default", self.reset_to_default),
            ("Save Custom", self.save_custom),
            ("Load Custom", self.load_custom),
            ("Apply", self.apply_changes),
            ("Cancel", self.cancel_changes)
        ]

        for text, command in buttons:
            ctk.CTkButton(
                toolbar,
                text=text,
                command=command,
                width=100
            ).pack(side="left", padx=5)

    def reset_to_default(self):
        """Reset preamble to default"""
        if messagebox.askyesno("Reset Preamble",
                             "Are you sure you want to reset to default preamble?"):
            self.editor.delete('1.0', 'end')
            self.editor.insert('1.0', self.default_preamble)
            self.syntax_highlighter.highlight()

    def save_custom(self):
        """Save current preamble as custom template"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".tex",
            filetypes=[("TeX files", "*.tex"), ("All files", "*.*")],
            title="Save Custom Preamble"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.editor.get('1.0', 'end-1c'))
                messagebox.showinfo("Success", "Custom preamble saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving preamble: {str(e)}")

    def load_custom(self):
        """Load custom preamble template"""
        file_path = filedialog.askopenfilename(
            filetypes=[("TeX files", "*.tex"), ("All files", "*.*")],
            title="Load Custom Preamble"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.editor.delete('1.0', 'end')
                    self.editor.insert('1.0', content)
                    self.syntax_highlighter.highlight()
            except Exception as e:
                messagebox.showerror("Error", f"Error loading preamble: {str(e)}")

    def apply_changes(self):
        """Apply preamble changes and close editor"""
        self.preamble = self.editor.get('1.0', 'end-1c')
        self.destroy()

    def cancel_changes(self):
        """Cancel changes and close editor"""
        self.preamble = None
        self.destroy()

    @staticmethod
    def edit_preamble(parent, current_preamble=None):
        """Static method to handle preamble editing"""
        editor = PreambleEditor(parent, current_preamble)
        editor.wait_window()
        return editor.preamble if hasattr(editor, 'preamble') else None
#------------------------------------------------------------------------------------------
class NotesToggleFrame(ctk.CTkFrame):
    """Frame containing notes display options with tooltips"""
    def __init__(self, parent, main_editor, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Store reference to main editor
        self.main_editor = main_editor

        # Notes mode variable
        self.notes_mode = tk.StringVar(value="both")

        # Create radio buttons for different notes modes
        modes = [
            ("PDF Only", "slides", "Hide all presentation notes"),
            ("Notes Only", "notes", "Show only presentation notes"),
            ("PDF with Notes", "both", "Show PDF with notes on second screen")
        ]

        # Create label
        label = ctk.CTkLabel(self, text="Notes Display:", anchor="w")
        label.pack(side="left", padx=5)
        self.create_tooltip(label, "Select how notes should appear in the final output")

        # Create radio buttons
        for text, value, tooltip in modes:
            btn = ctk.CTkRadioButton(
                self,
                text=text,
                variable=self.notes_mode,
                value=value
            )
            btn.pack(side="left", padx=10)
            self.create_tooltip(btn, tooltip)

    def get_notes_directive(self) -> str:
        """Return the appropriate beamer directive based on current mode"""
        mode = self.notes_mode.get()
        if mode == "slides":
            return "\\setbeameroption{hide notes}"
        elif mode == "notes":
            return "\\setbeameroption{show only notes}"
        else:  # both
            return "\\setbeameroption{show notes on second screen=right}"


class TerminalIO:
    """Improved terminal I/O handler for BSG-IDE integration"""
    def __init__(self, editor):
        self.editor = editor

    def write(self, text, color="white"):
        """Write to terminal with color"""
        if hasattr(self.editor, 'terminal'):
            self.editor.terminal.write(text, color)

    def terminal_input(self, prompt):
        """Get input from terminal with proper synchronization"""
        if hasattr(self.editor, 'terminal'):
            # Use the terminal's input method directly
            text = self.editor.terminal.terminal_input(prompt)
            # Write back the input for visual feedback
            self.editor.terminal.write(text + "\n", "green")
            return text
        else:
            # Fallback to standard input
            text = input(prompt)
            return text


class InstallationDialog(ctk.CTkToplevel):
    """Installation progress dialog with visual feedback"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("BSG-IDE Installation")
        self.geometry("400x300")

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Center dialog
        self.center_window()

        # Progress elements
        self.status_label = ctk.CTkLabel(self, text="Preparing installation...")
        self.status_label.pack(pady=20)

        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(pady=10, padx=20, fill="x")
        self.progress.set(0)

        self.detail_text = ctk.CTkTextbox(self, height=150)
        self.detail_text.pack(pady=10, padx=20, fill="both", expand=True)

    def center_window(self):
        """Center dialog on parent window"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def update_progress(self, value: float, message: str):
        """Update progress bar and status message"""
        self.progress.set(value)
        self.status_label.configure(text=message)
        self.detail_text.insert('end', f"{message}\n")
        self.detail_text.see('end')
        self.update()

    def write(self, message: str, color: str = None):
        """Write message to detail text with optional color"""
        if color:
            tag = f"color_{color}"
            self.detail_text.tag_configure(tag, foreground=color)
            self.detail_text.insert('end', message + "\n", tag)
        else:
            self.detail_text.insert('end', message + "\n")
        self.detail_text.see('end')
        self.update()

class InstallationManager:
    """Enhanced installation manager with GUI feedback"""
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
        self.system = platform.system()
        # Set is_admin attribute first
        self.is_admin = False  # Default value
        try:
            if self.system == "Windows":
                import ctypes
                self.is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
            else:
                self.is_admin = os.geteuid() == 0
        except Exception as e:
            print(f"Warning: Could not determine admin status: {e}")
            self.is_admin = False

        # Now get installation paths after is_admin is set
        self.install_paths = self._get_install_paths()

    def install(self):
        """Start installation process with GUI feedback"""
        try:
            self.dialog = InstallationDialog(self.parent)

            # Verify Python environment
            self.dialog.update_progress(0.1, "Checking Python environment...")
            self._verify_python_env()

            # Create installation directories
            self.dialog.update_progress(0.2, "Creating directories...")
            self._create_directories()

            # Copy files
            self.dialog.update_progress(0.4, "Copying required files...")
            self._copy_files()

            # Create launcher
            if not self.create_launcher():
                return False

            # Setup OS integration
            self.dialog.update_progress(0.6, "Setting up system integration...")
            self._setup_os_integration()

            # Install dependencies
            self.dialog.update_progress(0.8, "Installing dependencies...")
            self._install_dependencies()

            # Final checks
            self.dialog.update_progress(0.9, "Performing final checks...")
            self._verify_installation()

            # Complete
            self.dialog.update_progress(1.0, "Installation completed successfully!")
            self.dialog.write("✓ BSG-IDE installation completed!", "green")

            # Close dialog after delay
            self.dialog.after(2000, self.dialog.destroy)
            return True


        except Exception as e:
            if self.dialog:
                self.dialog.write(f"✗ Installation failed: {str(e)}", "red")
                self.dialog.write("\nDetails:", "red")
                self.dialog.write(traceback.format_exc(), "red")
                # Keep dialog open for error review
            return False

    def create_launcher(self):
        """Create platform-specific launcher scripts and shortcuts"""
        try:
            if self.system == "Linux":
                return self._create_linux_launcher()
            elif self.system == "Windows":
                return self._create_windows_launcher()
            else:  # macOS
                return self._create_macos_launcher()
        except Exception as e:
            if self.dialog:
                self.dialog.write(f"✗ Error creating launcher: {str(e)}", "red")
            else:
                print(f"✗ Error creating launcher: {str(e)}")
            return False

    def _create_linux_launcher(self):
        """Create Linux launcher script"""
        try:
            launcher_path = self.install_paths['bin'] / 'bsg-ide'
            launcher_content = f"""#!/usr/bin/env python3
    import sys
    import os
    from pathlib import Path

    # Add installation directory to Python path
    sys.path.insert(0, "{self.install_paths['base']}")

    # Import and run main program
    try:
        from BSG_IDE import main
        main()
    except Exception as e:
        print(f"Error starting BSG-IDE: {{str(e)}}")
        import traceback
        traceback.print_exc()
    """
            launcher_path.write_text(launcher_content)
            launcher_path.chmod(0o755)
            return True
        except Exception as e:
            print(f"Error creating launcher: {e}")
            return False

    def _create_windows_launcher(self):
        """Create Windows launcher script and shortcuts"""
        try:
            # Create batch file
            launcher_path = self.install_paths['bin'] / 'bsg-ide.bat'
            launcher_content = f"""@echo off
set PYTHONPATH={self.install_paths['base']};%PYTHONPATH%
python -c "from BSG_IDE import main; main()" %*
"""
            launcher_path.write_text(launcher_content)

            if self.dialog:
                self.dialog.write(f"✓ Created launcher script: {launcher_path}", "green")
            else:
                print(f"✓ Created launcher script: {launcher_path}")

            # Create Start Menu shortcut
            try:
                import winshell
                from win32com.client import Dispatch
                shortcut_dir = self.install_paths['start_menu'] / "BSG-IDE"
                shortcut_dir.mkdir(parents=True, exist_ok=True)

                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(str(shortcut_dir / "BSG-IDE.lnk"))
                shortcut.Targetpath = str(launcher_path)
                shortcut.save()

                if self.dialog:
                    self.dialog.write("✓ Created Start Menu shortcut", "green")
                else:
                    print("✓ Created Start Menu shortcut")
            except ImportError:
                if self.dialog:
                    self.dialog.write("! Warning: Could not create Start Menu shortcut", "yellow")
                else:
                    print("! Warning: Could not create Start Menu shortcut")

            return True

        except Exception as e:
            if self.dialog:
                self.dialog.write(f"✗ Error creating Windows launcher: {str(e)}", "red")
            else:
                print(f"✗ Error creating Windows launcher: {str(e)}")
            return False

    def _create_macos_launcher(self):
        """Create macOS launcher script and application bundle"""
        try:
            # Create launcher script
            launcher_path = self.install_paths['bin'] / 'bsg-ide'
            launcher_content = f"""#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add installation directory to Python path
sys.path.insert(0, "{self.install_paths['base']}")

# Import and run main program
try:
    from BSG_IDE import main
    main()
except Exception as e:
    print(f"Error starting BSG-IDE: {{str(e)}}")
    import traceback
    traceback.print_exc()
"""
            launcher_path.write_text(launcher_content)
            launcher_path.chmod(0o755)

            if self.dialog:
                self.dialog.write(f"✓ Created launcher script: {launcher_path}", "green")
            else:
                print(f"✓ Created launcher script: {launcher_path}")

            return True

        except Exception as e:
            if self.dialog:
                self.dialog.write(f"✗ Error creating macOS launcher: {str(e)}", "red")
            else:
                print(f"✗ Error creating macOS launcher: {str(e)}")
            return False

 #------------------------------------------------------------------------------------
    def copy_resources(self, source_dir):
        """Copy required resources to installation directories"""
        try:
            # Define required files and their destinations
            required_files = {
                'BSG_IDE.py': ['base', 'python_site'],
                'BeamerSlideGenerator.py': ['base', 'python_site'],
                'requirements.txt': ['base'],
                'airis4d_logo.png': ['base', 'resources', 'share'],  # Added multiple destinations
                'bsg-ide.png': ['base', 'resources', 'share']
            }

            # Copy each required file
            for filename, destinations in required_files.items():
                source_file = source_dir / filename
                if source_file.exists():
                    for dest_type in destinations:
                        if dest_type in self.install_paths:
                            # Create destination directory if needed
                            dest_dir = self.install_paths[dest_type]
                            dest_dir.mkdir(parents=True, exist_ok=True)

                            # For resources, ensure resources subdirectory exists
                            if dest_type == 'base':
                                resources_dir = dest_dir / 'resources'
                                resources_dir.mkdir(parents=True, exist_ok=True)
                                dest_path = resources_dir / filename
                            else:
                                dest_path = dest_dir / filename

                            try:
                                shutil.copy2(source_file, dest_path)
                                if self.dialog:
                                    self.dialog.write(f"✓ Copied {filename} to {dest_path}", "green")
                                else:
                                    print(f"✓ Copied {filename} to {dest_path}")
                            except Exception as e:
                                if self.dialog:
                                    self.dialog.write(f"! Warning: Could not copy {filename} to {dest_path}: {e}", "yellow")
                                else:
                                    print(f"! Warning: Could not copy {filename} to {dest_path}: {e}")
                else:
                    if self.dialog:
                        self.dialog.write(f"! Warning: Source file {filename} not found in {source_dir}", "yellow")
                    else:
                        print(f"! Warning: Source file {filename} not found in {source_dir}")

            # Create additional resource directories if needed
            for path_type in ['resources', 'share']:
                if path_type in self.install_paths:
                    resource_dir = self.install_paths[path_type] / 'resources'
                    resource_dir.mkdir(parents=True, exist_ok=True)
                    if self.dialog:
                        self.dialog.write(f"✓ Created resource directory: {resource_dir}", "green")

            return True

        except Exception as e:
            if self.dialog:
                self.dialog.write(f"✗ Error copying resources: {str(e)}", "red")
            else:
                print(f"✗ Error copying resources: {str(e)}")
            return False


    def _get_install_paths(self):
        """Get installation paths based on platform and permissions"""
        paths = {}

        # Get user's home directory
        home_dir = Path.home()

        if self.is_admin:
            # System-wide installation paths
            if self.system == "Linux":
                paths.update({
                    'base': Path('/usr/local/lib/bsg-ide'),
                    'bin': Path('/usr/local/bin'),
                    'share': Path('/usr/local/share/bsg-ide'),
                    'resources': Path('/usr/local/share/bsg-ide/resources'),
                    'applications': Path('/usr/share/applications'),
                    'icons': Path('/usr/share/icons/hicolor'),
                    'python_site': Path(site.getsitepackages()[0]) / 'bsg_ide'
                })
            elif self.system == "Windows":
                program_files = Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files'))
                paths.update({
                    'base': program_files / 'BSG-IDE',
                    'bin': program_files / 'BSG-IDE' / 'bin',
                    'share': program_files / 'BSG-IDE' / 'share',
                    'resources': program_files / 'BSG-IDE' / 'resources',
                    'start_menu': Path(os.environ['PROGRAMDATA']) / 'Microsoft/Windows/Start Menu/Programs',
                    'python_site': Path(site.getsitepackages()[0]) / 'bsg_ide'
                })
            else:  # macOS
                paths.update({
                    'base': Path('/Applications/BSG-IDE.app/Contents'),
                    'share': Path('/Applications/BSG-IDE.app/Contents/Resources'),
                    'resources': Path('/Applications/BSG-IDE.app/Contents/Resources'),
                    'bin': Path('/usr/local/bin'),
                    'python_site': Path(site.getsitepackages()[0]) / 'bsg_ide'
                })
        else:
            # User-specific installation paths
            if self.system == "Linux":
                paths.update({
                    'base': home_dir / '.local/lib/bsg-ide',
                    'bin': home_dir / '.local/bin',
                    'share': home_dir / '.local/share/bsg-ide',
                    'resources': home_dir / '.local/share/bsg-ide/resources',
                    'applications': home_dir / '.local/share/applications',
                    'icons': home_dir / '.local/share/icons/hicolor',
                    'python_site': Path(site.getusersitepackages()) / 'bsg_ide'
                })
            elif self.system == "Windows":
                appdata = Path(os.environ['APPDATA'])
                paths.update({
                    'base': appdata / 'BSG-IDE',
                    'bin': appdata / 'BSG-IDE' / 'bin',
                    'share': appdata / 'BSG-IDE' / 'share',
                    'resources': appdata / 'BSG-IDE' / 'resources',
                    'start_menu': appdata / 'Microsoft/Windows/Start Menu/Programs',
                    'python_site': Path(site.getusersitepackages()) / 'bsg_ide'
                })
            else:  # macOS
                paths.update({
                    'base': home_dir / 'Applications/BSG-IDE.app/Contents',
                    'share': home_dir / 'Library/Application Support/BSG-IDE',
                    'resources': home_dir / 'Library/Application Support/BSG-IDE/resources',
                    'bin': home_dir / '.local/bin',
                    'python_site': Path(site.getusersitepackages()) / 'bsg_ide'
                })

        return paths
 #-----------------------------------------------------------------------------------

    def create_directory_structure(self):
        """Create all required directories for installation"""
        try:
            # Create all directories from install_paths
            for path_type, path in self.install_paths.items():
                try:
                    # Skip creation of python_site as it's handled by pip
                    if path_type == 'python_site':
                        continue

                    path.mkdir(parents=True, exist_ok=True)
                    if self.dialog:
                        self.dialog.write(f"✓ Created directory: {path}", "green")
                    else:
                        print(f"✓ Created directory: {path}")
                except Exception as e:
                    if self.dialog:
                        self.dialog.write(f"! Warning: Could not create {path}: {e}", "yellow")
                    else:
                        print(f"! Warning: Could not create {path}: {e}")

            # Create additional required subdirectories
            media_dirs = [
                self.install_paths['base'] / 'media_files',
                self.install_paths['resources'] / 'templates',
                self.install_paths['resources'] / 'icons'
            ]

            for directory in media_dirs:
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                    if self.dialog:
                        self.dialog.write(f"✓ Created directory: {directory}", "green")
                    else:
                        print(f"✓ Created directory: {directory}")
                except Exception as e:
                    if self.dialog:
                        self.dialog.write(f"! Warning: Could not create {directory}: {e}", "yellow")
                    else:
                        print(f"! Warning: Could not create {directory}: {e}")

            # Create .keep files in empty directories to ensure they're tracked
            for directory in self.install_paths.values():
                if directory.is_dir() and not any(directory.iterdir()):
                    keep_file = directory / '.keep'
                    try:
                        keep_file.touch()
                    except Exception:
                        pass

            return True

        except Exception as e:
            if self.dialog:
                self.dialog.write(f"✗ Error creating directory structure: {str(e)}", "red")
            else:
                print(f"✗ Error creating directory structure: {str(e)}")
            return False



    def _verify_python_env(self):
        """Verify Python environment and dependencies"""
        required_version = (3, 7)
        if sys.version_info < required_version:
            raise RuntimeError(f"Python {required_version[0]}.{required_version[1]} or higher required")

        # Check virtual environment
        if not hasattr(sys, 'real_prefix') and not hasattr(sys, 'base_prefix') != sys.prefix:
            self.dialog.write("! Creating virtual environment...")
            venv_path = os.path.join(os.path.expanduser("~"), "my_python")
            venv.create(venv_path, with_pip=True)
            self.dialog.write("✓ Virtual environment created", "green")

    def _create_directories(self):
        """Create required directories with proper permissions"""
        for path in self.install_paths.values():
            path.mkdir(parents=True, exist_ok=True)
            self.dialog.write(f"✓ Created: {path}", "green")

    def _copy_files(self):
        """Copy required files to installation directories"""
        package_root = Path(__file__).parent
        required_files = {
            'BSG_IDE.py': {'dest': ['base', 'python_site']},
            'BeamerSlideGenerator.py': {'dest': ['base', 'python_site']},
            'requirements.txt': {'dest': ['base']},
            'airis4d_logo.png': {'dest': ['resources']},
            'bsg-ide.png': {'dest': ['resources']}
        }

        for filename, config in required_files.items():
            src = package_root / filename
            if src.exists():
                for dest_key in config['dest']:
                    dest = self.install_paths[dest_key] / filename
                    shutil.copy2(src, dest)
                    self.dialog.write(f"✓ Copied {filename} to {dest}", "green")
            else:
                self.dialog.write(f"! Warning: {filename} not found", "yellow")

    def setup_os_integration(self):
       """Setup OS icons and desktop integration"""
       icon_sizes = [16, 32, 48, 64, 128, 256]

       try:
           # Create icon objects for both logos
           icons = {}
           for icon_name in ['bsg-ide.png', 'airis4d_logo.png']:
               source = self.install_paths['resources'] / icon_name
               if source.exists():
                   with Image.open(source) as img:
                       icons[icon_name] = img.copy()

           if self.system == "Linux":
               # Linux hicolor theme structure
               for size in icon_sizes:
                   icon_dir = self.install_paths['icons'] / f"{size}x{size}" / 'apps'
                   icon_dir.mkdir(parents=True, exist_ok=True)

                   for icon_name, img in icons.items():
                       resized = img.copy()
                       resized.thumbnail((size, size), Image.Resampling.LANCZOS)
                       resized.save(icon_dir / icon_name)

               subprocess.run(['gtk-update-icon-cache', '--force', '--quiet',
                             str(self.install_paths['icons'])], check=False)

           elif self.system == "Windows":
               # Windows ICO format with multiple sizes
               for icon_name, img in icons.items():
                   ico_sizes = [(16,16), (32,32), (48,48), (256,256)]
                   ico_path = self.install_paths['resources'] / f"{icon_name[:-4]}.ico"

                   ico_images = []
                   for size in ico_sizes:
                       resized = img.copy()
                       resized.thumbnail(size, Image.Resampling.LANCZOS)
                       ico_images.append(resized)

                   ico_images[0].save(ico_path, format='ICO', sizes=ico_sizes, append_images=ico_images[1:])

                   # Associate icon with application
                   import winreg
                   with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "BSG-IDE") as key:
                       winreg.SetValue(key, "DefaultIcon", winreg.REG_SZ, str(ico_path))

           elif self.system == "Darwin":  # macOS
               # ICNS format for macOS
               for icon_name, img in icons.items():
                   icns_path = self.install_paths['resources'] / f"{icon_name[:-4]}.icns"

                   icns_sizes = [16, 32, 128, 256, 512]
                   icns_images = []

                   for size in icns_sizes:
                       resized = img.copy()
                       resized.thumbnail((size, size), Image.Resampling.LANCZOS)
                       icns_images.append(resized)

                   icns_images[0].save(icns_path, format='ICNS', append_images=icns_images[1:])

                   # Copy to app bundle
                   bundle_icons = self.install_paths['base'] / 'Contents' / 'Resources'
                   bundle_icons.mkdir(parents=True, exist_ok=True)
                   shutil.copy2(icns_path, bundle_icons)

           print("✓ Icons installed successfully")
           return True

       except Exception as e:
           print(f"Error setting up OS integration: {str(e)}")
           return False

    def _setup_linux_icons(self, icon_src):
        """Setup Linux icon themes"""
        sizes = [16, 32, 48, 64, 128, 256]

        for size in sizes:
            icon_dir = self.install_paths['icons'] / f"{size}x{size}" / 'apps'
            icon_dir.mkdir(parents=True, exist_ok=True)

            # Resize and save icon
            with Image.open(icon_src) as img:
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                resized.save(icon_dir / 'bsg-ide.png')

    def _setup_windows_icons(self, icon_src):
        """Setup Windows icons"""
        import win32api
        import win32con

        # Create .ico file
        ico_path = self.install_paths['resources'] / 'bsg-ide.ico'
        img = Image.open(icon_src)
        img.save(ico_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (256,256)])

        # Associate icon with file types
        file_types = ['.bsg', '.tex']
        for ext in file_types:
            win32api.RegSetValue(
                win32con.HKEY_CLASSES_ROOT,
                f"BSG-IDE{ext}\\DefaultIcon",
                win32con.REG_SZ,
                str(ico_path)
            )

    def _setup_macos_icons(self, icon_src):
        """Setup macOS icons"""
        # Create .icns file for macOS
        icns_path = self.install_paths['resources'] / 'bsg-ide.icns'

        with Image.open(icon_src) as img:
            # macOS icon sizes
            sizes = [16, 32, 128, 256, 512]
            icons = []
            for size in sizes:
                icons.append(img.resize((size, size), Image.Resampling.LANCZOS))

            # Save as icns
            icons[0].save(icns_path, format='ICNS', append_images=icons[1:])

    def _install_dependencies(self):
        """Install Python package dependencies"""
        requirements_file = self.install_paths['base'] / 'requirements.txt'
        if requirements_file.exists():
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "-r", str(requirements_file)
                ])
                self.dialog.write("✓ Installed Python dependencies", "green")
            except subprocess.CalledProcessError as e:
                self.dialog.write(f"! Warning: Some dependencies failed to install: {e}", "yellow")

    def _verify_installation(self):
        """Verify installation success"""
        problems = []

        # Check core files
        for path in self.install_paths.values():
            if not path.exists():
                problems.append(f"Missing directory: {path}")

        # Check dependencies
        try:
            import customtkinter
            import PIL
            self.dialog.write("✓ Required packages verified", "green")
        except ImportError as e:
            problems.append(f"Missing dependency: {e}")

        if problems:
            self.dialog.write("\nInstallation warnings:", "yellow")
            for problem in problems:
                self.dialog.write(f"! {problem}", "yellow")


#------------------------------------------------------------------------------------------
class SimpleRedirector:
    """Output redirector"""
    def __init__(self, terminal, color="white"):
        self.terminal = terminal
        self.color = color

    def write(self, text):
        if text.strip():
            self.terminal.write(text, self.color)

    def flush(self):
        pass


#------------------------------------------------------------------------------------------
class BeamerSyntaxHighlighter:
    """Syntax highlighting for Beamer/LaTeX content"""

    def __init__(self, text_widget: ctk.CTkTextbox):
        self.ctk_text = text_widget
        self.text = text_widget._textbox
        self.active = True

        # Create fonts
        self.normal_font = tk.font.Font(family="TkFixedFont")
        self.italic_font = tk.font.Font(family="TkFixedFont", slant="italic")

        # Define syntax highlighting colors
        self.colors = {
            'command': '#FF6B6B',     # LaTeX commands
            'media': '#4ECDC4',       # Media directives
            'bullet': '#95A5A6',      # Bullet points
            'url': '#45B7D1',         # URLs
            'bracket': '#FFB86C',     # Curly brackets
            'comment': '#6272A4',     # Comments
            'rgb': '#50FA7B',         # RGB color commands
            'textcolor': '#BD93F9' ,   # textcolor commands
            'tikz':'#8A2BE2'  # Blue violet for TikZ
        }

        # Configure tags on the underlying Text widget
        for tag, color in self.colors.items():
            self.text.tag_configure(tag, foreground=color, font=self.normal_font)

        # Special formatting for comments with italic font
        self.text.tag_configure("comment",
                              foreground=self.colors['comment'],
                              font=self.italic_font)

        # Define syntax patterns
        self.patterns = [
            (r'\\[a-zA-Z]+', 'command'),
            (r'\\(file|play|None)\s', 'media'),
            (r'^-\s.*$', 'bullet'),
            (r'https?://\S+', 'url'),
            (r'\{.*?\}', 'bracket'),
            (r'%.*$', 'comment'),
            (r'\\textcolor\{.*?\}', 'textcolor'),
            (r'\[RGB\]\{[^\}]*\}', 'rgb'),
            (r'\\begin\{tikzpicture\}', 'tikz'),  # TikZ start
            (r'\\end\{tikzpicture\}', 'tikz'),    # TikZ end
            (r'\\draw.*', 'tikz'),                # TikZ draw commands
            (r'\\node.*', 'tikz'),                # TikZ nodes
            (r'\\fill.*', 'tikz'),                # TikZ fill commands
        ]

        # Bind events to the CTkTextbox
        self.ctk_text.bind('<KeyRelease>', self.highlight)
        self.ctk_text.bind('<Control-v>', lambda e: self.after_paste())
        # Initialize presentation metadata
        self.presentation_info = {
            'title': '',
            'subtitle': '',
            'author': '',
            'institution': 'Artificial Intelligence Research and Intelligent Systems (airis4D)',
            'short_institute': 'airis4D',
            'date': '\\today'
        }


    def toggle(self) -> None:
        """Toggle syntax highlighting on/off"""
        self.active = not self.active
        if self.active:
            self.highlight()
        else:
            self.clear_highlighting()

    def clear_highlighting(self) -> None:
        """Remove all highlighting"""
        for tag in self.colors.keys():
            self.text.tag_remove(tag, "1.0", "end")

    def highlight(self, event=None) -> None:
        """Apply syntax highlighting to the text"""
        if not self.active:
            return

        self.clear_highlighting()
        for pattern, tag in self.patterns:
            self.highlight_pattern(pattern, tag)

    def highlight_pattern(self, pattern: str, tag: str) -> None:
        """Apply highlighting for a specific pattern"""
        content = self.text.get("1.0", "end-1c")
        lines = content.split('\n')

        for line_num, line in enumerate(lines, start=1):
            for match in re.finditer(pattern, line):
                start = match.start()
                end = match.end()
                start_index = f"{line_num}.{start}"
                end_index = f"{line_num}.{end}"
                self.text.tag_add(tag, start_index, end_index)

    def after_paste(self) -> None:
        """Handle highlighting after paste operation"""
        self.text.after(10, self.highlight)
        # Also trigger spell checking
        if hasattr(self.ctk_text.master, 'spell_checking_enabled') and self.ctk_text.master.spell_checking_enabled:
            self.ctk_text.master.check_spelling()

class LaTeXErrorEditor(ctk.CTkToplevel):
    r"""Interactive editor for fixing LaTeX compilation errors - works with TXT files directly"""

    def __init__(self, parent, file_path, error_line_num, error_message, error_context,
                 log_content=None, exact_line_content=None, is_txt_file=False, slide_num=0):
        # Handle different parent types gracefully
        if hasattr(parent, 'root') and isinstance(parent.root, (ctk.CTk, tk.Tk)):
            actual_parent = parent.root
        elif hasattr(parent, 'winfo_toplevel'):
            actual_parent = parent
        else:
            actual_parent = parent

        super().__init__(actual_parent)

        self.file_path = file_path
        self.is_txt_file = is_txt_file
        self.tex_file_path = file_path.replace('.txt', '.tex') if is_txt_file else file_path
        self.error_line_num = error_line_num
        self.slide_num = slide_num
        self.error_message = error_message
        self.error_context = error_context
        self.log_content = log_content
        self.exact_line_content = exact_line_content
        self.result = None
        self.fixed_content = None
        self.modified = False
        self.original_content = None
        self.parent_editor = parent

        # Update title with slide information
        if slide_num > 0:
            self.title(f"LaTeX Error Editor - Slide {slide_num}, Line {error_line_num} - {os.path.basename(file_path)}")
        else:
            self.title(f"LaTeX Error Editor - Line {error_line_num} - {os.path.basename(file_path)}")

        # Increase window size to show all buttons
        self.geometry("1000x800")

        # Make dialog modal and bring to top
        try:
            self.transient(actual_parent)
            self.grab_set()
            self.lift()
            self.focus_force()
            self.attributes('-topmost', True)
            self.after(100, lambda: self.attributes('-topmost', False))
        except:
            pass

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1000) // 2
        y = (self.winfo_screenheight() - 800) // 2
        self.geometry(f"+{x}+{y}")

        self.create_widgets()
        self.load_file()
        self.setup_brace_matching()
        # Setup enhanced help system (NEW)
        self.setup_enhanced_help_system()
        if self.slide_num > 0:
            self.after(100, self.navigate_to_error_slide)
            self.status_label.configure(
                text=f"⚠ Error in Slide {self.slide_num} - Scroll to highlighted area",
                text_color="#FFB86C"
            )
        else:
            self.setup_brace_matching()


    def write(self, text, color="white"):
        """Write to parent's terminal if available"""
        if hasattr(self.parent_editor, 'write'):
            self.parent_editor.write(text, color)
        else:
            print(text)

    # ========== SCROLLING METHODS ==========

    def on_scroll(self, *args):
        """Sync scrolling between editor and line numbers"""
        try:
            self.editor.yview(*args)
            self.line_numbers.yview(*args)
        except:
            pass

    def on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        try:
            if event.num == 4:
                delta = -1
            elif event.num == 5:
                delta = 1
            else:
                delta = -1 * (event.delta // 120)
            self.editor.yview_scroll(delta, "units")
            self.line_numbers.yview_scroll(delta, "units")
        except:
            pass
        return "break"

    # ========== BRACE MATCHING METHODS ==========

    def setup_brace_matching(self):
        """Setup brace matching for the editor"""
        try:
            self.editor.bind('<KeyRelease>', self.on_brace_match)
            self.editor.bind('<ButtonRelease-1>', self.on_brace_match)
            self.editor.bind('<Motion>', self.on_hover_brace_match)

            self.editor.tag_config('matching_brace', background='#4A90E2', foreground='white')
            self.editor.tag_config('matching_brace_hover', background='#FFB86C', foreground='black')
        except:
            pass

    def find_matching_brace(self, text_widget, pos):
        """Find matching brace for {, [, or ( at given position"""
        try:
            char = text_widget.get(pos, f"{pos}+1c")
            open_braces = {'{': '}', '[': ']', '(': ')'}
            close_braces = {'}': '{', ']': '[', ')': '('}

            if char in open_braces:
                open_char = char
                close_char = open_braces[open_char]
                count = 1
                pos_index = text_widget.index(pos)

                while True:
                    pos_index = text_widget.index(f"{pos_index}+1c")
                    if pos_index == "end":
                        break
                    next_char = text_widget.get(pos_index, f"{pos_index}+1c")
                    if next_char == open_char:
                        count += 1
                    elif next_char == close_char:
                        count -= 1
                        if count == 0:
                            return pos_index
                return None

            elif char in close_braces:
                close_char = char
                open_char = close_braces[close_char]
                count = 1
                pos_index = text_widget.index(pos)

                while True:
                    if pos_index == "1.0":
                        break
                    pos_index = text_widget.index(f"{pos_index}-1c")
                    prev_char = text_widget.get(pos_index, f"{pos_index}+1c")
                    if prev_char == close_char:
                        count += 1
                    elif prev_char == open_char:
                        count -= 1
                        if count == 0:
                            return pos_index
                return None
            return None
        except:
            return None

    def on_brace_match(self, event=None):
        """Highlight matching brace when clicked or typed"""
        try:
            self.editor.tag_remove('matching_brace', '1.0', 'end')
            cursor_pos = self.editor.index('insert')
            char_pos = self.editor.index(f"{cursor_pos}-1c")
            match_pos = self.find_matching_brace(self.editor, char_pos)

            if match_pos:
                self.editor.tag_add('matching_brace', char_pos, f"{char_pos}+1c")
                self.editor.tag_add('matching_brace', match_pos, f"{match_pos}+1c")
        except:
            pass

    def on_hover_brace_match(self, event=None):
        """Highlight matching brace on hover"""
        try:
            self.editor.tag_remove('matching_brace_hover', '1.0', 'end')
            index = self.editor.index(f"@{event.x},{event.y}")
            match_pos = self.find_matching_brace(self.editor, index)

            if match_pos:
                self.editor.tag_add('matching_brace_hover', index, f"{index}+1c")
                self.editor.tag_add('matching_brace_hover', match_pos, f"{match_pos}+1c")
        except:
            pass

    # ========== SLIDE MASKING METHOD ==========

    def mask_current_slide(self):
        """Mask out the current slide (comment out the entire slide)"""
        try:
            cursor_pos = self.editor.index('insert')
            line_num = int(cursor_pos.split('.')[0])

            lines = self.editor.get('1.0', 'end-1c').split('\n')

            # Find slide start
            slide_start = line_num - 1
            for i in range(line_num - 1, -1, -1):
                if i < len(lines) and lines[i].strip().startswith('\\title'):
                    slide_start = i
                    break

            # Find slide end
            slide_end = len(lines) - 1
            for i in range(slide_start + 1, len(lines)):
                if lines[i].strip().startswith('\\title'):
                    slide_end = i - 1
                    break

            slide_count = slide_end - slide_start + 1

            if messagebox.askyesno("Mask Slide",
                                   f"Mask slide at line {slide_start + 1}? ({slide_count} lines)\n\n"
                                   f"The slide will be commented out and hidden from PDF."):

                masked_lines = []
                for i in range(slide_start, slide_end + 1):
                    line = lines[i]
                    if line.strip() and not line.strip().startswith('%'):
                        masked_lines.append(f"% {line}")
                    else:
                        masked_lines.append(line)

                start_index = f"{slide_start + 1}.0"
                end_index = f"{slide_end + 2}.0"

                self.editor.delete(start_index, end_index)
                self.editor.insert(start_index, '\n'.join(masked_lines) + '\n')

                self.modified = True
                self.status_label.configure(text=f"✓ Masked slide at line {slide_start + 1}", text_color="#28a745")
                self.update_line_numbers()

                if messagebox.askyesno("Auto-Save", "Save changes now?"):
                    self.save_changes()
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="#dc3545")

    # ========== MAIN EDITOR METHODS ==========

    def load_file(self):
        r"""Load the file content into the editor with proper \None handling."""
        try:
            if not os.path.exists(self.file_path):
                self.editor.insert("1.0", f"% ERROR: File not found: {self.file_path}\n")
                self.status_label.configure(text=f"File not found: {self.file_path}", text_color="#dc3545")
                return

            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
                lines = file_content.splitlines(keepends=True)

            if not lines:
                self.editor.insert("1.0", "% File is empty\n")
                return

            self.original_content = file_content
            self.editor.delete("1.0", "end")

            # Build a mapping of line numbers to slide numbers
            self.line_to_slide = {}
            current_slide = 0
            for i, line in enumerate(lines, 1):
                if line.strip().startswith('\\title'):
                    current_slide += 1
                self.line_to_slide[i] = current_slide

            processed_content = []
            in_content_block = False
            found_first_line = False

            for line in lines:
                line_str = line.rstrip('\n')

                if re.match(r'^%?\s*\\begin{Content}\s*$', line_str):
                    in_content_block = True
                    found_first_line = False
                    processed_content.append(line_str)
                    continue
                elif re.match(r'^%?\s*\\end{Content}\s*$', line_str):
                    in_content_block = False
                    processed_content.append(line_str)
                    continue

                if in_content_block and not found_first_line:
                    found_first_line = True
                    is_masked = line_str.lstrip().startswith('%')
                    if is_masked:
                        clean_line = re.sub(r'^\s*%\s*', '', line_str)
                    else:
                        clean_line = line_str

                    if not clean_line.strip():
                        if is_masked:
                            processed_content.append(r"% \None")
                        else:
                            processed_content.append(r"\None")
                    else:
                        processed_content.append(line_str)
                else:
                    processed_content.append(line_str)

            final_content = '\n'.join(processed_content)
            self.editor.insert("1.0", final_content)
            self.update_line_numbers()

            # Enhanced error location with slide information
            if self.error_line_num:
                slide_num = self.line_to_slide.get(self.error_line_num, 0)
                self.highlight_error_line(self.error_line_num, slide_num)
                self.highlight_specific_issues(self.error_line_num, slide_num)

        except Exception as e:
            self.editor.insert("1.0", f"% Error loading file: {e}\n")
            import traceback
            traceback.print_exc()
            self.status_label.configure(text=f"Error loading file: {str(e)}", text_color="#dc3545")

    def highlight_error_line(self, line_num, slide_num=0):
        """Highlight the error line in the editor with slide information"""
        try:
            start_index = f"{line_num}.0"
            end_index = f"{line_num}.end"
            self.editor.tag_add("error_line", start_index, end_index)
            self.editor.see(start_index)

            # Update status label with slide information
            if slide_num > 0:
                self.status_label.configure(
                    text=f"Error at line {line_num} (Slide {slide_num}) - Use Ctrl+F to search",
                    text_color="#FFD700"
                )
            else:
                self.status_label.configure(
                    text=f"Error at line {line_num} - Use Ctrl+F to search",
                    text_color="#FFD700"
                )
        except Exception as e:
            print(f"Could not highlight error line: {e}")

    def highlight_specific_issues(self, line_num, slide_num=0):
        """Highlight specific issues like unclosed braces or math delimiters"""
        try:
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"
            line_content = self.editor.get(line_start, line_end)

            slide_info = f" (Slide {slide_num})" if slide_num > 0 else ""

            # Check for unclosed math mode ($ without matching $)
            dollar_count = line_content.count('$')
            if dollar_count % 2 != 0:
                last_dollar_pos = line_content.rfind('$')
                if last_dollar_pos != -1:
                    highlight_start = f"{line_num}.{last_dollar_pos}"
                    highlight_end = f"{line_num}.{last_dollar_pos + 1}"
                    self.editor.tag_add("error_highlight", highlight_start, highlight_end)
                    self.status_label.configure(
                        text=f"⚠ Unclosed math mode{slide_info}: missing $ after this position",
                        text_color="#FFB86C"
                    )

            # Check for unclosed braces
            open_braces = line_content.count('{')
            close_braces = line_content.count('}')
            if open_braces != close_braces:
                self.editor.tag_add("error_highlight", line_start, line_end)
                if open_braces > close_braces:
                    self.status_label.configure(
                        text=f"⚠ Unclosed brace{slide_info}: missing }} in this line",
                        text_color="#FFB86C"
                    )
                else:
                    self.status_label.configure(
                        text=f"⚠ Extra closing brace{slide_info}: too many }} in this line",
                        text_color="#FFB86C"
                    )

            # Check for missing closing bracket in math like $V_{oc}
            import re
            math_pattern = r'\$[^\$]*\{[^\}]*$'
            if re.search(math_pattern, line_content):
                self.editor.tag_add("error_highlight", line_start, line_end)
                self.status_label.configure(
                    text=f"⚠ Missing closing brace in math expression{slide_info} (e.g., V_{{oc}} should be V_{{oc}}$)",
                    text_color="#FFB86C"
                )

        except Exception as e:
            print(f"Error highlighting issues: {e}")

    def update_line_numbers(self):
        """Update line number display with slide indicators"""
        try:
            lines = self.editor.get("1.0", "end-1c").split('\n')

            # Build line numbers with slide indicators
            line_numbers = []
            current_slide = 0
            for i, line in enumerate(lines, 1):
                if line.strip().startswith('\\title'):
                    current_slide += 1
                    # Remove [DELETED] prefix for cleaner display
                    title_display = line.strip()
                    if '[DELETED]' in title_display:
                        title_display = '🗑 ' + title_display.replace('[DELETED]', '').strip()
                    line_numbers.append(f"{i:4d} ▶ Slide {current_slide}")
                else:
                    if current_slide > 0:
                        if i == self.error_line_num:
                            line_numbers.append(f"{i:4d} ⚠ Slide {current_slide}")
                        else:
                            line_numbers.append(f"{i:4d}   Slide {current_slide}")
                    else:
                        if i == self.error_line_num:
                            line_numbers.append(f"{i:4d} ⚠")
                        else:
                            line_numbers.append(f"{i:4d}")

            line_numbers_text = '\n'.join(line_numbers)
            self.line_numbers.configure(state="normal")
            self.line_numbers.delete("1.0", "end")
            self.line_numbers.insert("1.0", line_numbers_text)
            self.line_numbers.configure(state="disabled")
        except Exception as e:
            print(f"Error updating line numbers: {e}")

    def on_text_change(self, event=None):
        """Update line numbers when text changes"""
        self.update_line_numbers()
        self.modified = True
        self.status_label.configure(text="Changes made - Click 'Apply Fix & Recompile' to save", text_color="#FFB86C")

    def save_changes(self):
        r"""Save changes to file and regenerate TeX with proper \None handling."""
        try:
            content = self.editor.get("1.0", "end-1c")

            lines = content.split('\n')
            processed_lines = []
            in_content_block = False
            found_first_line = False

            for line in lines:
                if re.match(r'^%?\s*\\begin{Content}\s*$', line):
                    in_content_block = True
                    found_first_line = False
                    processed_lines.append(line)
                    continue
                elif re.match(r'^%?\s*\\end{Content}\s*$', line):
                    in_content_block = False
                    processed_lines.append(line)
                    continue

                if in_content_block and not found_first_line:
                    found_first_line = True
                    is_masked = line.lstrip().startswith('%')
                    if is_masked:
                        clean_line = re.sub(r'^\s*%\s*', '', line)
                    else:
                        clean_line = line

                    if not clean_line.strip() or clean_line.strip() == "\\None":
                        if is_masked:
                            processed_lines.append(r"% \None")
                        else:
                            processed_lines.append(r"\None")
                    else:
                        processed_lines.append(line)
                else:
                    processed_lines.append(line)

            final_content = '\n'.join(processed_lines)

            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)

            self.write(f"✓ Saved changes to {os.path.basename(self.file_path)}\n", "green")

            if self.is_txt_file:
                try:
                    from BeamerSlideGenerator import process_input_file
                    process_input_file(self.file_path, self.tex_file_path)
                    self.write(f"✓ Regenerated TeX file\n", "green")
                except Exception as e:
                    self.write(f"Warning: Could not regenerate TeX: {e}\n", "yellow")

            self.status_label.configure(text="✓ File saved successfully!", text_color="#28a745")
            self.modified = False
            return True

        except Exception as e:
            self.status_label.configure(text=f"✗ Error saving: {str(e)}", text_color="#dc3545")
            import traceback
            traceback.print_exc()
            return False

    def apply_and_recompile(self):
        """Apply changes, regenerate TeX, reload file in IDE, and signal recompile."""
        if self.save_changes():
            # Reload the file in the parent IDE to sync slide data
            if hasattr(self.parent_editor, 'load_file'):
                self.parent_editor.load_file(self.file_path)
                self.parent_editor.write(f"✓ Reloaded {os.path.basename(self.file_path)} after fixes\n", "green")
                # Also update slide list and reload current slide
                self.parent_editor.update_slide_list()
                if self.parent_editor.current_slide_index >= 0:
                    self.parent_editor.load_slide(self.parent_editor.current_slide_index)
            self.result = 'fixed'
            self.destroy()

    def abort_compilation(self):
        """Abort compilation - return to IDE without recompile."""
        self.result = 'abort'
        self.destroy()

    def skip_error(self):
        """Skip this error."""
        self.result = 'skip'
        self.destroy()

    def restore_original(self):
        """Restore original content."""
        if self.original_content:
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", self.original_content)
            self.modified = True
            self.status_label.configure(text="Restored original content", text_color="#ffc107")
            self.update_line_numbers()

    def fix_missing_item(self):
        r"""Fix missing \item error by adding \item commands."""
        content = self.editor.get("1.0", "end-1c")
        lines = content.split('\n')

        in_itemize = False
        fixed_lines = []
        fixed_count = 0

        for line in lines:
            stripped = line.strip()
            if '\\begin{itemize}' in line:
                in_itemize = True
                fixed_lines.append(line)
            elif '\\end{itemize}' in line:
                in_itemize = False
                fixed_lines.append(line)
            elif in_itemize and (stripped.startswith('-') or stripped.startswith('•')):
                fixed_lines.append('\\item ' + line.lstrip('-•').strip())
                fixed_count += 1
            else:
                fixed_lines.append(line)

        if fixed_count > 0:
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", '\n'.join(fixed_lines))
            self.modified = True
            self.status_label.configure(text=f"Added {fixed_count} missing \\item commands", text_color="#28a745")
            self.update_line_numbers()
        else:
            cursor_pos = self.editor.index("insert")
            self.editor.insert(cursor_pos, "\\item ")
            self.modified = True
            self.status_label.configure(text="Added \\item at cursor", text_color="#28a745")
            self.update_line_numbers()

    def toggle_mask_line(self):
        """Mask or unmask the current line."""
        try:
            current_pos = self.editor.index("insert")
            line_num = int(current_pos.split('.')[0])
            line_start = self.editor.index(f"{line_num}.0")
            line_end = self.editor.index(f"{line_num}.end")
            line_content = self.editor.get(line_start, line_end)

            if not line_content.strip():
                self.status_label.configure(text="Cannot mask empty line", text_color="#dc3545")
                return

            is_masked = line_content.lstrip().startswith('%')

            if is_masked:
                clean_line = re.sub(r'^\s*%\s*', '', line_content)
                self.editor.delete(line_start, line_end)
                self.editor.insert(line_start, clean_line)
                self.status_label.configure(text=f"✓ Unmasked line {line_num}", text_color="#28a745")
            else:
                indent_match = re.match(r'^(\s*)', line_content)
                indent = indent_match.group(1) if indent_match else ""
                rest = line_content[len(indent):]
                masked_line = f"{indent}% {rest}"
                self.editor.delete(line_start, line_end)
                self.editor.insert(line_start, masked_line)
                self.status_label.configure(text=f"✓ Masked line {line_num}", text_color="#ffc107")

            self.modified = True
            self.update_line_numbers()

        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="#dc3545")

    def comment_out_line(self):
        """Comment out the current line."""
        try:
            current_pos = self.editor.index("insert")
            line_num = int(current_pos.split('.')[0])
            line_start = self.editor.index(f"{line_num}.0")
            line_end = self.editor.index(f"{line_num}.end")
            line_content = self.editor.get(line_start, line_end)

            if not line_content.strip().startswith('%'):
                fixed = f'% {line_content}'
                self.editor.delete(line_start, line_end)
                self.editor.insert(line_start, fixed)
                self.modified = True
                self.status_label.configure(text=f"Commented out line {line_num}", text_color="#ffc107")
                self.update_line_numbers()
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="#dc3545")

    def copy_error(self):
        """Copy error to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(self.error_message)
        self.status_label.configure(text="Error copied to clipboard", text_color="#28a745")

    def create_widgets(self):
        """Create the editor UI with additional features"""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Error info frame
        error_frame = ctk.CTkFrame(main_frame, fg_color="#8B0000")
        error_frame.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkLabel(error_frame, text="⚠ ERROR DETECTED", font=("Arial", 14, "bold"), text_color="white").pack(anchor="w", padx=10, pady=(5, 2))

        # Error message with slide info
        if self.slide_num > 0:
            error_header = f"Slide {self.slide_num}, Line {self.error_line_num}"
            ctk.CTkLabel(error_frame, text=error_header, font=("Arial", 11), text_color="#FFD700").pack(anchor="w", padx=10, pady=(0, 2))

        ctk.CTkLabel(error_frame, text=self.error_message[:200], font=("Arial", 11), text_color="#FFB6C1", wraplength=950).pack(anchor="w", padx=10, pady=(0, 5))

        # Editor frame
        editor_frame = ctk.CTkFrame(main_frame)
        editor_frame.pack(fill="both", expand=True, padx=5, pady=5)

        paned = tk.PanedWindow(editor_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
        paned.pack(fill="both", expand=True)

        # Left side - Editor
        left_frame = tk.Frame(paned)
        paned.add(left_frame, width=600)

        line_number_frame = tk.Frame(left_frame, bg="#1e1e1e", width=70)
        line_number_frame.pack(side="left", fill="y")
        line_number_frame.pack_propagate(False)

        self.line_numbers = tk.Text(line_number_frame, width=8, padx=3, takefocus=0, border=0,
                                    background="#1e1e1e", foreground="#858585", font=("Courier", 11),
                                    wrap="none", state="disabled")
        self.line_numbers.pack(side="left", fill="y")

        editor_container = tk.Frame(left_frame)
        editor_container.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(editor_container)
        scrollbar.pack(side="right", fill="y")

        self.editor = tk.Text(editor_container, font=("Courier", 11), background="#1e1e1e",
                              foreground="#d4d4d4", insertbackground="white", wrap="none",
                              yscrollcommand=scrollbar.set, tabs=("4c", "8c", "12c", "16c", "20c", "24c"))
        self.editor.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.on_scroll)

        # Configure tags
        self.editor.tag_config("error_line", background="#8B0000", foreground="white")
        self.editor.tag_config("error_highlight", background="#FF4444", foreground="white")
        self.editor.tag_config("commented_line", background="#2d2d2d", foreground="#6a9955")

        # Bind events
        self.editor.bind("<KeyRelease>", self.on_text_change)
        self.editor.bind("<MouseWheel>", self.on_mousewheel)
        self.editor.bind("<Button-4>", self.on_mousewheel)
        self.editor.bind("<Button-5>", self.on_mousewheel)
        self.editor.bind("<Control-s>", lambda e: self.save_changes() or "break")
        self.editor.bind('<Control-f>', lambda e: self.create_search_replace_panel())
        self.editor.bind('<Control-F>', lambda e: self.create_search_replace_panel())

        # Right side - Suggestions and Actions
        right_frame = ctk.CTkFrame(paned)
        paned.add(right_frame, width=400)

        # Create a scrollable frame for right panel content
        right_scroll = ctk.CTkScrollableFrame(right_frame)
        right_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Quick Fixes section
        quick_frame = ctk.CTkFrame(right_scroll)
        quick_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(quick_frame, text="Quick Fixes", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=5)

        fixes = [
            ("🔍 Search & Replace (Ctrl+F)", self.create_search_replace_panel),
            ("📝 Fix Missing \\item", self.fix_missing_item),
            ("💬 Mask/Unmask Line", self.toggle_mask_line),
            ("📌 Comment Out Line", self.comment_out_line),
            ("🗑 Mask Entire Slide", self.mask_current_slide),
            ("↩ Restore Original", self.restore_original),
            ("💾 Save Only", self.save_changes),
        ]

        for text, cmd in fixes:
            btn = ctk.CTkButton(quick_frame, text=text, command=cmd, height=35)
            btn.pack(side="top", padx=5, pady=3, fill="x")

        # Brace Matching Info
        info_frame = ctk.CTkFrame(right_scroll)
        info_frame.pack(fill="x", padx=5, pady=10)

        ctk.CTkLabel(info_frame, text="Brace Matching", font=("Arial", 13, "bold")).pack(anchor="w", padx=5, pady=5)

        info_text = """• Hover over {, [, ( to see matching brace
• Click on a brace to highlight its match
• Helps find missing or extra braces"""

        info_label = ctk.CTkLabel(info_frame, text=info_text, font=("Arial", 11), justify="left", text_color="#888888")
        info_label.pack(anchor="w", padx=10, pady=5)

        # Slide Navigation Info
        nav_frame = ctk.CTkFrame(right_scroll)
        nav_frame.pack(fill="x", padx=5, pady=10)

        ctk.CTkLabel(nav_frame, text="Slide Navigation", font=("Arial", 13, "bold")).pack(anchor="w", padx=5, pady=5)

        nav_text = """• Slides start with \\title
• Current slide number shown in line numbers
• Mask problematic slides to bypass them
• Fix braces before recompiling"""

        nav_label = ctk.CTkLabel(nav_frame, text=nav_text, font=("Arial", 11), justify="left", text_color="#888888")
        nav_label.pack(anchor="w", padx=10, pady=5)

        # Keyboard shortcuts info
        shortcuts_frame = ctk.CTkFrame(right_scroll)
        shortcuts_frame.pack(fill="x", padx=5, pady=10)

        ctk.CTkLabel(shortcuts_frame, text="Keyboard Shortcuts", font=("Arial", 13, "bold")).pack(anchor="w", padx=5, pady=5)

        shortcuts_text = """• Ctrl+F: Search & Replace
• Ctrl+S: Save changes
• Ctrl+Z: Undo
• Ctrl+Y: Redo"""

        shortcuts_label = ctk.CTkLabel(shortcuts_frame, text=shortcuts_text, font=("Arial", 11), justify="left", text_color="#888888")
        shortcuts_label.pack(anchor="w", padx=10, pady=5)

        # Bottom buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=5, pady=(5, 0))

        ctk.CTkButton(button_frame, text="✓ Apply Fix & Recompile", command=self.apply_and_recompile,
                     width=160, height=40, fg_color="#28a745").pack(side="left", padx=5, pady=5)
        ctk.CTkButton(button_frame, text="⏭ Skip Error", command=self.skip_error,
                     width=120, height=40, fg_color="#ffc107", text_color="black").pack(side="left", padx=5, pady=5)
        ctk.CTkButton(button_frame, text="⏹ Abort", command=self.abort_compilation,
                     width=120, height=40, fg_color="#dc3545").pack(side="left", padx=5, pady=5)
        ctk.CTkButton(button_frame, text="📋 Copy Error", command=self.copy_error,
                     width=100, height=40).pack(side="right", padx=5, pady=5)

        self.status_label = ctk.CTkLabel(main_frame, text="Edit the code, then click 'Apply Fix & Recompile'",
                                        font=("Arial", 11), text_color="#888888")
        self.status_label.pack(fill="x", padx=5, pady=(0, 5))

    def create_search_replace_panel(self):
        """Open the search and replace panel"""
        SearchReplacePanel(self, self.editor)

    def navigate_to_error_slide(self):
        """Navigate to the slide containing the error using slide number"""
        if self.slide_num > 0 and hasattr(self.parent_editor, 'slides'):
            # Find the line number in TXT file for this slide
            txt_lines = self.editor.get("1.0", "end-1c").split('\n')

            current_slide = 0
            for i, line in enumerate(txt_lines, 1):
                if line.strip().startswith('\\title'):
                    current_slide += 1
                    if current_slide == self.slide_num:
                        # Found the slide - scroll to it
                        self.editor.see(f"{i}.0")
                        self.editor.mark_set("insert", f"{i}.0")

                        # Highlight the entire slide area
                        self.highlight_slide_region(i, txt_lines)
                        return i
            return None

    def highlight_slide_region(self, start_line, txt_lines):
        """Highlight the entire problematic slide"""
        # Find end of this slide (next \title or EOF)
        end_line = len(txt_lines)
        for i in range(start_line + 1, len(txt_lines)):
            if txt_lines[i].strip().startswith('\\title'):
                end_line = i - 1
                break

        # Highlight the slide region
        start_idx = f"{start_line}.0"
        end_idx = f"{end_line}.end"

        self.editor.tag_remove("error_slide", "1.0", "end")
        self.editor.tag_add("error_slide", start_idx, end_idx)
        self.editor.tag_config("error_slide", background="#2d1f1f")  # Subtle highlight

    def navigate_to_error_line(self):
        """Navigate to the exact error line in the TXT file"""
        if self.error_line and self.error_line > 0:
            try:
                # Scroll to the line
                self.editor.see(f"{self.error_line}.0")
                self.editor.mark_set("insert", f"{self.error_line}.0")

                # Highlight the entire line
                line_start = f"{self.error_line}.0"
                line_end = f"{self.error_line}.end"
                self.editor.tag_add("error_line", line_start, line_end)

                # Get the line content to show in status
                line_content = self.editor.get(line_start, line_end).strip()
                self.status_label.configure(
                    text=f"⚠ Error at line {self.error_line}: {line_content[:100]}",
                    text_color="#FFB86C"
                )

                # If this is a math mode error, offer quick fix
                if "Missing $" in self.error_message or "math mode" in self.error_message.lower():
                    if "_{" in line_content:
                        response = messagebox.askyesno(
                            "Quick Fix",
                            f"Detected subscript pattern (like V_oc) without math delimiters.\n\n"
                            f"Line {self.error_line}: {line_content[:80]}\n\n"
                            f"Would you like to automatically add $...$ around the expression?"
                        )
                        if response:
                            self.fix_math_mode_line(self.error_line, line_content)
            except Exception as e:
                print(f"Error navigating to error line: {e}")

    def fix_math_mode_line(self, line_num: int, line_content: str):
        """Quick fix for math mode errors by adding $...$ around subscripts"""
        import re

        # Fix pattern: word_{subscript} without $
        fixed_content = re.sub(r'([A-Za-z])_\{([^}]+)\}', r'$\1_{\2}$', line_content)

        if fixed_content != line_content:
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"
            self.editor.delete(line_start, line_end)
            self.editor.insert(line_start, fixed_content)
            self.status_label.configure(
                text=f"✓ Fixed: Added $...$ around subscript expression",
                text_color="#28a745"
            )
            self.modified = True
            self.update_line_numbers()

    def setup_enhanced_help_system(self):
        """Setup the existing LaTeX help system in the error editor"""
        try:
            # Import the existing help systems
            from EnhancedCommandDialog import LatexCommandHelper, CommandTooltip
            from Grammarly import LatexCommandHelper as BasicLatexCommandHelper

            # Try to use enhanced version first
            try:
                self.command_helper = LatexCommandHelper()
                self.use_enhanced_help = True
                print("✓ Using enhanced LaTeX help system")
            except:
                self.command_helper = BasicLatexCommandHelper()
                self.use_enhanced_help = False
                print("✓ Using basic LaTeX help system")

            # Initialize tooltip manager
            self.tooltip_manager = CommandTooltip(self)

            # Setup tooltip bindings for the editor
            self.setup_editor_tooltips()

        except Exception as e:
            print(f"Error setting up help system: {e}")
            self.setup_basic_help_fallback()

    def setup_editor_tooltips(self):
        """Setup tooltip bindings using the existing system"""
        # Bind hover events for command detection
        self.editor.bind('<Motion>', self.on_editor_hover)
        self.editor.bind('<Leave>', self.on_editor_leave)

        # Bind Alt+Click for detailed help
        self.editor.bind('<Alt-Button-1>', self.show_detailed_command_help)
        self.editor.bind('<Control-Button-1>', self.show_detailed_command_help)

    def on_editor_hover(self, event):
        """Handle hover over LaTeX commands using existing tooltip system"""
        try:
            index = self.editor.index(f"@{event.x},{event.y}")

            # Get the word under cursor
            word_start = self.editor.index(f"{index} wordstart")
            word_end = self.editor.index(f"{index} wordend")
            word = self.editor.get(word_start, word_end)

            # Check if it's a LaTeX command
            if word.startswith('\\') and len(word) > 1:
                # Use existing tooltip manager
                if hasattr(self, 'tooltip_manager'):
                    self.tooltip_manager.show_tooltip(
                        self.editor, word, event.x_root, event.y_root
                    )
                else:
                    # Fallback to basic tooltip
                    self.show_basic_command_tooltip(word, event.x_root, event.y_root)
            else:
                # Hide tooltip if not a command
                if hasattr(self, 'tooltip_manager'):
                    self.tooltip_manager.hide_tooltip()

        except Exception as e:
            print(f"Error in hover: {e}")

    def on_editor_leave(self, event):
        """Hide tooltip when mouse leaves editor"""
        if hasattr(self, 'tooltip_manager'):
            self.tooltip_manager.hide_tooltip()

    def show_detailed_command_help(self, event):
        """Show detailed command help on Alt+Click using existing system"""
        try:
            index = self.editor.index(f"@{event.x},{event.y}")

            # Get the command under cursor
            word_start = self.editor.index(f"{index} wordstart")
            word_end = self.editor.index(f"{index} wordend")
            command = self.editor.get(word_start, word_end)

            if command.startswith('\\') and hasattr(self, 'command_helper'):
                # Get detailed help from the existing helper
                help_text = self.command_helper.get_command_help(command)

                if help_text:
                    # Show in a proper dialog
                    self.show_command_help_dialog(command, help_text)
                else:
                    # Show that command wasn't found
                    self.show_bubble_message(f"Command '{command}' not found in database", "yellow")

        except Exception as e:
            print(f"Error showing detailed help: {e}")

    def show_command_help_dialog(self, command, help_text):
        """Show command help in a nice dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Command Help: {command}")
        dialog.geometry("600x500")
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 600) // 2
        y = (dialog.winfo_screenheight() - 500) // 2
        dialog.geometry(f"+{x}+{y}")

        # Create text widget with help content
        text_widget = ctk.CTkTextbox(dialog, font=("Courier", 11))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        # Format help text nicely
        formatted_help = f"""
    📖 LaTeX Command Reference: {command}
    {'=' * 50}

    {help_text}

    {'=' * 50}

    Tips:
    • Click "Insert" to add this command at cursor position
    • Use Ctrl+C to copy the command
    • Press Escape to close this dialog
    """
        text_widget.insert('1.0', formatted_help)
        text_widget.configure(state="disabled")

        # Button frame
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=10, pady=10)

        def insert_command():
            """Insert the command at cursor position"""
            self.editor.insert('insert', f"{command} ")
            dialog.destroy()
            self.status_label.configure(text=f"✓ Inserted {command}", text_color="#28a745")
            self.after(2000, lambda: self.status_label.configure(text=""))

        def copy_command():
            """Copy command to clipboard"""
            self.clipboard_clear()
            self.clipboard_append(command)
            self.status_label.configure(text=f"✓ Copied {command} to clipboard", text_color="#28a745")
            self.after(2000, lambda: self.status_label.configure(text=""))

        ctk.CTkButton(button_frame, text="Insert at Cursor", command=insert_command).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Copy to Clipboard", command=copy_command).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Close", command=dialog.destroy).pack(side="right", padx=5)

    def show_basic_command_tooltip(self, command, x, y):
        """Fallback basic tooltip if enhanced system isn't available"""
        tooltip = tk.Toplevel(self)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x+10}+{y+10}")
        tooltip.configure(bg='#ffffe0', relief='solid', borderwidth=1)

        # Get basic help text
        basic_help = {
            '\\title': 'Sets the presentation title\nUsage: \\title{Your Title}',
            '\\author': 'Sets the author name\nUsage: \\author{Author Name}',
            '\\institute': 'Sets the institution\nUsage: \\institute{Institution}',
            '\\date': 'Sets the date\nUsage: \\date{\\today}',
            '\\begin': 'Begins an environment\nUsage: \\begin{environment}',
            '\\end': 'Ends an environment\nUsage: \\end{environment}',
            '\\item': 'List item\nUsage: \\item Text here',
            '\\textbf': 'Bold text\nUsage: \\textbf{text}',
            '\\textit': 'Italic text\nUsage: \\textit{text}',
            '\\textcolor': 'Colored text\nUsage: \\textcolor{color}{text}',
            '\\includegraphics': 'Include image\nUsage: \\includegraphics[options]{file}',
            '\\cite': 'Cite reference\nUsage: \\cite{key}',
            '\\ref': 'Cross-reference\nUsage: \\ref{label}',
            '\\label': 'Set label\nUsage: \\label{name}',
            '\\pause': 'Create overlay pause\nUsage: \\pause',
            '\\only': 'Show on specific slides\nUsage: \\only<1>{content}',
        }

        help_text = basic_help.get(command, f"LaTeX command: {command}\nPress Alt+Click for more details")

        label = tk.Label(tooltip, text=help_text, justify='left',
                        bg='#ffffe0', fg='#333333', font=("Arial", 10),
                        padx=8, pady=5)
        label.pack()

        # Auto-hide after 3 seconds
        tooltip.after(3000, tooltip.destroy)

        # Store reference
        self.current_tooltip = tooltip

    def show_bubble_message(self, message, color="yellow"):
        """Show a temporary bubble message"""
        if hasattr(self, 'bubble_message') and self.bubble_message:
            try:
                self.bubble_message.destroy()
            except:
                pass

        self.bubble_message = tk.Toplevel(self)
        self.bubble_message.wm_overrideredirect(True)

        # Position near status label
        x = self.winfo_pointerx()
        y = self.winfo_pointery() - 30

        self.bubble_message.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.bubble_message, text=message, bg=color, fg='black',
                         padx=10, pady=5, font=("Arial", 10, "bold"),
                         relief='solid', borderwidth=1)
        label.pack()

        # Auto-hide after 2 seconds
        self.bubble_message.after(2000, lambda: self.bubble_message.destroy() if self.bubble_message else None)

    def setup_basic_help_fallback(self):
        """Setup basic help fallback if enhanced system isn't available"""
        self.command_helper = None
        self.tooltip_manager = None

        # Still provide basic tooltip functionality
        self.editor.bind('<Motion>', self.on_basic_hover)
        self.editor.bind('<Alt-Button-1>', self.on_basic_help_click)

    def on_basic_hover(self, event):
        """Basic hover handler for fallback mode"""
        try:
            index = self.editor.index(f"@{event.x},{event.y}")
            word_start = self.editor.index(f"{index} wordstart")
            word_end = self.editor.index(f"{index} wordend")
            word = self.editor.get(word_start, word_end)

            if word.startswith('\\'):
                self.show_basic_command_tooltip(word, event.x_root, event.y_root)
        except:
            pass

    def on_basic_help_click(self, event):
        """Basic help click handler for fallback mode"""
        try:
            index = self.editor.index(f"@{event.x},{event.y}")
            word_start = self.editor.index(f"{index} wordstart")
            word_end = self.editor.index(f"{index} wordend")
            command = self.editor.get(word_start, word_end)

            if command.startswith('\\'):
                messagebox.showinfo("Command Help",
                    f"Command: {command}\n\n"
                    f"Press Ctrl+Space for autocomplete\n"
                    f"Check the Command Index for more help")
        except:
            pass

class SearchReplacePanel(ctk.CTkToplevel):
    """Search and replace panel for the Error Editor"""

    def __init__(self, parent, editor_widget):
        super().__init__(parent)
        self.editor = editor_widget
        self.title("Search and Replace")
        self.geometry("500x250")
        self.transient(parent)
        self.grab_set()

        # Bring to top
        self.lift()
        self.focus_force()

        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 250) // 2
        self.geometry(f"+{x}+{y}")

        self.create_widgets()

    def create_widgets(self):
        """Create search and replace widgets"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Search section
        search_frame = ctk.CTkFrame(main_frame)
        search_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(search_frame, text="Search:", width=60).pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, width=300)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)

        # Search options frame
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", pady=5)

        self.case_sensitive = ctk.BooleanVar(value=False)
        case_check = ctk.CTkCheckBox(
            options_frame,
            text="Case sensitive",
            variable=self.case_sensitive,
            command=self.on_search_change
        )
        case_check.pack(side="left", padx=10)

        self.whole_word = ctk.BooleanVar(value=False)
        word_check = ctk.CTkCheckBox(
            options_frame,
            text="Whole word",
            variable=self.whole_word,
            command=self.on_search_change
        )
        word_check.pack(side="left", padx=10)

        self.use_regex = ctk.BooleanVar(value=False)
        regex_check = ctk.CTkCheckBox(
            options_frame,
            text="Regular expression",
            variable=self.use_regex,
            command=self.on_search_change
        )
        regex_check.pack(side="left", padx=10)

        # Replace section
        replace_frame = ctk.CTkFrame(main_frame)
        replace_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(replace_frame, text="Replace:", width=60).pack(side="left", padx=5)
        self.replace_entry = ctk.CTkEntry(replace_frame, width=300)
        self.replace_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Status label
        self.status_label = ctk.CTkLabel(main_frame, text="", font=("Arial", 10))
        self.status_label.pack(fill="x", pady=5)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=10)

        ctk.CTkButton(
            button_frame,
            text="Find Next",
            command=self.find_next,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Replace",
            command=self.replace_current,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Replace All",
            command=self.replace_all,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.destroy,
            width=80
        ).pack(side="right", padx=5)

        # Bind Escape key to close
        self.bind('<Escape>', lambda e: self.destroy())

    def get_search_pattern(self):
        """Get the search pattern based on options"""
        search_text = self.search_entry.get()
        if not search_text:
            return None

        if self.use_regex.get():
            try:
                flags = 0 if self.case_sensitive.get() else re.IGNORECASE
                return re.compile(search_text, flags)
            except re.error:
                self.status_label.configure(text="Invalid regular expression", text_color="red")
                return None
        else:
            return search_text

    def on_search_change(self, event=None):
        """Handle search text change - clear highlights and update status"""
        self.editor.tag_remove('search_highlight', '1.0', 'end')
        self.status_label.configure(text="", text_color="white")

    def find_next(self):
        """Find the next occurrence of search text"""
        pattern = self.get_search_pattern()
        if not pattern:
            return

        # Get current cursor position
        cursor_pos = self.editor.index('insert')

        # Search from cursor position
        if isinstance(pattern, str):
            # Plain text search
            start_pos = cursor_pos
            while True:
                start_pos = self.editor.search(pattern, start_pos, stopindex="end",
                                               nocase=not self.case_sensitive.get(),
                                               exact=not self.use_regex.get())
                if not start_pos:
                    # Wrap around to beginning
                    start_pos = self.editor.search(pattern, "1.0", stopindex=cursor_pos,
                                                   nocase=not self.case_sensitive.get(),
                                                   exact=not self.use_regex.get())
                    if not start_pos:
                        self.status_label.configure(text="No more matches found", text_color="yellow")
                        return
                    else:
                        self.status_label.configure(text="Search wrapped to beginning", text_color="cyan")
                        break
                else:
                    break
        else:
            # Regex search
            content = self.editor.get("1.0", "end-1c")
            matches = list(pattern.finditer(content))
            if not matches:
                self.status_label.configure(text="No matches found", text_color="yellow")
                return

            # Find match after cursor
            cursor_index = int(self.editor.index(cursor_pos).split('.')[0])
            for match in matches:
                match_start_line = content[:match.start()].count('\n') + 1
                if match_start_line >= cursor_index:
                    start_pos = f"{match_start_line}.{match.start() - content[:match.start()].rfind('\n') - 1}"
                    break
            else:
                # Wrap to first match
                match = matches[0]
                start_pos = f"{content[:match.start()].count('\n') + 1}.{match.start() - content[:match.start()].rfind('\n') - 1}"
                self.status_label.configure(text="Search wrapped to beginning", text_color="cyan")

        # Highlight the match
        end_pos = f"{start_pos}+{len(pattern) if isinstance(pattern, str) else len(match.group(0))}c"
        self.editor.tag_remove('search_highlight', '1.0', 'end')
        self.editor.tag_add('search_highlight', start_pos, end_pos)
        self.editor.tag_config('search_highlight', background='#FFB86C', foreground='black')
        self.editor.see(start_pos)
        self.editor.mark_set('insert', start_pos)

        match_text = self.editor.get(start_pos, end_pos)
        self.status_label.configure(text=f"Found: '{match_text}'", text_color="green")

    def replace_current(self):
        """Replace the current match"""
        # Get the current selection
        try:
            sel_start = self.editor.index('sel.first')
            sel_end = self.editor.index('sel.last')

            # Check if selection is a search highlight
            tags = self.editor.tag_names(sel_start)
            if 'search_highlight' in tags:
                replace_text = self.replace_entry.get()
                self.editor.delete(sel_start, sel_end)
                self.editor.insert(sel_start, replace_text)
                self.status_label.configure(text="Replaced", text_color="green")
                self.find_next()
            else:
                self.find_next()
        except tk.TclError:
            self.find_next()

    def replace_all(self):
        """Replace all occurrences"""
        pattern = self.get_search_pattern()
        if not pattern:
            return

        content = self.editor.get("1.0", "end-1c")
        replace_text = self.replace_entry.get()

        if isinstance(pattern, str):
            # Plain text replacement
            if self.case_sensitive.get():
                new_content = content.replace(pattern, replace_text)
            else:
                # Case-insensitive replacement
                new_content = re.compile(re.escape(pattern), re.IGNORECASE).sub(replace_text, content)
        else:
            # Regex replacement
            new_content = pattern.sub(replace_text, content)

        # Count replacements
        if isinstance(pattern, str):
            if self.case_sensitive.get():
                count = content.count(pattern)
            else:
                count = len(re.findall(re.escape(pattern), content, re.IGNORECASE))
        else:
            count = len(pattern.findall(content))

        if count > 0:
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", new_content)
            self.status_label.configure(text=f"Replaced {count} occurrence(s)", text_color="green")
            # Mark as modified
            if hasattr(self.master, 'modified'):
                self.master.modified = True
        else:
            self.status_label.configure(text="No matches found", text_color="yellow")

class MenuBar(ctk.CTkFrame):
    """Comprehensive menu bar for BSG-IDE"""

    def __init__(self, parent, editor):
        super().__init__(parent, fg_color="transparent")
        self.editor = editor
        self.create_menus()

    def create_menus(self):
        """Create all menu bars"""
        # Create main menu bar container
        self.menu_container = tk.Menu(self)

        # Create individual menus
        self.create_file_menu()
        self.create_edit_menu()
        self.create_slide_menu()
        self.create_view_menu()
        self.create_insert_menu()
        self.create_tools_menu()
        self.create_help_menu()

        # Configure the menu bar
        self.master.config(menu=self.menu_container)

    def create_file_menu(self):
        """Create File menu"""
        file_menu = tk.Menu(self.menu_container, tearoff=0)

        file_menu.add_command(label="New", command=self.editor.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.editor.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.editor.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()

        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self.update_recent_menu()

        file_menu.add_separator()
        file_menu.add_command(label="Load TeX File...", command=self.editor.load_tex_file)
        file_menu.add_command(label="Get Source from TeX...", command=self.editor.get_source_from_tex)
        file_menu.add_separator()
        file_menu.add_command(label="Export to Overleaf...", command=self.editor.create_overleaf_zip)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.editor.on_closing, accelerator="Ctrl+Q")

        self.menu_container.add_cascade(label="File", menu=file_menu)

    def update_recent_menu(self):
        """Update the recent files menu"""
        self.recent_menu.delete(0, 'end')
        if hasattr(self.editor, 'session_data') and self.editor.session_data.get('recent_files'):
            for filepath in self.editor.session_data['recent_files'][-10:]:
                if os.path.exists(filepath):
                    self.recent_menu.add_command(
                        label=os.path.basename(filepath),
                        command=lambda f=filepath: self.editor.load_file(f)
                    )
        else:
            self.recent_menu.add_command(label="No recent files", state="disabled")

    def create_edit_menu(self):
        """Create Edit menu with undo/redo and editing operations"""
        edit_menu = tk.Menu(self.menu_container, tearoff=0)

        edit_menu.add_command(label="Undo", command=self.editor.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.editor.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.editor_focused_action('cut'), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=lambda: self.editor_focused_action('copy'), accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=lambda: self.editor_focused_action('paste'), accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find/Replace", command=self.show_search_replace, accelerator="Ctrl+F")
        edit_menu.add_separator()

        # Slide operations submenu
        slide_ops = tk.Menu(edit_menu, tearoff=0)
        slide_ops.add_command(label="New Slide", command=self.editor.new_slide, accelerator="Ctrl+N")
        slide_ops.add_command(label="Duplicate Slide", command=self.editor.duplicate_slide, accelerator="Ctrl+D")
        slide_ops.add_command(label="Delete Slide", command=self.editor.delete_slide, accelerator="Delete")
        slide_ops.add_separator()
        slide_ops.add_command(label="Move Slide Up", command=lambda: self.editor.move_slide(-1), accelerator="Ctrl+Up")
        slide_ops.add_command(label="Move Slide Down", command=lambda: self.editor.move_slide(1), accelerator="Ctrl+Down")
        edit_menu.add_cascade(label="Slide Operations", menu=slide_ops)

        # Mask/Unmask operations
        mask_ops = tk.Menu(edit_menu, tearoff=0)
        mask_ops.add_command(label="Mask/Unmask Line", command=lambda: self.editor.mask_line_in_editor(), accelerator="Ctrl+Delete")
        mask_ops.add_command(label="Mask Current Slide", command=self.editor.mask_current_slide)
        mask_ops.add_command(label="Restore Current Slide", command=self.editor.restore_deleted_slide, accelerator="Ctrl+Shift+R")
        mask_ops.add_command(label="Restore All Deleted", command=self.editor.restore_all_deleted_slides)
        mask_ops.add_separator()
        mask_ops.add_command(label="Permanently Delete Masked", command=self.editor.permanently_delete_masked_slides)
        edit_menu.add_cascade(label="Mask/Unmask", menu=mask_ops)

        self.menu_container.add_cascade(label="Edit", menu=edit_menu)

    def editor_focused_action(self, action):
        """Perform edit action on focused widget"""
        focused = self.editor.focus_get()

        if action == 'cut':
            try:
                focused.event_generate('<<Cut>>')
            except:
                pass
        elif action == 'copy':
            try:
                focused.event_generate('<<Copy>>')
            except:
                pass
        elif action == 'paste':
            try:
                focused.event_generate('<<Paste>>')
            except:
                pass

    def show_search_replace(self):
        """Show search/replace dialog"""
        focused = self.editor.focus_get()
        if focused in [self.editor.content_editor._textbox, self.editor.notes_editor._textbox]:
            SearchReplacePanel(self.editor, focused)

    def create_slide_menu(self):
        """Create Slide menu"""
        slide_menu = tk.Menu(self.menu_container, tearoff=0)

        slide_menu.add_command(label="New Slide", command=self.editor.new_slide, accelerator="Ctrl+N")
        slide_menu.add_command(label="Insert Below", command=self.editor.insert_slide_below, accelerator="Ctrl+I")
        slide_menu.add_command(label="Duplicate Slide", command=self.editor.duplicate_slide, accelerator="Ctrl+D")
        slide_menu.add_separator()
        slide_menu.add_command(label="Delete/Mask Slide", command=self.editor.delete_slide, accelerator="Delete")
        slide_menu.add_command(label="Restore Deleted Slide", command=self.editor.restore_deleted_slide, accelerator="Ctrl+Shift+R")
        slide_menu.add_separator()
        slide_menu.add_command(label="Move Slide Up", command=lambda: self.editor.move_slide(-1), accelerator="Ctrl+Up")
        slide_menu.add_command(label="Move Slide Down", command=lambda: self.editor.move_slide(1), accelerator="Ctrl+Down")
        slide_menu.add_separator()
        slide_menu.add_command(label="Restore All Deleted Slides", command=self.editor.restore_all_deleted_slides)
        slide_menu.add_command(label="Permanently Delete Masked Slides", command=self.editor.permanently_delete_masked_slides)

        self.menu_container.add_cascade(label="Slide", menu=slide_menu)

    def create_view_menu(self):
        """Create View menu"""
        view_menu = tk.Menu(self.menu_container, tearoff=0)

        # Syntax highlighting toggle
        self.syntax_var = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Syntax Highlighting", variable=self.syntax_var,
                                  command=self.toggle_syntax_highlighting)

        # Terminal toggle
        view_menu.add_command(label="Toggle Terminal", command=self.editor.toggle_terminal, accelerator="Ctrl+T")
        view_menu.add_separator()

        # Notes mode submenu
        notes_menu = tk.Menu(view_menu, tearoff=0)
        self.notes_mode_var = tk.StringVar(value="both")

        notes_menu.add_radiobutton(label="Slides Only", variable=self.notes_mode_var,
                                   value="slides", command=lambda: self.set_notes_mode("slides"))
        notes_menu.add_radiobutton(label="Notes Only", variable=self.notes_mode_var,
                                   value="notes", command=lambda: self.set_notes_mode("notes"))
        notes_menu.add_radiobutton(label="Slides + Notes", variable=self.notes_mode_var,
                                   value="both", command=lambda: self.set_notes_mode("both"))
        view_menu.add_cascade(label="Notes Mode", menu=notes_menu)

        view_menu.add_separator()

        # Show deleted slides toggle
        self.show_deleted_var = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Show Deleted Slides", variable=self.show_deleted_var,
                                  command=self.toggle_show_deleted)

        self.menu_container.add_cascade(label="View", menu=view_menu)

    def toggle_syntax_highlighting(self):
        """Toggle syntax highlighting"""
        if hasattr(self.editor, 'syntax_highlighter'):
            if self.syntax_var.get():
                self.editor.syntax_highlighter.active = True
                self.editor.syntax_highlighter.highlight()
            else:
                self.editor.syntax_highlighter.active = False
                self.editor.syntax_highlighter.clear_highlighting()

    def set_notes_mode(self, mode):
        """Set notes mode"""
        if hasattr(self.editor, 'set_notes_mode'):
            self.editor.set_notes_mode(mode)

    def toggle_show_deleted(self):
        """Toggle showing deleted slides"""
        if hasattr(self.editor, 'show_deleted_slides'):
            self.editor.show_deleted_slides = self.show_deleted_var.get()
            self.editor.update_slide_list()

    def create_insert_menu(self):
        """Create Insert menu"""
        insert_menu = tk.Menu(self.menu_container, tearoff=0)

        # LaTeX commands
        insert_menu.add_command(label="LaTeX Command Index...", command=self.editor.show_enhanced_command_index)
        insert_menu.add_separator()

        # List elements
        insert_menu.add_command(label="Bullet Point", command=lambda: self.insert_into_focused("- "))
        insert_menu.add_command(label="Itemize Environment", command=lambda: self.insert_into_focused("\\begin{itemize}\n\\item \n\\end{itemize}"))
        insert_menu.add_command(label="Enumerate Environment", command=lambda: self.insert_into_focused("\\begin{enumerate}\n\\item \n\\end{enumerate}"))
        insert_menu.add_separator()

        # Text formatting
        format_menu = tk.Menu(insert_menu, tearoff=0)
        format_menu.add_command(label="Bold", command=lambda: self.wrap_selection(r'\textbf{', '}'))
        format_menu.add_command(label="Italic", command=lambda: self.wrap_selection(r'\textit{', '}'))
        format_menu.add_command(label="Color", command=self.insert_color_command)
        format_menu.add_command(label="Highlight", command=lambda: self.wrap_selection(r'\hl{', '}'))
        insert_menu.add_cascade(label="Text Formatting", menu=format_menu)

        insert_menu.add_separator()

        # Media
        media_menu = tk.Menu(insert_menu, tearoff=0)
        media_menu.add_command(label="Local File...", command=self.editor.browse_media)
        media_menu.add_command(label="YouTube Video...", command=self.editor.youtube_dialog)
        media_menu.add_command(label="Search Images...", command=self.editor.search_images)
        media_menu.add_command(label="Screen Capture...", command=self.editor.capture_screen)
        media_menu.add_command(label="Camera Capture...", command=self.editor.open_camera)
        insert_menu.add_cascade(label="Media", menu=media_menu)

        insert_menu.add_separator()

        # TikZ elements
        tikz_menu = tk.Menu(insert_menu, tearoff=0)
        tikz_menu.add_command(label="TikZ Color Helper...", command=self.editor.show_tikz_color_helper)
        tikz_menu.add_command(label="Basic Node", command=lambda: self.insert_into_focused("\\node[fill=airis4d_blue, text=white] {Text};"))
        tikz_menu.add_command(label="Simple Diagram", command=self.insert_tikz_diagram)
        insert_menu.add_cascade(label="TikZ Elements", menu=tikz_menu)

        self.menu_container.add_cascade(label="Insert", menu=insert_menu)

    def insert_into_focused(self, text):
        """Insert text into focused editor"""
        focused = self.editor.focus_get()
        if focused in [self.editor.content_editor._textbox, self.editor.notes_editor._textbox]:
            focused.insert("insert", text)
        elif focused == self.editor.title_entry:
            focused.insert("insert", text)

    def wrap_selection(self, prefix, suffix):
        """Wrap selected text with prefix and suffix"""
        focused = self.editor.focus_get()
        if focused in [self.editor.content_editor._textbox, self.editor.notes_editor._textbox]:
            try:
                selection = focused.get('sel.first', 'sel.last')
                focused.delete('sel.first', 'sel.last')
                focused.insert('insert', f'{prefix}{selection}{suffix}')
            except tk.TclError:
                focused.insert('insert', f'{prefix}{suffix}')

    def insert_color_command(self):
        """Insert textcolor command"""
        from tkinter import simpledialog
        color = simpledialog.askstring("Color", "Enter color name or RGB (e.g., red, blue, #FF0000):")
        if color:
            self.wrap_selection(f'\\textcolor{{{color}}}{{', '}')

    def insert_tikz_diagram(self):
        """Insert a simple TikZ diagram template"""
        diagram = """\\begin{tikzpicture}
    \\draw[fill=airis4d_blue] (0,0) rectangle (2,1);
    \\node[text=white] at (1,0.5) {Label};
\\end{tikzpicture}"""
        self.insert_into_focused(diagram)

    def create_tools_menu(self):
        """Create Tools menu"""
        tools_menu = tk.Menu(self.menu_container, tearoff=0)

        tools_menu.add_command(label="Presentation Settings...", command=self.editor.show_settings_dialog)
        tools_menu.add_command(label="Edit Preamble...", command=self.editor.edit_preamble)
        tools_menu.add_separator()

        # Generation
        gen_menu = tk.Menu(tools_menu, tearoff=0)
        gen_menu.add_command(label="Generate PDF", command=self.editor.generate_pdf)
        gen_menu.add_command(label="Convert to TeX", command=self.editor.convert_to_tex)
        gen_menu.add_command(label="Preview PDF", command=self.editor.preview_pdf)
        gen_menu.add_command(label="Present with Notes", command=self.editor.present_with_notes)
        tools_menu.add_cascade(label="Generation", menu=gen_menu)

        tools_menu.add_separator()

        # Grammarly
        self.grammarly_var = tk.BooleanVar(value=False)
        tools_menu.add_checkbutton(label="Grammarly Integration", variable=self.grammarly_var,
                                   command=self.toggle_grammarly)
        tools_menu.add_command(label="Setup Grammarly...", command=self.setup_grammarly)

        tools_menu.add_separator()
        tools_menu.add_command(label="Spell Check Settings...", command=self.editor.show_spellcheck_settings)

        self.menu_container.add_cascade(label="Tools", menu=tools_menu)

    def toggle_grammarly(self):
        """Toggle Grammarly integration"""
        if hasattr(self.editor, 'toggle_grammarly'):
            self.editor.toggle_grammarly()
            # Update button state if needed
            if hasattr(self.editor, 'grammarly_button'):
                self.grammarly_var.set(self.editor.grammarly.grammarly_enabled)

    def setup_grammarly(self):
        """Setup Grammarly integration"""
        if hasattr(self.editor, 'setup_grammarly_manually'):
            self.editor.setup_grammarly_manually()

    def create_help_menu(self):
        """Create Help menu"""
        help_menu = tk.Menu(self.menu_container, tearoff=0)

        help_menu.add_command(label="LaTeX Command Reference...", command=self.editor.show_enhanced_command_index)
        help_menu.add_command(label="Keyboard Shortcuts...", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About BSG-IDE", command=self.editor.create_about_dialog)

        self.menu_container.add_cascade(label="Help", menu=help_menu)

    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts_text = """
        Keyboard Shortcuts:

        File Operations:
        Ctrl+N - New presentation
        Ctrl+O - Open file
        Ctrl+S - Save file
        Ctrl+Q - Exit

        Edit Operations:
        Ctrl+Z - Undo
        Ctrl+Y - Redo
        Ctrl+X/C/V - Cut/Copy/Paste
        Ctrl+F - Find/Replace
        Ctrl+Delete - Mask/Unmask current line

        Slide Navigation:
        Ctrl+Up/Down - Move current slide
        Ctrl+Left/Right - Navigate to previous/next slide
        Delete - Delete/mask current slide
        Ctrl+Shift+R - Restore deleted slide

        View Operations:
        Ctrl+T - Toggle terminal

        Slide Creation:
        Ctrl+N - New slide
        Ctrl+I - Insert slide below
        Ctrl+D - Duplicate slide
        """

        dialog = ctk.CTkToplevel(self.editor)
        dialog.title("Keyboard Shortcuts")
        dialog.geometry("500x500")
        dialog.transient(self.editor)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 500) // 2
        y = (dialog.winfo_screenheight() - 500) // 2
        dialog.geometry(f"+{x}+{y}")

        text_widget = ctk.CTkTextbox(dialog, font=("Courier", 11))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", shortcuts_text)
        text_widget.configure(state="disabled")

        ctk.CTkButton(dialog, text="Close", command=dialog.destroy).pack(pady=10)


class BeamerSlideEditor(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Version and info - KEEP ORIGINAL
        AIRIS4D_ASCII_LOGO = """
        /\\
       /  \\   airis4D
      / /\\ \\
     /_/  \\_\\ LABS
    """
        self.__version__ = "5.7.4"
        self.__author__ = "Ninan Sajeeth Philip"
        self.__license__ = "Creative Commons"
        self.logo_ascii = AIRIS4D_ASCII_LOGO

        self.add_tikz_color_helper()

        # Initialize dictionary for notes buttons - KEEP ORIGINAL
        self.notes_buttons = {}

        # Initialize paths - KEEP ORIGINAL
        self.package_root, self.resources_dir = setup_paths()

        # Initialize logo before creating widgets - KEEP ORIGINAL but reordered
        self.has_logo = False
        self.logo_image = None
        self.setup_logo()  # Moved earlier for proper initialization

        # Rest of initialization... - PRESERVE ALL ORIGINAL SETUP
        self.create_widgets()

        # Create terminal I/O interface - KEEP ORIGINAL
        self.terminal_io = TerminalIO(self)

        # Initialize session manager with error handling - KEEP ORIGINAL
        try:
            self.session_manager = SessionManager()
            self.session_data = self.session_manager.load_session()
        except Exception as e:
            print(f"Warning: Session management unavailable: {str(e)}")
            self.session_manager = None

            documents_dir = None
            try:
                possible_docs = [
                    Path.home() / 'Documents',
                    Path.home() / 'documents',
                    Path(os.path.expandvars('%USERPROFILE%\\Documents'))
                ]
                for doc_path in possible_docs:
                    if doc_path.exists() and doc_path.is_dir():
                        documents_dir = doc_path
                        break
            except:
                pass

            self.session_data = {
                'last_file': None,
                'working_directory': str(Path.cwd()),
                'recent_files': [],
                'window_size': {'width': 1200, 'height': 800},
                'window_position': {'x': None, 'y': None}
            }

        # Configure window based on session data - KEEP ORIGINAL
        self.title("BeamerSlide Generator IDE")
        self.geometry(f"{self.session_data['window_size']['width']}x{self.session_data['window_size']['height']}")
        if all(v is not None for v in self.session_data['window_position'].values()):
            self.geometry(f"+{self.session_data['window_position']['x']}+{self.session_data['window_position']['y']}")

        # Change to working directory if valid - KEEP ORIGINAL
        try:
            working_dir = Path(self.session_data['working_directory'])
            if working_dir.exists():
                os.chdir(working_dir)
                print(f"Working directory set to: {working_dir}")
            else:
                # Try to use Documents folder
                documents_dir = None
                possible_docs = [
                    Path.home() / 'Documents',
                    Path.home() / 'documents',
                    Path(os.path.expandvars('%USERPROFILE%\\Documents'))
                ]
                for doc_path in possible_docs:
                    if doc_path.exists() and doc_path.is_dir():
                        documents_dir = doc_path
                        os.chdir(documents_dir)
                        print(f"Working directory set to Documents: {documents_dir}")
                        break
                else:
                    # Fall back to home directory
                    os.chdir(Path.home())
                    print(f"Working directory set to home: {Path.home()}")
        except Exception as e:
            print(f"Warning: Could not set working directory: {str(e)}")
            print("Falling back to current directory")

        # Set the terminal I/O in BeamerSlideGenerator - KEEP ORIGINAL
        from BeamerSlideGenerator import set_terminal_io
        set_terminal_io(self.terminal_io)

        # Initialize presentation metadata - KEEP ORIGINAL
        self.presentation_info = {
            'title': '',
            'subtitle': '',
            'author': '',
            'institution': 'Artificial Intelligence Research and Intelligent Systems (airis4D)',
            'short_institute': 'airis4D',
            'date': '\\today'
        }

        # Configure grid - KEEP ORIGINAL
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize variables - KEEP ORIGINAL
        self.current_file = None
        self.slides = []
        self.current_slide_index = -1

        # Setup keyboard shortcuts - KEEP ORIGINAL
        self.setup_keyboard_shortcuts()

        # Setup Python paths - KEEP ORIGINAL
        setup_python_paths()

        # Adjust grid weights to accommodate terminal - KEEP ORIGINAL
        self.grid_rowconfigure(1, weight=3)  # Main editor
        self.grid_rowconfigure(4, weight=1)  # Terminal

        # Setup output redirection after terminal creation - KEEP ORIGINAL
        self.setup_output_redirection()
        self.use_enhanced_tooltips=True
        # Change to working directory if valid - KEEP ORIGINAL (duplicate in original)
        try:
            if self.session_data['working_directory']:
                os.chdir(self.session_data['working_directory'])
        except Exception as e:
            print(f"Warning: Could not change to saved working directory: {str(e)}")

        # Load last file if it exists - KEEP ORIGINAL
        if self.session_data['last_file'] and os.path.exists(self.session_data['last_file']):
            self.after(100, lambda: self.load_file(self.session_data['last_file']))

        # Bind window events - KEEP ORIGINAL
        self.bind('<Configure>', self.on_window_configure)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize spell checking - KEEP ORIGINAL but ensure it runs after UI creation
        self.setup_spellchecking()

        # Add binding to close context menu - KEEP ORIGINAL
        self.bind("<Button-1>", self.hide_spelling_menu)

        # === ENHANCED FEATURES INITIALIZATION ===

        # Initialize enhanced LaTeX help system
        self.setup_enhanced_latex_help()

        # Initialize enhanced tooltip system
        self.setup_enhanced_tooltips()

        # Auto-create first slide - KEEP ORIGINAL
        self.auto_create_first_slide()

        # Initialize Grammarly features - MODIFIED: Delay binding until after UI is ready
        self.grammarly = GrammarlyIntegration(self)
        self.setup_grammarly_integration_delayed()

        self.setup_automated_grammarly()

        # Add command index button to toolbar - KEEP ORIGINAL
        self.enhance_toolbar()

        # DELAYED: Bind Grammarly to editors (after they are definitely created)
        self.after(100, self.setup_grammarly_bindings)

        # NEW: Auto-prompt for Grammarly setup on first run (optional)
        self.after(500, self.auto_prompt_grammarly_setup)

        # Initialize enhanced features
        self.enhanced_command_index = None

        # Initialize autocomplete system (replaces old setup_autocomplete calls)
        self.autocomplete_system = IntelligentAutocomplete(self)

        # Setup enhanced features after UI is ready
        self.after(150, self.initialize_enhanced_features)

        # Add undo/redo stacks for slide operations
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_history = 50  # Limit history size

        # Add a flag for tracking deleted slides visually
        self.show_deleted_slides = True

        self.setup_line_mask_context_menu()

        # Add a status label to show current context
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready | Ctrl+Delete: Mask slide (in slide list) or mask line (in editor)",
            font=("Arial", 10),
            text_color="#888888",
            height=20
        )
        self.status_label.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))

        self.content_editor._textbox.bind('<Button-1>', self.on_line_click_to_unmask)
        self.notes_editor._textbox.bind('<Button-1>', self.on_line_click_to_unmask)

        # Call this after loading a file to debug
        self.debug_slide_data()

        self.create_line_context_menu()

        # Initialize the package manager
        self.package_manager = CrossPlatformPackageManager(parent=self, verbose=True)

        # Add to the __init__ method of BeamerSlideEditor
        self._current_citation_map = {}  # For bibliography back-references

        # Create menu bar
        self.menu_bar = MenuBar(self, self)

    def create_line_context_menu(self):
        """Create context menu for line operations in editors"""
        self.line_context_menu = tk.Menu(self, tearoff=0)
        self.line_context_menu.add_command(label="Mask/Unmask Line (Ctrl+Delete)",
                                            command=lambda: self.mask_line_in_editor())
        self.line_context_menu.add_separator()
        self.line_context_menu.add_command(label="Undo (Ctrl+Z)",
                                            command=lambda: self.undo_line_in_content() if self.focus_get() == self.content_editor._textbox else self.undo_line_in_notes())
        self.line_context_menu.add_command(label="Redo (Ctrl+Y)",
                                            command=lambda: self.redo_line_in_content() if self.focus_get() == self.content_editor._textbox else self.redo_line_in_notes())
        self.line_context_menu.add_separator()
        self.line_context_menu.add_command(label="Restore All Lines in Slide",
                                            command=self.unmask_all_lines_in_current_slide)

        # Bind to editors
        for editor in [self.content_editor._textbox, self.notes_editor._textbox]:
            editor.bind("<Button-3>", self.show_line_context_menu)

    def show_line_context_menu(self, event):
        """Show line context menu"""
        self.line_context_menu.tk_popup(event.x_root, event.y_root)

    def setup_line_undo_redo(self):
        """Setup line-level undo/redo for content and notes editors"""

        def save_content_state(event=None):
            """Save current content editor state for undo"""
            current_state = self.content_editor.get('1.0', 'end-1c')
            if current_state != self.last_content_state:
                if len(self.content_undo_stack) >= self.max_line_history:
                    self.content_undo_stack.pop(0)
                self.content_undo_stack.append(self.last_content_state)
                self.content_redo_stack.clear()
                self.last_content_state = current_state

        def save_notes_state(event=None):
            """Save current notes editor state for undo"""
            current_state = self.notes_editor.get('1.0', 'end-1c')
            if current_state != self.last_notes_state:
                if len(self.notes_undo_stack) >= self.max_line_history:
                    self.notes_undo_stack.pop(0)
                self.notes_undo_stack.append(self.last_notes_state)
                self.notes_redo_stack.clear()
                self.last_notes_state = current_state

        # Bind events to save state
        self.content_editor._textbox.bind('<KeyRelease>', save_content_state)
        self.notes_editor._textbox.bind('<KeyRelease>', save_notes_state)

        # Also save on focus loss
        self.content_editor._textbox.bind('<FocusOut>', save_content_state)
        self.notes_editor._textbox.bind('<FocusOut>', save_notes_state)

    def undo_line_in_content(self, event=None):
        """Undo last change in content editor"""
        if self.content_undo_stack:
            # Save current state to redo stack
            current_state = self.content_editor.get('1.0', 'end-1c')
            self.content_redo_stack.append(current_state)

            # Restore previous state
            previous_state = self.content_undo_stack.pop()
            self.content_editor.delete('1.0', 'end')
            self.content_editor.insert('1.0', previous_state)
            self.last_content_state = previous_state

            self.write("↩ Undo in content editor\n", "cyan")
            return "break"
        else:
            self.write("Nothing to undo in content editor\n", "yellow")
            return "break"

    def redo_line_in_content(self, event=None):
        """Redo last undone change in content editor"""
        if self.content_redo_stack:
            # Save current state to undo stack
            current_state = self.content_editor.get('1.0', 'end-1c')
            self.content_undo_stack.append(current_state)

            # Restore redone state
            redone_state = self.content_redo_stack.pop()
            self.content_editor.delete('1.0', 'end')
            self.content_editor.insert('1.0', redone_state)
            self.last_content_state = redone_state

            self.write("↪ Redo in content editor\n", "cyan")
            return "break"
        else:
            self.write("Nothing to redo in content editor\n", "yellow")
            return "break"

    def undo_line_in_notes(self, event=None):
        """Undo last change in notes editor"""
        if self.notes_undo_stack:
            current_state = self.notes_editor.get('1.0', 'end-1c')
            self.notes_redo_stack.append(current_state)

            previous_state = self.notes_undo_stack.pop()
            self.notes_editor.delete('1.0', 'end')
            self.notes_editor.insert('1.0', previous_state)
            self.last_notes_state = previous_state

            self.write("↩ Undo in notes editor\n", "cyan")
            return "break"
        else:
            self.write("Nothing to undo in notes editor\n", "yellow")
            return "break"

    def redo_line_in_notes(self, event=None):
        """Redo last undone change in notes editor"""
        if self.notes_redo_stack:
            current_state = self.notes_editor.get('1.0', 'end-1c')
            self.notes_undo_stack.append(current_state)

            redone_state = self.notes_redo_stack.pop()
            self.notes_editor.delete('1.0', 'end')
            self.notes_editor.insert('1.0', redone_state)
            self.last_notes_state = redone_state

            self.write("↪ Redo in notes editor\n", "cyan")
            return "break"
        else:
            self.write("Nothing to redo in notes editor\n", "yellow")
            return "break"

    def mask_slide(self, slide_index: int) -> bool:
        """Mask a slide - completely remove it from TeX output"""
        if not 0 <= slide_index < len(self.slides):
            return False

        # Don't mask already masked slides
        if self.is_slide_masked(slide_index):
            return False

        # Save to undo stack
        original_slide = self._deep_copy_slide(self.slides[slide_index])

        # Mark as fully masked - this will cause it to be skipped in TeX generation
        self.slides[slide_index]['_fully_masked'] = True

        # Also add [DELETED] to title for visual indication
        if not self.slides[slide_index]['title'].startswith('[DELETED]'):
            self.slides[slide_index]['title'] = f"[DELETED] {self.slides[slide_index]['title']}"

        # Save to undo stack
        self._push_to_undo_stack({
            'action': 'mask',
            'index': slide_index,
            'original': original_slide,
            'masked': self.slides[slide_index]
        })

        # Clear redo stack
        self.redo_stack.clear()

        # Update UI
        self.update_slide_list()
        if self.current_slide_index == slide_index:
            # Move to next slide if current was masked
            if slide_index + 1 < len(self.slides):
                self.current_slide_index = slide_index + 1
            elif slide_index > 0:
                self.current_slide_index = slide_index - 1
            self.load_slide(self.current_slide_index)

        self.write(f"✓ Slide {slide_index + 1} masked (will be excluded from PDF)\n", "yellow")
        return True

    def unmask_slide(self, slide_index: int) -> bool:
        """
        Restore a masked slide to its original state.
        Returns True if successful, False otherwise.
        """
        if not 0 <= slide_index < len(self.slides):
            return False

        # Only unmask if it's actually masked
        if not self.is_slide_masked(slide_index):
            return False

        # Create a deep copy for undo history
        current_slide = self._deep_copy_slide(self.slides[slide_index])

        # Restore original content by removing comment markers
        restored_slide = self._restore_from_masked_slide(current_slide)

        # Save to undo stack
        self._push_to_undo_stack({
            'action': 'unmask',
            'index': slide_index,
            'original': current_slide,
            'restored': restored_slide
        })

        # Apply restoration
        self.slides[slide_index] = restored_slide

        # Clear redo stack
        self.redo_stack.clear()

        # Update UI
        self.update_slide_list()
        if self.current_slide_index == slide_index:
            self.load_slide(slide_index)

        self.write(f"✓ Slide {slide_index + 1} restored\n", "green")
        return True

    def delete_slide(self) -> None:
        """Modified delete_slide that masks instead of deleting and advances to next slide"""
        if self.current_slide_index >= 0 and self.current_slide_index < len(self.slides):
            if self.is_slide_masked(self.current_slide_index):
                # Ask for confirmation for permanent deletion of already masked slide
                if messagebox.askyesno("Permanent Delete",
                                       f"Slide {self.current_slide_index + 1} is already masked.\n\n"
                                       "Do you want to permanently delete it?\n"
                                       "This action cannot be undone with Ctrl+Z."):
                    deleted_index = self.current_slide_index
                    self._permanently_delete_slide(deleted_index)
                    self.write(f"✓ Slide {deleted_index + 1} permanently deleted\n", "red")

                    # After permanent deletion, move to appropriate slide
                    if self.slides:
                        if deleted_index >= len(self.slides):
                            self.current_slide_index = len(self.slides) - 1
                        else:
                            self.current_slide_index = deleted_index
                        self.load_slide(self.current_slide_index)
                    else:
                        self.clear_editor()
            else:
                # Mask the slide and advance
                self.mask_slide(self.current_slide_index)
                self.write(f"✓ Slide {self.current_slide_index + 1} masked (marked as deleted)\n", "yellow")

                # Advance to next slide
                if self.current_slide_index + 1 < len(self.slides):
                    self.current_slide_index += 1
                    self.load_slide(self.current_slide_index)
                    self.write(f"→ Advanced to slide {self.current_slide_index + 1}\n", "cyan")
                elif self.current_slide_index > 0:
                    self.current_slide_index -= 1
                    self.load_slide(self.current_slide_index)
                    self.write(f"← Reached end, moved to previous slide {self.current_slide_index + 1}\n", "cyan")

                self.update_slide_list()
                self.highlight_current_slide()
        else:
            messagebox.showwarning("Warning", "No slide to delete!")

    def _permanently_delete_slide(self, index: int) -> None:
        """Permanently remove a slide and update navigation"""
        if 0 <= index < len(self.slides):
            # Save to undo stack for potential restoration
            self._push_to_undo_stack({
                'action': 'permanent_delete',
                'index': index,
                'slide': self._deep_copy_slide(self.slides[index])
            })

            del self.slides[index]

            # Update current slide index after deletion
            if self.slides:
                if index >= len(self.slides):
                    # Deleted the last slide, move to previous
                    self.current_slide_index = len(self.slides) - 1
                else:
                    # Stay at same index (next slide shifts into place)
                    self.current_slide_index = index
            else:
                self.current_slide_index = -1

            self.redo_stack.clear()
            self.update_slide_list()

            if self.current_slide_index >= 0:
                self.load_slide(self.current_slide_index)
            else:
                self.clear_editor()

            self.write(f"✓ Slide {index + 1} permanently deleted\n", "red")

    def undo(self) -> None:
        """Undo the last slide operation (mask/unmask/delete)"""
        if not self.undo_stack:
            self.write("Nothing to undo\n", "yellow")
            return

        action = self.undo_stack.pop()

        # Save current state to redo stack
        current_state = self._get_current_slide_state(action['index']) if 'index' in action else None

        if action['action'] == 'mask':
            # Restore original slide
            self.slides[action['index']] = self._deep_copy_slide(action['original'])
            self._push_to_redo_stack({
                'action': 'unmask',
                'index': action['index'],
                'original': action['masked'],
                'restored': action['original']
            })
            self.write(f"↩ Undo: Restored slide {action['index'] + 1}\n", "cyan")

        elif action['action'] == 'unmask':
            # Re-mask the slide
            self.slides[action['index']] = self._deep_copy_slide(action['original'])
            self._push_to_redo_stack({
                'action': 'mask',
                'index': action['index'],
                'original': action['restored'],
                'masked': action['original']
            })
            self.write(f"↩ Undo: Re-masked slide {action['index'] + 1}\n", "cyan")

        elif action['action'] == 'permanent_delete':
            # Restore permanently deleted slide
            self.slides.insert(action['index'], self._deep_copy_slide(action['slide']))
            self._push_to_redo_stack({
                'action': 'permanent_delete_redo',
                'index': action['index'],
                'slide': action['slide']
            })
            self.write(f"↩ Undo: Restored permanently deleted slide {action['index'] + 1}\n", "cyan")

        # Update UI
        if 'index' in action:
            self.current_slide_index = action['index']
        self.update_slide_list()
        if self.current_slide_index >= 0:
            self.load_slide(self.current_slide_index)
        self.highlight_current_slide()

    def redo(self) -> None:
        """Redo a previously undone slide operation"""
        if not self.redo_stack:
            self.write("Nothing to redo\n", "yellow")
            return

        action = self.redo_stack.pop()

        if action['action'] == 'mask':
            self.mask_slide(action['index'])
        elif action['action'] == 'unmask':
            self.unmask_slide(action['index'])
        elif action['action'] == 'permanent_delete_redo':
            self._permanently_delete_slide(action['index'])

        self.write(f"↪ Redo: Applied {action['action']} on slide {action['index'] + 1}\n", "cyan")

    def is_slide_masked(self, slide_index: int) -> bool:
        """Check if a slide is masked (deleted)"""
        if not 0 <= slide_index < len(self.slides):
            return False

        slide = self.slides[slide_index]

        # Check if content items are commented
        content_masked = all(
            item.strip().startswith('%') or not item.strip()
            for item in slide.get('content', [])
        )

        # Check if notes are commented
        notes_masked = all(
            note.strip().startswith('%') or not note.strip()
            for note in slide.get('notes', [])
        )

        # A slide is considered masked if all its content is commented
        return content_masked and (not slide.get('notes') or notes_masked)

    def _create_masked_slide(self, slide: dict) -> dict:
        """Create a masked version of a slide"""
        masked_slide = self._deep_copy_slide(slide)

        # Mask content items
        masked_slide['content'] = [
            f"% {item}" if item.strip() and not item.strip().startswith('%') else item
            for item in masked_slide.get('content', [])
        ]

        # Mask notes
        if 'notes' in masked_slide:
            masked_slide['notes'] = [
                f"% {note}" if note.strip() and not note.strip().startswith('%') else note
                for note in masked_slide.get('notes', [])
            ]

        # Add a marker to the title if not already marked
        if not masked_slide['title'].startswith('[DELETED]'):
            masked_slide['title'] = f"[DELETED] {masked_slide['title']}"

        return masked_slide

    def _restore_from_masked_slide(self, masked_slide: dict) -> dict:
        """Restore a masked slide to its original state"""
        restored_slide = self._deep_copy_slide(masked_slide)

        # Remove comment markers from content
        restored_slide['content'] = [
            item[2:] if item.strip().startswith('%') else item
            for item in restored_slide.get('content', [])
        ]

        # Remove comment markers from notes
        if 'notes' in restored_slide:
            restored_slide['notes'] = [
                note[2:] if note.strip().startswith('%') else note
                for note in restored_slide.get('notes', [])
            ]

        # Remove [DELETED] marker from title
        if restored_slide['title'].startswith('[DELETED]'):
            restored_slide['title'] = restored_slide['title'][10:].strip()

        return restored_slide

    def _deep_copy_slide(self, slide: dict) -> dict:
        """Create a deep copy of a slide dictionary"""
        return {
            'title': slide.get('title', ''),
            'media': slide.get('media', ''),
            'content': slide.get('content', []).copy(),
            'notes': slide.get('notes', []).copy()
        }

    def _push_to_undo_stack(self, action: dict) -> None:
        """Push an action to the undo stack with size limit"""
        self.undo_stack.append(action)
        if len(self.undo_stack) > self.max_undo_history:
            self.undo_stack.pop(0)

    def _push_to_redo_stack(self, action: dict) -> None:
        """Push an action to the redo stack with size limit"""
        self.redo_stack.append(action)
        if len(self.redo_stack) > self.max_undo_history:
            self.redo_stack.pop(0)

    def _get_current_slide_state(self, index: int) -> dict:
        """Get current state of a slide for redo stack"""
        if 0 <= index < len(self.slides):
            return self._deep_copy_slide(self.slides[index])
        return None

    def update_slide_list(self):
        """Modified update_slide_list to show masked slides differently with safe tag handling"""
        # Clear the slide list first
        self.slide_list.delete('1.0', 'end')

        # Remove any existing tags to avoid conflicts (safe to do)
        try:
            for tag in ['current_slide', 'deleted_slide', 'deleted_current', 'normal_slide']:
                self.slide_list.tag_delete(tag)
        except:
            pass  # Tags might not exist yet

        # Configure tags fresh each time
        self.slide_list.tag_config('current_slide', background='#2F3542', foreground='#FFFFFF')
        self.slide_list.tag_config('deleted_slide', foreground='#888888')
        self.slide_list.tag_config('deleted_current', background='#2F3542', foreground='#888888')
        self.slide_list.tag_config('normal_slide', foreground='#FFFFFF')

        # Add each slide to the list
        for i, slide in enumerate(self.slides):
            is_current = (i == self.current_slide_index)
            prefix = "→ " if is_current else "  "

            title = slide.get('title', 'Untitled')
            is_masked = self.is_slide_masked(i)

            if is_masked:
                # Clean title by removing [DELETED] prefix for cleaner display
                display_title = title.replace('[DELETED]', '').strip()
                if not display_title:
                    display_title = "Untitled"

                # Format the line for deleted slide
                line_text = f"{prefix}🗑 DELETED: {display_title}\n"
                self.slide_list.insert('end', line_text)

                # Apply appropriate tag based on whether it's current
                line_start = f"{i+1}.0"
                line_end = f"{i+1}.end"
                if is_current:
                    self.slide_list.tag_add('deleted_current', line_start, line_end)
                else:
                    self.slide_list.tag_add('deleted_slide', line_start, line_end)
            else:
                # Normal slide
                media_type = " [None]" if not slide.get('media') or slide.get('media') == "\\None" else ""
                line_text = f"{prefix}Slide {i+1}: {title}{media_type}\n"
                self.slide_list.insert('end', line_text)

                # Apply tag for normal slide (only if not current, current handled separately)
                if not is_current:
                    line_start = f"{i+1}.0"
                    line_end = f"{i+1}.end"
                    self.slide_list.tag_add('normal_slide', line_start, line_end)

        # Highlight current slide separately
        self.highlight_current_slide()

    def highlight_current_slide(self):
        """Highlight current slide in list with proper error handling"""
        # Safety check: make sure slide_list exists and has content
        if not hasattr(self, 'slide_list') or not self.slide_list:
            return

        # Remove previous highlights safely
        try:
            self.slide_list.tag_remove('current_slide', '1.0', 'end')
            self.slide_list.tag_remove('deleted_current', '1.0', 'end')
        except:
            pass  # Tags might not exist

        # Add highlight to current slide if valid
        if self.current_slide_index >= 0 and self.current_slide_index < len(self.slides):
            try:
                start = f"{self.current_slide_index + 1}.0"
                end = f"{self.current_slide_index + 1}.end"

                # Check if the line exists
                if float(self.slide_list.index('end-1c')) >= self.current_slide_index + 1:
                    # Check if current slide is masked
                    if self.is_slide_masked(self.current_slide_index):
                        self.slide_list.tag_add('deleted_current', start, end)
                    else:
                        self.slide_list.tag_add('current_slide', start, end)

                    # Ensure the current slide is visible
                    self.slide_list.see(start)
            except Exception as e:
                print(f"Warning: Could not highlight current slide: {e}")

    def setup_keyboard_shortcuts(self) -> None:
        """Enhanced keyboard shortcuts with context-aware undo/redo and line masking"""

        # Slide-level operations (work globally but may be overridden by focused widgets)
        self.bind('<Control-n>', lambda e: self.new_slide())
        self.bind('<Control-i>', lambda e: self.insert_slide_below())
        self.bind('<Control-d>', lambda e: self.duplicate_slide())
        self.bind('<Control-s>', lambda e: self.save_file())

        # Context-sensitive Ctrl+Delete (mask slide or mask line based on focus)
        self.bind('<Control-Delete>', self.handle_ctrl_delete)

        # Context-sensitive Undo/Redo (Ctrl+Z, Ctrl+Y, Ctrl+Shift+Z)
        # These check which widget has focus and act accordingly
        self.bind('<Control-z>', self.handle_undo_redo)
        self.bind('<Control-y>', self.handle_undo_redo)
        self.bind('<Control-Shift-Z>', self.handle_undo_redo)

        # Restore deleted slide shortcut (Shift+Ctrl+R)
        self.bind('<Control-Shift-R>', lambda e: self.restore_deleted_slide())

        # Navigation shortcuts
        self.bind('<Control-Up>', lambda e: self.move_slide(-1))
        self.bind('<Control-Down>', lambda e: self.move_slide(1))

        # Quick navigation between slides
        self.bind('<Control-Right>', lambda e: self.navigate_to_next_slide())
        self.bind('<Control-Left>', lambda e: self.navigate_to_previous_slide())

        # Delete key for slide deletion when in slide list
        self.bind('<Delete>', self.handle_delete_key)

    def handle_undo_redo(self, event):
        """Handle undo/redo based on which widget has focus"""
        focused_widget = self.focus_get()

        # Check if content editor has focus
        if focused_widget == self.content_editor._textbox:
            if event.keysym == 'z' and (event.state & 0x4):  # Ctrl+Z
                return self.undo_line_in_content(event)
            elif event.keysym in ('y', 'Z') and (event.state & 0x4):  # Ctrl+Y or Ctrl+Shift+Z
                return self.redo_line_in_content(event)

        # Check if notes editor has focus
        elif focused_widget == self.notes_editor._textbox:
            if event.keysym == 'z' and (event.state & 0x4):  # Ctrl+Z
                return self.undo_line_in_notes(event)
            elif event.keysym in ('y', 'Z') and (event.state & 0x4):  # Ctrl+Y or Ctrl+Shift+Z
                return self.redo_line_in_notes(event)

        # Check if media entry has focus
        elif focused_widget == self.media_entry:
            if event.keysym == 'z' and (event.state & 0x4):
                self.undo_media_entry()
                return "break"
            elif event.keysym in ('y', 'Z') and (event.state & 0x4):
                self.redo_media_entry()
                return "break"

        # Default: slide-level undo/redo (for slide operations)
        else:
            if event.keysym == 'z' and (event.state & 0x4):  # Ctrl+Z
                self.undo()
            elif event.keysym in ('y', 'Z') and (event.state & 0x4):  # Ctrl+Y or Ctrl+Shift+Z
                self.redo()

        return "break"

    def undo_media_entry(self):
        """Undo media entry change"""
        if hasattr(self, '_media_undo_stack') and self._media_undo_stack:
            current = self.media_entry.get()
            self._media_redo_stack = getattr(self, '_media_redo_stack', [])
            self._media_redo_stack.append(current)
            previous = self._media_undo_stack.pop()
            self.media_entry.delete(0, 'end')
            self.media_entry.insert(0, previous)
            self.write("↩ Undo in media entry\n", "cyan")
        else:
            self.write("Nothing to undo in media entry\n", "yellow")

    def redo_media_entry(self):
        """Redo media entry change"""
        if hasattr(self, '_media_redo_stack') and self._media_redo_stack:
            current = self.media_entry.get()
            self._media_undo_stack = getattr(self, '_media_undo_stack', [])
            self._media_undo_stack.append(current)
            next_val = self._media_redo_stack.pop()
            self.media_entry.delete(0, 'end')
            self.media_entry.insert(0, next_val)
            self.write("↪ Redo in media entry\n", "cyan")
        else:
            self.write("Nothing to redo in media entry\n", "yellow")

    def setup_media_entry_undo(self):
        """Setup undo/redo for media entry"""
        self._media_undo_stack = []
        self._media_redo_stack = []
        self._last_media_state = ""

        def save_media_state(event=None):
            current = self.media_entry.get()
            if current != self._last_media_state:
                if len(self._media_undo_stack) >= 50:
                    self._media_undo_stack.pop(0)
                self._media_undo_stack.append(self._last_media_state)
                self._media_redo_stack.clear()
                self._last_media_state = current

        self.media_entry.bind('<KeyRelease>', save_media_state)
        self.media_entry.bind('<FocusOut>', save_media_state)


    def navigate_to_next_slide(self):
        """Navigate to next slide"""
        if self.current_slide_index + 1 < len(self.slides):
            self.save_current_slide()
            self.current_slide_index += 1
            self.load_slide(self.current_slide_index)
            self.update_slide_list()
            self.highlight_current_slide()
            self.slide_list.see(f"{self.current_slide_index + 1}.0")
            self.write(f"→ Navigated to slide {self.current_slide_index + 1}\n", "cyan")

    def navigate_to_previous_slide(self):
        """Navigate to previous slide"""
        if self.current_slide_index > 0:
            self.save_current_slide()
            self.current_slide_index -= 1
            self.load_slide(self.current_slide_index)
            self.update_slide_list()
            self.highlight_current_slide()
            self.slide_list.see(f"{self.current_slide_index + 1}.0")
            self.write(f"← Navigated to slide {self.current_slide_index + 1}\n", "cyan")

    def restore_deleted_slide(self) -> None:
        """Restore the currently selected slide if it's deleted"""
        if self.current_slide_index >= 0 and self.is_slide_masked(self.current_slide_index):
            self.unmask_slide(self.current_slide_index)
        else:
            self.write("Current slide is not deleted\n", "yellow")

    def restore_all_deleted_slides(self) -> None:
        """Restore all masked (deleted) slides"""
        restored_count = 0
        for i in range(len(self.slides) - 1, -1, -1):
            if self.is_slide_masked(i):
                self.unmask_slide(i)
                restored_count += 1

        if restored_count > 0:
            self.write(f"✓ Restored {restored_count} deleted slide(s)\n", "green")
        else:
            self.write("No deleted slides to restore\n", "yellow")

    def permanently_delete_masked_slides(self) -> None:
        """Permanently delete all masked slides"""
        if not any(self.is_slide_masked(i) for i in range(len(self.slides))):
            self.write("No deleted slides to permanently remove\n", "yellow")
            return

        if messagebox.askyesno("Confirm",
                               "This will permanently delete all masked slides.\n"
                               "This action cannot be undone.\n\n"
                               "Continue?"):

            # Create new list without masked slides
            new_slides = []
            for slide in self.slides:
                if not self.is_slide_masked(len(new_slides)):
                    new_slides.append(slide)

            removed_count = len(self.slides) - len(new_slides)
            self.slides = new_slides

            # Adjust current slide index
            if self.current_slide_index >= len(self.slides):
                self.current_slide_index = len(self.slides) - 1

            self.update_slide_list()
            if self.current_slide_index >= 0:
                self.load_slide(self.current_slide_index)

            self.write(f"✓ Permanently removed {removed_count} slide(s)\n", "red")

    def handle_ctrl_delete(self, event):
        """Context-sensitive handler for Ctrl+Delete"""
        focused_widget = self.focus_get()

        # Update status to show current context
        if focused_widget == self.slide_list._textbox:
            self.status_label.configure(text="Ctrl+Delete: Masking current slide...", text_color="#4ECDC4")
            self.after(2000, lambda: self.status_label.configure(text="Ready | Ctrl+Delete: Mask slide (in slide list) or mask line (in editor)", text_color="#888888"))
            self.mask_current_slide()
            return "break"

        elif focused_widget == self.content_editor._textbox:
            self.status_label.configure(text="Ctrl+Delete: Masking/unmasking current line in content editor...", text_color="#4ECDC4")
            self.after(2000, lambda: self.status_label.configure(text="Ready | Ctrl+Delete: Mask slide (in slide list) or mask line (in editor)", text_color="#888888"))
            self.mask_line_in_editor(event)
            return "break"

        elif focused_widget == self.notes_editor._textbox:
            self.status_label.configure(text="Ctrl+Delete: Masking/unmasking current line in notes editor...", text_color="#4ECDC4")
            self.after(2000, lambda: self.status_label.configure(text="Ready | Ctrl+Delete: Mask slide (in slide list) or mask line (in editor)", text_color="#888888"))
            self.mask_line_in_editor(event)
            return "break"

        elif focused_widget == self.media_entry:
            self.status_label.configure(text="Ctrl+Delete: Masking/unmasking media entry...", text_color="#4ECDC4")
            self.after(2000, lambda: self.status_label.configure(text="Ready | Ctrl+Delete: Mask slide (in slide list) or mask line (in editor)", text_color="#888888"))
            self.mask_media_entry()
            return "break"

        self.mask_current_slide()
        return "break"

    def handle_delete_key(self, event):
        """Handle plain Delete key - context-sensitive"""
        focused_widget = self.focus_get()

        # In slide list: delete/mask slide
        if focused_widget == self.slide_list._textbox:
            self.delete_slide()
            return "break"

        # In editors: let normal delete behavior happen
        return None

    def mask_current_slide(self):
        """Mask the currently selected slide and advance to next slide"""
        if self.current_slide_index >= 0 and self.current_slide_index < len(self.slides):
            if self.is_slide_masked(self.current_slide_index):
                # If already masked, ask if user wants to permanently delete
                if messagebox.askyesno("Delete Slide",
                                       f"Slide {self.current_slide_index + 1} is already masked.\n\n"
                                       "Do you want to permanently delete it?\n"
                                       "This action cannot be undone with Ctrl+Z."):
                    # Store the index before deletion
                    deleted_index = self.current_slide_index
                    self._permanently_delete_slide(deleted_index)
                    self.write(f"✓ Slide {deleted_index + 1} permanently deleted\n", "red")

                    # After permanent deletion, move to appropriate slide
                    if self.slides:
                        # If we deleted the last slide, move to previous
                        if deleted_index >= len(self.slides):
                            self.current_slide_index = len(self.slides) - 1
                        else:
                            # Otherwise stay at same index (next slide shifts into place)
                            self.current_slide_index = deleted_index
                        self.load_slide(self.current_slide_index)
                    else:
                        self.clear_editor()
            else:
                # Mask the slide
                self.mask_slide(self.current_slide_index)
                self.write(f"✓ Slide {self.current_slide_index + 1} masked (marked as deleted)\n", "yellow")

                # ADVANCE TO NEXT SLIDE AFTER MASKING
                if self.current_slide_index + 1 < len(self.slides):
                    # Move to next slide
                    self.current_slide_index += 1
                    self.load_slide(self.current_slide_index)
                    self.update_slide_list()
                    self.write(f"→ Advanced to slide {self.current_slide_index + 1}\n", "cyan")
                elif self.current_slide_index > 0:
                    # If this was the last slide, move to previous slide
                    self.current_slide_index -= 1
                    self.load_slide(self.current_slide_index)
                    self.update_slide_list()
                    self.write(f"← Reached end, moved to previous slide {self.current_slide_index + 1}\n", "cyan")
                else:
                    # Only one slide exists
                    self.update_slide_list()
                    self.write("ℹ No more slides to advance to\n", "yellow")

                # Ensure the current slide is highlighted in the list
                self.highlight_current_slide()
                self.slide_list.see(f"{self.current_slide_index + 1}.0")
        else:
            self.write("No slide to mask/delete\n", "yellow")

    def mask_media_entry(self):
        """Mask/unmask the media entry line"""
        current_media = self.media_entry.get()

        if current_media.startswith('%'):
            # Unmask: remove the % prefix
            unmasked = current_media.lstrip('%').lstrip()
            self.media_entry.delete(0, 'end')
            self.media_entry.insert(0, unmasked)
            self.write("✓ Media entry unmasked\n", "green")
            # Update the slide's media_masked flag
            if 0 <= self.current_slide_index < len(self.slides):
                self.slides[self.current_slide_index]['_media_masked'] = False
        else:
            # Mask: add % at beginning
            self.media_entry.delete(0, 'end')
            self.media_entry.insert(0, f"% {current_media}")
            self.write("✓ Media entry masked\n", "yellow")
            # Update the slide's media_masked flag
            if 0 <= self.current_slide_index < len(self.slides):
                self.slides[self.current_slide_index]['_media_masked'] = True

        # Save the change
        self.save_current_slide()

    def setup_enhanced_latex_help(self):
        """Setup enhanced LaTeX help using only EnhancedCommandDialog"""
        try:
            if ENHANCED_FEATURES_AVAILABLE:
                from EnhancedCommandDialog import LatexCommandHelper
                self.command_helper = LatexCommandHelper()
                self.use_enhanced_latex = True
                print("✓ Enhanced LaTeX help system loaded from EnhancedCommandDialog")
            else:
                # Fallback to basic implementation
                from Grammarly import LatexCommandHelper
                self.command_helper = LatexCommandHelper()
                self.use_enhanced_latex = False
                print("Using basic LaTeX help system")
        except ImportError as e:
            print(f"Error setting up LaTeX help: {e}")
            self.setup_basic_latex_help()

    def setup_enhanced_tooltips(self):
        """Setup enhanced command tooltips using only EnhancedCommandDialog"""
        try:
            if ENHANCED_FEATURES_AVAILABLE:
                from EnhancedCommandDialog import CommandTooltip
                self.tooltip_manager = CommandTooltip(self)
                self.use_enhanced_tooltips = True
                print("✓ Enhanced command tooltips loaded from EnhancedCommandDialog")
            else:
                # Fallback to basic implementation
                from Grammarly import CommandTooltip
                self.tooltip_manager = CommandTooltip(self)
                self.use_enhanced_tooltips = False
                print("Using basic command tooltips")
        except ImportError as e:
            print(f"Error setting up tooltips: {e}")
            self.tooltip_manager = None

    def show_enhanced_command_index(self):
        """Show the enhanced command index - simplified version"""
        try:
            if ENHANCED_FEATURES_AVAILABLE:
                from EnhancedCommandDialog import EnhancedCommandIndexDialog
                self.enhanced_command_index = EnhancedCommandIndexDialog(self)

                def on_closed():
                    if hasattr(self.enhanced_command_index, 'selected_command'):
                        command = self.enhanced_command_index.selected_command
                        if command:
                            self.insert_command_into_editor(command)
                    self.enhanced_command_index = None

                self.enhanced_command_index.protocol("WM_DELETE_WINDOW", on_closed)
            else:
                self.show_fallback_command_reference()
        except Exception as e:
            print(f"Error showing command index: {e}")
            self.show_fallback_command_reference()

    def initialize_enhanced_features(self):
        """Initialize enhanced features after UI is ready"""
        # Setup enhanced autocomplete
        self.setup_autocomplete()

        # Setup enhanced tooltips
        self.setup_command_tooltips()

    def setup_autocomplete(self):
        """Setup autocomplete system for editors"""
        self.autocomplete_system.setup_autocomplete(self.content_editor._textbox)
        self.autocomplete_system.setup_autocomplete(self.notes_editor._textbox)

    def setup_command_tooltips(self):
        """Setup command tooltip bindings for editors"""
        # Enhanced tooltips handle their own bindings automatically
        if self.use_enhanced_tooltips:
            print("Enhanced tooltip system active")
        else:
            # Fallback to basic tooltip setup
            self.setup_editor_tooltips(self.content_editor._textbox)
            self.setup_editor_tooltips(self.notes_editor._textbox)
            self.setup_entry_tooltips(self.media_entry)
#-----------------Init ends ----------------------------

    def setup_basic_latex_help(self):
        """Fallback to basic LaTeX help"""
        self.command_helper = LatexCommandHelper()
        self.autocomplete_system = None
        print("Using basic LaTeX help system")

    def setup_line_mask_context_menu(self):
        """Setup context menu for line masking in editors"""
        self.line_mask_menu = tk.Menu(self, tearoff=0)
        self.line_mask_menu.add_command(label="Mask/Unmask Line (Ctrl+Delete)",
                                        command=lambda: self.mask_line_in_editor())
        self.line_mask_menu.add_separator()
        self.line_mask_menu.add_command(label="Mask Multiple Lines...",
                                        command=self.mask_multiple_lines_dialog)

        # Bind to editors
        for editor in [self.content_editor._textbox, self.notes_editor._textbox]:
            editor.bind("<Button-3>", self.show_line_mask_menu)

    def show_line_mask_menu(self, event):
        """Show line mask context menu"""
        self.line_mask_menu.tk_popup(event.x_root, event.y_root)

    def mask_multiple_lines_dialog(self):
        """Dialog to mask multiple lines at once"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Mask Multiple Lines")
        dialog.geometry("400x300")
        dialog.transient(self)

        ctk.CTkLabel(dialog, text="Mask lines from:").pack(pady=5)
        start_entry = ctk.CTkEntry(dialog, width=100)
        start_entry.pack(pady=5)
        start_entry.insert(0, "1")

        ctk.CTkLabel(dialog, text="to:").pack(pady=5)
        end_entry = ctk.CTkEntry(dialog, width=100)
        end_entry.pack(pady=5)

        def apply_mask():
            try:
                start = int(start_entry.get())
                end = int(end_entry.get())

                # Get focused editor
                focused = self.focus_get()
                editor = None
                if focused in [self.content_editor._textbox, self.notes_editor._textbox]:
                    editor = focused

                if editor:
                    for line_num in range(start, end + 1):
                        line_start = editor.index(f"{line_num}.0")
                        line_end = editor.index(f"{line_num}.end")
                        line_content = editor.get(line_start, line_end)

                        if not line_content.lstrip().startswith('%'):
                            editor.delete(line_start, line_end)
                            editor.insert(line_start, f"% {line_content}")

                    self.save_current_slide()
                    self.write(f"✓ Masked lines {start}-{end}\n", "yellow")
                    dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error masking lines: {str(e)}")

        ctk.CTkButton(dialog, text="Apply", command=apply_mask).pack(pady=20)

    def insert_command_into_editor(self, command_data):
        """Insert selected command into current editor using enhanced system"""
        focused_widget = self.focus_get()

        if focused_widget == self.content_editor._textbox:
            editor = self.content_editor
        elif focused_widget == self.notes_editor._textbox:
            editor = self.notes_editor
        else:
            editor = self.content_editor

        # Use enhanced command data if available
        if isinstance(command_data, dict) and 'example' in command_data:
            editor.insert("insert", command_data['example'] + "\n")
        else:
            editor.insert("insert", command_data + "\n")

    def setup_automated_grammarly(self):
        """Setup automated Grammarly integration"""
        self.auto_grammarly = AutomatedGrammarlyIntegration(self)

        # Check if Grammarly is already configured
        config_file = Path.home() / '.bsg-ide' / 'grammarly_config.json'
        if not config_file.exists():
            # Auto-prompt for setup after a delay
            self.after(2000, self.auto_prompt_grammarly)

    def auto_prompt_grammarly(self):
        """Automatically prompt for Grammarly setup"""
        if not self.grammarly.grammarly_enabled:
            response = messagebox.askyesno(
                "Grammarly Auto-Setup",
                "Would you like to set up Grammarly integration automatically?\n\n"
                "We'll guide you through the process with browser automation."
            )
            if response:
                self.auto_grammarly.automated_setup()

    def auto_prompt_grammarly_setup(self):
        """Automatically prompt for Grammarly setup if not configured"""
        if not self.grammarly.grammarly_enabled and not self.grammarly.grammarly_api_key:
            response = messagebox.askyesno(
                "Grammarly Integration",
                "Would you like to set up Grammarly integration for advanced grammar checking?\n\n"
                "This will open a setup dialog where you can enter your Grammarly API key."
            )
            if response:
                self.toggle_grammarly()  # This will show the setup dialog

    def add_grammarly_setup_option(self):
        """Add Grammarly setup option to help menu or settings"""
        # Add to your existing menu setup
        # Or create a dedicated "Setup Grammarly" button

        setup_button = ctk.CTkButton(
            self.toolbar,
            text="Setup Grammarly",
            command=self.setup_grammarly_manually,
            width=120,
            fg_color="#17a2b8",
            hover_color="#138496"
        )
        setup_button.pack(side="left", padx=5)
        self.create_tooltip(setup_button, "Set up Grammarly integration")

    def setup_grammarly_manually(self):
        """Manual Grammarly setup trigger"""
        if not self.grammarly.grammarly_enabled:
            self.grammarly.show_grammarly_dialog()
        else:
            messagebox.showinfo("Grammarly", "Grammarly is already enabled and configured.")

    def setup_grammarly_integration_delayed(self):
        """Setup Grammarly integration without immediate binding"""
        # Create Grammarly context menu
        self.grammarly_menu = tk.Menu(self, tearoff=0)
        self.grammarly_menu.add_command(label="Apply Suggestion", command=self.apply_grammarly_suggestion)
        self.grammarly_menu.add_command(label="Ignore Issue", command=self.ignore_grammarly_issue)
        self.grammarly_menu.add_separator()
        self.grammarly_menu.add_command(label="Explain Issue", command=self.explain_grammarly_issue)

    def setup_grammarly_bindings(self):
        """Setup Grammarly bindings after UI is fully created"""
        try:
            # Bind to both editors - NOW they should exist
            if hasattr(self, 'content_editor') and hasattr(self, 'notes_editor'):
                # Bind right-click to Grammarly menu
                for widget in [self.content_editor._textbox, self.notes_editor._textbox]:
                    widget.bind("<Button-3>", self.show_grammarly_menu)

                # Setup real-time Grammarly checking with debouncing
                def check_grammarly(event=None):
                    if hasattr(self, '_grammarly_timer'):
                        self.after_cancel(self._grammarly_timer)
                    self._grammarly_timer = self.after(1000, self.perform_grammarly_check)

                # Bind key release events
                self.content_editor._textbox.bind('<KeyRelease>', check_grammarly)
                self.notes_editor._textbox.bind('<KeyRelease>', check_grammarly)

            else:
                print("Warning: Editors not available for Grammarly binding")

        except Exception as e:
            print(f"Warning: Could not setup Grammarly bindings: {e}")


#---------------Help Windows -----------------------------
    def auto_create_first_slide(self):
        """Automatically create first slide on startup"""
        # Create initial slide if none exists
        if not hasattr(self, 'slides') or not self.slides:
            self.slides = [{
                'title': 'Presentation Title',
                'media': '',
                'content': ['- First bullet point'],
                'notes': ['• Speaker notes for first slide']
            }]
            self.current_slide_index = 0
            self.load_slide(0)
            self.update_slide_list()

    def setup_editor_tooltips(self, text_widget):
        """Setup tooltips for text widgets"""
        text_widget.bind('<Motion>', self.on_editor_motion)
        text_widget.bind('<Leave>', self.on_editor_leave)

    def setup_entry_tooltips(self, entry_widget):
        """Setup tooltips for entry widgets"""
        entry_widget.bind('<Motion>', self.on_entry_motion)
        entry_widget.bind('<Leave>', self.on_entry_leave)

    def on_editor_motion(self, event):
        """Handle mouse motion in editor for command detection"""
        widget = event.widget
        index = widget.index(f"@{event.x},{event.y}")

        # Get the word under cursor
        word_start = widget.index(f"{index} wordstart")
        word_end = widget.index(f"{index} wordend")
        word = widget.get(word_start, word_end)

        # Check if it's a LaTeX command
        if word.startswith('\\') and len(word) > 1:
            self.show_command_tooltip(widget, word, event.x_root, event.y_root)
        else:
            self.tooltip_manager.hide_tooltip()

    def on_entry_motion(self, event):
        """Handle mouse motion in entry for command detection"""
        widget = event.widget
        content = widget.get()

        # Simple check for commands in entry
        if '\\' in content:
            # Find command near cursor position
            cursor_pos = widget.index(tk.INSERT)
            text_before = content[:cursor_pos]
            if '\\' in text_before:
                last_slash = text_before.rfind('\\')
                next_space = content.find(' ', last_slash)
                if next_space == -1:
                    next_space = len(content)

                command = content[last_slash:next_space]
                if command.startswith('\\') and len(command) > 1:
                    self.show_command_tooltip(widget, command, event.x_root, event.y_root)
                    return

        self.tooltip_manager.hide_tooltip()

    def on_editor_leave(self, event):
        """Handle mouse leaving editor"""
        self.tooltip_manager.hide_tooltip()

    def on_entry_leave(self, event):
        """Handle mouse leaving entry"""
        self.tooltip_manager.hide_tooltip()

    def show_command_tooltip(self, widget, command, x, y):
        """Show tooltip for LaTeX command"""
        self.tooltip_manager.show_tooltip(widget, command, x, y)
#---------------Help Windows Ends Grammarly starts-------------------------
    def enhance_toolbar(self):
        """Add new features to toolbar"""
        # Add command index button
        self.command_index_button = ctk.CTkButton(
            self.toolbar,
            text="Enhanced Command Index",
            command=self.show_enhanced_command_index,  # Use enhanced version
            width=140,
            fg_color="#6f42c1",
            hover_color="#5a2d91"
        )
        self.command_index_button.pack(side="left", padx=5)

        # Add Grammarly button - FIXED: Use correct initial state
        grammarly_status = "On" if self.grammarly.grammarly_enabled else "Off"
        grammarly_color = "#28a745" if self.grammarly.grammarly_enabled else "#dc3545"

        self.grammarly_button = ctk.CTkButton(
            self.toolbar,
            text=f"Grammarly: {grammarly_status}",
            command=self.toggle_grammarly,  # Ensure this points to the correct method
            width=120,
            fg_color=grammarly_color,
            hover_color="#a71e2a"
        )
        self.grammarly_button.pack(side="left", padx=5)

        # Update tooltips
        self.create_tooltip(self.command_index_button, "Show complete command reference with examples")
        self.create_tooltip(self.grammarly_button, "Enable/disable Grammarly grammar checking")

        # Add automated Grammarly setup button
        self.auto_grammarly_button = ctk.CTkButton(
            self.toolbar,
            text="🚀 Auto-Setup Grammarly",
            command=self.auto_grammarly.automated_setup,
            width=140,
            fg_color="#FF6B35",
            hover_color="#E55A2B"
        )
        self.auto_grammarly_button.pack(side="left", padx=5)
        self.create_tooltip(self.auto_grammarly_button,
                           "Automated Grammarly setup with browser guidance")

    def show_fallback_command_reference(self):
        """Fallback command reference if dialog fails"""
        simple_commands = """
    Basic LaTeX Commands Quick Reference:

    Document Structure:
    \\title{Presentation Title} - Sets presentation title
    \\author{Author Name} - Sets author name
    \\institute{Institution} - Sets institution name
    \\date{\\today} - Sets presentation date

    Slide Content:
    \\file{media_files/image.png} - Insert image
    \\play{media_files/video.mp4} - Embed video
    - Bullet point - Creates a bullet point

    Text Formatting:
    \\textcolor{red}{Text} - Colors text
    \\textbf{Bold Text} - Bold text
    \\textit{Italic Text} - Italic text

    For complete reference, check the full Command Index.
    """

        messagebox.showinfo("LaTeX Commands Quick Reference", simple_commands)

    def insert_command_into_editor(self, command_data):
        """Insert selected command into current editor"""
        # Determine which editor has focus
        focused_widget = self.focus_get()

        if focused_widget == self.content_editor._textbox:
            editor = self.content_editor
        elif focused_widget == self.notes_editor._textbox:
            editor = self.notes_editor
        else:
            editor = self.content_editor  # Default to content editor

        # Insert the command example
        editor.insert("insert", command_data['example'] + "\n")

    def toggle_grammarly(self):
        """Toggle Grammarly integration with proper setup dialog"""
        if not self.grammarly.grammarly_enabled:
            # Show setup dialog when enabling Grammarly
            self.grammarly.show_grammarly_dialog()
        else:
            # Disable Grammarly
            self.grammarly.grammarly_enabled = False
            self.grammarly.save_grammarly_settings()
            if hasattr(self, 'grammarly_button'):
                self.grammarly_button.configure(text="Grammarly: Off", fg_color="#dc3545")
            self.write("Grammarly disabled\n", "yellow")

        # Update button state based on current status
        if self.grammarly.grammarly_enabled:
            if hasattr(self, 'grammarly_button'):
                self.grammarly_button.configure(text="Grammarly: On", fg_color="#28a745")
            self.setup_realtime_grammarly()

    def setup_realtime_grammarly(self):
        """Setup real-time Grammarly checking"""
        if not self.grammarly.grammarly_enabled:
            return

    # Bind to content changes with debouncing
    def check_grammarly(event=None):
        if hasattr(self, '_grammarly_timer'):
            self.after_cancel(self._grammarly_timer)

        self._grammarly_timer = self.after(1000, self.perform_grammarly_check)


    def perform_grammarly_check(self):
        """Perform Grammarly check on current text"""
        if not self.grammarly.grammarly_enabled:
            return

        # Get text from focused editor
        focused_widget = self.focus_get()

        if focused_widget in [self.content_editor._textbox, self.notes_editor._textbox]:
            text = focused_widget.get("1.0", "end-1c")

            if len(text.strip()) > 10:  # Only check substantial text
                suggestions = self.grammarly.check_text_grammarly(text)
                if suggestions:
                    self.grammarly.apply_grammarly_suggestions(focused_widget, suggestions)

    def setup_grammarly_integration(self):
        """Setup Grammarly integration UI"""
        # Create Grammarly context menu
        self.grammarly_menu = tk.Menu(self, tearoff=0)
        self.grammarly_menu.add_command(label="Apply Suggestion", command=self.apply_grammarly_suggestion)
        self.grammarly_menu.add_command(label="Ignore Issue", command=self.ignore_grammarly_issue)
        self.grammarly_menu.add_separator()
        self.grammarly_menu.add_command(label="Explain Issue", command=self.explain_grammarly_issue)

        # Bind right-click to Grammarly menu
        for widget in [self.content_editor._textbox, self.notes_editor._textbox]:
            widget.bind("<Button-3>", self.show_grammarly_menu)

    def show_grammarly_menu(self, event):
        """Show Grammarly context menu"""
        if not self.grammarly.grammarly_enabled:
            return

        widget = event.widget
        index = widget.index(f"@{event.x},{event.y}")

        # Check if click is on a Grammarly issue
        tags = widget.tag_names(index)
        if "grammarly_issue" in tags:
            self.current_grammarly_issue = index
            self.grammarly_menu.tk_popup(event.x_root, event.y_root)

    def apply_grammarly_suggestion(self):
        """Apply selected Grammarly suggestion"""
        # Implementation for applying suggestions
        pass

    def ignore_grammarly_issue(self):
        """Ignore Grammarly issue"""
        pass

    def explain_grammarly_issue(self):
        """Explain Grammarly issue"""
        pass

#---------------------------------------Grammarly Ends--------------------------------

    def extract_presentation_info_from_tex(self, content: str) -> None:
        """Extract presentation metadata from TeX content"""
        import re

        # Patterns for extracting presentation info
        patterns = {
            'title': r'\\title{([^}]*)}',
            'subtitle': r'\\subtitle{([^}]*)}',
            'author': r'\\author{([^}]*)}',
            'institute': r'\\institute{([^}]*)}',
            'date': r'\\date{([^}]*)}'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                # Clean up LaTeX formatting
                value = match.group(1)
                value = re.sub(r'\\textcolor{[^}]*}{([^}]*)}', r'\1', value)
                value = re.sub(r'\\[a-zA-Z]+{([^}]*)}', r'\1', value)
                self.presentation_info[key] = value.strip()

        # Extract logo if present
        logo_match = re.search(r'\\logo{([^}]*)}', content)
        if logo_match:
            logo_content = logo_match.group(1)
            # Extract image path from includegraphics
            img_match = re.search(r'\\includegraphics(?:\[[^\]]*\])?{([^}]*)}', logo_content)
            if img_match:
                self.presentation_info['logo'] = img_match.group(1)

    def enhanced_extract_slides_from_tex(self, content: str) -> list:
        """Enhanced slide extraction with comprehensive LaTeX feature support"""
        slides = []
        import re

        # First isolate the document body
        doc_match = re.search(r'\\begin{document}(.*?)\\end{document}', content, re.DOTALL)
        if not doc_match:
            self.write("✗ Could not find document body\n", "red")
            return slides

        document_content = doc_match.group(1)

        # Extract preamble information
        preamble_info = self.extract_preamble_info(content)

        # Enhanced frame detection with multiple patterns
        frame_patterns = [
            r'\\begin{frame}(?:\[[^\]]*\])?(?:{([^}]*)})?(.*?)\\end{frame}',
            r'\\frame(?:\[[^\]]*\])?(?:{([^}]*)})?{(.*?)}'
        ]

        all_frames = []
        for pattern in frame_patterns:
            frames = re.finditer(pattern, document_content, re.DOTALL)
            all_frames.extend(frames)

        if not all_frames:
            self.write("✗ No frames found in document\n", "red")
            return slides

        self.write(f"Found {len(all_frames)} frames in document\n", "green")

        for i, frame_match in enumerate(all_frames):
            try:
                title = frame_match.group(1) if frame_match.group(1) else ""
                frame_content = frame_match.group(2) if frame_match.group(2) else ""

                # Skip title page frames but preserve their content
                if '\\titlepage' in frame_content or '\\maketitle' in frame_content:
                    self.write(f"Processing title frame {i+1}\n", "yellow")
                    # Extract title page content - use the correct method name
                    try:
                        title_slide = self.process_title_frame(frame_content, preamble_info)
                        if title_slide:
                            slides.append(title_slide)
                    except AttributeError:
                        # If process_title_frame doesn't exist, create a basic title slide
                        self.write(f"Warning: Could not process title frame {i+1}\n", "yellow")
                        title_slide = {
                            'title': 'Title Page',
                            'media': '',
                            'content': [
                                f"\\title{{{preamble_info.get('title', '')}}}",
                                f"\\author{{{preamble_info.get('author', '')}}}",
                                f"\\date{{{preamble_info.get('date', '')}}}",
                                f"\\institute{{{preamble_info.get('institute', '')}}}",
                                "\\titlepage"
                            ],
                            'notes': [],
                            'preamble_info': preamble_info
                        }
                        slides.append(title_slide)
                    continue

                # Extract frametitle if no title in frame declaration
                if not title:
                    ft_match = re.search(r'\\frametitle{([^}]*)}', frame_content)
                    if ft_match:
                        title = ft_match.group(1)

                # Extract framesubtitle
                subtitle = ""
                subtitle_match = re.search(r'\\framesubtitle{([^}]*)}', frame_content)
                if subtitle_match:
                    subtitle = subtitle_match.group(1)

                # Clean title and subtitle
                if title:
                    title = self.clean_latex_content(title)
                else:
                    title = f"Slide {i+1}"

                if subtitle:
                    title += f" - {self.clean_latex_content(subtitle)}"

                # Extract media including TikZ diagrams
                media = self.extract_enhanced_media_from_frame(frame_content)

                # Extract content with enhanced LaTeX support
                content_items = self.extract_enhanced_content_from_frame(frame_content)

                # Extract notes with proper formatting
                notes = self.extract_enhanced_notes_from_frame(frame_content)

                slide_data = {
                    'title': title,
                    'media': media,
                    'content': content_items,
                    'notes': notes,
                    'preamble_info': preamble_info
                }

                slides.append(slide_data)
                self.write(f"✓ Processed slide: {title}\n", "green")

            except Exception as e:
                self.write(f"✗ Error processing frame {i+1}: {str(e)}\n", "red")
                continue

        return slides

    def extract_preamble_info(self, content: str) -> dict:
        """Extract preamble information including themes and packages"""
        preamble_info = {
            'theme': '',
            'packages': [],
            'title': '',
            'author': '',
            'date': '',
            'institute': ''
        }

        import re

        # Extract theme
        theme_match = re.search(r'\\usetheme{([^}]*)}', content)
        if theme_match:
            preamble_info['theme'] = theme_match.group(1)

        # Extract packages
        package_matches = re.findall(r'\\usepackage(?:\[[^\]]*\])?{([^}]*)}', content)
        preamble_info['packages'] = package_matches

        # Extract document info
        title_match = re.search(r'\\title{([^}]*)}', content)
        if title_match:
            preamble_info['title'] = self.clean_latex_content(title_match.group(1))

        author_match = re.search(r'\\author{([^}]*)}', content)
        if author_match:
            preamble_info['author'] = self.clean_latex_content(author_match.group(1))

        date_match = re.search(r'\\date{([^}]*)}', content)
        if date_match:
            preamble_info['date'] = self.clean_latex_content(date_match.group(1))

        institute_match = re.search(r'\\institute{([^}]*)}', content)
        if institute_match:
            preamble_info['institute'] = self.clean_latex_content(institute_match.group(1))

        return preamble_info

    def process_title_frame(self, frame_content: str, preamble_info: dict) -> dict:
        """Process title page frames with better error handling"""
        try:
            title_slide = {
                'title': 'Title Page',
                'media': '',
                'content': [],
                'notes': [],
                'preamble_info': preamble_info  # Add this to preserve preamble info
            }

            # Add title information to content with safe dictionary access
            if preamble_info.get('title'):
                title_slide['content'].append(f"\\title{{{preamble_info['title']}}}")

            if preamble_info.get('author'):
                title_slide['content'].append(f"\\author{{{preamble_info['author']}}}")

            if preamble_info.get('date'):
                title_slide['content'].append(f"\\date{{{preamble_info['date']}}}")

            if preamble_info.get('institute'):
                title_slide['content'].append(f"\\institute{{{preamble_info['institute']}}}")

            # Add title page command
            title_slide['content'].append("\\titlepage")

            return title_slide

        except Exception as e:
            # Log the error but return a basic title slide
            print(f"Warning: Error in process_title_frame: {str(e)}")
            # Return minimal title slide
            return {
                'title': 'Title Page',
                'media': '',
                'content': ["\\titlepage"],
                'notes': [],
                'preamble_info': preamble_info
            }

    def extract_enhanced_media_from_frame(self, frame_content: str) -> str:
        """Extract media including TikZ diagrams and graphics"""
        import re

        media_components = []

        # Check for graphics
        graphics_matches = re.finditer(r'\\includegraphics(?:\[[^\]]*\])?{([^}]*)}', frame_content)
        for match in graphics_matches:
            media_path = match.group(1)
            media_components.append(f"\\file {media_path}")

        # Check for TikZ environments
        tikz_matches = re.finditer(r'\\begin{tikzpicture}(.*?)\\end{tikzpicture}', frame_content, re.DOTALL)
        for i, match in enumerate(tikz_matches):
            tikz_content = match.group(0).strip()
            # Save TikZ code as a separate file or include it directly
            filename = f"tikz_diagram_{i+1}.tex"
            media_components.append(f"% TikZ Diagram {i+1}:\n{tikz_content}")

        # Check for movies/videos
        movie_match = re.search(r'\\movie(?:\[[^\]]*\])?{[^}]*}{([^}]*)}', frame_content)
        if movie_match:
            media_path = movie_match.group(1)
            media_components.append(f"\\play {media_path}")

        return "\n".join(media_components) if media_components else ""

    def extract_enhanced_content_from_frame(self, frame_content: str) -> list:
        """Extract content with enhanced LaTeX feature support"""
        import re

        content_items = []

        # Remove notes and media commands to isolate main content
        clean_content = re.sub(r'\\note{.*?}', '', frame_content, flags=re.DOTALL)
        clean_content = re.sub(r'\\includegraphics[^}]*}|\\movie[^}]*}|\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', '', clean_content, flags=re.DOTALL)

        # Extract blocks (block, example, alertblock)
        block_patterns = [
            (r'\\begin\{block\}\{([^}]*)\}(.*?)\\end\{block\}', 'block'),
            (r'\\begin\{example\}\{([^}]*)\}(.*?)\\end\{example\}', 'example'),
            (r'\\begin\{alertblock\}\{([^}]*)\}(.*?)\\end\{alertblock\}', 'alertblock'),
            (r'\\begin\{columns\}(.*?)\\end\{columns\}', 'columns')
        ]

        for pattern, block_type in block_patterns:
            blocks = re.finditer(pattern, clean_content, re.DOTALL)
            for block in blocks:
                if block_type == 'columns':
                    # Process columns environment
                    columns_content = self.process_columns_environment(block.group(1))
                    content_items.extend(columns_content)
                else:
                    title = self.clean_latex_content(block.group(1))
                    content = self.clean_latex_content(block.group(2))
                    content_items.append(f"\\begin{{{block_type}}}{{{title}}}")
                    content_items.extend(self.process_block_content(content))
                    content_items.append(f"\\end{{{block_type}}}")

        # Extract items from itemize and enumerate environments
        list_environments = ['itemize', 'enumerate']
        for env in list_environments:
            env_matches = re.finditer(r'\\begin\{' + env + r'\}(.*?)\\end\{' + env + r'\}', clean_content, re.DOTALL)
            for match in env_matches:
                env_content = match.group(1)
                items = re.finditer(r'\\item\s*(.*?)(?=\\item|\\end\{' + env + r'\}|$)', env_content, re.DOTALL)
                for item in items:
                    item_text = self.clean_latex_content(item.group(1).strip())
                    if item_text:
                        content_items.append(f"- {item_text}")

        # Extract standalone equations
        equation_matches = re.finditer(r'\\\[(.*?)\\\]', clean_content, re.DOTALL)
        for match in equation_matches:
            equation = match.group(1).strip()
            content_items.append(f"\\[{equation}\\]")

        # Extract inline math and other content
        paragraphs = re.split(r'\n\s*\n', clean_content)
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph and not any(env in paragraph for env in ['block', 'example', 'alertblock', 'columns', 'itemize', 'enumerate']):
                # Clean up the paragraph but preserve LaTeX commands
                paragraph = self.preserve_latex_commands(paragraph)
                if paragraph and len(paragraph) > 3:
                    content_items.append(paragraph)

        return content_items

    def extract_enhanced_notes_from_frame(self, frame_content: str) -> list:
        """Extract speaker notes with proper formatting"""
        import re

        notes = []

        # Extract note commands with [item] support
        note_matches = re.finditer(r'\\note(?:\[([^\]]*)\])?\{(.*?)\}', frame_content, re.DOTALL)
        for match in note_matches:
            note_type = match.group(1)  # [item] or None
            note_content = match.group(2).strip()

            if note_type == 'item':
                # Process itemized notes
                items = re.finditer(r'\\item\s*(.*?)(?=\\item|$)', note_content, re.DOTALL)
                for item in items:
                    item_text = self.clean_latex_content(item.group(1).strip())
                    if item_text:
                        notes.append(f"• {item_text}")
            else:
                # Regular note content
                lines = note_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        notes.append(f"• {self.clean_latex_content(line)}")

        return notes

    def process_block_content(self, content: str) -> list:
        """Process content within blocks"""
        import re

        lines = []

        # Extract items from block content
        items = re.finditer(r'\\item\s*(.*?)(?=\\item|$)', content, re.DOTALL)
        for item in items:
            item_text = self.clean_latex_content(item.group(1).strip())
            if item_text:
                lines.append(f"- {item_text}")

        # If no items found, treat as regular content
        if not lines:
            paragraphs = content.split('\n')
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if paragraph:
                    lines.append(self.preserve_latex_commands(paragraph))

        return lines

    def preserve_latex_commands(self, text: str) -> str:
        """Clean text while preserving important LaTeX commands"""
        import re

        # Preserve math environments
        text = re.sub(r'\\\[(.*?)\\\]', r'\\[\1\\]', text)
        text = re.sub(r'\\\((.*?)\\\)', r'\\(\1\\)', text)

        # Preserve text formatting commands
        text = re.sub(r'\\textbf{([^}]*)}', r'\\textbf{\1}', text)
        text = re.sub(r'\\textit{([^}]*)}', r'\\textit{\1}', text)
        text = re.sub(r'\\emph{([^}]*)}', r'\\emph{\1}', text)

        # Preserve other common commands
        text = re.sub(r'\\mathbb{([^}]*)}', r'\\mathbb{\1}', text)
        text = re.sub(r'\\mathcal{([^}]*)}', r'\\mathcal{\1}', text)
        text = re.sub(r'\\bm{([^}]*)}', r'\\bm{\1}', text)

        # Clean up extra whitespace but preserve command structure
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def clean_latex_content(self, text: str) -> str:
        """Clean LaTeX content while preserving structure"""
        import re

        if not text:
            return ""

        # Remove comments
        text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)

        # Replace common LaTeX commands with plain text equivalents
        replacements = [
            (r'\\textcolor{[^}]*}{([^}]*)}', r'\1'),
            (r'~', ' '),
            (r'\\&', '&'),
            (r'\\%', '%'),
            (r'\\#', '#'),
            (r'\\_', '_'),
            (r'\\ldots', '...'),
            (r'\\quad', '    '),
            (r'\\qquad', '        '),
        ]

        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def load_tex_file(self) -> None:
        """Load and convert a Beamer .tex file to IDE format with error handling"""
        tex_file = filedialog.askopenfilename(
            filetypes=[("TeX files", "*.tex"), ("All files", "*.*")],
            title="Select Beamer TeX File to Load"
        )

        if not tex_file:
            return

        try:
            # Convert TeX to simple text format with error tracking
            result = convert_beamer_tex_to_simple_text(tex_file)

            if isinstance(result, tuple):
                text_file, errors = result
            else:
                text_file = result
                errors = []

            if not text_file:
                messagebox.showerror("Error", "Failed to convert TeX file")
                return

            # Now load the converted text file
            self.load_file(text_file)

            self.write(f"✓ Successfully loaded and converted: {os.path.basename(tex_file)}\n", "green")

            # Show errors if any
            if errors:
                self.write(f"\n⚠ Found {len(errors)} issue(s) during conversion:\n", "yellow")
                for err in errors:
                    self.write(f"   Line {err['line']}: {err['message']}\n", "yellow")

                # Ask if user wants to fix errors
                if messagebox.askyesno("Issues Found",
                                       f"Found {len(errors)} issue(s) during conversion.\n\n"
                                       "Would you like to open the error editor to fix them?"):
                    # Open the error editor for the first error
                    first_error = errors[0]
                    self.open_error_editor(text_file, first_error['line'], first_error['message'])

            # Ask if user wants to generate PDF
            if messagebox.askyesno("Success",
                                 "TeX file converted successfully!\n\n"
                                 "Would you like to generate PDF now?"):
                self.generate_pdf()

        except Exception as e:
            error_msg = f"Error loading TeX file:\n{str(e)}"
            self.write(f"✗ {error_msg}\n", "red")
            messagebox.showerror("Error", error_msg)

    def extract_preamble_info_safe(self, content: str) -> dict:
        """Extract preamble information with safer regex patterns"""
        import re

        preamble_info = {
            'theme': '',
            'packages': [],
            'title': '',
            'author': '',
            'date': '',
            'institute': ''
        }

        try:
            # Extract theme with safer pattern
            theme_match = re.search(r'\\usetheme\s*\{([^}]+)\}', content)
            if theme_match:
                preamble_info['theme'] = theme_match.group(1).strip()

            # Extract packages with safer pattern
            package_matches = re.findall(r'\\usepackage\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}', content)
            if package_matches:
                preamble_info['packages'] = [pkg.strip() for pkg in package_matches]

            # Extract document info with safer patterns
            title_match = re.search(r'\\title\s*\{((?:[^{}]|\{[^{}]*\})*)\}', content, re.DOTALL)
            if title_match:
                preamble_info['title'] = self.clean_latex_content_safe(title_match.group(1))

            author_match = re.search(r'\\author\s*\{((?:[^{}]|\{[^{}]*\})*)\}', content, re.DOTALL)
            if author_match:
                preamble_info['author'] = self.clean_latex_content_safe(author_match.group(1))

            date_match = re.search(r'\\date\s*\{((?:[^{}]|\{[^{}]*\})*)\}', content, re.DOTALL)
            if date_match:
                preamble_info['date'] = self.clean_latex_content_safe(date_match.group(1))

            institute_match = re.search(r'\\institute\s*\{((?:[^{}]|\{[^{}]*\})*)\}', content, re.DOTALL)
            if institute_match:
                preamble_info['institute'] = self.clean_latex_content_safe(institute_match.group(1))

        except Exception as e:
            self.write(f"Warning: Error extracting preamble info: {str(e)}\n", "yellow")

        return preamble_info

    def enhanced_extract_slides_from_tex_safe(self, content: str) -> list:
        """Enhanced slide extraction with comprehensive LaTeX feature support and better error handling"""
        slides = []
        import re

        try:
            # First isolate the document body
            doc_match = re.search(r'\\begin{document}(.*?)\\end{document}', content, re.DOTALL)
            if not doc_match:
                self.write("✗ Could not find document body\n", "red")
                return slides

            document_content = doc_match.group(1)

            # Extract preamble information
            preamble_info = self.extract_preamble_info_safe(content)

            # Enhanced frame detection with multiple patterns and better handling
            # Pattern 1: \begin{frame}...\end{frame}
            frame_pattern = r'\\begin\{frame\}(.*?)\\end\{frame\}'

            all_frames = []
            try:
                frames = re.finditer(frame_pattern, document_content, re.DOTALL)
                all_frames = list(frames)
            except Exception as e:
                self.write(f"Warning: Error finding frames with pattern 1: {str(e)}\n", "yellow")
                # Try alternative pattern
                try:
                    # Pattern 2: \frame{...}
                    frame_pattern2 = r'\\frame\{((?:[^{}]|\{[^{}]*\})*)\}'
                    frames = re.finditer(frame_pattern2, document_content, re.DOTALL)
                    all_frames = list(frames)
                except Exception as e2:
                    self.write(f"Warning: Error finding frames with pattern 2: {str(e2)}\n", "yellow")

            if not all_frames:
                self.write("✗ No frames found in document\n", "red")
                return slides

            self.write(f"Found {len(all_frames)} frames in document\n", "green")

            for i, frame_match in enumerate(all_frames):
                try:
                    frame_content = frame_match.group(1) if frame_match.groups() else frame_match.group(0)

                    # Skip title page frames but preserve their content
                    if '\\titlepage' in frame_content or '\\maketitle' in frame_content:
                        self.write(f"Processing title frame {i+1}\n", "yellow")
                        # Extract title page content - USE THE ORIGINAL METHOD
                        title_slide = self.process_title_frame(frame_content, preamble_info)
                        if title_slide:
                            slides.append(title_slide)
                        continue

                    # Extract title
                    title = ""
                    # Try frametitle first
                    ft_match = re.search(r'\\frametitle\s*\{((?:[^{}]|\{[^{}]*\})*)\}', frame_content, re.DOTALL)
                    if ft_match:
                        title = self.clean_latex_content_safe(ft_match.group(1))

                    # If no frametitle, check for frame title in options
                    if not title:
                        # Check for frame with title option: \begin{frame}{Title}
                        title_match = re.match(r'^\s*\{((?:[^{}]|\{[^{}]*\})*)\}', frame_content.strip())
                        if title_match:
                            title = self.clean_latex_content_safe(title_match.group(1))

                    if not title:
                        title = f"Slide {i+1}"

                    # Extract framesubtitle
                    subtitle = ""
                    subtitle_match = re.search(r'\\framesubtitle\s*\{((?:[^{}]|\{[^{}]*\})*)\}', frame_content, re.DOTALL)
                    if subtitle_match:
                        subtitle = self.clean_latex_content_safe(subtitle_match.group(1))
                        title += f" - {subtitle}"

                    # Extract media including TikZ diagrams - USE THE ORIGINAL METHOD
                    media = self.extract_enhanced_media_from_frame(frame_content)

                    # Extract content with enhanced LaTeX support - USE THE ORIGINAL METHOD
                    content_items = self.extract_enhanced_content_from_frame(frame_content)

                    # Extract notes with proper formatting - USE THE ORIGINAL METHOD
                    notes = self.extract_enhanced_notes_from_frame(frame_content)

                    slide_data = {
                        'title': title,
                        'media': media,
                        'content': content_items,
                        'notes': notes,
                        'preamble_info': preamble_info
                    }

                    slides.append(slide_data)
                    self.write(f"✓ Processed slide: {title}\n", "green")

                except Exception as e:
                    self.write(f"✗ Error processing frame {i+1}: {str(e)}\n", "red")
                    # Add a placeholder slide to maintain slide count
                    slides.append({
                        'title': f"Slide {i+1} (Error)",
                        'media': '',
                        'content': [f"% Error processing this slide: {str(e)}"],
                        'notes': [],
                        'preamble_info': preamble_info
                    })
                    continue

            return slides

        except Exception as e:
            self.write(f"✗ Error in slide extraction: {str(e)}\n", "red")
            return []

    def clean_latex_content_safe(self, text: str) -> str:
        """Clean LaTeX content while preserving structure with safer regex handling"""
        import re

        if not text:
            return ""

        try:
            # Remove comments first
            text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)

            # Replace common LaTeX commands with plain text equivalents
            # Use raw strings and be careful with backslashes
            replacements = [
                (r'\\textcolor\{[^}]*\}\{([^}]*)\}', r'\1'),  # Remove textcolor
                (r'~', ' '),  # Replace non-breaking space
                (r'\\&', '&'),
                (r'\\%', '%'),
                (r'\\#', '#'),
                (r'\\_', '_'),
                (r'\\ldots', '...'),
                (r'\\quad', '    '),
                (r'\\qquad', '        '),
            ]

            for pattern, replacement in replacements:
                try:
                    text = re.sub(pattern, replacement, text)
                except:
                    pass  # Skip if pattern causes issues

            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()

            return text

        except Exception as e:
            self.write(f"Warning: Error cleaning LaTeX content: {str(e)}\n", "yellow")
            # Return the original text if cleaning fails
            return text

    def extract_enhanced_media_from_frame_safe(self, frame_content: str) -> str:
        """Extract media including TikZ diagrams with complete code preservation"""
        import re

        media_components = []

        try:
            # Check for TikZ environments - preserve COMPLETE code
            tikz_pattern = r'\\begin\{tikzpicture\}(.*?)\\end\{tikzpicture\}'
            tikz_matches = re.finditer(tikz_pattern, frame_content, re.DOTALL)

            for i, match in enumerate(tikz_matches):
                tikz_content = match.group(0).strip()  # Get the ENTIRE TikZ code
                # Preserve the complete TikZ code as-is
                media_components.append(f"% TikZ Diagram:\n{tikz_content}")

            # Check for graphics
            graphics_pattern = r'\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}'
            graphics_matches = re.finditer(graphics_pattern, frame_content)

            for match in graphics_matches:
                media_path = match.group(1).strip()
                media_components.append(f"\\file {media_path}")

            # Check for movies/videos
            movie_pattern = r'\\movie\s*(?:\[[^\]]*\])?\s*\{[^}]*\}\s*\{([^}]+)\}'
            movie_match = re.search(movie_pattern, frame_content)
            if movie_match:
                media_path = movie_match.group(1).strip()
                media_components.append(f"\\play {media_path}")

            # Join with double newlines to ensure proper separation
            return "\n\n".join(media_components) if media_components else ""

        except Exception as e:
            self.write(f"Warning: Error extracting media: {str(e)}\n", "yellow")
            return ""

    def extract_enhanced_content_from_frame_safe(self, frame_content: str) -> list:
        """Extract content with enhanced LaTeX feature support and safer patterns"""
        import re

        content_items = []

        try:
            # Remove notes and media commands to isolate main content
            # Use safer patterns that don't cause regex issues
            clean_content = frame_content

            # Remove note commands
            clean_content = re.sub(r'\\note\s*\{[^}]*\}', '', clean_content, flags=re.DOTALL)

            # Remove graphics commands
            clean_content = re.sub(r'\\includegraphics[^}]*\}', '', clean_content)

            # Remove movie commands
            clean_content = re.sub(r'\\movie[^}]*\}', '', clean_content)


            # Extract blocks with safer patterns
            block_patterns = [
                (r'\\begin\{block\}\s*\{((?:[^{}]|\{[^{}]*\})*)\}(.*?)\\end\{block\}', 'block'),
                (r'\\begin\{example\}\s*\{((?:[^{}]|\{[^{}]*\})*)\}(.*?)\\end\{example\}', 'example'),
                (r'\\begin\{alertblock\}\s*\{((?:[^{}]|\{[^{}]*\})*)\}(.*?)\\end\{alertblock\}', 'alertblock'),
                (r'\\begin\{columns\}(.*?)\\end\{columns\}', 'columns')
            ]

            for pattern, block_type in block_patterns:
                try:
                    blocks = re.finditer(pattern, clean_content, re.DOTALL)
                    for block in blocks:
                        if block_type == 'columns':
                            # Process columns environment
                            columns_content = self.process_columns_environment_safe(block.group(1))
                            content_items.extend(columns_content)
                        else:
                            title = self.clean_latex_content_safe(block.group(1))
                            content = self.clean_latex_content_safe(block.group(2))
                            content_items.append(f"\\begin{{{block_type}}}{{{title}}}")
                            content_items.extend(self.process_block_content_safe(content))
                            content_items.append(f"\\end{{{block_type}}}")
                except:
                    continue  # Skip if pattern causes issues

            # Extract items from itemize and enumerate environments with safer patterns
            list_environments = ['itemize', 'enumerate']
            for env in list_environments:
                try:
                    env_pattern = f'\\\\begin\\{{{env}\\}}(.*?)\\\\end\\{{{env}\\}}'
                    env_matches = re.finditer(env_pattern, clean_content, re.DOTALL)
                    for match in env_matches:
                        env_content = match.group(1)
                        item_pattern = r'\\item\s*(.*?)(?=\\item|\\end\{' + env + r'\}|$)'
                        items = re.finditer(item_pattern, env_content, re.DOTALL)
                        for item in items:
                            item_text = self.clean_latex_content_safe(item.group(1).strip())
                            if item_text:
                                content_items.append(f"- {item_text}")
                except:
                    continue

            # Extract standalone equations with safer pattern
            try:
                equation_pattern = r'\\\[(.*?)\\\]'
                equation_matches = re.finditer(equation_pattern, clean_content, re.DOTALL)
                for match in equation_matches:
                    equation = match.group(1).strip()
                    content_items.append(f"\\[{equation}\\]")
            except:
                pass

            # Extract inline math and other content
            paragraphs = re.split(r'\n\s*\n', clean_content)
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if paragraph and not any(env in paragraph for env in ['block', 'example', 'alertblock', 'columns', 'itemize', 'enumerate']):
                    # Clean up the paragraph but preserve LaTeX commands
                    paragraph = self.preserve_latex_commands_safe(paragraph)
                    if paragraph and len(paragraph) > 3:
                        content_items.append(paragraph)

            return content_items

        except Exception as e:
            self.write(f"Warning: Error extracting content: {str(e)}\n", "yellow")
            return ["% Error extracting content from this slide"]

    def preserve_latex_commands_safe(self, text: str) -> str:
        """Clean text while preserving important LaTeX commands with safer patterns"""
        import re

        try:
            # Preserve math environments with safer patterns
            text = re.sub(r'\\\[(.*?)\\\]', r'\\[\1\\]', text, flags=re.DOTALL)
            text = re.sub(r'\\\((.*?)\\\)', r'\\(\1\\)', text, flags=re.DOTALL)

            # Preserve text formatting commands with safer patterns
            commands_to_preserve = ['textbf', 'textit', 'emph', 'mathbb', 'mathcal', 'bm']
            for cmd in commands_to_preserve:
                pattern = f'\\\\{cmd}\\{{((?:[^{{}}]|\\{{[^{{}}]*\\}})*)\\}}'
                try:
                    text = re.sub(pattern, f'\\\\{cmd}{{\\1}}', text, flags=re.DOTALL)
                except:
                    pass  # Skip if pattern causes issues

            # Clean up extra whitespace but preserve command structure
            text = re.sub(r'\s+', ' ', text)

            return text.strip()

        except Exception as e:
            self.write(f"Warning: Error preserving LaTeX commands: {str(e)}\n", "yellow")
            return text

    def extract_media_from_frame(self, frame_content: str) -> str:
        """Extract media references from frame content"""
        import re

        media = ""

        # Check for graphics
        graphics_match = re.search(r'\\includegraphics(?:\[[^\]]*\])?{([^}]*)}', frame_content)
        if graphics_match:
            media_path = graphics_match.group(1)
            media = f"\\file {media_path}"

        # Check for movies/videos
        movie_match = re.search(r'\\movie(?:\[[^\]]*\])?{[^}]*}{([^}]*)}', frame_content)
        if movie_match:
            media_path = movie_match.group(1)
            media = f"\\play {media_path}"

        return media

    def extract_content_from_frame(self, frame_content: str) -> list:
        r"""Extract content items from frame - treat as plain text unless explicit \item"""
        import re

        content_items = []

        # Remove media commands and notes to isolate main content
        clean_content = re.sub(r'\\includegraphics[^}]*}|\\movie[^}]*}|\\note{[^}]*}', '', frame_content)

        # Only extract explicit \item commands with bullets
        # Look for \item commands anywhere in the content
        items = re.finditer(r'\\item\s*(.*?)(?=\\item|\\end{itemize}|\\end{enumerate}|$)',
                           clean_content, re.DOTALL)

        for item in items:
            item_text = self.clean_latex_content(item.group(1).strip())
            if item_text:
                content_items.append(f"- {item_text}")

        # If no explicit items found, extract the main content as plain text blocks
        if not content_items:
            # Remove all LaTeX environments to get plain text
            plain_content = re.sub(r'\\begin\{.*?\}.*?\\end\{.*?\}', '', clean_content, flags=re.DOTALL)
            plain_content = re.sub(r'\\[a-zA-Z]+\{.*?\}', '', plain_content)  # Remove other LaTeX commands

            # Split into paragraphs and clean
            paragraphs = re.split(r'\n\s*\n', plain_content)
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                # Clean up the paragraph
                paragraph = re.sub(r'\s+', ' ', paragraph)  # Normalize whitespace
                paragraph = self.clean_latex_content(paragraph)

                if paragraph and len(paragraph) > 3:  # Minimum length
                    content_items.append(paragraph)  # No bullet for plain text

        return content_items

    def extract_notes_from_frame(self, frame_content: str) -> list:
        """Extract speaker notes from frame"""
        import re

        notes = []

        note_match = re.search(r'\\note{(.*?)}', frame_content, re.DOTALL)
        if note_match:
            note_content = note_match.group(1)
            # Extract items from note content
            note_items = re.finditer(r'\\item\s*(.*?)(?=\\item|$)', note_content, re.DOTALL)
            for item in note_items:
                note_text = self.clean_latex_content(item.group(1).strip())
                if note_text:
                    notes.append(f"• {note_text}")

        return notes

    def overwrite_tex_and_generate_pdf(self) -> None:
        """Convert current presentation back to TeX and generate PDF"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your presentation first!")
            return

        try:
            # Save current state
            self.save_current_slide()
            self.save_file()

            # Get corresponding .tex filename
            base_name = os.path.splitext(self.current_file)[0]
            if base_name.endswith('_converted'):
                base_name = base_name[:-10]  # Remove _converted suffix

            tex_file = base_name + '.tex'

            # Ask for confirmation before overwriting
            if os.path.exists(tex_file):
                if not messagebox.askyesno("Confirm Overwrite",
                                         f"The file '{os.path.basename(tex_file)}' already exists.\n\n"
                                         "Do you want to overwrite it?"):
                    return

            self.write(f"Converting to TeX: {tex_file}\n", "white")

            # Convert to TeX
            self.convert_to_tex()

            if not os.path.exists(tex_file):
                self.write("✗ TeX file was not created successfully\n", "red")
                return

            self.write("✓ TeX file created successfully\n", "green")

            # Generate PDF
            self.write("Generating PDF...\n", "white")
            self.generate_pdf()

            # Preview PDF
            pdf_file = base_name + '.pdf'
            if os.path.exists(pdf_file):
                if messagebox.askyesno("Success",
                                     "PDF generated successfully!\n\n"
                                     "Would you like to view it now?"):
                    self.preview_pdf(pdf_file)

        except Exception as e:
            error_msg = f"Error in TeX conversion and PDF generation:\n{str(e)}"
            self.write(f"✗ {error_msg}\n", "red")
            messagebox.showerror("Error", error_msg)

#-------------------------------------------------------------------------------------
    def setup_spellchecking(self):
        """Initialize spell checking with always-on enforcement and automatic dictionary handling"""
        try:
            from spellchecker import SpellChecker

            # ENFORCE ALWAYS ON - Remove any disable capability
            self.spell_checking_enabled = True  # Force always enabled

            # Initialize spell checker with default language
            self.spell_checker = SpellChecker()

            # Language and dialect support
            self.available_languages = self.load_available_languages()
            self.current_language = 'en'
            self.current_language_name = 'English (US)'

            # Spell check settings
            self.case_sensitive = False
            self.ignore_numbers = True

            # Use unique tag names
            self.spell_tags = {
                'misspelled': 'spell_misspelled',
                'misspelled_highlight': 'spell_highlight',
            }

            # VERIFY AND PROCURE DICTIONARIES
            self.verify_dictionaries_available()

            for editor in [self.content_editor._textbox, self.notes_editor._textbox]:
                # Configure spell checking tags
                editor.tag_configure(self.spell_tags['misspelled'],
                                   underline=True, underlinefg="red")
                editor.tag_configure(self.spell_tags['misspelled_highlight'],
                                   background="#2F3542")

                # Bind spellcheck events
                editor.bind("<Button-1>", self.on_text_click_spellcheck)
                editor.bind("<Button-3>", self.on_right_click_spellcheck)
                editor.bind("<KeyRelease>", self.delayed_spell_check, add='+')

            print("✓ Spell checking ENABLED (always on)")
            self.write("✓ Spell checking initialized with dictionary verification\n", "green")

            # Create spelling context menu and anchored tooltip
            self.create_spelling_context_menu()
            self.create_anchored_tooltip()

            # Add language selection to toolbar
            self.add_language_selection_to_toolbar()

            # Perform initial spell check
            self.after(1000, self.perform_initial_spell_check)

        except ImportError as e:
            self.spell_checking_enabled = False
            error_msg = f"✗ Spell checking disabled: pyspellchecker not installed: {e}"
            print(error_msg)
            self.write(f"{error_msg}\n", "red")
        except Exception as e:
            error_msg = f"✗ Error initializing spell checking: {str(e)}"
            print(error_msg)
            self.write(f"{error_msg}\n", "red")
            import traceback
            traceback.print_exc()

    def verify_dictionaries_available(self):
        """Verify dictionaries are available and attempt to procure missing ones"""
        try:
            print("Verifying spell check dictionaries...")

            # Test basic spell checking functionality
            test_words = ['test', 'spelling', 'verification']
            known_words = self.spell_checker.known(test_words)

            if len(known_words) == len(test_words):
                print("✓ Default English dictionary is available")
                self.write("✓ Default English dictionary loaded\n", "green")
            else:
                print("! Default dictionary may be incomplete")
                self.write("! Default dictionary may need enhancement\n", "yellow")

            # Check if we can load additional languages
            self.attempt_dictionary_procurement()

        except Exception as e:
            error_msg = f"Error verifying dictionaries: {str(e)}"
            print(f"✗ {error_msg}")
            self.write(f"✗ {error_msg}\n", "red")

    def attempt_dictionary_procurement(self):
        """Attempt to procure and load additional dictionaries - FIXED VERSION"""
        try:
            print("Checking for additional dictionaries...")

            # List of languages to attempt loading
            target_languages = ['en_GB', 'es', 'fr', 'de']

            for lang_code in target_languages:
                try:
                    # Import here to avoid scope issues
                    from spellchecker import SpellChecker

                    # Try to create a spell checker with this language
                    test_speller = SpellChecker(language=lang_code)
                    # Test with a simple word
                    test_word = 'test'
                    if test_speller.correction(test_word) == test_word:
                        lang_name = self.get_language_name(lang_code)
                        print(f"✓ Dictionary available: {lang_name} ({lang_code})")
                        self.write(f"✓ Loaded dictionary: {lang_name}\n", "green")
                except Exception as e:
                    print(f"✗ Dictionary not available: {lang_code} - {e}")
                    continue

        except Exception as e:
            print(f"Error during dictionary procurement: {e}")

    def get_language_name(self, lang_code):
        """Get display name for language code"""
        language_names = {
            'en': 'English (US)',
            'en_GB': 'English (UK)',
            'en_CA': 'English (Canada)',
            'en_AU': 'English (Australia)',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese'
        }
        return language_names.get(lang_code, lang_code)

    def load_available_languages(self):
        """Load available languages with enhanced error handling"""
        languages = {
            'English (US)': 'en',
            'English (UK)': 'en_GB',
            'English (Canada)': 'en_CA',
            'English (Australia)': 'en_AU',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
            'Italian': 'it',
            'Portuguese': 'pt',
            'Dutch': 'nl',
            'Russian': 'ru',
            'Chinese (Simplified)': 'zh',
            'Japanese': 'ja',
            'Korean': 'ko',
            'Arabic': 'ar',
            'Hindi': 'hi'
        }

        available_languages = {'English (US)': 'en'}  # Always available

        try:
            from spellchecker import SpellChecker

            print("Loading available dictionaries...")

            for lang_name, lang_code in languages.items():
                try:
                    # Try to create a spell checker with this language
                    test_speller = SpellChecker(language=lang_code)
                    # Test functionality
                    test_word = 'test'
                    correction = test_speller.correction(test_word)

                    if correction:  # If we get any correction, dictionary works
                        available_languages[lang_name] = lang_code
                        print(f"✓ Loaded dictionary: {lang_name}")
                        self.write(f"✓ Dictionary available: {lang_name}\n", "green")
                    else:
                        print(f"✗ Dictionary empty or invalid: {lang_name}")

                except Exception as e:
                    print(f"✗ Dictionary not available: {lang_name} - {e}")
                    continue

        except Exception as e:
            error_msg = f"Error loading languages: {e}"
            print(error_msg)
            self.write(f"✗ {error_msg}\n", "red")

        return available_languages

    def on_text_click_spellcheck(self, event):
        """Handle left-click on text for spell checking - RESTORED"""
        if not self.spell_checking_enabled:
            return

        widget = event.widget
        index = widget.index(f"@{event.x},{event.y}")

        # Check if we're clicking on a misspelled word
        if self.spell_tags['misspelled'] in widget.tag_names(index):
            # Get the word under cursor
            word_start = widget.index(f"{index} wordstart")
            word_end = widget.index(f"{index} wordend")
            word = widget.get(word_start, word_end)

            # Remove any previous highlighting
            widget.tag_remove(self.spell_tags['misspelled_highlight'], "1.0", "end")

            # Highlight the clicked word
            widget.tag_add(self.spell_tags['misspelled_highlight'], word_start, word_end)

            # Show anchored tooltip (popup window)
            self.show_anchored_tooltip(widget, word, word_start, word_end, event.x_root, event.y_root)

            # Prevent event from propagating to other handlers
            return "break"
        else:
            # Clicked on normal text, hide tooltip
            self.hide_anchored_tooltip()

    def on_right_click_spellcheck(self, event):
        """Handle right-click on text for spell checking (alternative method)"""
        if not self.spell_checking_enabled:
            return

        widget = event.widget
        index = widget.index(f"@{event.x},{event.y}")

        # Check if right-click is on a misspelled word
        if self.spell_tags['misspelled'] in widget.tag_names(index):
            # Get the word and its position
            word_start = widget.index(f"{index} wordstart")
            word_end = widget.index(f"{index} wordend")
            word = widget.get(word_start, word_end)

            # Store current word info
            self.current_spellcheck_word = {
                'widget': widget,
                'word': word,
                'start': word_start,
                'end': word_end
            }

            # Highlight the word temporarily
            widget.tag_remove(self.spell_tags['misspelled_highlight'], "1.0", "end")
            widget.tag_add(self.spell_tags['misspelled_highlight'], word_start, word_end)

            # Show context menu instead of tooltip
            self.show_spelling_suggestions_menu(event.x_root, event.y_root, word)

            return "break"

    def create_anchored_tooltip(self):
        """Create the popup tooltip window for spell suggestions - RESTORED"""
        self.anchored_tooltip = tk.Toplevel(self)
        self.anchored_tooltip.wm_overrideredirect(True)
        self.anchored_tooltip.configure(bg='#ffffe0', relief='solid', borderwidth=2)
        self.anchored_tooltip.attributes('-topmost', True)

        # Title frame
        self.title_frame = tk.Frame(self.anchored_tooltip, bg='#ffffe0')
        self.title_frame.pack(fill='x', padx=8, pady=(8, 4))

        self.title_label = tk.Label(
            self.title_frame,
            text="Spelling Suggestions:",
            bg='#ffffe0',
            fg='#333333',
            font=("Arial", 9, "bold"),
            justify='left'
        )
        self.title_label.pack(anchor='w')

        # Suggestions frame
        self.suggestions_frame = tk.Frame(self.anchored_tooltip, bg='#ffffe0')
        self.suggestions_frame.pack(fill='x', padx=8, pady=4)

        # Control frame
        self.control_frame = tk.Frame(self.anchored_tooltip, bg='#ffffe0')
        self.control_frame.pack(fill='x', padx=8, pady=(4, 8))

        self.control_label = tk.Label(
            self.control_frame,
            text="↑↓: Navigate • Enter: Select • Esc: Close",
            bg='#ffffe0',
            fg='#666666',
            font=("Arial", 8),
            justify='left'
        )
        self.control_label.pack(anchor='w')

        # Initially hide the tooltip
        self.anchored_tooltip.withdraw()

        # Keyboard navigation
        self.anchored_tooltip.bind("<Escape>", lambda e: self.hide_anchored_tooltip())
        self.anchored_tooltip.bind("<KeyPress>", self.on_tooltip_keypress)

        # Track selection
        self.current_suggestions = []
        self.selected_index = 0
        self.anchored_word_info = None

    def show_anchored_tooltip(self, widget, word, word_start, word_end, x_root, y_root):
        """Show the popup tooltip with spelling suggestions - with enhanced error handling"""
        try:
            # Get spelling suggestions
            try:
                suggestions = list(self.spell_checker.candidates(word))[:8]
                if not suggestions:
                    # Fallback to correction
                    correction = self.spell_checker.correction(word)
                    if correction and correction != word:
                        suggestions = [correction]
            except Exception as e:
                error_msg = f"Error getting suggestions: {str(e)}"
                print(f"✗ {error_msg}")
                self.write(f"✗ {error_msg}\n", "red")
                suggestions = []

            if not suggestions:
                print(f"No suggestions available for word: '{word}'")
                return

            # Store current word info
            self.anchored_word_info = {
                'widget': widget,
                'word_start': word_start,
                'word_end': word_end,
                'original_word': word
            }
            self.current_suggestions = suggestions
            self.selected_index = 0

            # Update tooltip content
            self.title_label.configure(text=f"Suggestions for '{word}':")

            # Clear previous suggestions
            for child in self.suggestions_frame.winfo_children():
                child.destroy()

            # Create suggestion buttons
            self.suggestion_labels = []
            for i, suggestion in enumerate(suggestions):
                try:
                    suggestion_label = tk.Label(
                        self.suggestions_frame,
                        text=suggestion,
                        bg='#ffffe0',
                        fg='#0066cc',
                        font=("Arial", 9),
                        cursor="hand2",
                        justify='left',
                        relief='flat',
                        padx=4,
                        pady=2
                    )
                    suggestion_label.pack(fill='x', anchor='w', pady=1)

                    # Bind click event
                    suggestion_label.bind("<Button-1>",
                        lambda e, idx=i: self.select_suggestion(idx))

                    # Hover effects
                    suggestion_label.bind("<Enter>",
                        lambda e, idx=i: self.highlight_suggestion(idx))
                    suggestion_label.bind("<Leave>",
                        lambda e, idx=i: self.unhighlight_suggestion(idx))

                    self.suggestion_labels.append(suggestion_label)
                except Exception as e:
                    print(f"Error creating suggestion label: {e}")
                    continue

            # Position tooltip (offset from click position)
            tooltip_x = x_root + 20
            tooltip_y = y_root + 20

            # Ensure tooltip stays on screen
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()

            tooltip_width = 200
            tooltip_height = 150

            if tooltip_x + tooltip_width > screen_width:
                tooltip_x = x_root - tooltip_width - 20
            if tooltip_y + tooltip_height > screen_height:
                tooltip_y = y_root - tooltip_height - 20

            self.anchored_tooltip.wm_geometry(f"+{tooltip_x}+{tooltip_y}")

            # Show and focus tooltip
            self.anchored_tooltip.deiconify()
            self.anchored_tooltip.focus_set()

            # Highlight first suggestion
            self.highlight_suggestion(0)

            print(f"✓ Showing {len(suggestions)} suggestions for '{word}'")

        except Exception as e:
            error_msg = f"Error showing spell check tooltip: {str(e)}"
            print(f"✗ {error_msg}")
            self.write(f"✗ {error_msg}\n", "red")

    def select_suggestion(self, index):
        """Select and apply a spelling suggestion from tooltip - with error handling"""
        try:
            if (not self.anchored_word_info or
                not self.current_suggestions or
                index >= len(self.current_suggestions)):
                print("Invalid suggestion selection parameters")
                return

            suggestion = self.current_suggestions[index]
            widget = self.anchored_word_info['widget']
            word_start = self.anchored_word_info['word_start']
            word_end = self.anchored_word_info['word_end']
            original_word = self.anchored_word_info['original_word']

            # Replace the word
            widget.delete(word_start, word_end)
            widget.insert(word_start, suggestion)

            # Hide tooltip
            self.hide_anchored_tooltip()

            # Re-check spelling
            self.check_spelling()

            print(f"✓ Replaced '{original_word}' with '{suggestion}'")

        except Exception as e:
            error_msg = f"Error applying spelling suggestion: {str(e)}"
            print(f"✗ {error_msg}")
            self.write(f"✗ {error_msg}\n", "red")

    def hide_anchored_tooltip(self, event=None):
        """Hide the popup tooltip - RESTORED"""
        if hasattr(self, 'anchored_word_info') and self.anchored_word_info:
            # Remove word highlighting
            widget = self.anchored_word_info['widget']
            widget.tag_remove(self.spell_tags['misspelled_highlight'], "1.0", "end")

        if hasattr(self, 'anchored_tooltip'):
            self.anchored_tooltip.withdraw()

        self.current_suggestions = []
        self.selected_index = 0
        self.anchored_word_info = None

        # Return focus to main window
        self.focus_set()

    def on_tooltip_keypress(self, event):
        """Handle keyboard navigation in tooltip - RESTORED"""
        if not self.current_suggestions:
            return

        if event.keysym == "Escape":
            self.hide_anchored_tooltip()
        elif event.keysym == "Up":
            new_index = max(0, self.selected_index - 1)
            self.highlight_suggestion(new_index)
        elif event.keysym == "Down":
            new_index = min(len(self.current_suggestions) - 1, self.selected_index + 1)
            self.highlight_suggestion(new_index)
        elif event.keysym == "Return":
            self.select_suggestion(self.selected_index)

    def highlight_suggestion(self, index):
        """Highlight a suggestion in the tooltip - RESTORED"""
        # Unhighlight previous
        if hasattr(self, 'suggestion_labels') and self.suggestion_labels:
            for i, label in enumerate(self.suggestion_labels):
                if i == self.selected_index:
                    label.configure(bg='#ffffe0', fg='#0066cc', relief='flat')

        # Highlight new
        self.selected_index = index
        if hasattr(self, 'suggestion_labels') and self.suggestion_labels:
            if 0 <= index < len(self.suggestion_labels):
                self.suggestion_labels[index].configure(
                    bg='#4A90E2',
                    fg='white',
                    relief='sunken'
                )

    def unhighlight_suggestion(self, index):
        """Unhighlight a suggestion - RESTORED"""
        if index != self.selected_index and hasattr(self, 'suggestion_labels'):
            if 0 <= index < len(self.suggestion_labels):
                self.suggestion_labels[index].configure(
                    bg='#ffffe0',
                    fg='#0066cc',
                    relief='flat'
                )

    def add_language_selection_to_toolbar(self):
        """Add language selection dropdown to toolbar"""
        if not self.spell_checking_enabled:
            return

        # Add to existing toolbar
        toolbar = self.toolbar

        # Language selection frame
        lang_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        lang_frame.pack(side="left", padx=10)

        ctk.CTkLabel(lang_frame, text="Spell Check:").pack(side="left", padx=5)

        self.language_var = ctk.StringVar(value=self.current_language_name)
        self.language_menu = ctk.CTkOptionMenu(
            lang_frame,
            values=list(self.available_languages.keys()),
            variable=self.language_var,
            command=self.change_spellcheck_language,
            width=140
        )
        self.language_menu.pack(side="left", padx=5)

        # Add load dictionary button
        self.load_dict_button = ctk.CTkButton(
            lang_frame,
            text="Load Dictionary",
            command=self.load_custom_dictionary,
            width=120
        )
        self.load_dict_button.pack(side="left", padx=5)
        self.create_tooltip(self.load_dict_button, "Load custom dictionary file")

    def change_spellcheck_language(self, language_name):
        """Change spell checking language"""
        if not self.spell_checking_enabled:
            return

        try:
            language_code = self.available_languages[language_name]

            # Reinitialize spell checker with new language
            from spellchecker import SpellChecker
            self.spell_checker = SpellChecker(language=language_code)
            self.current_language = language_code
            self.current_language_name = language_name

            # Clear and re-check all text
            self.clear_spellcheck_highlights()
            self.check_spelling()

            self.write(f"✓ Spell check language changed to {language_name}\n", "green")

        except Exception as e:
            self.write(f"✗ Error changing language: {str(e)}\n", "red")
            # Revert to previous selection
            self.language_var.set(self.current_language_name)

    def load_custom_dictionary(self):
        """Load custom dictionary from file"""
        file_path = filedialog.askopenfilename(
            title="Select Custom Dictionary File",
            filetypes=[
                ("Dictionary files", "*.dic"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            # Read custom dictionary
            with open(file_path, 'r', encoding='utf-8') as f:
                words = [line.strip() for line in f if line.strip()]

            # Add words to spell checker
            for word in words:
                self.spell_checker.word_frequency.add(word)

            # Re-check spelling
            self.check_spelling()

            self.write(f"✓ Loaded custom dictionary with {len(words)} words\n", "green")
            messagebox.showinfo("Success", f"Loaded {len(words)} words from custom dictionary")

        except Exception as e:
            error_msg = f"Error loading dictionary: {str(e)}"
            self.write(f"✗ {error_msg}\n", "red")
            messagebox.showerror("Error", error_msg)

    # Keep the existing check_spelling method that works
    def check_spelling(self, event=None):
        """Check spelling in real-time"""
        if not self.spell_checking_enabled:
            return

        # Process both editors
        for editor in [self.content_editor._textbox, self.notes_editor._textbox]:
            # Remove previous spell checking markings
            editor.tag_remove(self.spell_tags['misspelled'], "1.0", "end")

            # Get all text
            content = editor.get("1.0", "end")

            # Skip if content is too short
            if len(content.strip()) < 4:
                continue

            # Find all words longer than 3 characters
            words = re.findall(r'\b\w{4,}\b', content)

            # Get positions of all words
            word_positions = []
            for word in words:
                start_index = "1.0"
                while True:
                    start_index = editor.search(rf"\y{word}\y", start_index,
                                              stopindex="end", regexp=True)
                    if not start_index:
                        break
                    end_index = f"{start_index}+{len(word)}c"
                    word_positions.append((word, start_index, end_index))
                    start_index = end_index

            # Check each word
            for word, start, end in word_positions:
                # Skip words that are in syntax highlighting tags (LaTeX commands, etc.)
                skip_tags = ['command', 'media', 'bullet', 'url', 'bracket', 'rgb', 'textcolor']

                skip = False
                for tag in skip_tags:
                    if tag in editor.tag_names(start):
                        skip = True
                        break

                if skip:
                    continue

                # Check spelling (case insensitive unless specified)
                check_word = word if self.case_sensitive else word.lower()

                # Skip words with numbers if option is enabled
                if self.ignore_numbers and any(char.isdigit() for char in word):
                    continue

                # Actual spell check
                if not self.spell_checker.known([check_word]):
                    editor.tag_add(self.spell_tags['misspelled'], start, end)

    def clear_spellcheck_highlights(self):
        """Clear all spell check highlighting"""
        for editor in [self.content_editor._textbox, self.notes_editor._textbox]:
            for tag in self.spell_tags.values():
                editor.tag_remove(tag, "1.0", "end")


    def create_spelling_context_menu(self):
        """Create context menu for spelling suggestions"""
        self.spelling_menu = tk.Menu(self, tearoff=0)

        # Suggestions will be added dynamically
        self.suggestion_items = []

        # Static menu items
        self.spelling_menu.add_separator()
        self.spelling_menu.add_command(label="Ignore All", command=self.ignore_all_occurrences)
        self.spelling_menu.add_command(label="Add to Dictionary", command=self.add_to_dictionary)
        self.spelling_menu.add_separator()
        self.spelling_menu.add_command(label="Spell Check Settings...", command=self.show_spellcheck_settings)


    def show_spelling_suggestions_menu(self, x, y, word):
        """Show spelling suggestions in context menu"""
        # Clear previous suggestions
        for item in self.suggestion_items:
            self.spelling_menu.delete(0)
        self.suggestion_items.clear()

        # Get spelling suggestions
        try:
            suggestions = list(self.spell_checker.candidates(word))[:8]  # More suggestions
            if not suggestions:
                # Fallback to correction
                correction = self.spell_checker.correction(word)
                if correction and correction != word:
                    suggestions = [correction]
        except Exception:
            suggestions = []

        # Add suggestions to menu
        if suggestions:
            for i, suggestion in enumerate(suggestions):
                self.spelling_menu.insert_command(
                    i,
                    label=suggestion,
                    command=lambda s=suggestion: self.replace_spelling_suggestion(s)
                )
                self.suggestion_items.append(suggestion)
        else:
            self.spelling_menu.insert_command(
                0,
                label="No suggestions available",
                state="disabled"
            )
            self.suggestion_items.append("No suggestions")

        # Show the menu
        self.spelling_menu.tk_popup(x, y)

        # Set up menu close handler to remove temporary highlighting
        def on_menu_close():
            if hasattr(self, 'current_spellcheck_word'):
                widget = self.current_spellcheck_word['widget']
                widget.tag_remove(self.spell_tags['misspelled_highlight'], "1.0", "end")

        # Bind to menu close
        self.spelling_menu.bind("<Unmap>", lambda e: on_menu_close())

    def replace_spelling_suggestion(self, suggestion):
        """Replace misspelled word with suggestion"""
        if not hasattr(self, 'current_spellcheck_word'):
            return

        word_info = self.current_spellcheck_word
        widget = word_info['widget']

        # Replace the word
        widget.delete(word_info['start'], word_info['end'])
        widget.insert(word_info['start'], suggestion)

        # Remove highlighting
        widget.tag_remove(self.spell_tags['misspelled_highlight'], "1.0", "end")

        # Re-check spelling
        self.check_spelling()

    def ignore_all_occurrences(self):
        """Ignore all occurrences of the current word"""
        if not hasattr(self, 'current_spellcheck_word'):
            return

        word = self.current_spellcheck_word['word']
        widget = self.current_spellcheck_word['widget']

        # Add to spell checker's known words
        self.spell_checker.word_frequency.add(word.lower())

        # Remove all instances of this word from misspelled tags
        content = widget.get("1.0", "end")
        start_index = "1.0"

        while True:
            start_index = widget.search(rf"\y{word}\y", start_index,
                                      stopindex="end", regexp=True)
            if not start_index:
                break
            end_index = f"{start_index}+{len(word)}c"

            # Remove misspelled tag from this occurrence
            widget.tag_remove(self.spell_tags['misspelled'], start_index, end_index)
            widget.tag_remove(self.spell_tags['misspelled_highlight'], start_index, end_index)

            start_index = end_index

        self.write(f"✓ Added '{word}' to dictionary (ignored everywhere)\n", "green")

    def add_to_dictionary(self):
        """Add current word to custom dictionary"""
        if not hasattr(self, 'current_spellcheck_word'):
            return

        word = self.current_spellcheck_word['word']
        widget = self.current_spellcheck_word['widget']

        # Add to spell checker
        self.spell_checker.word_frequency.add(word.lower())

        # Remove highlighting for this word
        widget.tag_remove(self.spell_tags['misspelled'],
                         self.current_spellcheck_word['start'],
                         self.current_spellcheck_word['end'])
        widget.tag_remove(self.spell_tags['misspelled_highlight'],
                         self.current_spellcheck_word['start'],
                         self.current_spellcheck_word['end'])

        self.write(f"✓ Added '{word}' to dictionary\n", "green")

    def show_spellcheck_settings(self):
        """Show spell check settings dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Spell Check Settings")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 400) // 2
        y = (dialog.winfo_screenheight() - 300) // 2
        dialog.geometry(f"+{x}+{y}")

        # Language selection
        lang_frame = ctk.CTkFrame(dialog)
        lang_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(lang_frame, text="Language:", font=("Arial", 12, "bold")).pack(anchor="w")

        lang_var = ctk.StringVar(value=self.current_language_name)
        lang_menu = ctk.CTkOptionMenu(
            lang_frame,
            values=list(self.available_languages.keys()),
            variable=lang_var,
            width=200
        )
        lang_menu.pack(fill="x", pady=5)

        # Options frame
        options_frame = ctk.CTkFrame(dialog)
        options_frame.pack(fill="x", padx=20, pady=10)

        # Case sensitivity option
        case_sensitive_var = ctk.BooleanVar(value=self.case_sensitive)
        case_check = ctk.CTkCheckBox(
            options_frame,
            text="Case sensitive spell checking",
            variable=case_sensitive_var
        )
        case_check.pack(anchor="w", pady=5)

        # Ignore words with numbers
        ignore_numbers_var = ctk.BooleanVar(value=self.ignore_numbers)
        numbers_check = ctk.CTkCheckBox(
            options_frame,
            text="Ignore words containing numbers",
            variable=ignore_numbers_var
        )
        numbers_check.pack(anchor="w", pady=5)

        # Buttons frame
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=20, pady=20)

        def apply_settings():
            new_language = lang_var.get()
            if new_language != self.current_language_name:
                self.change_spellcheck_language(new_language)

            # Update settings
            self.case_sensitive = case_sensitive_var.get()
            self.ignore_numbers = ignore_numbers_var.get()

            dialog.destroy()
            # Re-check with new settings
            self.check_spelling()

        ctk.CTkButton(
            button_frame,
            text="Apply",
            command=apply_settings,
            width=100
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=100
        ).pack(side="right", padx=5)

    # RESTORE THE ORIGINAL REAL-TIME SPELL CHECKING
    def delayed_spell_check(self, event=None):
        """Delayed spell check to avoid conflict with syntax highlighting"""
        if not self.spell_checking_enabled:
            return

        # Cancel any pending spell check
        if hasattr(self, '_spell_check_timer'):
            self.after_cancel(self._spell_check_timer)

        # Schedule spell check to run after syntax highlighting
        self._spell_check_timer = self.after(100, self.check_spelling)

    def perform_initial_spell_check(self):
        """Perform initial spell check after UI is fully loaded"""
        if self.spell_checking_enabled:
            self.check_spelling()
            print("✓ Initial spell check completed")

     #----------------------------------------------------------------


    def on_text_click(self, event):
        """Handle text click to show anchored spelling suggestions"""
        if not self.spell_checking_enabled:
            return

        widget = event.widget
        index = widget.index(f"@{event.x},{event.y}")

        # Check if we're clicking on a misspelled word
        if "misspelled" in widget.tag_names(index):
            # Get the word under cursor
            word_start = widget.index(f"{index} wordstart")
            word_end = widget.index(f"{index} wordend")
            word = widget.get(word_start, word_end)

            # Remove any previous highlighting
            widget.tag_remove("misspelled_anchor", "1.0", "end")

            # Highlight the clicked word
            widget.tag_add("misspelled_anchor", word_start, word_end)

            # Show anchored tooltip
            self.show_anchored_tooltip(widget, word, word_start, word_end, event.x_root, event.y_root)
        else:
            # Clicked on normal text, hide tooltip
            self.hide_anchored_tooltip()

    def on_text_hover(self, event):
        """Show spelling suggestions when hovering over misspelled words"""
        if not self.spell_checking_enabled:
            return

        widget = event.widget
        index = widget.index(f"@{event.x},{event.y}")

        # Check if we're hovering over a misspelled word
        if "misspelled" in widget.tag_names(index):
            # Get the word under cursor
            word_start = widget.index(f"{index} wordstart")
            word_end = widget.index(f"{index} wordend")
            word = widget.get(word_start, word_end)

            # Only show tooltip if it's a different word than current
            if word != self.current_hover_word:
                self.current_hover_word = word
                self.show_spelling_tooltip(widget, word, event.x_root, event.y_root)
        else:
            self.hide_spelling_tooltip()

    def show_spelling_tooltip(self, widget, word, x, y):
        """Show spelling suggestions in a tooltip bubble"""
        # Hide any existing tooltip
        self.hide_spelling_tooltip()

        # Get spelling suggestions
        try:
            suggestions = list(self.spell_checker.candidates(word))[:5]
            if not suggestions:
                # Fall back to correction method
                correction = self.spell_checker.correction(word)
                if correction and correction != word:
                    suggestions = [correction]
        except Exception:
            suggestions = []

        if not suggestions:
            return

        # Create tooltip window
        self.spelling_tooltip = tk.Toplevel(self)
        self.spelling_tooltip.wm_overrideredirect(True)
        self.spelling_tooltip.wm_geometry(f"+{x+15}+{y+15}")
        self.spelling_tooltip.configure(bg='#ffffe0', relief='solid', borderwidth=1)

        # Make tooltip semi-transparent (if supported)
        try:
            self.spelling_tooltip.attributes('-alpha', 0.95)
        except:
            pass

        # Add title
        title_label = tk.Label(
            self.spelling_tooltip,
            text=f"Suggestions for '{word}':",
            bg='#ffffe0',
            fg='#333333',
            font=("Arial", 9, "bold"),
            justify='left'
        )
        title_label.pack(padx=8, pady=(8, 4), anchor='w')

        # Add suggestions
        for i, suggestion in enumerate(suggestions):
            suggestion_frame = tk.Frame(self.spelling_tooltip, bg='#ffffe0')
            suggestion_frame.pack(fill='x', padx=8, pady=2)

            suggestion_label = tk.Label(
                suggestion_frame,
                text=suggestion,
                bg='#ffffe0',
                fg='#0066cc',
                font=("Arial", 9),
                cursor="hand2",
                justify='left'
            )
            suggestion_label.pack(side='left', anchor='w')

            # Bind click event to replace word
            suggestion_label.bind("<Button-1>",
                lambda e, s=suggestion, ws=word_start, we=word_end:
                self.replace_word_from_tooltip(s, ws, we))

            # Add hover effect
            suggestion_label.bind("<Enter>",
                lambda e, lbl=suggestion_label: lbl.configure(bg='#e6f3ff'))
            suggestion_label.bind("<Leave>",
                lambda e, lbl=suggestion_label: lbl.configure(bg='#ffffe0'))

        # Add ignore option
        ignore_frame = tk.Frame(self.spelling_tooltip, bg='#ffffe0')
        ignore_frame.pack(fill='x', padx=8, pady=(4, 8))

        ignore_label = tk.Label(
            ignore_frame,
            text="Ignore",
            bg='#ffffe0',
            fg='#666666',
            font=("Arial", 8, "italic"),
            cursor="hand2"
        )
        ignore_label.pack(side='left', anchor='w')
        ignore_label.bind("<Button-1>", lambda e: self.hide_spelling_tooltip())

    def hide_spelling_tooltip(self, event=None):
        """Hide the spelling suggestion tooltip"""
        if self.spelling_tooltip:
            try:
                self.spelling_tooltip.destroy()
            except:
                pass
            self.spelling_tooltip = None
        self.current_hover_word = None

    def replace_word_from_tooltip(self, suggestion, word_start, word_end):
        """Replace word from tooltip selection"""
        focused_widget = self.focus_get()
        if focused_widget in [self.content_editor._textbox, self.notes_editor._textbox]:
            focused_widget.delete(word_start, word_end)
            focused_widget.insert(word_start, suggestion)
            self.hide_spelling_tooltip()
            # Re-check spelling after replacement
            self.check_spelling()

    def show_spelling_suggestions(self, event):
        """Show spelling suggestions on right-click"""
        if not self.spell_checking_enabled:
            return

        widget = event.widget
        # Get the word under the cursor
        index = widget.index(f"@{event.x},{event.y}")
        word_start = widget.index(f"{index} wordstart")
        word_end = widget.index(f"{index} wordend")
        word = widget.get(word_start, word_end)

        # Skip if word is too short or not misspelled
        if len(word) < 4 or word.lower() in self.spell_checker:
            return

        # Highlight the word and show anchored tooltip
        widget.tag_remove("misspelled_anchor", "1.0", "end")
        widget.tag_add("misspelled_anchor", word_start, word_end)

        self.show_anchored_tooltip(widget, word, word_start, word_end, event.x_root, event.y_root)

    def replace_word(self, widget, start, end, replacement):
        """Replace a word with the selected suggestion"""
        widget.delete(start, end)
        widget.insert(start, replacement)
        # Remove highlight
        widget.tag_remove("misspelled_highlight", start, end)
        # Re-check spelling after replacement
        self.check_spelling()


    def hide_spelling_menu(self, event):
        """Hide spelling menu when clicking elsewhere"""
        try:
            self.spelling_menu.unpost()
        except:
            pass
        # Remove highlight
        for widget in [self.content_editor._textbox, self.notes_editor._textbox]:
            widget.tag_remove("misspelled_highlight", "1.0", "end")


#-------------------------------------------------------------------------------------
    def setup_logo(self):
        """Initialize logo with correct path handling"""
        try:
            # Get package paths
            package_root, resources_dir = setup_paths()

            # Possible logo locations in priority order
            possible_paths = [
                resources_dir / 'airis4d_logo.png',  # In resources directory
                package_root / 'icons' / 'airis4d_logo.png',  # In icons subdirectory
                package_root / 'airis4d_logo.png',  # In package root
                Path(__file__).parent / 'icons' / 'airis4d_logo.png',  # Relative to script
                Path(os.path.abspath(sys.prefix)) / 'share' / 'bsg-ide' / 'resources' / 'airis4d_logo.png',  # System share
                Path.home() / '.local' / 'share' / 'bsg-ide' / 'resources' / 'airis4d_logo.png'  # User data
            ]

            # Try each location
            for path in possible_paths:
                if path.exists():
                    try:
                        self.logo_image = ctk.CTkImage(
                            light_image=Image.open(path),
                            dark_image=Image.open(path),
                            size=(50, 50)
                        )
                        self.has_logo = True
                        self.logo_dir = path.parent
                        print(f"✓ Found logo at: {path}")
                        break
                    except Exception as e:
                        print(f"Warning: Could not load logo from {path}: {e}")
                        continue

            if not self.has_logo:
                print("Warning: Using ASCII logo - no image found in:")
                for path in possible_paths:
                    print(f"  - {path}")
                self.has_logo = False

        except Exception as e:
            print(f"Warning: Could not setup logo: {str(e)}")
            self.has_logo = False
#---------------------------------------------------------------------------------------

    def create_widgets(self):
        """Create and initialize all UI widgets"""
        try:
            # Create menu frame first
            #self.setup_top_menu()

            # Configure grid
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(0, weight=1)

            # Create main components
            self.create_sidebar()
            self.create_main_editor()
            self.create_toolbar()
            self.create_context_menu()
            self.create_footer()

            # Create terminal after other UI elements
            self.create_terminal()

            # Setup output redirection after terminal creation
            self.setup_output_redirection()

            # Initialize variables
            self.current_file = None
            self.slides = []
            self.current_slide_index = -1

            # Setup keyboard shortcuts
            self.setup_keyboard_shortcuts()

            # Setup Python paths
            setup_python_paths()

            # Adjust grid weights to accommodate terminal
            self.grid_rowconfigure(1, weight=3)  # Main editor
            self.grid_rowconfigure(4, weight=1)  # Terminal

            # Initialize syntax highlighter
            self.syntax_highlighter = None
            if hasattr(self, 'content_editor'):
                self.syntax_highlighter = BeamerSyntaxHighlighter(self.content_editor)

            # Create notes highlighter if notes editor exists
            if hasattr(self, 'notes_editor'):
                self.notes_highlighter = BeamerSyntaxHighlighter(self.notes_editor)

        except Exception as e:
            print(f"Error creating widgets: {str(e)}")
            raise

    def create_recent_files_menu(self):
        """Create recent files menu with error handling"""
        try:
            recent_menu = tk.Menu(self.menu_frame, tearoff=0)
            for filepath in self.session_data['recent_files']:
                if os.path.exists(filepath):
                    recent_menu.add_command(
                        label=os.path.basename(filepath),
                        command=lambda f=filepath: self.load_file(f)
                    )

            if recent_menu.index('end') is not None:  # Only add if menu has items
                self.menu_frame.add_cascade(label="Recent Files", menu=recent_menu)
        except Exception as e:
            print(f"Warning: Could not create recent files menu: {str(e)}")

    def print_loading_summary(self):
        """Print a summary of loaded slides for debugging"""
        logger.info("\n" + "="*60)
        logger.info("LOADING SUMMARY")
        logger.info("="*60)

        for idx, slide in enumerate(self.slides):
            logger.info(f"\nSlide {idx + 1}:")
            logger.info(f"  Title: {slide.get('title')}")
            logger.info(f"  Media: {slide.get('media')} (masked: {slide.get('_media_masked', False)})")
            logger.info(f"  Content lines: {len(slide.get('content', []))}")
            logger.info(f"    Hidden indices: {slide.get('_hidden_content_indices', [])}")
            for i, line in enumerate(slide.get('content', [])):
                is_hidden = i in slide.get('_hidden_content_indices', [])
                logger.info(f"    [{i}] {'[HIDDEN]' if is_hidden else '[VISIBLE]'} {line[:50]}")
            logger.info(f"  Notes lines: {len(slide.get('notes', []))}")
            logger.info(f"    Hidden note indices: {slide.get('_hidden_note_indices', [])}")
            logger.info(f"  Fully masked: {slide.get('_fully_masked', False)}")

        logger.info("="*60)

    def update_recent_files(self, filepath):
        """Update recent files list"""
        if filepath not in self.session_data['recent_files']:
            self.session_data['recent_files'].append(filepath)
        if len(self.session_data['recent_files']) > 10:
            self.session_data['recent_files'].pop(0)
        self.create_recent_files_menu()

    def on_window_configure(self, event=None):
        """Track window size and position changes"""
        if event and event.widget == self:
            self.session_data['window_size'] = {
                'width': self.winfo_width(),
                'height': self.winfo_height()
            }
            self.session_data['window_position'] = {
                'x': self.winfo_x(),
                'y': self.winfo_y()
            }

    def on_closing(self):
        """Handle window closing with error handling"""
        try:
            # Unbind all dynamic toolbar events
            if hasattr(self, 'upper_dynamic_toolbar'):
                self.upper_dynamic_toolbar.unbind_events()
            if hasattr(self, 'lower_dynamic_toolbar'):
                self.lower_dynamic_toolbar.unbind_events()
            if hasattr(self, 'media_dynamic_toolbar'):
                self.media_dynamic_toolbar.unbind_events()
            if hasattr(self, 'notes_mode_dynamic_toolbar'):
                self.notes_mode_dynamic_toolbar.unbind_events()

            # Rest of your existing on_closing code...
            if self.session_manager:
                self.session_data.update({
                    'last_file': self.current_file,
                    'working_directory': os.getcwd()
                })
                self.session_manager.save_session(self.session_data)
        except Exception as e:
            print(f"Warning: Could not save session on exit: {str(e)}")
        finally:
            self.destroy()

#--------------------------------------------------------------------------------
    def ide_callback(self, action, data):
        """Enhanced IDE callback handler with proper \\None handling"""
        if action == "update_current_slide":
            # Update slide title
            self.title_entry.delete(0, 'end')
            self.title_entry.insert(0, data.get('title', ''))

            # Ensure proper highlight in slide list
            self.current_slide_index = data.get('index', 0)
            self.update_slide_list()
            self.highlight_current_slide()

            # Important: Reset media when changing slides
            self.media_entry.delete(0, 'end')

        elif action == "update_content":
            # Update content editor, ensuring clean state
            self.content_editor.delete('1.0', 'end')
            for line in data.get('content', []):
                if line and line.strip():  # Only add non-empty lines
                    self.content_editor.insert('end', f"{line}\n")

        elif action == "update_media":
            # Update media entry with proper \None handling
            self.media_entry.delete(0, 'end')
            media = data.get('media')

            # Handle different media cases
            if media is None or media == "\\None":
                self.media_entry.insert(0, "\\None")
            elif media:  # Only insert if there's actual media content
                self.media_entry.insert(0, media)

        elif action == "show_current_slide":
            # Show complete slide with proper state reset
            self.current_slide_index = data.get('index', 0)

            # Clear everything first
            self.title_entry.delete(0, 'end')
            self.media_entry.delete(0, 'end')
            self.content_editor.delete('1.0', 'end')

            # Update title
            if title := data.get('title'):
                self.title_entry.insert(0, title)

            # Update media with explicit \None handling
            media = data.get('media')
            if media is None or media == "\\None":
                self.media_entry.insert(0, "\\None")
            elif media:
                self.media_entry.insert(0, media)

            # Update content
            content = data.get('content', [])
            if content:
                for line in content:
                    if line and line.strip():
                        self.content_editor.insert('end', f"{line}\n")

            # Update slide list display
            self.update_slide_list()
            self.slide_list.see(f"{self.current_slide_index + 1}.0")
            self.highlight_current_slide()

        elif action == "navigate_to_slide":
            # Navigate to specific slide with complete state reset
            index = data.get('index', 0)
            if 0 <= index < len(self.slides):
                # Clear current state
                self.media_entry.delete(0, 'end')
                self.content_editor.delete('1.0', 'end')

                self.current_slide_index = index
                self.load_slide(index)
                self.update_slide_list()

                if data.get('focus'):
                    self.slide_list.see(f"{index + 1}.0")
                    self.highlight_current_slide()

        elif action == "error":
            # Show error in terminal
            if hasattr(self, 'terminal'):
                self.terminal.write(f"Error: {data.get('message', 'Unknown error')}\n", "red")

    def load_slide(self, index):
        r"""Enhanced load_slide with proper hidden content display and \None handling"""
        if 0 <= index < len(self.slides):
            slide = self.slides[index]

            # Clear all fields first
            self.title_entry.delete(0, 'end')
            self.media_entry.delete(0, 'end')
            self.content_editor.delete('1.0', 'end')
            self.notes_editor.delete('1.0', 'end')

            # Update title
            title_text = slide.get('title', '')
            self.title_entry.insert(0, title_text)

            # Update media with masking if needed
            media = slide.get('media', '')
            media_masked = slide.get('_media_masked', False)

            # CRITICAL FIX: Proper \None handling
            # Always show \None if media is empty, None, or explicitly set to "\None"
            if not media or media == "" or media == "\\None":
                # Show \None (may be masked if media_masked is True)
                if media_masked:
                    self.media_entry.insert(0, "% \\None")
                else:
                    self.media_entry.insert(0, "\\None")
                # Also ensure slide data is consistent
                if media == "" or media is None:
                    slide['media'] = ""
            else:
                # Normal media display
                if media_masked:
                    self.media_entry.insert(0, f"% {media}")
                else:
                    self.media_entry.insert(0, media)

            # Configure tags for hidden content (dimmed/strikethrough)
            try:
                self.content_editor._textbox.tag_delete('hidden_content')
                self.notes_editor._textbox.tag_delete('hidden_note')
            except:
                pass

            self.content_editor._textbox.tag_config('hidden_content',
                                                      foreground='#888888',
                                                      font=('TkFixedFont', 10, 'overstrike'))
            self.notes_editor._textbox.tag_config('hidden_note',
                                                   foreground='#888888',
                                                   font=('TkFixedFont', 10, 'overstrike'))

            # Get hidden indices
            hidden_content_indices = set(slide.get('_hidden_content_indices', []))
            hidden_note_indices = set(slide.get('_hidden_note_indices', []))

            # Update content with proper masking display
            content_items = slide.get('content', [])

            # If there's no content but we have media, add a placeholder
            if not content_items and media:
                # Just show the content as is (no extra placeholder)
                pass

            for i, item in enumerate(content_items):
                if item and item.strip():
                    # Check if this line should be hidden
                    is_hidden = i in hidden_content_indices

                    if is_hidden:
                        # Insert with % marker and apply hidden tag
                        self.content_editor.insert('end', f"% {item}\n")
                        # Apply tag to the line we just inserted
                        line_start = f"{self.content_editor.index('end-2l')}"
                        line_end = f"{self.content_editor.index('end-1c')}"
                        self.content_editor._textbox.tag_add('hidden_content', line_start, line_end)
                    else:
                        self.content_editor.insert('end', f"{item}\n")

            # Add placeholder text if empty
            if not slide.get('content'):
                self.content_editor.insert('end', "% No content for this slide\n")

            # Update notes with proper masking display
            for i, note in enumerate(slide.get('notes', [])):
                if note and note.strip():
                    is_hidden = i in hidden_note_indices

                    if is_hidden:
                        self.notes_editor.insert('end', f"% {note}\n")
                        line_start = f"{self.notes_editor.index('end-2l')}"
                        line_end = f"{self.notes_editor.index('end-1c')}"
                        self.notes_editor._textbox.tag_add('hidden_note', line_start, line_end)
                    else:
                        self.notes_editor.insert('end', f"{note}\n")

            # Add placeholder text if empty
            if not slide.get('notes'):
                self.notes_editor.insert('end', "% No notes for this slide\n")

            # Refresh syntax highlighting
            if hasattr(self, 'syntax_highlighter') and self.syntax_highlighter.active:
                self.syntax_highlighter.highlight()

            # Also refresh notes highlighting if available
            if hasattr(self, 'notes_highlighter') and self.notes_highlighter.active:
                self.notes_highlighter.highlight()

    def format_tikz_for_output(self, media_content: str) -> str:
        """Format TikZ code for proper output in the text file"""
        if "% TikZ Diagram:" in media_content:
            # Extract just the TikZ code part
            lines = media_content.split('\n')
            tikz_code = []
            in_tikz = False

            for line in lines:
                if '\\begin{tikzpicture}' in line:
                    in_tikz = True
                if in_tikz:
                    tikz_code.append(line)
                if '\\end{tikzpicture}' in line:
                    in_tikz = False

            return '\n'.join(tikz_code)
        return media_content

    def on_line_click_to_unmask(self, event):
        """Handle clicking on a masked line to show unmask option"""
        if not hasattr(self, 'spell_checking_enabled'):
            return

        focused_widget = event.widget

        # Check if this is one of our editors
        if focused_widget not in [self.content_editor._textbox, self.notes_editor._textbox]:
            return

        index = focused_widget.index(f"@{event.x},{event.y}")

        # Check if clicking on a hidden line
        if 'hidden_content' in focused_widget.tag_names(index) or 'hidden_note' in focused_widget.tag_names(index):
            # Show a tooltip or context menu with unmask option
            self.show_unmask_prompt(focused_widget, index)

    def show_unmask_prompt(self, widget, index):
        """Show prompt to unmask a line"""
        # Get the line content
        line_start = widget.index(f"{index} linestart")
        line_end = widget.index(f"{index} lineend")
        line_content = widget.get(line_start, line_end)

        # Create a popup menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Unmask this line",
                         command=lambda: self.unmask_line_at_index(widget, line_start, line_end))
        menu.add_command(label="Unmask all lines in this slide",
                         command=lambda: self.unmask_all_lines_in_current_slide())
        menu.add_separator()
        menu.add_command(label="Cancel")

        # Show the menu at mouse position
        x = widget.winfo_pointerx()
        y = widget.winfo_pointery()
        menu.tk_popup(x, y)

    def unmask_line_at_index(self, widget, line_start, line_end):
        """Unmask a specific line"""
        line_content = widget.get(line_start, line_end)
        # Remove the % prefix
        unmasked = re.sub(r'^\s*%\s*', '', line_content)
        widget.delete(line_start, line_end)
        widget.insert(line_start, unmasked)

        # Update the slide data
        self.save_current_slide()
        self.write("✓ Line unmasked\n", "green")

    def unmask_all_lines_in_current_slide(self):
        """Unmask all hidden lines in the current slide"""
        if self.current_slide_index < 0:
            return

        # Process content editor
        content_text = self.content_editor.get('1.0', 'end-1c')
        content_lines = content_text.split('\n')
        unmasked_content = []

        for line in content_lines:
            if line.lstrip().startswith('%'):
                unmasked = re.sub(r'^\s*%\s*', '', line)
                unmasked_content.append(unmasked)
            else:
                unmasked_content.append(line)

        # Update content editor
        self.content_editor.delete('1.0', 'end')
        self.content_editor.insert('1.0', '\n'.join(unmasked_content))

        # Process notes editor similarly
        notes_text = self.notes_editor.get('1.0', 'end-1c')
        notes_lines = notes_text.split('\n')
        unmasked_notes = []

        for line in notes_lines:
            if line.lstrip().startswith('%'):
                unmasked = re.sub(r'^\s*%\s*', '', line)
                unmasked_notes.append(unmasked)
            else:
                unmasked_notes.append(line)

        self.notes_editor.delete('1.0', 'end')
        self.notes_editor.insert('1.0', '\n'.join(unmasked_notes))

        # Clear hidden indices in slide data
        if 0 <= self.current_slide_index < len(self.slides):
            self.slides[self.current_slide_index]['_hidden_content_indices'] = []
            self.slides[self.current_slide_index]['_hidden_note_indices'] = []
            self.slides[self.current_slide_index]['_media_masked'] = False

        self.save_current_slide()
        self.write(f"✓ All lines unmasked in slide {self.current_slide_index + 1}\n", "green")

#--------------------------------------------------------------------------------------------------------------------
    def setup_output_redirection(self):
        """Set up output redirection to terminal"""
        if hasattr(self, 'terminal'):
            sys.stdout = SimpleRedirector(self.terminal, "white")
            sys.stderr = SimpleRedirector(self.terminal, "red")

    # Method to update working directory
    def update_terminal_directory(self, directory: str) -> None:
        """Update terminal working directory"""
        if hasattr(self, 'terminal'):
            self.terminal.set_working_directory(directory)
#---------------------------------------------------------------------------New run pdflatex ----------------
    # First, add an input method to handle terminal input
    def terminal_input(self, prompt: str) -> str:
        """Get input from terminal with prompt"""
        try:
            self.write(prompt, "yellow")
            # Use terminal's built-in input handling
            future_input = []
            input_ready = threading.Event()

            def on_input(text):
                future_input.append(text)
                input_ready.set()

            # Store current input handler
            old_handler = self.terminal._handle_input

            # Set temporary input handler
            def temp_handler(event):
                text = self.terminal.display._textbox.get("insert linestart", "insert lineend")
                if text.startswith("$ "):
                    text = text[2:].strip()
                    self.terminal.write("\n")
                    on_input(text)
                    return "break"
                return "break"

            self.terminal.display.bind("<Return>", temp_handler)

            # Wait for input
            input_ready.wait()

            # Restore original handler
            self.terminal.display.bind("<Return>", old_handler)

            return future_input[0] if future_input else ""

        except Exception as e:
            self.write(f"Error getting input: {str(e)}\n", "red")
            return ""

    def navigate_slides(self, event):
        """Handle keyboard navigation between slides"""
        if not self.slides:
            return

        # Save current slide before navigation
        self.save_current_slide()

        if event.keysym == 'Up':
            if self.current_slide_index > 0:
                self.current_slide_index -= 1
        elif event.keysym == 'Down':
            if self.current_slide_index < len(self.slides) - 1:
                self.current_slide_index += 1
        elif event.keysym == 'Left':
            if self.current_slide_index > 0:
                self.current_slide_index -= 1
        elif event.keysym == 'Right':
            if self.current_slide_index < len(self.slides) - 1:
                self.current_slide_index += 1

        # Load the new slide
        self.load_slide(self.current_slide_index)
        self.update_slide_list()

        # Ensure the current slide is visible in the list
        line_number = self.current_slide_index + 1
        self.slide_list.see(f"{line_number}.0")

        # Update visual highlighting
        self.highlight_current_slide()

        return "break"  # Prevent default handling
    #----------------------------------------------------------------
    def write_to_terminal(self, text: str, color: str = "white") -> None:
        """Alias for write method to maintain compatibility"""
        self.write(text, color)


    def create_terminal(self) -> None:
        """Create terminal initially hidden"""
        # Create terminal instance
        self.terminal = InteractiveTerminal(self, initial_directory=os.getcwd())
        self.terminal.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.grid_rowconfigure(4, weight=0)  # Initially no weight

        # Hide terminal initially
        self.terminal.grid_remove()

        # Set up redirections
        sys.stdout = SimpleRedirector(self.terminal, "white")
        sys.stderr = SimpleRedirector(self.terminal, "red")

        # Store process reference
        self.current_process = None

    def toggle_terminal(self) -> None:
        """Toggle terminal visibility"""
        self.terminal_visible = not self.terminal_visible

        if self.terminal_visible:
            # Show terminal
            self.terminal.grid()
            self.grid_rowconfigure(4, weight=1)  # Give weight when visible
            self.terminal_button.configure(text="▼ Hide Terminal")

            # Optionally resize window to accommodate terminal
            current_height = self.winfo_height()
            if current_height < 800:  # Minimum height with terminal
                new_height = min(800, self.winfo_screenheight() - 100)
                self.geometry(f"{self.winfo_width()}x{new_height}")
        else:
            # Hide terminal
            self.terminal.grid_remove()
            self.grid_rowconfigure(4, weight=0)  # Remove weight when hidden
            self.terminal_button.configure(text="▲ Show Terminal")

            # Optionally resize window back
            if self.winfo_height() > 600:  # Minimum height without terminal
                self.geometry(f"{self.winfo_width()}x600")


    def flush(self):
        """Required for stdout/stderr redirection"""
        pass

    # Replace the clear_terminal method
    def clear_terminal(self) -> None:
        """Clear terminal content"""
        if hasattr(self, 'terminal'):
            self.terminal.clear()

    def stop_compilation(self) -> None:
        """Stop current compilation process"""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.write("\n[Compilation process terminated by user]\n")
            except:
                pass
            finally:
                self.current_process = None

#--------------------------------------------------------------------------------------------------------------------
    def create_footer(self):
        """Create footer with institution info and properly tracked logo"""
        # Footer frame with dark theme
        self.footer = ctk.CTkFrame(self)
        self.footer.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Left side - Logo and Institution name
        left_frame = ctk.CTkFrame(self.footer, fg_color="transparent")
        left_frame.pack(side="left", padx=10)

        # Add terminal toggle button
        self.terminal_visible = False
        self.terminal_button = ctk.CTkButton(
            left_frame,
            text="▲ Show Terminal",
            command=self.toggle_terminal,
            width=120,
            height=24,
            fg_color="#2F3542",
            hover_color="#404859"
        )
        self.terminal_button.pack(side="left", padx=10)

        # Logo (image or ASCII)
        if self.has_logo and hasattr(self, 'logo_image'):
            try:
                logo_label = ctk.CTkLabel(
                    left_frame,
                    image=self.logo_image,
                    text=""
                )
                logo_label.pack(side="left", padx=(0, 10))
            except Exception as e:
                print(f"Warning: Could not create logo label: {e}")
                self.create_ascii_logo(left_frame)
        else:
            self.create_ascii_logo(left_frame)

        # Institution name
        inst_label = ctk.CTkLabel(
            left_frame,
            text="Artificial Intelligence Research and Intelligent Systems (airis4D)",
            font=("Arial", 12, "bold"),
            text_color="#4ECDC4"
        )
        inst_label.pack(side="left", padx=10)

        # Right side - Contact and GitHub links
        links_frame = ctk.CTkFrame(self.footer, fg_color="transparent")
        links_frame.pack(side="right", padx=10)

        # Version info
        version_label = ctk.CTkLabel(
            links_frame,
            text=f"v{self.__version__}",
            font=("Arial", 10),
            text_color="#6272A4"
        )
        version_label.pack(side="left", padx=5)

        # Contact link
        contact_button = ctk.CTkButton(
            links_frame,
            text="nsp@airis4d.com",
            command=lambda: webbrowser.open("mailto:nsp@airis4d.com"),
            fg_color="transparent",
            text_color="#FFB86C",
            hover_color="#2F3542",
            height=20
        )
        contact_button.pack(side="left", padx=5)

        # Separator
        separator = ctk.CTkLabel(
            links_frame,
            text="|",
            text_color="#6272A4"
        )
        separator.pack(side="left", padx=5)

        # GitHub link
        github_button = ctk.CTkButton(
            links_frame,
            text="GitHub",
            command=lambda: webbrowser.open("https://github.com/sajeethphilip/Beamer-Slide-Generator.git"),
            fg_color="transparent",
            text_color="#FFB86C",
            hover_color="#2F3542",
            height=20
        )
        github_button.pack(side="left", padx=5)

        # License info
        license_label = ctk.CTkLabel(
            links_frame,
            text=f"({self.__license__})",
            font=("Arial", 10),
            text_color="#6272A4"
        )
        license_label.pack(side="left", padx=5)

    def create_ascii_logo(self, parent):
        """Create ASCII logo as fallback"""
        logo_label = ctk.CTkLabel(
            parent,
            text=self.logo_ascii,
            font=("Courier", 10),
            justify="left"
        )
        logo_label.pack(side="left", padx=(0, 10))

    def create_about_dialog(self) -> None:
        """Create about dialog with logo and information"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("About BeamerSlide Generator")
        dialog.geometry("400x300")

        # Center the dialog on the main window
        dialog.transient(self)
        dialog.grab_set()

        # Logo
        if self.has_logo:
            logo_label = ctk.CTkLabel(
                dialog,
                image=self.logo_image,
                text=""
            )
        else:
            logo_label = ctk.CTkLabel(
                dialog,
                text=self.logo_ascii,
                font=("Courier", 10),
                justify="left"
            )
        logo_label.pack(pady=20)

        # Information
        info_text = f"""
BeamerSlide Generator IDE
Version {self.__version__}

Created by {self.__author__}
{self.presentation_info['institution']}

{self.__license__} License
        """

        info_label = ctk.CTkLabel(
            dialog,
            text=info_text,
            font=("Arial", 12),
            justify="center"
        )
        info_label.pack(pady=20)

        # Close button
        close_button = ctk.CTkButton(
            dialog,
            text="Close",
            command=dialog.destroy
        )
        close_button.pack(pady=20)
#----------------------------------------------------------------------------------------
    def setup_top_menu(self) -> None:
        """Create top menu bar with proper spacing and visibility"""

        # Create a proper menu bar using tkinter Menu
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # ========== FILE MENU ==========
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()

        # Recent Files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self.update_recent_menu()

        file_menu.add_separator()
        file_menu.add_command(label="Load TeX File...", command=self.load_tex_file)
        file_menu.add_command(label="Get Source from TeX...", command=self.get_source_from_tex)
        file_menu.add_separator()
        file_menu.add_command(label="Export to Overleaf...", command=self.create_overleaf_zip)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing, accelerator="Ctrl+Q")
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # ========== EDIT MENU ==========
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self._editor_action('cut'), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=lambda: self._editor_action('copy'), accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=lambda: self._editor_action('paste'), accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find/Replace", command=self.show_search_replace_dialog, accelerator="Ctrl+F")
        edit_menu.add_separator()

        # Slide Operations submenu
        slide_ops = tk.Menu(edit_menu, tearoff=0)
        slide_ops.add_command(label="New Slide", command=self.new_slide, accelerator="Ctrl+N")
        slide_ops.add_command(label="Insert Below", command=self.insert_slide_below, accelerator="Ctrl+I")
        slide_ops.add_command(label="Duplicate Slide", command=self.duplicate_slide, accelerator="Ctrl+D")
        slide_ops.add_separator()
        slide_ops.add_command(label="Move Up", command=lambda: self.move_slide(-1), accelerator="Ctrl+Up")
        slide_ops.add_command(label="Move Down", command=lambda: self.move_slide(1), accelerator="Ctrl+Down")
        edit_menu.add_cascade(label="Slide Operations", menu=slide_ops)

        # Mask/Unmask submenu
        mask_ops = tk.Menu(edit_menu, tearoff=0)
        mask_ops.add_command(label="Mask/Unmask Line", command=self.mask_line_in_editor, accelerator="Ctrl+Delete")
        mask_ops.add_command(label="Mask Current Slide", command=self.mask_current_slide)
        mask_ops.add_command(label="Restore Current Slide", command=self.restore_deleted_slide, accelerator="Ctrl+Shift+R")
        mask_ops.add_separator()
        mask_ops.add_command(label="Restore All Deleted", command=self.restore_all_deleted_slides)
        mask_ops.add_command(label="Permanently Delete Masked", command=self.permanently_delete_masked_slides)
        edit_menu.add_cascade(label="Mask/Unmask", menu=mask_ops)

        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # ========== VIEW MENU ==========
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        view_menu.add_checkbutton(label="Syntax Highlighting", variable=self.highlight_var,
                                  command=self.toggle_highlighting)
        view_menu.add_command(label="Toggle Terminal", command=self.toggle_terminal, accelerator="Ctrl+T")
        view_menu.add_separator()

        # Notes Mode submenu
        notes_menu = tk.Menu(view_menu, tearoff=0)
        self.notes_mode_var = tk.StringVar(value="both")
        notes_menu.add_radiobutton(label="Slides Only", variable=self.notes_mode_var,
                                   value="slides", command=lambda: self.set_notes_mode("slides"))
        notes_menu.add_radiobutton(label="Notes Only", variable=self.notes_mode_var,
                                   value="notes", command=lambda: self.set_notes_mode("notes"))
        notes_menu.add_radiobutton(label="Slides + Notes", variable=self.notes_mode_var,
                                   value="both", command=lambda: self.set_notes_mode("both"))
        view_menu.add_cascade(label="Notes Mode", menu=notes_menu)

        self.menu_bar.add_cascade(label="View", menu=view_menu)

        # ========== INSERT MENU ==========
        insert_menu = tk.Menu(self.menu_bar, tearoff=0)

        # LaTeX Commands
        insert_menu.add_command(label="LaTeX Command Index...", command=self.show_enhanced_command_index)
        insert_menu.add_separator()

        # List Environments
        list_menu = tk.Menu(insert_menu, tearoff=0)
        list_menu.add_command(label="Bullet Point", command=lambda: self._insert_text("- "))
        list_menu.add_command(label="Itemize Environment",
                             command=lambda: self._insert_text("\\begin{itemize}\n    \\item \n\\end{itemize}"))
        list_menu.add_command(label="Enumerate Environment",
                             command=lambda: self._insert_text("\\begin{enumerate}\n    \\item \n\\end{enumerate}"))
        insert_menu.add_cascade(label="List Environments", menu=list_menu)

        # Text Formatting
        format_menu = tk.Menu(insert_menu, tearoff=0)
        format_menu.add_command(label="Bold", command=lambda: self._wrap_selection(r'\textbf{', '}'))
        format_menu.add_command(label="Italic", command=lambda: self._wrap_selection(r'\textit{', '}'))
        format_menu.add_command(label="Color", command=self._insert_color_command)
        format_menu.add_command(label="Highlight", command=lambda: self._wrap_selection(r'\hl{', '}'))
        insert_menu.add_cascade(label="Text Formatting", menu=format_menu)

        # Media
        media_menu = tk.Menu(insert_menu, tearoff=0)
        media_menu.add_command(label="Local File...", command=self.browse_media)
        media_menu.add_command(label="YouTube Video...", command=self.youtube_dialog)
        media_menu.add_command(label="Search Images...", command=self.search_images)
        media_menu.add_command(label="Screen Capture...", command=self.capture_screen)
        media_menu.add_command(label="Camera Capture...", command=self.open_camera)
        insert_menu.add_cascade(label="Media", menu=media_menu)

        # TikZ
        tikz_menu = tk.Menu(insert_menu, tearoff=0)
        tikz_menu.add_command(label="TikZ Color Helper...", command=self.show_tikz_color_helper)
        tikz_menu.add_command(label="Basic Node",
                             command=lambda: self._insert_text("\\node[fill=airis4d_blue, text=white] {Text};"))
        tikz_menu.add_command(label="Simple Diagram", command=self._insert_tikz_diagram)
        insert_menu.add_cascade(label="TikZ Elements", menu=tikz_menu)

        self.menu_bar.add_cascade(label="Insert", menu=insert_menu)

        # ========== TOOLS MENU ==========
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)

        # Presentation Tools
        tools_menu.add_command(label="Presentation Settings...", command=self.show_settings_dialog)
        tools_menu.add_command(label="Edit Preamble...", command=self.edit_preamble)
        tools_menu.add_separator()

        # Generation Tools
        gen_menu = tk.Menu(tools_menu, tearoff=0)
        gen_menu.add_command(label="Generate PDF", command=self.generate_pdf)
        gen_menu.add_command(label="Convert to TeX", command=self.convert_to_tex)
        gen_menu.add_command(label="Preview PDF", command=self.preview_pdf)
        gen_menu.add_command(label="Present with Notes", command=self.present_with_notes)
        tools_menu.add_cascade(label="Generation", menu=gen_menu)

        tools_menu.add_separator()

        # Grammar & Spell Check
        tools_menu.add_command(label="Grammarly Settings...", command=self.toggle_grammarly)
        tools_menu.add_command(label="Spell Check Settings...", command=self.show_spellcheck_settings)
        tools_menu.add_separator()

        # Color Tools
        tools_menu.add_command(label="TikZ Color Helper...", command=self.show_tikz_color_helper)

        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)

        # ========== HELP MENU ==========
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="LaTeX Command Reference...", command=self.show_enhanced_command_index)
        help_menu.add_separator()
        help_menu.add_command(label="Create Desktop Shortcut", command=self.create_desktop_shortcut)
        help_menu.add_separator()
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_keyboard_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About BSG-IDE", command=self.create_about_dialog)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

        # Keep the original button row for backward compatibility (optional)
        # You can comment this out if you want only the menu bar
        self._create_button_row()

    def _create_button_row(self):
        """Create the original button row (kept for compatibility)"""
        # Main menu container
        self.menu_frame = ctk.CTkFrame(self)
        self.menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.menu_frame.grid_columnconfigure(1, weight=1)

        # Left side buttons
        left_buttons = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        left_buttons.grid(row=0, column=0, sticky="w", padx=5)

        menu_buttons = [
            ("Edit Preamble", self.edit_preamble, "Edit LaTeX preamble"),
            ("Presentation Settings", self.show_settings_dialog, "Configure presentation settings"),
            ("Get Source", self.get_source_from_tex, "Extract source from TEX file"),
            ("Load TeX File", self.load_tex_file, "Load and convert Beamer TeX file"),
            ("Overwrite TeX+PDF", self.overwrite_tex_and_generate_pdf, "Convert back to TeX and generate PDF"),
        ]

        for text, command, tooltip in menu_buttons:
            btn = ctk.CTkButton(left_buttons, text=text, command=command, width=130)
            btn.pack(side="left", padx=5)
            self.create_tooltip(btn, tooltip)

        # Right side buttons
        right_buttons = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        right_buttons.grid(row=0, column=1, sticky="e", padx=5)

        self.highlight_var = ctk.BooleanVar(value=True)
        self.highlight_switch = ctk.CTkSwitch(
            right_buttons,
            text="Syntax Highlighting",
            variable=self.highlight_var,
            command=self.toggle_highlighting,
            width=150
        )
        self.highlight_switch.pack(side="right", padx=5)

    # ========== HELPER METHODS FOR MENU ACTIONS ==========

    def _editor_action(self, action):
        """Perform edit action on focused widget"""
        focused = self.focus_get()
        if focused in [self.content_editor._textbox, self.notes_editor._textbox]:
            try:
                if action == 'cut':
                    focused.event_generate('<<Cut>>')
                elif action == 'copy':
                    focused.event_generate('<<Copy>>')
                elif action == 'paste':
                    focused.event_generate('<<Paste>>')
            except:
                pass

    def _insert_text(self, text):
        """Insert text into focused editor"""
        focused = self.focus_get()
        if focused == self.content_editor._textbox:
            self.content_editor.insert("insert", text)
        elif focused == self.notes_editor._textbox:
            self.notes_editor.insert("insert", text)
        elif focused == self.title_entry:
            self.title_entry.insert("insert", text)

    def _wrap_selection(self, prefix, suffix):
        """Wrap selected text with prefix and suffix"""
        focused = self.focus_get()
        if focused in [self.content_editor._textbox, self.notes_editor._textbox]:
            try:
                selection = focused.get('sel.first', 'sel.last')
                focused.delete('sel.first', 'sel.last')
                focused.insert('insert', f'{prefix}{selection}{suffix}')
            except tk.TclError:
                focused.insert('insert', f'{prefix}{suffix}')

    def _insert_color_command(self):
        """Insert textcolor command"""
        from tkinter import simpledialog
        color = simpledialog.askstring("Color", "Enter color name or RGB (e.g., red, blue, #FF0000):")
        if color:
            self._wrap_selection(f'\\textcolor{{{color}}}{{', '}')

    def _insert_tikz_diagram(self):
        """Insert a simple TikZ diagram template"""
        diagram = """\\begin{tikzpicture}
        \\draw[fill=airis4d_blue] (0,0) rectangle (2,1);
        \\node[text=white] at (1,0.5) {Label};
    \\end{tikzpicture}"""
        self._insert_text(diagram)

    def show_search_replace_dialog(self):
        """Show search/replace dialog for the focused editor"""
        focused = self.focus_get()
        if focused in [self.content_editor._textbox, self.notes_editor._textbox]:
            SearchReplacePanel(self, focused)

    def _show_keyboard_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts_text = """
        ╔══════════════════════════════════════════════════════════════╗
        ║                   BSG-IDE KEYBOARD SHORTCUTS                 ║
        ╚══════════════════════════════════════════════════════════════╝

        ┌─────────────── FILE OPERATIONS ───────────────┐
        │ Ctrl+N   - New presentation                    │
        │ Ctrl+O   - Open file                          │
        │ Ctrl+S   - Save file                          │
        │ Ctrl+Q   - Exit                               │
        └────────────────────────────────────────────────┘

        ┌─────────────── EDIT OPERATIONS ───────────────┐
        │ Ctrl+Z   - Undo                               │
        │ Ctrl+Y   - Redo                               │
        │ Ctrl+X   - Cut                                │
        │ Ctrl+C   - Copy                               │
        │ Ctrl+V   - Paste                              │
        │ Ctrl+F   - Find/Replace                       │
        │ Ctrl+Delete - Mask/Unmask current line        │
        └────────────────────────────────────────────────┘

        ┌─────────────── SLIDE NAVIGATION ──────────────┐
        │ Ctrl+Up/Down     - Move current slide         │
        │ Ctrl+Left/Right  - Navigate slides            │
        │ Delete           - Delete/mask current slide  │
        │ Ctrl+Shift+R     - Restore deleted slide      │
        └────────────────────────────────────────────────┘

        ┌─────────────── SLIDE CREATION ────────────────┐
        │ Ctrl+N   - New slide (in slide list)          │
        │ Ctrl+I   - Insert slide below                 │
        │ Ctrl+D   - Duplicate slide                    │
        └────────────────────────────────────────────────┘

        ┌─────────────── VIEW OPERATIONS ───────────────┐
        │ Ctrl+T   - Toggle terminal                    │
        └────────────────────────────────────────────────┘
        """

        dialog = ctk.CTkToplevel(self)
        dialog.title("Keyboard Shortcuts")
        dialog.geometry("650x550")
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 650) // 2
        y = (dialog.winfo_screenheight() - 550) // 2
        dialog.geometry(f"+{x}+{y}")

        text_widget = ctk.CTkTextbox(dialog, font=("Courier", 11))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", shortcuts_text)
        text_widget.configure(state="disabled")

        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(button_frame, text="Close", command=dialog.destroy).pack(side="right", padx=5)

    def update_recent_menu(self):
        """Update the recent files menu"""
        if hasattr(self, 'recent_menu'):
            self.recent_menu.delete(0, 'end')
            if hasattr(self, 'session_data') and self.session_data.get('recent_files'):
                for filepath in self.session_data['recent_files'][-10:]:
                    if os.path.exists(filepath):
                        self.recent_menu.add_command(
                            label=os.path.basename(filepath),
                            command=lambda f=filepath: self.load_file(f)
                        )
            else:
                self.recent_menu.add_command(label="No recent files", state="disabled")

    def create_desktop_shortcut(self):
        """Create desktop shortcut/menu entry from within the IDE"""
        import platform
        import subprocess
        from pathlib import Path

        system = platform.system()
        home = Path.home()

        # Check if already exists
        if system == "Linux":
            desktop_file = home / ".local" / "share" / "applications" / "bsg-ide.desktop"
            if desktop_file.exists():
                response = messagebox.askyesno("Shortcut Exists",
                    "A menu entry already exists.\n\nDo you want to recreate it?")
                if not response:
                    return

        elif system == "Windows":
            start_menu = Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            shortcut_path = start_menu / "BSG-IDE" / "BSG-IDE.lnk"
            if shortcut_path.exists():
                response = messagebox.askyesno("Shortcut Exists",
                    "A Start Menu shortcut already exists.\n\nDo you want to recreate it?")
                if not response:
                    return

        elif system == "Darwin":
            app_path = home / "Applications" / "BSG-IDE.app"
            if app_path.exists():
                response = messagebox.askyesno("Shortcut Exists",
                    "An application bundle already exists.\n\nDo you want to recreate it?")
                if not response:
                    return

        try:
            self.write("Creating system menu entry...\n", "cyan")

            if system == "Linux":
                # Create desktop entry for Linux
                desktop_content = f"""[Desktop Entry]
    Version=1.0
    Type=Application
    Name=BSG-IDE
    Comment=Beamer Slide Generator IDE
    Exec=bsg-ide
    Icon=bsg-ide
    Terminal=false
    Categories=Office;Development;Education;
    StartupNotify=true
    """
                desktop_file = home / ".local" / "share" / "applications" / "bsg-ide.desktop"
                desktop_file.parent.mkdir(parents=True, exist_ok=True)
                desktop_file.write_text(desktop_content)
                desktop_file.chmod(0o755)

                # Update desktop database
                subprocess.run(['update-desktop-database', str(desktop_file.parent)],
                             capture_output=True)
                self.write("✓ Menu entry created in Applications menu\n", "green")
                messagebox.showinfo("Success",
                    "Menu entry created!\n\nYou can now find BSG-IDE in your Applications menu.")

            elif system == "Windows":
                # Create Start Menu shortcut for Windows
                start_menu = Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
                start_menu_dir = start_menu / "BSG-IDE"
                start_menu_dir.mkdir(parents=True, exist_ok=True)

                shortcut_path = start_menu_dir / "BSG-IDE.lnk"

                # Find the Python executable and module path
                import bsg_ide
                bsg_path = Path(bsg_ide.__file__).parent

                # Create using PowerShell
                ps_script = f'''
    $WScriptShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WScriptShell.CreateShortcut("{shortcut_path}")
    $Shortcut.TargetPath = "python"
    $Shortcut.Arguments = "-c ""from bsg_ide.BSG_IDE import launch_ide; launch_ide()"""
    $Shortcut.WorkingDirectory = "{os.path.expanduser('~')}\\Documents"
    $Shortcut.IconLocation = "{bsg_path / 'resources' / 'bsg-ide.ico' if (bsg_path / 'resources' / 'bsg-ide.ico').exists() else 'python.exe'}"
    $Shortcut.Save()
    '''
                result = subprocess.run(['powershell', '-Command', ps_script],
                                      capture_output=True, text=True)

                if result.returncode == 0:
                    self.write("✓ Start Menu shortcut created\n", "green")
                    messagebox.showinfo("Success",
                        "Start Menu shortcut created!\n\nYou can now find BSG-IDE in your Start Menu.")
                else:
                    self.write("⚠ Shortcut created with warnings\n", "yellow")
                    messagebox.showwarning("Partial Success",
                        "Shortcut created but with warnings.\n\nYou may need to run as administrator.")

            elif system == "Darwin":  # macOS
                # Create application bundle for macOS
                app_path = home / "Applications" / "BSG-IDE.app"
                contents = app_path / "Contents"
                macos = contents / "MacOS"
                resources = contents / "Resources"

                for d in [macos, resources]:
                    d.mkdir(parents=True, exist_ok=True)

                # Create launcher script
                launcher = macos / "bsg-ide"
                launcher.write_text('''#!/bin/bash
    exec python3 -c "from bsg_ide.BSG_IDE import launch_ide; launch_ide()"
    ''')
                launcher.chmod(0o755)

                self.write("✓ Application bundle created in Applications folder\n", "green")
                messagebox.showinfo("Success",
                    "Application bundle created!\n\nYou can now find BSG-IDE in your Applications folder.")

            else:
                self.write(f"⚠ Menu entry creation not supported on {system}\n", "yellow")
                messagebox.showwarning("Not Supported",
                    f"Automatic menu entry creation is not supported on {system}.\n\n"
                    "You can still launch BSG-IDE from the command line using 'bsg-ide'.")

        except Exception as e:
            error_msg = f"Failed to create menu entry: {str(e)}"
            self.write(f"✗ {error_msg}\n", "red")
            messagebox.showerror("Error",
                f"{error_msg}\n\n"
                "You can still launch BSG-IDE from the command line using 'bsg-ide'.")

    def get_source_from_tex(self) -> None:
        """Convert a tex file back to source text format using simple converter"""
        tex_file = filedialog.askopenfilename(
            filetypes=[("TeX files", "*.tex"), ("All files", "*.*")],
            title="Select TeX File to Convert"
        )

        if not tex_file:
            return

        try:
            # Use the standalone converter
            output_file = convert_beamer_tex_to_simple_text(tex_file)

            if output_file:
                messagebox.showinfo("Success", f"Source file created: {output_file}")

                # Ask if user wants to load the generated source file
                if messagebox.askyesno("Load File", "Would you like to load the generated source file?"):
                    self.load_file(output_file)
            else:
                messagebox.showerror("Error", "Failed to convert TeX file")

        except Exception as e:
            messagebox.showerror("Error", f"Error converting TeX file:\n{str(e)}")

    def extract_presentation_info(self, content: str) -> dict:
        """Extract presentation information from document body only"""
        info = {
            'title': '',
            'subtitle': '',
            'author': '',
            'institution': '',
            'short_institute': '',
            'date': '\\today'
        }

        import re

        # First isolate the document body
        doc_match = re.search(r'\\begin{document}(.*?)\\end{document}', content, re.DOTALL)
        if doc_match:
            document_content = doc_match.group(1).strip()

            # Look for title frame content
            title_frame = re.search(r'\\begin{frame}.*?\\titlepage.*?\\end{frame}\n',
                                  document_content,
                                  re.DOTALL)
            if title_frame:
                # Extract information from the title frame
                for key in info.keys():
                    pattern = f"\\\\{key}{{(.*?)}}"
                    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                    if match:
                        # Clean up LaTeX formatting
                        value = match.group(1).strip()
                        value = re.sub(r'\\textcolor{[^}]*}{([^}]*)}', r'\1', value)
                        value = re.sub(r'\\[a-zA-Z]+{([^}]*)}', r'\1', value)
                        info[key] = value

        return info

    def extract_slides_from_tex(self, content: str) -> list:
        """Extract slides from TeX content with simplified content extraction"""
        slides = []
        import re

        # First isolate the document body
        doc_match = re.search(r'\\begin{document}(.*?)\\end{document}', content, re.DOTALL)
        if not doc_match:
            self.write("✗ Could not find document body\n", "red")
            return slides

        document_content = doc_match.group(1)

        # Find all frame blocks in the document body
        frame_blocks = re.finditer(
            r'\\begin{frame}\s*(?:\{\\Large\\textbf{([^}]*?)}\}|\{([^}]*)\})?(.*?)\\end{frame}\n',
            document_content,
            re.DOTALL
        )

        for block in frame_blocks:
            # Extract title from different possible patterns
            title = block.group(1) if block.group(1) else block.group(2) if block.group(2) else ""
            frame_content = block.group(3).strip() if block.group(3) else ""

            # If no title found in frame declaration, look for frametitle
            if not title:
                title_match = re.search(r'\\frametitle{([^}]*)}', frame_content)
                if title_match:
                    title = title_match.group(1)

            # Clean up title - remove \Large, \textbf, etc.
            if title:
                title = re.sub(r'\\[a-zA-Z]+{([^}]*)}', r'\1', title)
            else:
                title = "Untitled Slide"

            # Skip title page frames
            if "\\titlepage" in frame_content or "\\maketitle" in frame_content:
                self.write(f"Skipping title frame\n", "yellow")
                continue

            # Extract media
            media = self.extract_media_from_frame(frame_content)

            # Extract content using simplified approach
            content_items = self.extract_content_from_frame(frame_content)

            # Extract notes
            notes = self.extract_notes_from_frame(frame_content)

            # Only add non-empty slides
            if content_items or media:
                slides.append({
                    'title': title.strip(),
                    'media': media,
                    'content': content_items,
                    'notes': notes
                })

        return slides

    def create_sidebar(self) -> None:
        """Create sidebar with slide list and controls including insert slide below and restore functions"""
        self.sidebar = ctk.CTkFrame(self)
        self.sidebar.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)

        # Slide list label
        ctk.CTkLabel(self.sidebar, text="Slides",
                    font=("Arial", 14, "bold")).grid(row=0, column=0, padx=5, pady=5)

        # Slide list with scroll
        self.slide_list = ctk.CTkTextbox(self.sidebar, width=180, height=300)
        self.slide_list.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Enhanced bindings for navigation
        self.slide_list.bind('<Button-1>', self.on_slide_select)
        self.slide_list.bind('<Up>', self.navigate_slides)
        self.slide_list.bind('<Down>', self.navigate_slides)
        self.slide_list.bind('<Left>', self.navigate_slides)
        self.slide_list.bind('<Right>', self.navigate_slides)
        self.bind('<Control-Up>', lambda e: self.move_slide(-1))
        self.bind('<Control-Down>', lambda e: self.move_slide(1))

        # Focus binding to enable keyboard navigation
        self.slide_list.bind('<FocusIn>', self.on_list_focus)
        self.slide_list.bind('<FocusOut>', self.on_list_unfocus)

        # Slide control buttons with enhanced tooltips
        button_data = [
            ("New Slide", self.new_slide, "Add a new slide at the end (Ctrl+N)"),
            ("Insert Below", self.insert_slide_below, "Insert a new slide below current (Ctrl+I)"),
            ("Duplicate Slide", self.duplicate_slide, "Create a copy of current slide (Ctrl+D)"),
            ("Delete Slide", self.delete_slide, "Mask/delete current slide (Del)"),
            ("Move Up", lambda: self.move_slide(-1), "Move current slide up (Ctrl+Up)"),
            ("Move Down", lambda: self.move_slide(1), "Move current slide down (Ctrl+Down)")
        ]

        for i, (text, command, tooltip) in enumerate(button_data, start=2):
            btn = ctk.CTkButton(self.sidebar, text=text, command=command)
            btn.grid(row=i, column=0, padx=5, pady=5)
            self.create_tooltip(btn, tooltip)

        # Add separator
        separator = ttk.Separator(self.sidebar, orient='horizontal')
        separator.grid(row=8, column=0, padx=5, pady=10, sticky="ew")

        # Restore and management buttons frame
        restore_frame = ctk.CTkFrame(self.sidebar)
        restore_frame.grid(row=9, column=0, padx=5, pady=5, sticky="ew")

        # Restore current slide button
        restore_btn = ctk.CTkButton(
            restore_frame,
            text="↩ Restore Slide",
            command=self.restore_deleted_slide,
            fg_color="#28a745",
            hover_color="#218838",
            height=32
        )
        restore_btn.pack(side="left", padx=2, fill="x", expand=True)
        self.create_tooltip(restore_btn, "Restore current deleted slide (Ctrl+Shift+R)")

        # Restore all deleted slides button
        restore_all_btn = ctk.CTkButton(
            restore_frame,
            text="♻ Restore All",
            command=self.restore_all_deleted_slides,
            fg_color="#17a2b8",
            hover_color="#138496",
            height=32
        )
        restore_all_btn.pack(side="left", padx=2, fill="x", expand=True)
        self.create_tooltip(restore_all_btn, "Restore all deleted slides")

        # Purge permanently button
        purge_btn = ctk.CTkButton(
            restore_frame,
            text="🗑 Purge All",
            command=self.permanently_delete_masked_slides,
            fg_color="#dc3545",
            hover_color="#c82333",
            height=32
        )
        purge_btn.pack(side="left", padx=2, fill="x", expand=True)
        self.create_tooltip(purge_btn, "Permanently delete all masked slides (cannot undo)")

        # Add undo/redo info label
        info_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        info_frame.grid(row=10, column=0, padx=5, pady=(10, 5), sticky="ew")

        info_label = ctk.CTkLabel(
            info_frame,
            text="💡 Undo: Ctrl+Z | Redo: Ctrl+Y",
            font=("Arial", 10),
            text_color="#4ECDC4"
        )
        info_label.pack()

        # Configure grid weights for proper resizing
        self.sidebar.grid_rowconfigure(1, weight=1)  # Slide list gets extra space
        self.sidebar.grid_columnconfigure(0, weight=1)

    def insert_slide_below(self) -> None:
        """Insert a new slide below the current slide"""
        # Save current slide first
        self.save_current_slide()

        new_slide = {
            'title': 'New Slide',
            'media': '',
            'content': [],
            'notes': []
        }

        # If there are no slides or current_slide_index is invalid
        if not self.slides or self.current_slide_index < 0:
            self.slides.append(new_slide)
            self.current_slide_index = 0
        else:
            # Insert after current slide
            insert_position = self.current_slide_index + 1
            self.slides.insert(insert_position, new_slide)
            self.current_slide_index = insert_position

        # Update UI
        self.update_slide_list()
        self.load_slide(self.current_slide_index)

        # Focus title entry for immediate editing
        self.title_entry.focus_set()
        self.title_entry.select_range(0, 'end')

    def create_app_menu(self):
        """Create a proper application menu bar"""

        # Create menu bar
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # ========== FILE MENU ==========
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Load TeX File...", command=self.load_tex_file)
        file_menu.add_command(label="Get Source from TeX...", command=self.get_source_from_tex)
        file_menu.add_separator()
        file_menu.add_command(label="Export to Overleaf...", command=self.create_overleaf_zip)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing, accelerator="Ctrl+Q")
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # ========== EDIT MENU ==========
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self._editor_action('cut'), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=lambda: self._editor_action('copy'), accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=lambda: self._editor_action('paste'), accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Mask/Unmask Line", command=self.mask_line_in_editor, accelerator="Ctrl+Delete")
        edit_menu.add_separator()
        edit_menu.add_command(label="Presentation Settings...", command=self.show_settings_dialog)
        edit_menu.add_command(label="Edit Preamble...", command=self.edit_preamble)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # ========== SLIDE MENU ==========
        slide_menu = tk.Menu(self.menu_bar, tearoff=0)
        slide_menu.add_command(label="New Slide", command=self.new_slide, accelerator="Ctrl+N")
        slide_menu.add_command(label="Insert Below", command=self.insert_slide_below, accelerator="Ctrl+I")
        slide_menu.add_command(label="Duplicate Slide", command=self.duplicate_slide, accelerator="Ctrl+D")
        slide_menu.add_separator()
        slide_menu.add_command(label="Move Up", command=lambda: self.move_slide(-1), accelerator="Ctrl+Up")
        slide_menu.add_command(label="Move Down", command=lambda: self.move_slide(1), accelerator="Ctrl+Down")
        slide_menu.add_separator()
        slide_menu.add_command(label="Mask Current Slide", command=self.mask_current_slide)
        slide_menu.add_command(label="Restore Current Slide", command=self.restore_deleted_slide, accelerator="Ctrl+Shift+R")
        slide_menu.add_separator()
        slide_menu.add_command(label="Restore All Deleted", command=self.restore_all_deleted_slides)
        slide_menu.add_command(label="Permanently Delete Masked", command=self.permanently_delete_masked_slides)
        self.menu_bar.add_cascade(label="Slide", menu=slide_menu)

        # ========== VIEW MENU ==========
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        view_menu.add_checkbutton(label="Syntax Highlighting", variable=self.highlight_var,
                                  command=self.toggle_highlighting)
        view_menu.add_command(label="Toggle Terminal", command=self.toggle_terminal, accelerator="Ctrl+T")
        view_menu.add_separator()

        # Notes Mode submenu
        notes_menu = tk.Menu(view_menu, tearoff=0)
        self.notes_mode_var = tk.StringVar(value="both")
        notes_menu.add_radiobutton(label="Slides Only", variable=self.notes_mode_var,
                                   value="slides", command=lambda: self.set_notes_mode("slides"))
        notes_menu.add_radiobutton(label="Notes Only", variable=self.notes_mode_var,
                                   value="notes", command=lambda: self.set_notes_mode("notes"))
        notes_menu.add_radiobutton(label="Slides + Notes", variable=self.notes_mode_var,
                                   value="both", command=lambda: self.set_notes_mode("both"))
        view_menu.add_cascade(label="Notes Mode", menu=notes_menu)

        self.menu_bar.add_cascade(label="View", menu=view_menu)

        # ========== TOOLS MENU ==========
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        tools_menu.add_command(label="Generate PDF", command=self.generate_pdf)
        tools_menu.add_command(label="Convert to TeX", command=self.convert_to_tex)
        tools_menu.add_command(label="Preview PDF", command=self.preview_pdf)
        tools_menu.add_command(label="Present with Notes", command=self.present_with_notes)
        tools_menu.add_separator()
        tools_menu.add_command(label="TikZ Color Helper...", command=self.show_tikz_color_helper)
        tools_menu.add_command(label="Command Index...", command=self.show_enhanced_command_index)
        tools_menu.add_separator()
        tools_menu.add_command(label="Grammarly", command=self.toggle_grammarly)
        tools_menu.add_command(label="Spell Check Settings...", command=self.show_spellcheck_settings)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)

        # ========== HELP MENU ==========
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="LaTeX Command Reference...", command=self.show_enhanced_command_index)
        help_menu.add_separator()
        help_menu.add_command(label="Create Desktop Shortcut", command=self.create_desktop_shortcut)
        help_menu.add_separator()
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_keyboard_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About BSG-IDE", command=self.create_about_dialog)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

    def on_list_focus(self, event) -> None:
        """Handle slide list focus"""
        self.highlight_current_slide()
        # Visual feedback that list is focused
        self.slide_list.configure(border_color="#4ECDC4")

    def on_list_unfocus(self, event) -> None:
        """Handle slide list losing focus"""
        # Remove focus visual feedback
        self.slide_list.configure(border_color="")

    def _create_slide_from_parsed_data(self, title, media, media_masked, content_lines, notes_lines, is_fully_masked, slide_num):
        """Create a slide dictionary from parsed data with proper hidden indices"""

        # Track which content lines are hidden
        hidden_content_indices = []
        # We need to know which lines were originally masked
        # Since we lost that info during parsing, we need to reconstruct from content_lines
        # For now, we'll assume all lines are visible unless we have a way to track

        # For fully masked slides, mark all content as hidden
        if is_fully_masked:
            hidden_content_indices = list(range(len(content_lines)))
            hidden_note_indices = list(range(len(notes_lines)))
            # Add [DELETED] prefix to title if not already there
            if not title.startswith('[DELETED]'):
                title = f"[DELETED] {title}"
        else:
            # For partially masked slides, we need to preserve which lines were masked
            # Since we lost this info, we'll need to re-parse the original file differently
            # For now, create empty lists
            hidden_content_indices = []
            hidden_note_indices = []

        slide_data = {
            'title': title,
            'media': media,
            'content': content_lines,
            'notes': notes_lines,
            '_hidden_content_indices': hidden_content_indices,
            '_hidden_note_indices': hidden_note_indices,
            '_media_masked': media_masked,
            '_fully_masked': is_fully_masked
        }

        logger.info(f"Created slide: {title[:50]} (fully_masked={is_fully_masked}, content_lines={len(content_lines)}, hidden={len(hidden_content_indices)})")
        return slide_data

    def duplicate_slide(self) -> None:
            """Duplicate the current slide"""
            if self.current_slide_index >= 0:
                # Save the current slide first to ensure we have the latest changes
                self.save_current_slide()

                # Create a deep copy of the current slide
                current_slide = self.slides[self.current_slide_index]
                new_slide = {
                    'title': f"{current_slide['title']} (Copy)",
                    'media': current_slide['media'],
                    'content': current_slide['content'].copy()  # Create a new list with the same content
                }

                # Insert the new slide after the current slide
                insert_position = self.current_slide_index + 1
                self.slides.insert(insert_position, new_slide)

                # Update the current slide index to point to the new slide
                self.current_slide_index = insert_position

                # Update the UI
                self.update_slide_list()
                self.load_slide(self.current_slide_index)

                # Show confirmation message
                messagebox.showinfo("Success", "Slide duplicated successfully!")
            else:
                messagebox.showwarning("Warning", "No slide to duplicate!")
#---------------------------------------------------------------------------------------------------
    def create_main_editor(self) -> None:
        """Create main editor area with enhanced media controls and editor options"""
        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Title section
        title_frame = ctk.CTkFrame(self.editor_frame)
        title_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(title_frame, text="Title:").pack(side="left", padx=5)
        self.title_entry = ctk.CTkEntry(title_frame, width=400)
        self.title_entry.pack(side="left", padx=5, fill="x", expand=True)

        # ========== MEDIA SECTION WITH DYNAMIC TOOLBAR ==========
        media_frame = ctk.CTkFrame(self.editor_frame)
        media_frame.pack(fill="x", padx=5, pady=5)

        # Media label and entry
        media_label_frame = ctk.CTkFrame(media_frame)
        media_label_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(media_label_frame, text="Media:").pack(side="left", padx=5)
        self.media_entry = ctk.CTkEntry(media_label_frame, width=300)
        self.media_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Media buttons frame with dynamic toolbar
        media_buttons = ctk.CTkFrame(media_frame)
        media_buttons.pack(side="right", padx=5)

        # Initialize dynamic toolbar for media buttons
        self.media_dynamic_toolbar = DynamicToolbar(media_buttons)

        # ALL original media buttons preserved with priorities
        button_configs = [
            ("Local File", self.browse_media, "Browse local media files", 100),
            ("YouTube", self.youtube_dialog, "Add YouTube video", 90),
            ("Search Images", self.search_images, "Search for images online", 80),
            ("📷 Camera", self.open_camera, "Capture from camera", 70),
            ("🖥️ Screen", self.capture_screen, "Capture screen area", 70),
            ("❌ No Media", lambda: self.media_entry.insert(0, "\\None"), "Create slide without media", 60)
        ]

        for text, command, tooltip, priority in button_configs:
            is_capture = text.startswith(('📷', '🖥️', '❌'))

            btn = ctk.CTkButton(
                media_buttons,
                text=text,
                command=command,
                width=90,
                fg_color="#4A90E2" if is_capture else None,
                hover_color="#357ABD" if is_capture else None
            )
            self.create_tooltip(btn, tooltip)
            self.media_dynamic_toolbar.add_button(btn, priority, pack_kwargs={'side': 'left', 'padx': 2})

        # Pack all media buttons dynamically
        self.media_dynamic_toolbar.pack_all()

        # Create editors container
        editors_frame = ctk.CTkFrame(self.editor_frame)
        editors_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Content editor section
        content_frame = ctk.CTkFrame(editors_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        content_label_frame = ctk.CTkFrame(content_frame)
        content_label_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(content_label_frame, text="Content:").pack(side="left", padx=5)

        self.content_editor = ctk.CTkTextbox(content_frame, height=200)
        self.content_editor.pack(fill="both", expand=True, padx=5, pady=5)

        # Notes section
        notes_frame = ctk.CTkFrame(self.editor_frame)
        notes_frame.pack(fill="both", expand=True, padx=5, pady=5)

        notes_header = ctk.CTkFrame(notes_frame)
        notes_header.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(notes_header, text="Presentation Notes:").pack(side="left", padx=5)

        # Notes control buttons on the right
        notes_buttons = ctk.CTkFrame(notes_header)
        notes_buttons.pack(side="right", padx=5)

        # Initialize notes mode
        self.notes_mode = tk.StringVar(value="both")

        # Notes mode buttons
        buttons_config = [
            ("slides", "Slides Only", "Generate slides without notes", "#2B87BB", "#1B5577", 100),
            ("notes", "Notes Only", "Generate notes only", "#27AE60", "#1A7340", 90),
            ("both", "Slides + Notes", "Generate slides with notes", "#8E44AD", "#5E2D73", 80)
        ]

        # Initialize dynamic toolbar for notes mode buttons
        self.notes_mode_dynamic_toolbar = DynamicToolbar(notes_buttons)

        for mode, text, tooltip, active_color, hover_color, priority in buttons_config:
            btn = ctk.CTkButton(
                notes_buttons,
                text=text,
                command=lambda m=mode: self.set_notes_mode(m),
                width=100,
                fg_color=active_color if self.notes_mode.get() == mode else "gray",
                hover_color=hover_color
            )
            self.create_tooltip(btn, tooltip)
            self.notes_mode_dynamic_toolbar.add_button(btn, priority, pack_kwargs={'side': 'left', 'padx': 2})

            # Store button references for later updates
            if not hasattr(self, 'notes_buttons'):
                self.notes_buttons = {}
            self.notes_buttons[mode] = {
                'button': btn,
                'active_color': active_color,
                'hover_color': hover_color
            }

        # Pack notes mode buttons dynamically
        self.notes_mode_dynamic_toolbar.pack_all()

        # Editor options row
        editor_options = ctk.CTkFrame(notes_frame)
        editor_options.pack(fill="x", padx=5, pady=(10, 5))

        # Add syntax highlighting switch
        self.highlight_var = ctk.BooleanVar(value=True)
        self.highlight_switch = ctk.CTkSwitch(
            editor_options,
            text="Syntax Highlighting",
            variable=self.highlight_var,
            command=self.toggle_highlighting,
            width=150
        )
        self.highlight_switch.pack(side="left", padx=5)

        # Notes editor
        self.notes_editor = ctk.CTkTextbox(notes_frame, height=150)
        self.notes_editor.pack(fill="both", expand=True, padx=5, pady=5)

        # Initialize syntax highlighters
        self.syntax_highlighter = BeamerSyntaxHighlighter(self.content_editor)
        self.notes_highlighter = BeamerSyntaxHighlighter(self.notes_editor)

        # Set initial button colors
        self.update_notes_buttons(self.notes_mode.get())

        # Add help indicator
        help_frame = ctk.CTkFrame(self.editor_frame)
        help_frame.pack(fill="x", padx=5, pady=2)

        help_label = ctk.CTkLabel(
            help_frame,
            text="💡 Hover over LaTeX commands (starting with \\) for help",
            font=("Arial", 10),
            text_color="#4ECDC4"
        )
        help_label.pack(side="left")

    def check_dependencies(self) -> dict:
        """Check if required packages are installed in current environment"""
        dependencies = {
            'PIL': {'import_name': 'PIL', 'package_name': 'pillow', 'installed': False},
            'pyautogui': {'import_name': 'pyautogui', 'package_name': 'pyautogui', 'installed': False},
            'cv2': {'import_name': 'cv2', 'package_name': 'opencv-python', 'installed': False}
        }

        for dep_name, dep_info in dependencies.items():
            try:
                __import__(dep_info['import_name'])
                dep_info['installed'] = True
            except ImportError:
                dep_info['installed'] = False

        return dependencies

#-------------------------------------------------------Capture Screen ---------------------------------------

    def capture_screen(self):
        """
        Screen capture by pasting from clipboard.
        User takes screenshot, then clicks OK to paste.
        Does NOT clear or modify clipboard contents.
        """
        try:
            from PIL import Image
            import time
            import platform
            import subprocess

            system = platform.system()

            # Create media_files directory
            os.makedirs('media_files', exist_ok=True)

            # Generate timestamp for filename
            timestamp = time.strftime("%Y%m%d-%H%M%S")

            # Helper function to get clipboard image on Linux - NON-BLOCKING
            def get_clipboard_image_linux():
                """Get image from clipboard on Linux without blocking"""
                try:
                    # Try wl-paste (Wayland) with short timeout
                    if shutil.which('wl-paste'):
                        # First check if there's an image in clipboard
                        check_cmd = ['wl-paste', '--list-types']
                        check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=2)
                        if 'image/png' in check_result.stdout or 'image' in check_result.stdout:
                            result = subprocess.run(['wl-paste', '--type', 'image/png'],
                                                   capture_output=True, timeout=3)
                            if result.returncode == 0 and result.stdout:
                                from PIL import Image
                                import io
                                return Image.open(io.BytesIO(result.stdout))

                    # Try xclip (X11)
                    if shutil.which('xclip'):
                        # Check if there's an image in clipboard
                        check_cmd = ['xclip', '-selection', 'clipboard', '-o', '-t', 'image/png']
                        result = subprocess.run(check_cmd, capture_output=True, timeout=2)
                        if result.returncode == 0 and result.stdout:
                            from PIL import Image
                            import io
                            return Image.open(io.BytesIO(result.stdout))

                    return None

                except subprocess.TimeoutExpired:
                    # Timeout is fine - just means no image or command hung
                    return None
                except Exception as e:
                    self.write(f"  Clipboard check error: {e}\n", "yellow")
                    return None

            # Helper function to get clipboard image on macOS
            def get_clipboard_image_macos():
                """Get image from clipboard on macOS"""
                try:
                    from PIL import ImageGrab
                    return ImageGrab.grabclipboard()
                except:
                    return None

            # Helper function to get clipboard image on Windows
            def get_clipboard_image_windows():
                """Get image from clipboard on Windows"""
                try:
                    from PIL import ImageGrab
                    return ImageGrab.grabclipboard()
                except:
                    return None

            # Check which mode we're in from the toolbar
            mode = self.capture_mode.get()

            if mode == "animation":
                self.write(f"\n🎬 Animation Capture Mode (Paste from Clipboard)\n", "cyan")
                self.write(f"  Settings: {self.frame_count.get()} frames, {self.frame_delay.get()}s delay\n", "cyan")
                self.write(f"\n  Instructions:\n", "yellow")
                self.write(f"    For each frame:\n", "white")
                self.write(f"      1. Take a screenshot using your system's tool\n", "white")
                self.write(f"      2. The screenshot is now in your clipboard\n", "white")
                self.write(f"      3. Click 'Yes' to paste it\n", "white")
                self.write(f"      4. The image will be captured WITHOUT clearing the clipboard\n\n", "white")

                frames = []
                frame_count = self.frame_count.get()

                # Create progress dialog for animation
                progress = tk.Toplevel(self)
                progress.title("Capturing Animation Frames")
                progress.geometry("400x250")
                progress.transient(self)

                # Center progress dialog
                progress.update_idletasks()
                x = (progress.winfo_screenwidth() - 400) // 2
                y = (progress.winfo_screenheight() - 250) // 2
                progress.geometry(f"+{x}+{y}")

                # Instructions in progress dialog
                instr_label = tk.Label(progress, text="", font=("Arial", 10), wraplength=350)
                instr_label.pack(pady=10)

                progress_label = tk.Label(progress, text="", font=("Arial", 12, "bold"))
                progress_label.pack(pady=10)

                pbar = ttk.Progressbar(progress, length=350, mode='determinate')
                pbar.pack(pady=10)

                cancel_flag = {'cancelled': False}

                def cancel_capture():
                    cancel_flag['cancelled'] = True
                    progress.destroy()

                cancel_btn = tk.Button(progress, text="Cancel", command=cancel_capture)
                cancel_btn.pack(pady=10)

                try:
                    for i in range(frame_count):
                        if cancel_flag['cancelled']:
                            self.write(f"\n❌ Animation capture cancelled at frame {i+1}\n", "yellow")
                            break

                        progress_label.config(text=f"Frame {i+1}/{frame_count}")
                        pbar['value'] = (i + 1) / frame_count * 100
                        instr_label.config(text=f"Take screenshot for frame {i+1}\nThen click Yes to paste")
                        progress.update()

                        # Show dialog for each frame
                        response = messagebox.askyesno(
                            f"Capture Frame {i+1}/{frame_count}",
                            f"Frame {i+1} of {frame_count}\n\n"
                            f"1. Take a screenshot using your system's tool\n"
                            f"   - Windows: Win+Shift+S (region) or PrtScn\n"
                            f"   - macOS: Cmd+Shift+4 (region) or Cmd+Shift+3\n"
                            f"   - Linux: PrtScn or use your desktop's screenshot tool\n\n"
                            f"2. The screenshot is now in your clipboard\n\n"
                            f"Click Yes to paste this frame (clipboard will NOT be cleared)"
                        )

                        if not response:
                            self.write(f"❌ Frame {i+1} skipped by user\n", "yellow")
                            continue

                        self.write(f"  Pasting frame {i+1}/{frame_count}...\n", "cyan")

                        # Get image from clipboard based on OS (NON-BLOCKING)
                        if system == "Linux":
                            screenshot = get_clipboard_image_linux()
                        elif system == "Darwin":
                            screenshot = get_clipboard_image_macos()
                        else:
                            screenshot = get_clipboard_image_windows()

                        if screenshot is None:
                            self.write(f"  ❌ No image in clipboard for frame {i+1}\n", "red")
                            self.write(f"  💡 Make sure you took a screenshot and it's in the clipboard\n", "yellow")

                            retry = messagebox.askyesno("No Image Found",
                                f"No image found in clipboard for frame {i+1}!\n\n"
                                f"Please take a screenshot and make sure it's in the clipboard.\n\n"
                                f"Retry frame {i+1}?")

                            if retry:
                                i -= 1  # Retry this frame
                                continue
                            else:
                                continue

                        # Save frame
                        frame_path = os.path.join('media_files', f'temp_frame_{timestamp}_{i:03d}.png')
                        screenshot.save(frame_path, 'PNG')
                        frames.append(frame_path)
                        self.write(f"  ✓ Frame {i+1} captured and saved\n", "green")

                        if i < frame_count - 1:
                            time.sleep(self.frame_delay.get())

                    progress.destroy()

                    if len(frames) >= 2:
                        # Create GIF from frames
                        filename = f"screen_animation_{timestamp}.gif"
                        filepath = os.path.join('media_files', filename)

                        images = []
                        for f in frames:
                            img = Image.open(f)
                            images.append(img)

                        delay_ms = int(self.frame_delay.get() * 1000)
                        images[0].save(filepath, save_all=True, append_images=images[1:],
                                      duration=delay_ms, loop=0, format='GIF')

                        # Clean up temp frames
                        for f in frames:
                            try:
                                os.unlink(f)
                            except:
                                pass

                        size_kb = os.path.getsize(filepath) / 1024
                        self.write(f"\n✅ Animation saved: {filename} ({len(frames)} frames, {size_kb:.1f} KB)\n", "green")
                        self.write(f"   Full path: {os.path.abspath(filepath)}\n", "green")

                        # Update media entry
                        self.media_entry.delete(0, 'end')
                        self.media_entry.insert(0, f"\\file media_files/{filename}")
                        self.save_current_slide()

                        # Refresh slide display
                        if self.current_slide_index >= 0:
                            self.load_slide(self.current_slide_index)
                            self.update_slide_list()

                        messagebox.showinfo("Success",
                            f"Animation created successfully!\n\n"
                            f"Saved as: {filename}\n"
                            f"Frames: {len(frames)}\n"
                            f"Size: {size_kb:.1f} KB")
                    elif len(frames) == 1:
                        self.write(f"⚠ Only 1 frame captured. Need at least 2 frames for animation.\n", "yellow")
                        messagebox.showwarning("Not Enough Frames",
                            "Only 1 frame was captured.\n\n"
                            "Animation requires at least 2 frames.\n"
                            "The single frame has been saved as a screenshot instead.")

                        # Save as single screenshot instead
                        filename = f"screen_capture_{timestamp}.png"
                        filepath = os.path.join('media_files', filename)
                        img = Image.open(frames[0])
                        img.save(filepath, 'PNG')
                        os.unlink(frames[0])

                        self.media_entry.delete(0, 'end')
                        self.media_entry.insert(0, f"\\file media_files/{filename}")
                        self.save_current_slide()

                    else:
                        self.write(f"❌ Failed to capture any frames\n", "red")

                except Exception as e:
                    progress.destroy()
                    raise e

            else:  # Single mode
                self.write(f"\n📸 Single Screenshot Mode (Paste from Clipboard)\n", "cyan")
                self.write(f"  Instructions:\n", "yellow")
                self.write(f"    1. Take a screenshot using your system's tool:\n", "white")
                self.write(f"       - Windows: Win+Shift+S (region) or PrtScn\n", "white")
                self.write(f"       - macOS: Cmd+Shift+4 (region) or Cmd+Shift+3\n", "white")
                self.write(f"       - Linux: PrtScn or use your desktop's screenshot tool\n", "white")
                self.write(f"    2. The screenshot is now in your clipboard\n", "white")
                self.write(f"    3. Click OK to paste it (clipboard will NOT be cleared)\n\n", "white")

                # Ask user if they've taken the screenshot
                response = messagebox.askyesno(
                    "Paste from Clipboard",
                    "Have you taken a screenshot?\n\n"
                    "Make sure it's in your clipboard.\n\n"
                    "Click Yes to paste the screenshot into this slide.\n\n"
                    "Note: The clipboard will NOT be cleared."
                )

                if not response:
                    self.write("❌ Capture cancelled by user\n", "yellow")
                    return

                # Get image from clipboard based on OS (NON-BLOCKING)
                self.write("  Pasting from clipboard...\n", "cyan")

                if system == "Linux":
                    screenshot = get_clipboard_image_linux()
                elif system == "Darwin":
                    screenshot = get_clipboard_image_macos()
                else:
                    screenshot = get_clipboard_image_windows()

                if screenshot is None:
                    self.write("❌ No image found in clipboard\n", "red")
                    messagebox.showerror("Error",
                        "No image found in clipboard!\n\n"
                        "Please take a screenshot first.\n\n"
                        "Make sure the screenshot is copied to your clipboard.\n\n"
                        "On Linux, ensure wl-clipboard or xclip is installed:\n"
                        "  sudo apt install wl-clipboard   # For Wayland\n"
                        "  sudo apt install xclip          # For X11")
                    return

                # Save the image
                filename = f"screen_capture_{timestamp}.png"
                filepath = os.path.join('media_files', filename)
                screenshot.save(filepath, 'PNG')

                # Verify file was saved
                if os.path.exists(filepath):
                    size_kb = os.path.getsize(filepath) / 1024
                    self.write(f"✅ Screenshot pasted and saved: {filename} ({size_kb:.1f} KB)\n", "green")
                    self.write(f"   Full path: {os.path.abspath(filepath)}\n", "green")
                    self.write(f"   Note: Clipboard content was preserved\n", "cyan")

                    # Update media entry
                    self.media_entry.delete(0, 'end')
                    self.media_entry.insert(0, f"\\file media_files/{filename}")
                    self.save_current_slide()

                    # Refresh slide display
                    if self.current_slide_index >= 0:
                        self.load_slide(self.current_slide_index)
                        self.update_slide_list()

                    messagebox.showinfo("Success",
                        f"Screenshot pasted successfully!\n\n"
                        f"Saved as: {filename}\n"
                        f"Size: {size_kb:.1f} KB\n\n"
                        f"The image has been linked to your slide.\n\n"
                        f"Your clipboard content was preserved.")
                else:
                    self.write(f"❌ Failed to save screenshot\n", "red")
                    messagebox.showerror("Error", "Failed to save screenshot to file.")

        except Exception as e:
            self.write(f"❌ Capture failed: {str(e)}\n", "red")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Capture failed:\n{str(e)}")

    def debug_file_location(self):
        """Debug method to show where files are being saved"""
        self.write("\n=== FILE LOCATION DEBUG ===\n", "cyan")

        # Current working directory
        cwd = os.getcwd()
        self.write(f"Current working directory: {cwd}\n", "white")

        # Media_files directory
        media_path = os.path.join(cwd, 'media_files')
        self.write(f"Expected media_files path: {media_path}\n", "white")

        # Check if exists
        if os.path.exists(media_path):
            self.write(f"media_files EXISTS\n", "green")
            files = os.listdir(media_path)
            if files:
                self.write(f"Files in media_files:\n", "cyan")
                for f in files:
                    self.write(f"  - {f}\n", "white")
            else:
                self.write(f"media_files is EMPTY\n", "yellow")
        else:
            self.write(f"media_files does NOT exist\n", "red")

            # Try to create it
            try:
                os.makedirs(media_path, exist_ok=True)
                self.write(f"Created media_files directory\n", "green")
            except Exception as e:
                self.write(f"Could not create media_files: {e}\n", "red")

        # If we have a current file, check its directory
        if self.current_file:
            file_dir = os.path.dirname(os.path.abspath(self.current_file))
            self.write(f"\nCurrent file directory: {file_dir}\n", "white")
            media_in_file_dir = os.path.join(file_dir, 'media_files')
            self.write(f"media_files in file dir: {media_in_file_dir}\n", "white")
            if os.path.exists(media_in_file_dir):
                self.write(f"EXISTS - files: {os.listdir(media_in_file_dir)}\n", "green")
            else:
                self.write(f"DOES NOT EXIST\n", "yellow")

        self.write("==========================\n\n", "cyan")

    def _preview_captured_file(self, filepath):
        """Preview a captured image or animation"""
        try:
            if filepath.endswith('.gif'):
                # For GIFs, try to open with default application
                if sys.platform.startswith('win'):
                    os.startfile(filepath)
                elif sys.platform.startswith('darwin'):
                    subprocess.run(['open', filepath])
                else:
                    subprocess.run(['xdg-open', filepath])
            else:
                # For images, try to show a quick preview
                from PIL import Image, ImageTk

                preview = ctk.CTkToplevel(self)
                preview.title("Preview - Captured Image")
                preview.geometry("600x500")
                preview.transient(self)

                # Load and display image
                img = Image.open(filepath)

                # Scale to fit window while maintaining aspect ratio
                display_size = (550, 400)
                img.thumbnail(display_size, Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(img)

                label = tk.Label(preview, image=photo)
                label.image = photo  # Keep reference
                label.pack(pady=20, padx=20)

                # Info label
                info = ctk.CTkLabel(
                    preview,
                    text=f"File: {os.path.basename(filepath)}\nSize: {img.size[0]}x{img.size[1]} pixels",
                    font=("Arial", 10)
                )
                info.pack(pady=10)

                # Close button
                ctk.CTkButton(
                    preview,
                    text="Close",
                    command=preview.destroy,
                    width=100
                ).pack(pady=10)

                # Center preview window
                preview.update_idletasks()
                x = (preview.winfo_screenwidth() - 600) // 2
                y = (preview.winfo_screenheight() - 500) // 2
                preview.geometry(f"+{x}+{y}")

        except Exception as e:
            self.write(f"Could not preview: {e}\n", "yellow")

    def _create_animation_capture_dialog(self, parent, bbox, capture_func):
        """Create dialog for animation capture with progress"""
        dialog = ctk.CTkToplevel(parent)
        dialog.title("Capturing Animation")
        dialog.geometry("400x200")
        dialog.transient(parent)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 400) // 2
        y = (dialog.winfo_screenheight() - 200) // 2
        dialog.geometry(f"+{x}+{y}")

        # Status label
        status_label = ctk.CTkLabel(
            dialog,
            text="Preparing capture...",
            font=("Arial", 12)
        )
        status_label.pack(pady=20)

        # Progress bar
        progress_bar = ctk.CTkProgressBar(dialog, width=300)
        progress_bar.pack(pady=10)
        progress_bar.set(0)

        # Cancel flag
        cancelled = {'value': False}

        def update_progress(current, total):
            if cancelled['value']:
                return False
            progress = (current + 1) / total
            progress_bar.set(progress)
            status_label.configure(text=f"Capturing frame {current + 1}/{total}...")
            dialog.update()
            return True

        def start_capture():
            try:
                # Override the capture function's callback
                original_capture = capture_func

                def wrapped_capture(bbox):
                    # Create a modified capture function that updates progress
                    self.screen_capture.capture_animation(
                        bbox,
                        self.frame_count.get(),
                        self.frame_delay.get(),
                        None,  # We'll save later
                        update_progress
                    )
                    return original_capture(bbox)

                wrapped_capture(bbox)
                dialog.destroy()
            except Exception as e:
                status_label.configure(text=f"Error: {str(e)}", text_color="red")
                dialog.after(2000, dialog.destroy)

        def cancel_capture():
            cancelled['value'] = True
            dialog.destroy()

        # Button frame
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            button_frame,
            text="Start Capture",
            command=start_capture,
            width=120,
            fg_color="#28a745"
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=cancel_capture,
            width=120,
            fg_color="#dc3545"
        ).pack(side="right", padx=10)

        return dialog

    def _fix_x11_authorization(self):
        """Fix X11 authorization issues on Linux"""
        import platform
        import subprocess
        from pathlib import Path

        if platform.system() != "Linux":
            return True

        try:
            # Set DISPLAY if not set
            if not os.environ.get('DISPLAY'):
                os.environ['DISPLAY'] = ':0'

            # Try to fix xauth
            xauth_path = shutil.which('xauth')
            if xauth_path:
                user_xauth = Path.home() / '.Xauthority'

                # Try to merge system Xauthority if it exists
                system_xauth = '/run/user/1000/gdm/Xauthority'
                if not os.path.exists(system_xauth):
                    system_xauth = '/etc/X11/xauth/Xauthority'

                if os.path.exists(system_xauth) and user_xauth.exists():
                    try:
                        subprocess.run([xauth_path, '-f', system_xauth, 'extract', '/tmp/xauth.tmp', os.environ['DISPLAY']],
                                     capture_output=True, timeout=5)
                        subprocess.run([xauth_path, '-f', str(user_xauth), 'merge', '/tmp/xauth.tmp'],
                                     capture_output=True, timeout=5)
                        os.environ['XAUTHORITY'] = str(user_xauth)
                    except:
                        pass

            # Try xhost as fallback
            xhost_path = shutil.which('xhost')
            if xhost_path:
                try:
                    # Allow local connections
                    subprocess.run([xhost_path, '+local:'], capture_output=True, timeout=5)
                    # Allow current user
                    user = os.environ.get('USER', '')
                    if user:
                        subprocess.run([xhost_path, f'+SI:localuser:{user}'], capture_output=True, timeout=5)
                except:
                    pass

            return True

        except Exception as e:
            print(f"Warning: Could not fix X11 authorization: {e}")
            return False

#---------------------------------------------------------------------------------------------------------------------


 #-------------------------------Get Camera and Set Camera--------------------------------------------
    def open_camera(self) -> None:
            """Enhanced cross-platform camera capture with full feature set"""
            try:
                # Check for required imports
                import cv2
                from PIL import Image, ImageTk
                import platform
                from pathlib import Path
                import subprocess
                import time
                import sys

                # Create media_files directory if it doesn't exist
                os.makedirs('media_files', exist_ok=True)

                def get_available_cameras():
                    """Get list of available cameras with proper device detection for all platforms"""
                    available_cameras = []
                    system = platform.system()

                    def check_camera(index, device_path=None, device_name=None):
                        """Helper to check camera capabilities across different platforms"""
                        try:
                            # Initialize camera based on platform
                            if device_path and system == "Linux":
                                cap = cv2.VideoCapture(device_path)
                            elif system == "Windows":
                                cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # Use DirectShow on Windows
                            else:
                                cap = cv2.VideoCapture(index)

                            if cap.isOpened():
                                ret, _ = cap.read()
                                if ret:
                                    # Store original settings
                                    original_settings = {
                                        cv2.CAP_PROP_FRAME_WIDTH: cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                                        cv2.CAP_PROP_FRAME_HEIGHT: cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
                                        cv2.CAP_PROP_FPS: cap.get(cv2.CAP_PROP_FPS),
                                        cv2.CAP_PROP_BRIGHTNESS: cap.get(cv2.CAP_PROP_BRIGHTNESS),
                                        cv2.CAP_PROP_CONTRAST: cap.get(cv2.CAP_PROP_CONTRAST),
                                        cv2.CAP_PROP_SATURATION: cap.get(cv2.CAP_PROP_SATURATION)
                                    }

                                    # Test resolutions with platform-specific considerations
                                    test_resolutions = [
                                        (3840, 2160),  # 4K
                                        (2560, 1440),  # 2K
                                        (1920, 1080),  # Full HD
                                        (1280, 720),   # HD
                                        (800, 600),    # SVGA
                                        (640, 480)     # VGA
                                    ]

                                    supported_resolutions = []
                                    highest_resolution = None

                                    for width, height in test_resolutions:
                                        try:
                                            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                                            actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                            actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                                            # Verify resolution with actual capture
                                            if actual_w > 0 and actual_h > 0:
                                                test_ret, test_frame = cap.read()
                                                if test_ret and test_frame is not None:
                                                    resolution = f"{actual_w}x{actual_h}"
                                                    if resolution not in supported_resolutions:
                                                        supported_resolutions.append(resolution)
                                                        if not highest_resolution or (actual_w * actual_h > highest_resolution[0] * highest_resolution[1]):
                                                            highest_resolution = (actual_w, actual_h)
                                        except:
                                            continue

                                    # Restore original settings
                                    for prop, value in original_settings.items():
                                        try:
                                            cap.set(prop, value)
                                        except:
                                            pass

                                    # Get current settings after restore
                                    current_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                    current_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                                    current_fps = int(cap.get(cv2.CAP_PROP_FPS))

                                    # Build camera info dictionary with platform-specific details
                                    camera_info = {
                                        'index': index,
                                        'device_path': device_path,
                                        'name': device_name or f"Camera {index}",
                                        'current_resolution': f"{current_width}x{current_height}",
                                        'supported_resolutions': supported_resolutions,
                                        'highest_resolution': highest_resolution,
                                        'fps': current_fps,
                                        'original_settings': original_settings,
                                        'platform': system
                                    }

                                    cap.release()
                                    return camera_info

                            if cap.isOpened():
                                cap.release()
                        except Exception as e:
                            print(f"Error checking camera {index}: {e}")
                        return None

                    # Platform-specific camera detection
                    if system == "Linux":
                        # Linux: Check /dev/video* devices with udev information
                        try:
                            import glob
                            import pyudev
                            video_devices = sorted(glob.glob('/dev/video*'))
                            context = pyudev.Context()

                            for device_path in video_devices:
                                try:
                                    device = pyudev.Devices.from_device_file(context, device_path)
                                    # Get detailed device information
                                    device_name = device.get('ID_MODEL', '')
                                    vendor = device.get('ID_VENDOR_ID', '')
                                    product = device.get('ID_MODEL_ID', '')

                                    if not device_name:
                                        device_name = f"Camera ({device_path})"
                                    elif vendor and product:
                                        device_name = f"{device_name} ({vendor}:{product})"

                                    index = int(device_path.split('video')[-1])
                                    camera = check_camera(index, device_path, device_name)
                                    if camera:
                                        # Add additional Linux-specific information
                                        camera['device_info'] = {
                                            'vendor': vendor,
                                            'product': product,
                                            'subsystem': device.get('SUBSYSTEM', ''),
                                            'driver': device.get('ID_V4L_DRIVER', '')
                                        }
                                        available_cameras.append(camera)
                                except Exception as e:
                                    print(f"Error processing Linux device {device_path}: {e}")
                                    continue

                        except ImportError:
                            # Fallback if pyudev not available
                            for i in range(10):  # Check first 10 indices
                                camera = check_camera(i)
                                if camera:
                                    available_cameras.append(camera)

                    elif system == "Darwin":  # macOS
                        # Try built-in camera first with specific name
                        camera = check_camera(0, device_name="FaceTime Camera")
                        if camera:
                            # Add macOS-specific information
                            camera['is_builtin'] = True
                            available_cameras.append(camera)

                        # Check additional cameras
                        for i in range(1, 5):
                            camera = check_camera(i)
                            if camera:
                                camera['is_builtin'] = False
                                available_cameras.append(camera)

                    else:  # Windows
                        try:
                            # Try using Windows Management Instrumentation for device info
                            import win32com.client
                            wmi = win32com.client.GetObject("winmgmts:")

                            # Get all video devices from WMI
                            cameras_wmi = {}
                            for device in wmi.InstancesOf("Win32_PnPEntity"):
                                if "Camera" in device.Name or "Webcam" in device.Name:
                                    cameras_wmi[device.DeviceID] = device.Name

                            # Check available cameras with DirectShow
                            for i in range(10):  # Check first 10 indices
                                try:
                                    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                                    if cap.isOpened():
                                        # Try to match with WMI device
                                        device_name = next(
                                            (name for id, name in cameras_wmi.items() if str(i) in id),
                                            f"Camera {i}"
                                        )
                                        camera = check_camera(i, device_name=device_name)
                                        if camera:
                                            available_cameras.append(camera)
                                    cap.release()
                                except:
                                    continue

                        except ImportError:
                            # Fallback if WMI access fails
                            for i in range(10):
                                camera = check_camera(i)
                                if camera:
                                    available_cameras.append(camera)

                    return available_cameras

                def start_camera_capture(camera_index, camera_info=None):  # Modified to accept camera_info
                    """Initialize and start camera capture with camera-specific highest resolution"""
                    try:
                        # Create camera dialog
                        dialog = ctk.CTkToplevel(self)
                        dialog.title("Camera Capture")
                        dialog.geometry("800x600")
                        dialog.transient(self)
                        dialog.grab_set()

                        # Center the dialog
                        dialog.update_idletasks()
                        x = (dialog.winfo_screenwidth() - 800) // 2
                        y = (dialog.winfo_screenheight() - 600) // 2
                        dialog.geometry(f"+{x}+{y}")

                        # Initialize camera
                        #cap = cv2.VideoCapture(camera_index)
                        # Initialize camera with default settings
                        if platform.system() == "Linux" and camera_info.get('device_path'):
                            cap = cv2.VideoCapture(camera_info['device_path'])
                        else:
                            cap = cv2.VideoCapture(camera_index)
                        if not cap.isOpened():
                            raise Exception(f"Could not open camera {camera_index}")
                        max_res=None
                        # Only set resolution if highest_resolution is available for this camera
                        if camera_info.get('highest_resolution'):
                            width, height = camera_info['highest_resolution']
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

                            # Get actual resolution achieved
                            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
                            max_res = (actual_width, actual_height)


                        # Create main content frame
                        content_frame = ctk.CTkFrame(dialog)
                        content_frame.pack(fill="both", expand=True, padx=10, pady=5)

                        # Preview frame
                        preview_frame = ctk.CTkFrame(content_frame)
                        preview_frame.pack(fill="both", expand=True, padx=5, pady=5)

                        preview_label = tk.Label(preview_frame, background="black")
                        preview_label.pack(fill="both", expand=True)

                        # Status frame
                        status_frame = ctk.CTkFrame(dialog)
                        status_frame.pack(fill="x", padx=10, pady=5)

                        # Resolution label
                        if max_res:
                            res_text = f"Resolution: {max_res[0]}x{max_res[1]}"
                        else:
                            res_text = "Resolution: Unknown"

                        resolution_label = ctk.CTkLabel(
                            status_frame,
                            text=res_text,
                            font=("Arial", 12)
                        )
                        resolution_label.pack(side="left", padx=5)

                        # Status label
                        status_label = ctk.CTkLabel(
                            status_frame,
                            text="",
                            font=("Arial", 12)
                        )
                        status_label.pack(side="right", padx=5)

                        # Control frame
                        control_frame = ctk.CTkFrame(dialog)
                        control_frame.pack(fill="x", padx=10, pady=5)

                        # Variables for recording
                        recording_data = {
                            'is_recording': False,
                            'start_time': None,
                            'output': None,
                            'current_file': None
                        }

                        def create_camera_controls(dialog, cap, preview_frame, status_label, recording_data):
                            """Create enhanced camera controls with resolution and file management"""
                            # Create control panels
                            settings_frame = ctk.CTkFrame(dialog)
                            settings_frame.pack(fill="x", padx=10, pady=5)

                            # Resolution controls
                            resolution_frame = ctk.CTkFrame(settings_frame)
                            resolution_frame.pack(side="left", padx=5, pady=5, fill="x", expand=True)

                            resolutions = [
                                "3840x2160 (4K)",
                                "1920x1080 (Full HD)",
                                "1280x720 (HD)",
                                "800x600 (SVGA)",
                                "640x480 (VGA)"
                            ]

                            current_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            current_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            current_res = f"{current_width}x{current_height}"

                            ctk.CTkLabel(
                                resolution_frame,
                                text="Resolution:",
                                font=("Arial", 12)
                            ).pack(side="left", padx=5)

                            def change_resolution(choice):
                                try:
                                    width, height = map(int, choice.split()[0].split('x'))
                                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                                    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                                    if actual_width == width and actual_height == height:
                                        status_label.configure(text=f"Resolution changed to {width}x{height}")
                                    else:
                                        status_label.configure(
                                            text=f"Actual resolution: {actual_width}x{actual_height}"
                                        )
                                    dialog.after(2000, lambda: status_label.configure(text=""))
                                except Exception as e:
                                    status_label.configure(text=f"Error changing resolution: {str(e)}")
                                    dialog.after(2000, lambda: status_label.configure(text=""))

                            resolution_menu = ctk.CTkOptionMenu(
                                resolution_frame,
                                values=resolutions,
                                command=change_resolution,
                                width=150
                            )
                            resolution_menu.pack(side="left", padx=5)

                            # Set current resolution in menu
                            for res in resolutions:
                                if res.startswith(current_res):
                                    resolution_menu.set(res)
                                    break

                            # File management functions
                            def get_save_location(default_name, file_type):
                                """Get save location with custom filename"""
                                file_types = {
                                    'photo': [('PNG files', '*.png'), ('JPEG files', '*.jpg')],
                                    'video': [('MP4 files', '*.mp4'), ('AVI files', '*.avi')]
                                }

                                initialdir = os.path.abspath('media_files')
                                if not os.path.exists(initialdir):
                                    os.makedirs(initialdir)

                                return filedialog.asksaveasfilename(
                                    initialfile=default_name,
                                    defaultextension=file_types[file_type][0][1],
                                    filetypes=file_types[file_type],
                                    initialdir=initialdir,
                                    title=f"Save {file_type.title()} As"
                                )

                            def capture_photo():
                                """Enhanced photo capture with custom save location"""
                                try:
                                    ret, frame = cap.read()
                                    if ret:
                                        # Convert to RGB for PIL
                                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                        image = Image.fromarray(rgb_frame)

                                        # Default filename
                                        timestamp = time.strftime("%Y%m%d-%H%M%S")
                                        default_name = f"camera_photo_{timestamp}.png"

                                        # Get save location
                                        filepath = get_save_location(default_name, 'photo')
                                        if not filepath:  # User cancelled
                                            return

                                        # Save image
                                        image.save(filepath)

                                        # Update media entry with relative path if in media_files
                                        rel_path = os.path.relpath(filepath, 'media_files')
                                        if not rel_path.startswith('..'):
                                            self.media_entry.delete(0, 'end')
                                            self.media_entry.insert(0, f"\\file media_files/{rel_path}")
                                        else:
                                            self.media_entry.delete(0, 'end')
                                            self.media_entry.insert(0, f"\\file {filepath}")

                                        # Show success message
                                        status_label.configure(text="✓ Photo saved!")
                                        dialog.after(2000, lambda: status_label.configure(text=""))

                                        # Flash effect
                                        preview_frame.configure(fg_color="white")
                                        dialog.after(100, lambda: preview_frame.configure(fg_color="black"))

                                except Exception as e:
                                    status_label.configure(text=f"Error: {str(e)}")
                                    dialog.after(2000, lambda: status_label.configure(text=""))

                            def toggle_recording():
                                """Enhanced video recording with custom save location"""
                                try:
                                    if not recording_data['is_recording']:
                                        # Get save location first
                                        timestamp = time.strftime("%Y%m%d-%H%M%S")
                                        default_name = f"camera_video_{timestamp}.mp4"
                                        filepath = get_save_location(default_name, 'video')

                                        if not filepath:  # User cancelled
                                            return

                                        # Start recording
                                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                                        fps = int(cap.get(cv2.CAP_PROP_FPS))

                                        # Create video writer
                                        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                                        recording_data['output'] = cv2.VideoWriter(
                                            filepath, fourcc, fps, (width, height)
                                        )
                                        recording_data['current_file'] = filepath
                                        recording_data['is_recording'] = True
                                        recording_data['start_time'] = time.time()

                                        # Update UI
                                        record_button.configure(
                                            text="Stop Recording",
                                            fg_color="#FF4444",
                                            hover_color="#CC3333"
                                        )
                                        photo_button.configure(state="disabled")
                                        resolution_menu.configure(state="disabled")
                                        update_recording_time()

                                    else:
                                        # Stop recording
                                        recording_data['is_recording'] = False
                                        if recording_data['output']:
                                            recording_data['output'].release()

                                        # Update media entry with relative path if in media_files
                                        filepath = recording_data['current_file']
                                        rel_path = os.path.relpath(filepath, 'media_files')
                                        if not rel_path.startswith('..'):
                                            self.media_entry.delete(0, 'end')
                                            self.media_entry.insert(0, f"\\file media_files/{rel_path}")
                                        else:
                                            self.media_entry.delete(0, 'end')
                                            self.media_entry.insert(0, f"\\file {filepath}")

                                        # Reset UI
                                        record_button.configure(
                                            text="Record Video",
                                            fg_color="#4A90E2",
                                            hover_color="#357ABD"
                                        )
                                        photo_button.configure(state="normal")
                                        resolution_menu.configure(state="normal")
                                        status_label.configure(text="✓ Video saved!")
                                        dialog.after(2000, lambda: status_label.configure(text=""))

                                except Exception as e:
                                    status_label.configure(text=f"Error: {str(e)}")
                                    dialog.after(2000, lambda: status_label.configure(text=""))
                                    recording_data['is_recording'] = False
                                    photo_button.configure(state="normal")
                                    resolution_menu.configure(state="normal")

                            def update_recording_time():
                                """Update recording duration display"""
                                if recording_data['is_recording']:
                                    elapsed = time.time() - recording_data['start_time']
                                    minutes = int(elapsed // 60)
                                    seconds = int(elapsed % 60)
                                    status_label.configure(
                                        text=f"Recording: {minutes:02d}:{seconds:02d} ({os.path.basename(recording_data['current_file'])})"
                                    )
                                    dialog.after(1000, update_recording_time)

                            # Create control buttons
                            control_frame = ctk.CTkFrame(dialog)
                            control_frame.pack(fill="x", padx=10, pady=5)

                            photo_button = ctk.CTkButton(
                                control_frame,
                                text="Take Photo",
                                command=capture_photo,
                                width=120,
                                font=("Arial", 13),
                                fg_color="#4A90E2",
                                hover_color="#357ABD"
                            )
                            photo_button.pack(side="left", padx=5)

                            record_button = ctk.CTkButton(
                                control_frame,
                                text="Record Video",
                                command=toggle_recording,
                                width=120,
                                font=("Arial", 13),
                                fg_color="#4A90E2",
                                hover_color="#357ABD"
                            )
                            record_button.pack(side="left", padx=5)

                            close_button = ctk.CTkButton(
                                control_frame,
                                text="Close",
                                command=dialog.destroy,
                                width=100,
                                font=("Arial", 13),
                                fg_color="#FF4444",
                                hover_color="#CC3333"
                            )
                            close_button.pack(side="right", padx=5)

                            return photo_button, record_button, resolution_menu



                        def close_camera():
                            """Clean up and close camera"""
                            try:
                                # Stop recording if active
                                if recording_data['is_recording']:
                                    recording_data['is_recording'] = False
                                    if recording_data['output']:
                                        recording_data['output'].release()

                                # Release camera
                                cap.release()
                                dialog.destroy()

                            except Exception as e:
                                print(f"Error closing camera: {str(e)}")
                                dialog.destroy()

                        # Create controls
                        photo_button, record_button, resolution_menu = create_camera_controls(
                            dialog, cap, preview_frame, status_label, recording_data
                        )

                        close_button = ctk.CTkButton(
                            control_frame,
                            text="Close",
                            command=close_camera,
                            width=100,
                            font=("Arial", 13),
                            fg_color="#FF4444",
                            hover_color="#CC3333"
                        )
                        close_button.pack(side="right", padx=5)

                        def update_preview():
                            """Update camera preview"""
                            if cap.isOpened():
                                ret, frame = cap.read()
                                if ret:
                                    # Record frame if recording
                                    if recording_data['is_recording']:
                                        recording_data['output'].write(frame)

                                    # Convert frame for display
                                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                    image = Image.fromarray(rgb_frame)

                                    # Scale for display
                                    display_size = (800, 600)
                                    image.thumbnail(display_size, Image.Resampling.LANCZOS)

                                    # Convert to PhotoImage
                                    photo = ImageTk.PhotoImage(image=image)
                                    preview_label.configure(image=photo)
                                    preview_label.image = photo  # Keep reference

                                    # Schedule next update
                                    dialog.after(10, update_preview)

                        # Start preview
                        update_preview()

                        # Handle window closing
                        dialog.protocol("WM_DELETE_WINDOW", close_camera)

                    except Exception as e:
                        messagebox.showerror("Error", f"Camera initialization failed: {str(e)}")
                        dialog.destroy()

                # Main camera initialization
                cameras = get_available_cameras()
                if not cameras:
                    messagebox.showerror(
                        "No Cameras",
                        "No working cameras found.\nPlease connect a camera and try again."
                    )
                    return

                # Create camera selection dialog if multiple cameras found
                if len(cameras) > 1:
                    select_dialog = ctk.CTkToplevel(self)
                    select_dialog.title("Select Camera")
                    select_dialog.geometry("400x400")
                    select_dialog.transient(self)
                    select_dialog.grab_set()

                    # Center dialog
                    select_dialog.update_idletasks()
                    x = (select_dialog.winfo_screenwidth() - 400) // 2
                    y = (select_dialog.winfo_screenheight() - 400) // 2
                    select_dialog.geometry(f"+{x}+{y}")

                    # Title label
                    ctk.CTkLabel(
                        select_dialog,
                        text="Available Cameras",
                        font=("Arial", 16, "bold")
                    ).pack(pady=10, padx=20)

                    # Create scrollable frame for camera options
                    scroll_frame = ctk.CTkScrollableFrame(
                        select_dialog,
                        width=360,
                        height=280
                    )
                    scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

                    # Camera selection variable
                    selected_camera = tk.StringVar(value="0")  # Default to first camera

                    # Create radio buttons for each camera
                    for camera in cameras:
                        # Create frame for each camera option
                        camera_frame = ctk.CTkFrame(scroll_frame)
                        camera_frame.pack(fill="x", padx=5, pady=5)

                        # Radio button with camera name
                        rb = ctk.CTkRadioButton(
                            camera_frame,
                            text=camera['name'],
                            variable=selected_camera,
                            value=str(camera['index']),
                            font=("Arial", 13)
                        )
                        rb.pack(side="top", padx=10, pady=2, anchor="w")

                        # Add resolution and FPS info
                        info_text = f"Resolution: {camera['current_resolution']}"
                        if camera.get('supported_resolutions'):
                            info_text += f"\nSupported: {', '.join(camera['supported_resolutions'][:3])}"
                        if camera.get('fps'):
                            info_text += f"\nFPS: {camera['fps']}"

                        info_label = ctk.CTkLabel(
                            camera_frame,
                            text=info_text,
                            font=("Arial", 12),
                            justify="left",
                            text_color="gray"
                        )
                        info_label.pack(side="top", padx=30, pady=2, anchor="w")

                    # Create buttons frame
                    button_frame = ctk.CTkFrame(select_dialog)
                    button_frame.pack(fill="x", padx=10, pady=10)

                    def on_camera_selected():
                        camera_index = int(selected_camera.get())
                        selected_camera_info = next(
                            (cam for cam in cameras if cam['index'] == camera_index),
                            None
                        )
                        select_dialog.destroy()
                        # Start capture with selected camera
                        if selected_camera_info:
                            start_camera_capture(camera_index, selected_camera_info)


                        #start_camera_capture(camera_index)

                    # Select button
                    ctk.CTkButton(
                        button_frame,
                        text="Open Camera",
                        command=on_camera_selected,
                        width=200,
                        font=("Arial", 13),
                        fg_color="#4A90E2",
                        hover_color="#357ABD"
                    ).pack(side="left", padx=10)

                    # Cancel button
                    ctk.CTkButton(
                        button_frame,
                        text="Cancel",
                        command=select_dialog.destroy,
                        width=100,
                        font=("Arial", 13),
                        fg_color="#FF4444",
                        hover_color="#CC3333"
                    ).pack(side="right", padx=10)

                else:
                    # If only one camera, use it directly with its info
                    start_camera_capture(cameras[0]['index'], cameras[0])
                    # If only one camera, use it directly
                    #start_camera_capture(cameras[0]['index'])

            except ImportError as e:
                messagebox.showerror(
                    "Missing Dependencies",
                    "Camera capture requires additional modules.\n" +
                    "Please install required packages:\n\n" +
                    "pip install opencv-python pillow"
                )
            except Exception as e:
                messagebox.showerror(
                    "Camera Error",
                    f"Camera initialization failed:\n{str(e)}\n\n" +
                    "Please check your camera connection and permissions."
                )


 #----------------------------------------------------------------------------


    def update_notes_buttons(self, active_mode: str) -> None:
        """Update button colors based on active mode"""
        for mode, btn_info in self.notes_buttons.items():
            if mode == active_mode:
                btn_info['button'].configure(
                    fg_color=btn_info['active_color'],
                    hover_color=btn_info['hover_color']
                )
            else:
                btn_info['button'].configure(
                    fg_color="gray",
                    hover_color="#4A4A4A"
                )


    def create_toolbar(self) -> None:
        """Create main editor toolbar with dynamic layout - ALL FEATURES PRESERVED"""
        # Create main toolbar container
        self.toolbar = ctk.CTkFrame(self)
        self.toolbar.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Initialize dynamic toolbar managers
        self.upper_dynamic_toolbar = DynamicToolbar(self.toolbar)
        self.lower_dynamic_toolbar = DynamicToolbar(self.toolbar)

        # ========== UPPER ROW - File and presentation operations ==========
        upper_row = ctk.CTkFrame(self.toolbar)

        # ALL original upper buttons preserved with priorities
        # Higher priority = stays visible longer
        buttons_upper = [
            ("New", self.new_file, "Create new presentation", 100),
            ("Open", self.open_file, "Open existing presentation", 100),
            ("Save", self.save_file, "Save current presentation", 100),
            ("Generate PDF", self.generate_pdf, "Generate PDF file", 95),  # High priority
            ("Convert to TeX", self.convert_to_tex, "Convert to LaTeX format", 85),
            ("Preview PDF", self.preview_pdf, "View generated PDF", 80),
            ("Present with Notes", self.present_with_notes, "Launch dual-screen presentation with notes", 75),
            ("Load TeX", self.load_tex_file, "Load and convert Beamer TeX file", 70),
            ("Overwrite TeX+PDF", self.overwrite_tex_and_generate_pdf, "Convert back to TeX and generate PDF", 65)
        ]

        for text, command, tooltip, priority in buttons_upper:
            if text == "Export to Overleaf":
                btn = ctk.CTkButton(
                    upper_row,
                    text=text,
                    command=command,
                    width=120,
                    fg_color="#47A141",
                    hover_color="#2E8B57"
                )
            elif text == "Present with Notes":
                btn = ctk.CTkButton(
                    upper_row,
                    text=text,
                    command=command,
                    width=120,
                    fg_color="#4A90E2",
                    hover_color="#357ABD"
                )
            else:
                btn = ctk.CTkButton(
                    upper_row,
                    text=text,
                    command=command,
                    width=100
                )
            self.create_tooltip(btn, tooltip)
            self.upper_dynamic_toolbar.add_button(btn, priority, pack_kwargs={'side': 'left', 'padx': 5})

        # Pack upper row
        upper_row.pack(fill="x", padx=5, pady=(5, 2))
        self.upper_dynamic_toolbar.pack_all()


        # ========== LOWER ROW - Screen capture and additional controls ==========
        lower_row = ctk.CTkFrame(self.toolbar)

        # ========== LEFT SIDE - Screen capture controls ==========
        capture_frame = ctk.CTkFrame(lower_row, fg_color="transparent")

        # Screen capture label (PRESERVED)
        capture_label = ctk.CTkLabel(capture_frame, text="Screen Capture:")
        capture_label.pack(side="left", padx=5)
        self.create_tooltip(capture_label, "Choose capture mode and settings")

        # Initialize capture settings (PRESERVED)
        self.capture_mode = tk.StringVar(value="single")
        self.frame_count = tk.IntVar(value=10)
        self.frame_delay = tk.DoubleVar(value=0.5)

        # Single frame mode (PRESERVED)
        single_btn = ctk.CTkRadioButton(
            capture_frame,
            text="Single",
            variable=self.capture_mode,
            value="single"
        )
        single_btn.pack(side="left", padx=5)
        self.create_tooltip(single_btn, "Capture single screenshot")

        # Animation mode (PRESERVED)
        anim_btn = ctk.CTkRadioButton(
            capture_frame,
            text="Animation",
            variable=self.capture_mode,
            value="animation"
        )
        anim_btn.pack(side="left", padx=5)
        self.create_tooltip(anim_btn, "Capture animated GIF")

        # Animation settings frame (PRESERVED - initially hidden)
        self.anim_settings = ctk.CTkFrame(capture_frame, fg_color="transparent")

        # Frames control (PRESERVED)
        frames_frame = ctk.CTkFrame(self.anim_settings, fg_color="transparent")
        frames_frame.pack(side="left", padx=5)
        ctk.CTkLabel(frames_frame, text="Frames:").pack(side="left")
        frames_entry = ctk.CTkEntry(frames_frame, textvariable=self.frame_count, width=40)
        frames_entry.pack(side="left", padx=2)
        self.create_tooltip(frames_entry, "Number of frames to capture")

        # Delay control (PRESERVED)
        delay_frame = ctk.CTkFrame(self.anim_settings, fg_color="transparent")
        delay_frame.pack(side="left", padx=5)
        ctk.CTkLabel(delay_frame, text="Delay:").pack(side="left")
        delay_entry = ctk.CTkEntry(delay_frame, textvariable=self.frame_delay, width=40)
        delay_entry.pack(side="left", padx=2)
        self.create_tooltip(delay_entry, "Delay between frames (seconds)")

        # Capture button (PRESERVED)
        capture_btn = ctk.CTkButton(
            capture_frame,
            text="Capture",
            command=self.capture_screen,
            width=80,
            fg_color="#4A90E2",
            hover_color="#357ABD"
        )
        capture_btn.pack(side="left", padx=5)
        self.create_tooltip(capture_btn, "Start screen capture")

        # Add capture frame to dynamic toolbar (high priority)
        self.lower_dynamic_toolbar.add_frame(capture_frame, priority=100, pack_kwargs={'side': 'left', 'padx': 5})

        # ========== SEPARATOR (PRESERVED) ==========
        separator = ttk.Separator(lower_row, orient="vertical")
        self.lower_dynamic_toolbar.add_button(separator, priority=90, pack_kwargs={'side': 'left', 'padx': 10, 'fill': 'y', 'pady': 5})

        # ========== RIGHT SIDE - Additional buttons (PRESERVED) ==========
        right_frame = ctk.CTkFrame(lower_row, fg_color="transparent")

        # ALL original right buttons preserved
        right_buttons = [
            ("Edit Preamble", self.edit_preamble, "Edit LaTeX preamble", 80),
            ("Presentation Settings", self.show_settings_dialog, "Configure presentation settings", 80),
            ("Get Source", self.get_source_from_tex, "Extract source from TEX file", 70),
            ("Export to Overleaf", self.create_overleaf_zip, "Create Overleaf-compatible zip", 60),
            ("TikZ Colors", self.show_tikz_color_helper, "TikZ Color Helper", 50),
            ("Command Index", self.show_enhanced_command_index, "LaTeX Command Reference", 50),
            ("Grammarly", self.toggle_grammarly, "Toggle Grammarly grammar checking", 40)
        ]

        for text, command, tooltip, priority in right_buttons:
            if text == "Export to Overleaf":
                btn = ctk.CTkButton(
                    right_frame,
                    text=text,
                    command=command,
                    width=130,
                    fg_color="#47A141",
                    hover_color="#2E8B57"
                )
            elif text == "Grammarly":
                btn = ctk.CTkButton(
                    right_frame,
                    text=f"{text}: Off",
                    command=command,
                    width=100,
                    fg_color="#dc3545"
                )
                self.grammarly_button = btn  # Store reference for later updates
            else:
                btn = ctk.CTkButton(
                    right_frame,
                    text=text,
                    command=command,
                    width=130
                )
            btn.pack(side="left", padx=5)
            self.create_tooltip(btn, tooltip)
            self.lower_dynamic_toolbar.add_button(btn, priority, pack_kwargs={'side': 'left', 'padx': 5})

        # Add right frame to dynamic toolbar
        self.lower_dynamic_toolbar.add_frame(right_frame, priority=70, pack_kwargs={'side': 'right', 'padx': 5})

        # Pack lower row
        lower_row.pack(fill="x", padx=5, pady=(2, 5))
        self.lower_dynamic_toolbar.pack_all()

        # ========== ANIMATION SETTINGS TOGGLE (PRESERVED) ==========
        def toggle_anim_settings(*args):
            """Show/hide animation settings based on mode - PRESERVED"""
            if self.capture_mode.get() == "animation":
                self.anim_settings.pack(side='left', padx=5)
                # Update layout after showing
                self.lower_dynamic_toolbar.update_layout()
            else:
                self.anim_settings.pack_forget()
                self.lower_dynamic_toolbar.update_layout()

        # Bind mode changes (PRESERVED)
        self.capture_mode.trace('w', toggle_anim_settings)

        # Initial state (PRESERVED)
        toggle_anim_settings()

#------------------------------------------------------------------------------------------------------

    def on_notes_mode_change(self, mode: str) -> None:
        """Handle notes mode change"""
        self.notes_mode.set(mode)

        # Update button colors
        for btn in self.mode_buttons:
            if btn.mode == mode:
                btn.configure(fg_color=btn.active_color)
            else:
                btn.configure(fg_color="gray")

        # Configure editor state
        if mode == "slides":
            self.notes_editor.configure(state="disabled")
        else:
            self.notes_editor.configure(state="normal")



    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(tooltip, text=text, justify='left',
                           background="#ffffe0", relief='solid', borderwidth=1,
                           font=("Arial", 10))
            label.pack()

            def hide_tooltip():
                tooltip.destroy()

            widget.tooltip = tooltip
            widget.tooltip_timer = self.after(2000, hide_tooltip)

        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                if hasattr(widget, 'tooltip_timer'):
                    self.after_cancel(widget.tooltip_timer)

        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    def generate_odp(self) -> None:
        """Generate ODP presentation with automatic TEX generation if needed"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first!")
            return

        try:
            #self.save_file()  # Save current state to ensure latest content

            # Get base filename without extension
            base_filename = os.path.splitext(self.current_file)[0]
            tex_file = base_filename + '.tex'

            # Clear terminal
            self.clear_terminal()
            self.write_to_terminal("Starting ODP generation process...\n")

            # Check if TEX file exists and generate if needed
            if not os.path.exists(tex_file):
                self.write_to_terminal("TEX file not found. Generating from source...\n")
                try:
                    from BeamerSlideGenerator import process_input_file
                    process_input_file(self.current_file, tex_file)
                    self.write_to_terminal("✓ TEX file generated successfully\n", "green")
                except Exception as e:
                    self.write_to_terminal(f"✗ Error generating TEX file: {str(e)}\n", "red")
                    raise Exception("TEX generation failed")

            # Convert TEX to ODP
            self.write_to_terminal("Converting TEX to ODP...\n")
            try:
                #from Beam2odp import BeamerToODP
                converter = BeamerToODP(tex_file)
                self.write_to_terminal("Parsing TEX content...\n")
                converter.parse_input()

                self.write_to_terminal("Generating ODP file...\n")
                odp_file = converter.generate_odp()

                if odp_file and os.path.exists(odp_file):
                    self.write_to_terminal("✓ ODP file generated successfully!\n", "green")

                    # Ask to open the generated file
                    if messagebox.askyesno("Success",
                                         "ODP presentation generated successfully! Would you like to open it?"):
                        if sys.platform.startswith('win'):
                            os.startfile(odp_file)
                        elif sys.platform.startswith('darwin'):
                            subprocess.run(['open', odp_file])
                        else:
                            subprocess.run(['xdg-open', odp_file])
                else:
                    self.write_to_terminal("✗ Error: No output file was generated\n", "red")

            except Exception as e:
                error_text = f"✗ Error in ODP conversion: {str(e)}\n"
                error_text += "Detailed error information:\n"
                error_text += traceback.format_exc()
                self.write_to_terminal(error_text, "red")
                raise Exception("ODP conversion failed")

        except Exception as e:
            messagebox.showerror("Error", f"Error generating ODP presentation:\n{str(e)}")
            print(f"Error details: {str(e)}")
            traceback.print_exc()

    def get_required_media_files(self, tex_content: str) -> set:
        """Parse TEX file to identify all required media files including multimedia content and previews"""
        required_files = set()

        # Regular expressions for different media references
        patterns = {
            'images': [
                r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}',    # Standard images
                r'\\pgfimage(?:\[.*?\])?\{([^}]+)\}',          # PGF images
                r'media_files/([^}]+_preview\.png)'             # Preview images
            ],
            'video': [
                r'\\movie(?:\[.*?\])?\{.*?\}\{\.?/?media_files/([^}]+)\}',  # Movie elements (handle ./ prefix)
                r'\\href\{run:([^}]+)\}',                       # Runnable media links
                r'\\movie\[.*?\]\{.*?\}\{([^}]+)\}'            # Movie with options
            ],
            'animations': [
                r'\\animategraphics(?:\[.*?\])?\{[^}]*\}\{([^}]+)\}',  # Animated graphics
                r'\\animate(?:\[.*?\])?\{[^}]*\}\{([^}]+)\}'           # General animations
            ],
            'audio': [
                r'\\sound(?:\[.*?\])?\{.*?\}\{([^}]+)\}',      # Sound elements
                r'\\audiofile\{([^}]+)\}'                       # Audio files
            ],
            'general_media': [
                r'\\file\s+media_files/([^\s}]+)',             # General media files
                r'\\play\s+\\file\s+media_files/([^\s}]+)',    # Playable media
                r'\\mediapath\{([^}]+)\}'                       # Media path references
            ]
        }

        self.write_to_terminal("\nAnalyzing required media files:\n")

        # Find all media references
        for media_type, pattern_list in patterns.items():
            self.write_to_terminal(f"\nChecking {media_type} references:\n")
            for pattern in pattern_list:
                matches = re.finditer(pattern, tex_content)
                for match in matches:
                    filepath = match.group(1)
                    # Clean up the path
                    filepath = filepath.replace('media_files/', '')
                    filepath = filepath.replace('./', '')  # Remove any ./ prefix
                    filepath = filepath.strip()

                    # Add the file to required files
                    required_files.add(filepath)
                    self.write_to_terminal(f"  ✓ Found: {filepath}\n", "green")

                    # If this is a preview image, also add the corresponding video
                    if filepath.endswith('_preview.png'):
                        base_video_name = filepath.replace('_preview.png', '.mp4')
                        required_files.add(base_video_name)
                        self.write_to_terminal(f"  ✓ Added corresponding video: {base_video_name}\n", "green")

                    # If this is a video, check for its preview image
                    if filepath.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                        preview_name = filepath.rsplit('.', 1)[0] + '_preview.png'
                        if preview_name not in required_files:
                            required_files.add(preview_name)
                            self.write_to_terminal(f"  ✓ Added corresponding preview: {preview_name}\n", "green")

        return required_files

    def verify_media_files(self, required_files: set) -> tuple:
        """Verify existence of required media files and classify them"""
        verified_files = set()
        missing_files = set()
        media_types = {
            'images': [],
            'videos': [],
            'audio': [],
            'animations': [],
            'other': []
        }

        for filepath in required_files:
            full_path = os.path.join('media_files', filepath)
            if os.path.exists(full_path):
                verified_files.add(filepath)
                # Classify file by extension
                ext = os.path.splitext(filepath)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.pdf', '.eps']:
                    media_types['images'].append(filepath)
                elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']:
                    media_types['videos'].append(filepath)
                elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
                    media_types['audio'].append(filepath)
                elif ext in ['.gif', '.webp']:
                    media_types['animations'].append(filepath)
                else:
                    media_types['other'].append(filepath)
            else:
                missing_files.add(filepath)

        return verified_files, missing_files, media_types

    def create_manifest(self, tex_file: str, verified_files: set, missing_files: set, media_types: dict) -> str:
        """Create detailed manifest content"""
        manifest_content = [
            "# Project Media Files Manifest",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "\n## Project Files:",
            f"- {os.path.basename(tex_file)} (Main TeX file)",
            "\n## Media Files by Type:"
        ]

        # Add categorized media files
        for media_type, files in media_types.items():
            if files:
                manifest_content.extend([
                    f"\n### {media_type.title()}:",
                    *[f"- media_files/{file}" for file in sorted(files)]
                ])

        # Add missing files section if any
        if missing_files:
            manifest_content.extend([
                "\n## Missing Files (Please Check):",
                *[f"- {file}" for file in sorted(missing_files)]
            ])

        manifest_content.extend([
            "\n## File Statistics:",
            f"Total Files: {len(verified_files) + len(missing_files)}",
            f"Successfully Included: {len(verified_files)}",
            f"Missing: {len(missing_files)}"
        ])

        return '\n'.join(manifest_content)

    def create_overleaf_zip(self) -> None:
        """Create a zip file compatible with Overleaf containing tex and all required media files"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first!")
            return

        try:
            # First ensure current state is saved and tex is generated
            #self.save_file()

            # Get base filename without extension
            base_filename = os.path.splitext(self.current_file)[0]
            tex_file = base_filename + '.tex'

            # Clear terminal and show progress
            self.clear_terminal()
            self.write_to_terminal("Creating Overleaf-compatible zip file...\n")

            # Convert to tex if not already done
            if not os.path.exists(tex_file):
                self.write_to_terminal("Generating TeX file...\n")
                from BeamerSlideGenerator import process_input_file
                process_input_file(self.current_file, tex_file)
                self.write_to_terminal("✓ TeX file generated successfully\n", "green")

            # Read TEX content and identify required files
            with open(tex_file, 'r', encoding='utf-8') as f:
                tex_content = f.read()

            # Create the progress dialog
            self.update_idletasks()  # Ensure main window is updated
            progress = self.create_progress_dialog(
                "Creating Zip File",
                "Analyzing required files..."
            )

            try:
                # Analyze and verify media files
                required_files = self.get_required_media_files(tex_content)
                verified_files, missing_files, media_types = self.verify_media_files(required_files)

                # Create zip file
                zip_filename = base_filename + '_overleaf.zip'
                total_files = len(verified_files) + 1  # +1 for tex file
                processed_files = 0

                progress.update_progress(0, "Creating zip file...")

                with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Add the tex file
                    progress.update_progress(
                        (processed_files / total_files) * 100,
                        "Adding TeX file..."
                    )
                    zipf.write(tex_file, os.path.basename(tex_file))
                    processed_files += 1
                    self.write_to_terminal(f"✓ Added: {os.path.basename(tex_file)}\n", "green")

                    # Add verified media files
                    self.write_to_terminal("\nAdding media files:\n")
                    for filename in verified_files:
                        file_path = os.path.join('media_files', filename)
                        progress.update_progress(
                            (processed_files / total_files) * 100,
                            f"Adding {filename}..."
                        )

                        # Ensure the media_files directory exists in the zip
                        if processed_files == 1:  # First media file
                            zipf.writestr('media_files/.keep', '')  # Create empty file to ensure directory exists

                        zipf.write(file_path, os.path.join('media_files', filename))
                        self.write_to_terminal(f"✓ Added: {filename}\n", "green")
                        processed_files += 1

                    # Create detailed manifest
                    manifest_content = self.create_manifest(
                        tex_file, verified_files, missing_files, media_types
                    )
                    zipf.writestr('manifest.txt', manifest_content)

                progress.update_progress(100, "Complete!")
                time.sleep(0.5)  # Brief pause to show completion

                # Show completion message with details
                message = [f"Zip file created successfully!"]

                # Add statistics
                stats = []
                total_files = sum(len(files) for files in media_types.values())
                if total_files > 0:
                    stats.extend([
                        "",
                        "Media files included:",
                        *[f"- {media_type.title()}: {len(files)} files"
                          for media_type, files in media_types.items() if files]
                    ])

                # Add warnings for missing files
                if missing_files:
                    stats.extend([
                        "",
                        f"Warning: {len(missing_files)} required files were missing.",
                        "Check manifest.txt in the zip file for details."
                    ])

                # Add total size
                try:
                    zip_size = os.path.getsize(zip_filename)
                    stats.append("")
                    stats.append(f"Total zip size: {self.format_file_size(zip_size)}")
                except OSError:
                    pass

                message.extend(stats)
                message.append("\nWould you like to open the containing folder?")

                # Close progress dialog before showing message
                progress.close()

                if messagebox.askyesno("Success", "\n".join(message)):
                    # Open the folder containing the zip file
                    if sys.platform.startswith('win'):
                        os.system(f'explorer /select,"{zip_filename}"')
                    elif sys.platform.startswith('darwin'):
                        subprocess.run(['open', '-R', zip_filename])
                    else:
                        subprocess.run(['xdg-open', os.path.dirname(zip_filename)])

            except Exception as e:
                if 'progress' in locals():
                    progress.close()
                raise

        except Exception as e:
            error_msg = f"Error creating zip file: {str(e)}\n"
            self.write_to_terminal(f"✗ {error_msg}", "red")
            traceback.print_exc()  # Print full traceback to help with debugging
            messagebox.showerror("Error", f"Error creating zip file:\n{str(e)}")

    def format_file_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def create_progress_dialog(self, title: str, message: str) -> 'ProgressDialog':
        """Create a progress dialog window"""
        class ProgressDialog:
            def __init__(self, parent, title, message):
                self.window = ctk.CTkToplevel(parent)
                self.window.title(title)
                self.window.geometry("300x150")
                self.window.transient(parent)

                # Center the window
                self.window.update_idletasks()
                width = self.window.winfo_width()
                height = self.window.winfo_height()
                x = (self.window.winfo_screenwidth() // 2) - (width // 2)
                y = (self.window.winfo_screenheight() // 2) - (height // 2)
                self.window.geometry(f'+{x}+{y}')

                self.message = ctk.CTkLabel(self.window, text=message)
                self.message.pack(pady=10)

                self.progress = ctk.CTkProgressBar(self.window)
                self.progress.pack(pady=10, padx=20, fill="x")
                self.progress.set(0)

                self.progress_text = ctk.CTkLabel(self.window, text="0%")
                self.progress_text.pack(pady=5)

                # Wait for window to be visible before grabbing
                self.window.wait_visibility()
                self.window.grab_set()

                # Keep dialog on top
                self.window.lift()
                self.window.focus_force()

            def update_progress(self, value: float, message: str = None) -> None:
                """Update progress bar and message"""
                try:
                    if self.window.winfo_exists():
                        self.progress.set(value / 100)
                        self.progress_text.configure(text=f"{value:.1f}%")
                        if message:
                            self.message.configure(text=message)
                        self.window.update()
                except tk.TclError:
                    pass  # Window might have been closed

            def close(self) -> None:
                """Close the progress dialog"""
                try:
                    if self.window.winfo_exists():
                        self.window.grab_release()
                        self.window.destroy()
                except tk.TclError:
                    pass  # Window might have been closed

        return ProgressDialog(self, title, message)



    def open_presentation(self, file_path):
        """Open the generated presentation with appropriate application"""
        try:
            if sys.platform.startswith('win'):
                os.startfile(file_path)
            elif sys.platform.startswith('darwin'):
                subprocess.run(['open', file_path])
            else:
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            self.write_to_terminal(f"Error opening presentation: {str(e)}\n", "red")
            messagebox.showerror("Error",
                               f"Error opening presentation:\n{str(e)}")

    def create_context_menu(self) -> None:
        """Create right-click context menu"""
        self.context_menu = ctk.CTkFrame(self)

        commands = [
            ("Add Bullet", "- "),
            ("Add textcolor", "\\textcolor[RGB]{255,165,0}{}"),
            ("Add Media Directive", "\\file media_files/"),
            ("Add Play Directive", "\\play "),
            ("Add URL", "https://"),
            ("Add Comment", "% ")
        ]

        for text, insert_text in commands:
            ctk.CTkButton(
                self.context_menu,
                text=text,
                command=lambda t=insert_text: self.insert_text(t)
            ).pack(fill="x", padx=2, pady=2)


    def toggle_highlighting(self) -> None:
        """Toggle syntax highlighting"""
        self.syntax_highlighter.toggle()
        # Also toggle spell checking if enabled
        if self.spell_checking_enabled:
            if self.syntax_highlighter.active:
                self.check_spelling(None)
            else:
                # Clear all misspelled tags if highlighting is disabled
                for widget in [self.content_editor._textbox, self.notes_editor._textbox]:
                    widget.tag_remove("misspelled", "1.0", "end")

    def show_context_menu(self, event) -> None:
        """Show context menu at mouse position"""
        self.context_menu.place(x=event.x_root, y=event.y_root)

    def hide_context_menu(self, event) -> None:
        """Hide context menu"""
        self.context_menu.place_forget()

    def insert_text(self, text: str) -> None:
        """Insert text at cursor position"""
        self.content_editor.insert("insert", text)
        self.hide_context_menu(None)
        if self.syntax_highlighter.active:
            self.syntax_highlighter.highlight()

    # File Operations
    def new_file(self) -> None:
        """Create new presentation"""
        self.current_file = None
        self.slides = []
        self.current_slide_index = -1
        self.update_slide_list()
        self.clear_editor()

        # Reset presentation info
        self.presentation_info = {
            'title': '',
            'subtitle': '',
            'author': '',
            'institution': '',
            'short_institute': '',
            'date': '\\today'
        }

    def open_file(self) -> None:
        global working_folder
        global original_dir
        """Open existing presentation"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.load_file(filename)
            # Change to tet file directory
            working_folder= os.path.dirname(filename) or '.'
            os.chdir(working_folder)
            original_dir=working_folder
            # Update working directory in terminal
            self.terminal.set_working_directory(working_folder)

#-----------------------------------------------------------------------------

    def convert_media_to_latex(self, line: str) -> str:
        """Convert media directives to proper LaTeX commands"""
        if '\\file' in line:
            # Convert \file to \includegraphics
            media_path = line.split('\\file')[-1].strip()
            return f"\\includegraphics[width=0.48\\textwidth,keepaspectratio]{{{media_path}}}"
        elif '\\play' in line:
            # Handle play directives
            if '\\file' in line:
                media_path = line.split('\\file')[-1].strip()
                # Using raw string to handle nested braces
                return (r"\movie[externalviewer]{"
                       r"\includegraphics[width=0.48\textwidth,keepaspectratio]"
                       f"{{{media_path}}}}}{{{media_path}}}")
            elif '\\url' in line:
                url = line.split('\\url')[-1].strip()
                return f"\\href{{{url}}}{{\\textcolor{{blue}}{{Click to play video}}}}"
        elif '\\None' in line:
            return ""  # Return empty string for \None directive
        return line

    def convert_to_tex(self):
        """Convert text to TeX while preserving line-level masking"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first!")
            return

        try:
            self.save_file()
            base_filename = os.path.splitext(self.current_file)[0]
            tex_file = base_filename + '.tex'

            self.clear_terminal()
            self.write("Converting text to TeX while preserving masked content...\n")

            # Generate TeX content with preserved masking
            tex_content = self.generate_tex_with_preserved_masking()

            if tex_content:
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(tex_content)
                self.write(f"✓ TeX file generated: {tex_file}\n", "green")

                # Show summary of masked content in TeX
                self.write_tex_masking_summary(tex_content)
            else:
                self.write("✗ Failed to generate TeX content\n", "red")

        except Exception as e:
            self.write(f"✗ Error in conversion: {str(e)}\n", "red")
            messagebox.showerror("Error", f"Error converting to TeX:\n{str(e)}")

    def generate_tex_with_preserved_masking(self):
        """Generate TeX content - remove masked content, preserve original styling and layout directives"""
        try:
            # Get the original custom preamble (with all styling)
            full_tex_content = self.get_custom_preamble()

            # Find the exact position of \begin{document}
            doc_pos = full_tex_content.find("\\begin{document}")
            if doc_pos == -1:
                self.write("Error: Could not find \\begin{document} in preamble\n", "red")
                return None

            # Extract preamble (everything before \begin{document})
            preamble = full_tex_content[:doc_pos].strip()

            if not preamble.endswith('\n'):
                preamble += '\n'

            # Start building new document body
            new_document_body = "\\begin{document}\n\n"

            # Create title page slide
            new_document_body += "\\begin{frame}[plain]\n"
            new_document_body += "\\titlepage\n"
            new_document_body += "\\end{frame}\n\n"

            # Track statistics
            total_visible_slides = 0
            total_skipped_slides = 0

            # COMPLETE list of ALL layout directives (these are special, not regular LaTeX)
            ALL_LAYOUT_DIRECTIVES = [
                '\\mosaic', '\\wm', '\\ff', '\\pip', '\\split',
                '\\hl', '\\bg', '\\tb', '\\ol', '\\corner'
            ]

            def is_layout_directive(line):
                """Check if line contains a layout directive (NOT regular LaTeX commands)"""
                if not line or not line.strip():
                    return False
                stripped = line.strip()

                # IMPORTANT: Only check against specific layout directives
                # Do NOT match standard LaTeX environments
                layout_directives = [
                    '\\mosaic', '\\wm', '\\ff', '\\pip', '\\split',
                    '\\hl', '\\bg', '\\tb', '\\ol', '\\corner'
                ]

                for directive in layout_directives:
                    if stripped.startswith(directive):
                        return True

                # Explicitly exclude standard LaTeX environments
                if stripped.startswith('\\begin{') or stripped.startswith('\\end{'):
                    return False

                return False

            def find_layout_in_content(content_list):
                """
                Find layout directive anywhere in content.
                Returns (layout_type, layout_params, line_index) or (None, None, -1)
                NOTE: This only detects explicit layout directives, NOT regular LaTeX environments
                """
                layout_directives = ['\\mosaic', '\\wm', '\\ff', '\\pip', '\\split',
                                     '\\hl', '\\bg', '\\tb', '\\ol', '\\corner']

                for i, line in enumerate(content_list):
                    if not line or not line.strip():
                        continue
                    stripped = line.strip()

                    # Skip standard LaTeX environments
                    if stripped.startswith('\\begin{') or stripped.startswith('\\end{'):
                        continue

                    for directive in layout_directives:
                        if stripped.startswith(directive):
                            # Extract directive type and params
                            if directive == '\\mosaic':
                                import re
                                match = re.search(r'\\mosaic\{(\d+),(\d+)\}\{(.*?)\}', stripped)
                                if match:
                                    return ('mosaic', stripped, i)
                                else:
                                    return ('mosaic', stripped, i)
                            else:
                                params = stripped[len(directive):].strip()
                                return (directive[1:], params, i)
                return (None, None, -1)

            # Valid media directives
            valid_media_directives = ['\\file', '\\play', '\\url', '\\movie', '\\sound',
                                       '\\includegraphics', '\\href']

            def is_valid_media_directive(line):
                if not line or not line.strip():
                    return False
                stripped = line.strip()
                if is_layout_directive(stripped):
                    return False
                for directive in valid_media_directives:
                    if stripped.startswith(directive):
                        return True
                return False

            def convert_file_to_includegraphics(line):
                if '\\file' in line and not is_layout_directive(line):
                    file_path = line.replace('\\file', '').strip()
                    file_path = file_path.strip('{}')

                    actual_path = None
                    if os.path.exists(file_path):
                        actual_path = file_path
                    elif os.path.exists(f"media_files/{file_path}"):
                        actual_path = f"media_files/{file_path}"
                    else:
                        return f"\\textcolor{{gray}}{{[Image not found: {os.path.basename(file_path)}]}}"

                    return f"\\includegraphics[width=\\textwidth,keepaspectratio]{{{actual_path}}}"
                return line

            # Process each slide
            for idx, slide in enumerate(self.slides):
                is_fully_masked = slide.get('_fully_masked', False)

                if is_fully_masked:
                    total_skipped_slides += 1
                    continue

                hidden_content_indices = set(slide.get('_hidden_content_indices', []))
                hidden_note_indices = set(slide.get('_hidden_note_indices', []))
                media_masked = slide.get('_media_masked', False)

                # Get media from slide
                media = slide.get('media', '')
                if media_masked:
                    media = ""

                raw_content = slide.get('content', [])
                visible_content = []

                for i, line in enumerate(raw_content):
                    if i not in hidden_content_indices:
                        visible_content.append(line)

                visible_notes = []
                for i, note in enumerate(slide.get('notes', [])):
                    if note.strip() and i not in hidden_note_indices:
                        visible_notes.append(note)

                # ========== BIBLIOGRAPHY DETECTION ==========
                # Check if this slide contains a bibliography environment
                # This runs BEFORE any other processing to ensure proper splitting
                is_bibliography = False
                bib_content_lines = []
                in_bibliography = False

                for line in visible_content:
                    if '\\begin{thebibliography}' in line:
                        is_bibliography = True
                        in_bibliography = True
                        bib_content_lines.append(line)
                    elif '\\end{thebibliography}' in line:
                        in_bibliography = False
                        bib_content_lines.append(line)
                    elif in_bibliography:
                        bib_content_lines.append(line)

                # If this is a bibliography slide, process it with the professional handler
                if is_bibliography and bib_content_lines:
                    self.write(f"  ✓ Processing bibliography slide {idx + 1}\n", "cyan")
                    slide_title = slide.get('title', 'References')
                    clean_title = re.sub(r'^\[DELETED\]\s*', '', slide_title)

                    # Use the professional bibliography handler
                    frame_latex = self._handle_bibliography_slide(bib_content_lines, clean_title, idx)
                    new_document_body += frame_latex + "\n\n"
                    total_visible_slides += 1
                    continue  # Skip to next slide - prevents double-processing

                # ========== END OF BIBLIOGRAPHY DETECTION ==========

                # Check if slide has a valid image (not masked and not empty)
                has_valid_image = False
                image_path = None

                if media and media != "\\None" and not media_masked:
                    if media.startswith('\\file') and not is_layout_directive(media):
                        file_path = media.replace('\\file', '').strip()
                        file_path = file_path.strip('{}')
                        if file_path and 'example-image' not in file_path.lower():
                            if os.path.exists(file_path):
                                has_valid_image = True
                                image_path = file_path
                            elif os.path.exists(f"media_files/{file_path}"):
                                has_valid_image = True
                                image_path = f"media_files/{file_path}"

                # Check if content already has columns (regular LaTeX, NOT a layout directive)
                has_existing_columns = any('\\begin{columns}' in line for line in visible_content)

                if not visible_content and not visible_notes and not has_valid_image:
                    total_skipped_slides += 1
                    continue

                total_visible_slides += 1

                slide_title = slide.get('title', 'Untitled')
                clean_title = re.sub(r'^\[DELETED\]\s*', '', slide_title)

                # ============================================================
                # CHECK FOR LAYOUT DIRECTIVES ANYWHERE IN CONTENT
                # IMPORTANT: This ONLY detects explicit layout directives like \mosaic, \wm, etc.
                # NOT regular LaTeX environments like \begin{columns}
                # ============================================================
                layout_type, layout_params, layout_line_index = find_layout_in_content(visible_content)
                has_layout = layout_type is not None

                # ============================================================
                # CASE 1: Layout directive found - use specialized handler
                # ============================================================
                if has_layout:
                    # Remove the layout directive line from visible_content
                    content_without_layout = [line for j, line in enumerate(visible_content) if j != layout_line_index]

                    self.write(f"  ✓ Processing {layout_type} layout in slide {idx + 1}\n", "green")

                    # Generate the frame using the layout handler
                    if layout_type == 'mosaic':
                        frame_latex = self._generate_mosaic_layout(
                            layout_params, content_without_layout, clean_title
                        )
                    else:
                        frame_latex = self._generate_layout_latex(
                            layout_type, layout_params, content_without_layout, clean_title
                        )

                    # Add notes if any
                    if visible_notes:
                        real_notes = []
                        for note in visible_notes:
                            clean_note = re.sub(r'^[-•]\s*', '', note.strip())
                            if clean_note and clean_note.lower() not in ["no notes for this slide", "no notes", "none"]:
                                real_notes.append(clean_note)

                        if real_notes:
                            notes_latex = "\n\\note{\n\\begin{itemize}\n"
                            for note in real_notes:
                                notes_latex += f"    \\item {note}\n"
                            notes_latex += "\\end{itemize}\n}\n"
                            # Insert notes before \end{frame}
                            frame_end = frame_latex.rfind('\\end{frame}')
                            if frame_end != -1:
                                frame_latex = frame_latex[:frame_end] + notes_latex + frame_latex[frame_end:]

                    new_document_body += frame_latex + "\n\n"
                    continue

                # ============================================================
                # CASE 2: No layout directive - use standard processing
                # This handles regular slides with or without \begin{columns}
                # ============================================================
                frame_lines = []
                frame_lines.append(f"\\begin{{frame}}{{{clean_title}}}")
                frame_lines.append(f"\\frametitle{{{clean_title}}}")
                frame_lines.append("")

                # If we have a valid image and no existing columns, create two-column layout
                if has_valid_image and not has_existing_columns:
                    frame_lines.append("\\begin{columns}[T]")
                    frame_lines.append("\\column{0.45\\textwidth}")
                    # Add image in left column
                    frame_lines.append(f"\\begin{{center}}")
                    frame_lines.append(f"\\includegraphics[width=\\textwidth,keepaspectratio]{{{image_path}}}")
                    frame_lines.append(f"\\end{{center}}")
                    frame_lines.append("")
                    frame_lines.append("\\column{0.5\\textwidth}")

                    # Process content for right column
                    i = 0
                    in_list = False
                    list_type = None

                    while i < len(visible_content):
                        line = visible_content[i]
                        stripped = line.strip()

                        # Handle enumerate/itemize environment boundaries
                        if '\\begin{enumerate}' in line:
                            in_list = True
                            list_type = 'enumerate'
                            frame_lines.append(line)
                            i += 1
                            continue
                        elif '\\begin{itemize}' in line:
                            in_list = True
                            list_type = 'itemize'
                            frame_lines.append(line)
                            i += 1
                            continue
                        elif '\\end{enumerate}' in line or '\\end{itemize}' in line:
                            in_list = False
                            list_type = None
                            frame_lines.append(line)
                            i += 1
                            continue

                        # Handle media directives (skip if already handled as main image)
                        if is_valid_media_directive(line):
                            i += 1
                            continue

                        # Handle bullet points (convert - to \item)
                        if stripped.startswith(('- ', '• ')):
                            bullet_content = re.sub(r'^[-•]\s*', '', stripped)
                            if not in_list:
                                frame_lines.append("\\begin{itemize}")
                                frame_lines.append(f"\\item {bullet_content}")
                                frame_lines.append("\\end{itemize}")
                            else:
                                frame_lines.append(f"\\item {bullet_content}")
                            i += 1
                            continue

                        # Handle standalone \item commands
                        if stripped.startswith('\\item'):
                            if not in_list:
                                frame_lines.append("\\begin{itemize}")
                                frame_lines.append(line)
                                j = i + 1
                                while j < len(visible_content) and visible_content[j].strip().startswith('\\item'):
                                    frame_lines.append(visible_content[j])
                                    j += 1
                                i = j
                                frame_lines.append("\\end{itemize}")
                            else:
                                frame_lines.append(line)
                                i += 1
                            continue

                        # Regular line
                        if stripped or line == '':
                            frame_lines.append(line)
                        i += 1

                    frame_lines.append("\\end{columns}")

                elif has_existing_columns:
                    # Content already has columns - preserve as-is
                    i = 0
                    in_list = False
                    list_type = None

                    while i < len(visible_content):
                        line = visible_content[i]
                        stripped = line.strip()

                        # Preserve column commands exactly
                        if '\\begin{columns}' in line or '\\end{columns}' in line or '\\column' in line:
                            frame_lines.append(line)
                            i += 1
                            continue

                        # Handle enumerate/itemize environment boundaries
                        if '\\begin{enumerate}' in line:
                            in_list = True
                            list_type = 'enumerate'
                            frame_lines.append(line)
                            i += 1
                            continue
                        elif '\\begin{itemize}' in line:
                            in_list = True
                            list_type = 'itemize'
                            frame_lines.append(line)
                            i += 1
                            continue
                        elif '\\end{enumerate}' in line or '\\end{itemize}' in line:
                            in_list = False
                            list_type = None
                            frame_lines.append(line)
                            i += 1
                            continue

                        # Handle media directives inside columns
                        if is_valid_media_directive(line):
                            if '\\file' in line:
                                converted = convert_file_to_includegraphics(line)
                                frame_lines.append(converted)
                            else:
                                frame_lines.append(line)
                            i += 1
                            continue

                        # Handle bullet points
                        if stripped.startswith(('- ', '• ')):
                            bullet_content = re.sub(r'^[-•]\s*', '', stripped)
                            if not in_list:
                                frame_lines.append("\\begin{itemize}")
                                frame_lines.append(f"\\item {bullet_content}")
                                frame_lines.append("\\end{itemize}")
                            else:
                                frame_lines.append(f"\\item {bullet_content}")
                            i += 1
                            continue

                        # Handle standalone \item commands
                        if stripped.startswith('\\item'):
                            if not in_list:
                                frame_lines.append("\\begin{itemize}")
                                frame_lines.append(line)
                                j = i + 1
                                while j < len(visible_content) and visible_content[j].strip().startswith('\\item'):
                                    frame_lines.append(visible_content[j])
                                    j += 1
                                i = j
                                frame_lines.append("\\end{itemize}")
                            else:
                                frame_lines.append(line)
                                i += 1
                            continue

                        # Regular line
                        if stripped or line == '':
                            frame_lines.append(line)
                            i += 1

                else:
                    # No image and no columns - normal full-width content
                    i = 0
                    in_list = False
                    list_type = None

                    while i < len(visible_content):
                        line = visible_content[i]
                        stripped = line.strip()

                        # Handle enumerate/itemize environment boundaries
                        if '\\begin{enumerate}' in line:
                            in_list = True
                            list_type = 'enumerate'
                            frame_lines.append(line)
                            i += 1
                            continue
                        elif '\\begin{itemize}' in line:
                            in_list = True
                            list_type = 'itemize'
                            frame_lines.append(line)
                            i += 1
                            continue
                        elif '\\end{enumerate}' in line or '\\end{itemize}' in line:
                            in_list = False
                            list_type = None
                            frame_lines.append(line)
                            i += 1
                            continue

                        # Handle media directives
                        if is_valid_media_directive(line):
                            if '\\file' in line:
                                converted = convert_file_to_includegraphics(line)
                                frame_lines.append(f"\\begin{{center}}")
                                frame_lines.append(converted)
                                frame_lines.append(f"\\end{{center}}")
                            else:
                                frame_lines.append(line)
                            i += 1
                            continue

                        # Handle bullet points
                        if stripped.startswith(('- ', '• ')):
                            bullet_content = re.sub(r'^[-•]\s*', '', stripped)
                            if not in_list:
                                frame_lines.append("\\begin{itemize}")
                                frame_lines.append(f"\\item {bullet_content}")
                                frame_lines.append("\\end{itemize}")
                            else:
                                frame_lines.append(f"\\item {bullet_content}")
                            i += 1
                            continue

                        # Handle standalone \item commands
                        if stripped.startswith('\\item'):
                            if not in_list:
                                frame_lines.append("\\begin{itemize}")
                                frame_lines.append(line)
                                j = i + 1
                                while j < len(visible_content) and visible_content[j].strip().startswith('\\item'):
                                    frame_lines.append(visible_content[j])
                                    j += 1
                                i = j
                                frame_lines.append("\\end{itemize}")
                            else:
                                frame_lines.append(line)
                                i += 1
                            continue

                        # Regular line
                        if stripped or line == '':
                            frame_lines.append(line)
                        i += 1

                # Add notes
                if visible_notes:
                    real_notes = []
                    for note in visible_notes:
                        clean_note = re.sub(r'^[-•]\s*', '', note.strip())
                        if clean_note and clean_note.lower() not in ["no notes for this slide", "no notes", "none"]:
                            real_notes.append(clean_note)

                    if real_notes:
                        frame_lines.append("")
                        frame_lines.append("\\note{")
                        frame_lines.append("\\begin{itemize}")
                        for note in real_notes:
                            frame_lines.append(f"    \\item {note}")
                        frame_lines.append("\\end{itemize}")
                        frame_lines.append("}")

                frame_lines.append("\\end{frame}")
                frame_lines.append("")

                new_document_body += "\n".join(frame_lines) + "\n\n"

            new_document_body += "\\end{document}\n"

            full_tex = preamble + "\n" + new_document_body

            # ========== ADD CITATION BACK-REFERENCES ==========
            # This adds hyperref package and configurations for clickable citations
            full_tex = self._add_citation_back_references_to_slides(full_tex)

            debug_file = "debug_output.tex"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(full_tex)
            self.write(f"  📝 Debug TeX saved to: {debug_file}\n", "cyan")

            self.write(f"\n📊 TeX Generation Statistics:\n", "cyan")
            self.write(f"  • Title page included\n", "green")
            self.write(f"  • Visible slides included: {total_visible_slides}\n", "green")
            if total_skipped_slides > 0:
                self.write(f"  • Masked slides skipped: {total_skipped_slides}\n", "yellow")

            return full_tex

        except Exception as e:
            self.write(f"Error generating TeX: {str(e)}\n", "red")
            import traceback
            traceback.print_exc()
            return None

    def context_aware_convert_media(self, media: str, content_items: list) -> str:
        """Context-aware media conversion - identifies the environment and converts appropriately"""
        if not media or media == "\\None":
            return ""

        # Handle \None directive - return empty string (consumed, not output)
        if media.strip() == "\\None":
            return ""

        # Extract file path for \file directives
        if media.startswith('\\file'):
            file_path = media.replace('\\file', '').strip()
        elif media.startswith('\\play'):
            play_content = media.replace('\\play', '').strip()
            if play_content.startswith('\\file'):
                file_path = play_content.replace('\\file', '').strip()
                return f"\\movie[externalviewer]{{\\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{file_path}}}}}{{{file_path}}}"
            elif play_content.startswith('http'):
                return f"\\href{{{play_content}}}{{\\textcolor{{blue}}{{\\underline{{Play video}}}}}}"
            else:
                return media
        else:
            # Return other directives as-is (mosaic, bg, ff, etc.)
            return media

        # Check context for appropriate sizing
        # Look at content items to determine environment
        full_content = '\n'.join(content_items) if content_items else ""

        in_table = '\\begin{tabular}' in full_content
        in_columns = '\\begin{columns}' in full_content
        is_mosaic = '\\mosaic' in full_content

        # Context-aware conversion
        if in_table:
            # In a table, use smaller width
            return f"\\includegraphics[width=0.3\\textwidth,keepaspectratio]{{{file_path}}}"
        elif in_columns:
            # In columns, use column-appropriate width
            return f"\\includegraphics[width=\\textwidth,keepaspectratio]{{{file_path}}}"
        elif is_mosaic:
            # In mosaic, use smaller size
            return f"\\includegraphics[width=0.3\\textwidth,keepaspectratio]{{{file_path}}}"
        else:
            # Default - centered image
            return f"\\begin{{center}}\\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{file_path}}}\\end{{center}}"

    def context_aware_process_content(self, content_lines: list, hidden_indices: set, is_note: bool = False) -> list:
        """Context-aware content processing - identifies environments and preserves formatting"""
        processed = []
        in_table = False
        in_itemize = False
        in_enumerate = False
        in_columns = False
        in_mosaic = False
        in_math = False
        i = 0

        while i < len(content_lines):
            line = content_lines[i].rstrip()
            is_hidden = i in hidden_indices

            if is_hidden:
                processed.append(f"% {line}")
                i += 1
                continue

            # Skip empty lines
            if not line.strip():
                i += 1
                continue

            # CRITICAL: Handle \None directive - consume it, don't output anything
            if line.strip() == "\\None":
                i += 1
                continue

            # Track environments
            if '\\begin{tabular}' in line:
                in_table = True
                # Fix: Replace any \& with & in table lines
                line = line.replace('\\&', '&')
                processed.append(line)
                i += 1
                continue
            elif '\\end{tabular}' in line:
                in_table = False
                line = line.replace('\\&', '&')
                processed.append(line)
                i += 1
                continue

            if '\\begin{columns}' in line:
                in_columns = True
                processed.append(line)
                i += 1
                continue
            elif '\\end{columns}' in line:
                in_columns = False
                processed.append(line)
                i += 1
                continue

            if '\\begin{itemize}' in line:
                in_itemize = True
                processed.append(line)
                i += 1
                continue
            elif '\\end{itemize}' in line:
                in_itemize = False
                processed.append(line)
                i += 1
                continue

            if '\\begin{enumerate}' in line:
                in_enumerate = True
                processed.append(line)
                i += 1
                continue
            elif '\\end{enumerate}' in line:
                in_enumerate = False
                processed.append(line)
                i += 1
                continue

            # Handle \mosaic directive - convert to tabular
            if '\\mosaic' in line:
                in_mosaic = True
                converted = self.convert_mosaic_to_tabular(line)
                processed.append(converted)
                i += 1
                continue

            # Track math mode for proper underscore handling
            dollar_count = line.count('$') - line.count('\\$')
            if dollar_count % 2 != 0:
                in_math = not in_math

            # In table mode - preserve everything, don't modify & or \\
            if in_table:
                # Replace any escaped & back to normal &
                line = line.replace('\\&', '&')
                processed.append(line)
                i += 1
                continue

            # In columns mode - preserve structure
            if in_columns:
                processed.append(line)
                i += 1
                continue

            # Handle bullet points (only in content, not in tables/columns)
            if not in_table and not in_columns and not in_mosaic:
                # Fix bullet point with missing space
                if line.startswith('-') and len(line) > 1 and line[1] != ' ':
                    line = '- ' + line[1:]

                # Convert standalone - to \item if in itemize/enumerate
                if line.startswith('-') or line.startswith('•'):
                    bullet_content = line[1:].strip()
                    if in_itemize or in_enumerate:
                        processed.append(f"\\item {bullet_content}")
                    else:
                        # Not in a list environment, keep as simple bullet
                        processed.append(line)
                    i += 1
                    continue

            # Handle standalone \item commands
            if line.startswith('\\item'):
                if not in_itemize and not in_enumerate:
                    # Wrap in itemize
                    processed.append("\\begin{itemize}")
                    processed.append(line)
                    # Look ahead to see if there are more items
                    j = i + 1
                    while j < len(content_lines):
                        next_line = content_lines[j].strip()
                        if next_line.startswith('\\item'):
                            processed.append(content_lines[j].rstrip())
                            j += 1
                        else:
                            break
                    processed.append("\\end{itemize}")
                    i = j
                else:
                    processed.append(line)
                    i += 1
                continue

            # Handle URLs
            if line.startswith('http') or '\\url{' in line:
                processed.append(line)
                i += 1
                continue

            # Handle LaTeX commands that should pass through
            is_latex_cmd = line.startswith(('\\begin{', '\\end{', '\\textbf', '\\textcolor',
                                             '\\alert', '\\href', '\\block', '\\column',
                                             '\\centering', '\\vspace', '\\hline', '\\cite',
                                             '\\ref', '\\label', '\\caption', '\\footnote',
                                             '\\textbf', '\\textit', '\\emph', '\\textsuperscript',
                                             '\\textsubscript', '\\colorbox', '\\fcolorbox'))

            if is_latex_cmd:
                processed.append(line)
                i += 1
                continue

            # Handle math mode - preserve underscores
            if in_math:
                processed.append(line)
                i += 1
                continue

            # Regular text - preserve as-is, but escape underscores in text mode
            line = line.replace('_', r'\_')
            processed.append(line)
            i += 1

        return processed

    def convert_mosaic_to_tabular(self, mosaic_line: str) -> str:
        """Convert \mosaic{rows,cols}{images} to a proper tabular environment"""
        import re

        match = re.match(r'\\mosaic\{(\d+),(\d+)\}\{(.*?)\}', mosaic_line)
        if not match:
            return mosaic_line

        rows = int(match.group(1))
        cols = int(match.group(2))
        images = [img.strip() for img in match.group(3).split(',')]

        # Calculate width per column (max 0.3 of textwidth for 3+ columns)
        col_width = min(0.3, 0.9 / cols)

        result = []
        result.append("\\begin{center}")
        result.append(f"\\begin{{tabular}}{{{'c' * cols}}}")
        result.append("\\hline")

        for idx, img in enumerate(images):
            # Clean up image path
            if not img.startswith(('media_files/', './')) and not img.startswith('/'):
                img = f"media_files/{img}"

            result.append(f"\\includegraphics[width={col_width}\\textwidth,keepaspectratio]{{{img}}}")

            # Add column separator or row end
            if (idx + 1) % cols == 0:
                if idx < len(images) - 1:
                    result.append("\\\\ \\hline")
            else:
                # Add & to the previous line
                result[-1] = result[-1] + " &"

        # Ensure proper closing
        if len(result) > 0 and result[-1].endswith('&'):
            result[-1] = result[-1].rstrip('&') + "\\\\ \\hline"
        elif len(result) > 0 and '\\hline' not in result[-1] and result[-1] != "\\hline":
            result.append("\\\\ \\hline")

        result.append("\\end{tabular}")
        result.append("\\end{center}")

        return '\n'.join(result)

        def context_aware_convert_media(self, media: str, content_items: list) -> str:
            """Context-aware media conversion - identifies the environment and converts appropriately"""
            if not media or media == "\\None":
                return ""

            # Extract file path
            if media.startswith('\\file'):
                file_path = media.replace('\\file', '').strip()
            elif media.startswith('\\play'):
                play_content = media.replace('\\play', '').strip()
                if play_content.startswith('\\file'):
                    file_path = play_content.replace('\\file', '').strip()
                else:
                    return media
            else:
                return media

            # Check if we're in a table environment
            in_table = any('\\begin{tabular}' in line or '\\end{tabular}' in line for line in content_items)

            # Check if we're in a columns environment
            in_columns = any('\\begin{columns}' in line or '\\end{columns}' in line for line in content_items)

            # Check if this is a mosaic
            is_mosaic = any('\\mosaic' in line for line in content_items)

            # Context-aware conversion
            if in_table:
                # In a table, use smaller width
                return f"\\includegraphics[width=0.3\\textwidth,keepaspectratio]{{{file_path}}}"
            elif in_columns:
                # In columns, use column-appropriate width
                return f"\\includegraphics[width=\\textwidth,keepaspectratio]{{{file_path}}}"
            elif is_mosaic:
                # In mosaic, use smaller size
                return f"\\includegraphics[width=0.3\\textwidth,keepaspectratio]{{{file_path}}}"
            else:
                # Default - centered image
                return f"\\begin{{center}}\\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{file_path}}}\\end{{center}}"

    def context_aware_process_content(self, content_lines: list, hidden_indices: set, is_note: bool = False) -> list:
        """Context-aware content processing - identifies environments and preserves formatting"""
        processed = []
        in_table = False
        in_itemize = False
        in_enumerate = False
        in_columns = False
        in_mosaic = False
        in_math = False
        i = 0

        while i < len(content_lines):
            line = content_lines[i].rstrip()
            is_hidden = i in hidden_indices

            if is_hidden:
                processed.append(f"% {line}")
                i += 1
                continue

            # CRITICAL: Handle \None directive - consume it, don't output anything
            if line.strip() == "\\None":
                # This is a "no media" marker - skip it entirely
                i += 1
                continue

            # Track environments
            if '\\begin{tabular}' in line:
                in_table = True
                processed.append(line)
                i += 1
                continue
            elif '\\end{tabular}' in line:
                in_table = False
                processed.append(line)
                i += 1
                continue

            if '\\begin{columns}' in line:
                in_columns = True
                processed.append(line)
                i += 1
                continue
            elif '\\end{columns}' in line:
                in_columns = False
                processed.append(line)
                i += 1
                continue

            if '\\begin{itemize}' in line:
                in_itemize = True
                processed.append(line)
                i += 1
                continue
            elif '\\end{itemize}' in line:
                in_itemize = False
                processed.append(line)
                i += 1
                continue

            if '\\begin{enumerate}' in line:
                in_enumerate = True
                processed.append(line)
                i += 1
                continue
            elif '\\end{enumerate}' in line:
                in_enumerate = False
                processed.append(line)
                i += 1
                continue

            # Handle \mosaic directive
            if '\\mosaic' in line:
                in_mosaic = True
                converted = self.convert_mosaic_to_tabular(line)
                processed.append(converted)
                i += 1
                continue

            # Track math mode
            dollar_count = line.count('$') - line.count('\\$')
            if dollar_count % 2 != 0:
                in_math = not in_math

            # In table mode - preserve everything, don't modify & or \\
            if in_table:
                processed.append(line)
                i += 1
                continue

            # In columns mode - preserve structure
            if in_columns:
                processed.append(line)
                i += 1
                continue

            # Handle bullet points
            if not in_table and not in_columns and not in_mosaic:
                # Fix bullet point with missing space
                if line.startswith('-') and len(line) > 1 and line[1] != ' ':
                    line = '- ' + line[1:]

                # Convert standalone - to \item if in itemize
                if line.startswith('-') or line.startswith('•'):
                    bullet_content = line[1:].strip()
                    if in_itemize or in_enumerate:
                        processed.append(f"\\item {bullet_content}")
                    else:
                        processed.append(line)
                    i += 1
                    continue

            # Handle standalone \item commands
            if line.startswith('\\item'):
                if not in_itemize and not in_enumerate:
                    # Wrap in itemize
                    processed.append("\\begin{itemize}")
                    processed.append(line)
                    # Look ahead to see if there are more items
                    j = i + 1
                    while j < len(content_lines) and content_lines[j].strip().startswith('\\item'):
                        processed.append(content_lines[j].strip())
                        j += 1
                    processed.append("\\end{itemize}")
                    i = j
                else:
                    processed.append(line)
                    i += 1
                continue

            # Handle URLs
            if line.startswith('http') or '\\url{' in line:
                processed.append(line)
                i += 1
                continue

            # Handle LaTeX commands that should pass through
            is_latex_cmd = line.startswith(('\\begin{', '\\end{', '\\textbf', '\\textcolor',
                                             '\\alert', '\\href', '\\block', '\\column',
                                             '\\centering', '\\vspace', '\\hline', '\\cite',
                                             '\\ref', '\\label', '\\caption', '\\footnote'))

            if is_latex_cmd:
                processed.append(line)
                i += 1
                continue

            # Regular text - preserve as-is
            processed.append(line)
            i += 1

        return processed

    def convert_mosaic_to_tabular(self, mosaic_line: str) -> str:
        """Convert \mosaic{rows,cols}{images} to a proper tabular environment"""
        import re

        match = re.match(r'\\mosaic\{(\d+),(\d+)\}\{(.*?)\}', mosaic_line)
        if not match:
            return mosaic_line

        rows = int(match.group(1))
        cols = int(match.group(2))
        images = [img.strip() for img in match.group(3).split(',')]

        col_width = 0.3  # 30% of textwidth for each image

        result = []
        result.append("\\begin{center}")
        result.append(f"\\begin{{tabular}}{{{'c' * cols}}}")
        result.append("\\hline")

        for idx, img in enumerate(images):
            # Clean up image path
            if not img.startswith(('media_files/', './')):
                img = f"media_files/{img}"

            result.append(f"\\includegraphics[width={col_width}\\textwidth,keepaspectratio]{{{img}}}")

            # Add column separator or row end
            if (idx + 1) % cols == 0:
                if idx < len(images) - 1:
                    result.append("\\\\ \\hline")
            else:
                result[-1] = result[-1] + " &"

        # Close table
        if result[-1].endswith('&'):
            result[-1] = result[-1].rstrip('&') + "\\\\ \\hline"
        else:
            result.append("\\\\ \\hline")

        result.append("\\end{tabular}")
        result.append("\\end{center}")

        return '\n'.join(result)

    def detect_package_from_line(self, line: str) -> str:
        """Detect required package from a content line"""
        line_lower = line.lower()

        # Package detection patterns
        if re.search(r'\\toprule|\\midrule|\\bottomrule|\\cmidrule', line):
            return 'booktabs'
        elif re.search(r'\\multirow\{|\\multirowcell', line):
            return 'multirow'
        elif re.search(r'\\makecell|\\thead', line):
            return 'makecell'
        elif re.search(r'\\begin\{tabularx\}', line):
            return 'tabularx'
        elif re.search(r'\\begin\{longtable\}', line):
            return 'longtable'
        elif re.search(r'\\begin\{tikzpicture\}', line):
            return 'tikz'
        elif re.search(r'\\begin\{axis\}', line):
            return 'pgfplots'
        elif re.search(r'\\begin\{align\}', line):
            return 'amsmath'
        elif re.search(r'\\mathbb\{|\\mathfrak\{', line):
            return 'amssymb'
        elif re.search(r'\\SI\{|\\num\{', line):
            return 'siunitx'
        elif re.search(r'\\qty\{|\\dv\{|\\pdv\{', line):
            return 'physics'
        elif re.search(r'\\href\{|\\url\{', line):
            return 'hyperref'
        elif re.search(r'\\textcolor\{', line):
            return 'xcolor'
        elif re.search(r'\\begin\{lstlisting\}', line):
            return 'listings'
        elif re.search(r'\\begin\{tcolorbox\}', line):
            return 'tcolorbox'

        return None

    def clean_latex_for_conversion(self, content: str) -> str:
        """Clean LaTeX content to prevent conversion errors"""
        import re

        # Fix 1: Replace \textendash with -- (proper en dash)
        # But NOT inside math mode - need to detect math mode boundaries
        lines = content.split('\n')
        fixed_lines = []
        in_math = False

        for line in lines:
            # Track math mode
            dollar_count = line.count('$') - line.count('\\$')
            if dollar_count % 2 != 0:
                in_math = not in_math

            if in_math:
                # Inside math mode: replace \textendash with --
                line = line.replace(r'\textendash', '--')
            else:
                # Outside math mode: keep as is or convert to --
                line = line.replace(r'\textendash', '--')

            # Fix 2: Fix corrupted frame titles like {Open-Circuit Voltage ($V_{oc}
            # These have missing closing braces
            if '\\begin{frame}{' in line and line.count('{') != line.count('}'):
                # Count braces to fix
                open_count = line.count('{')
                close_count = line.count('}')
                if open_count > close_count:
                    line = line + '}' * (open_count - close_count)

            # Fix 3: Fix \Omega\cdotcm^2 -> \Omega\cdot\text{cm}^2
            line = re.sub(r'\\Omega\\cdotcm\^2', r'\\Omega\\cdot\\text{cm}^2', line)
            line = re.sub(r'\\Omega\\cdotcm\^2', r'\\Omega\\cdot\\text{cm}^2', line)

            # Fix 4: Fix \textmu - ensure textcomp package or convert to \mu
            line = line.replace(r'\textmu', r'\mu')

            # Fix 5: Fix malformed \cite commands
            line = re.sub(r'\\cite\{([^}]*?)\s*\}', r'\\cite{\1}', line)

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def add_required_packages_to_preamble(self, content: str) -> str:
        """Add required packages to prevent missing command errors"""
        packages_to_add = []

        # Check for \textmu usage
        if r'\textmu' in content:
            packages_to_add.append('textcomp')

        # Check for \textendash usage outside math mode
        # (inside math mode we already replaced it)
        if r'\textendash' in content and not re.search(r'\$[^$]*\\textendash[^$]*\$', content):
            packages_to_add.append('textcomp')

        # Check for \Omega\cdotcm pattern
        if re.search(r'\\Omega\\cdotcm', content):
            packages_to_add.append('siunitx')  # For proper units

        if not packages_to_add:
            return content

        # Find insertion point (before \begin{document})
        doc_pos = content.find('\\begin{document}')
        if doc_pos == -1:
            return content

        # Build package includes
        package_lines = []
        for pkg in packages_to_add:
            if pkg == 'siunitx':
                package_lines.append(r'\usepackage{siunitx}')
            elif pkg == 'textcomp':
                package_lines.append(r'\usepackage{textcomp}')

        # Insert before \begin{document}
        return content[:doc_pos] + '\n'.join(package_lines) + '\n' + content[doc_pos:]

    def validate_frame_titles(self, tex_content: str) -> str:
        """Validate and fix frame titles to ensure proper LaTeX syntax"""
        import re

        def fix_title(match):
            full_match = match.group(0)
            title_content = match.group(1) if match.group(1) else ''

            # Check for unbalanced braces in title
            if title_content.count('{') != title_content.count('}'):
                # Fix by adding missing closing braces
                open_count = title_content.count('{')
                close_count = title_content.count('}')
                if open_count > close_count:
                    title_content += '}' * (open_count - close_count)

            # Remove any trailing $ that would cause math mode issues
            title_content = re.sub(r'\$+$', '', title_content)

            # Escape special characters in title
            title_content = title_content.replace('&', r'\&')
            title_content = title_content.replace('%', r'\%')
            title_content = title_content.replace('#', r'\#')
            title_content = title_content.replace('_', r'\_')

            return f'\\begin{{{match.group(2)}}}{{{title_content}}}'

        # Fix frame titles with pattern: \begin{frame}{...}
        pattern = r'\\begin\{(frame|block|exampleblock|alertblock)\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        tex_content = re.sub(pattern, fix_title, tex_content)

        return tex_content

    def convert_media_to_latex_clean(self, media: str) -> str:
        """Convert media directive to clean LaTeX - SIMPLE VERSION"""
        if not media or media == "\\None":
            return ""

        # Handle \file directive
        if media.startswith('\\file'):
            file_path = media.replace('\\file', '').strip()
            # Don't modify the path - just wrap in includegraphics
            return f"\\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{file_path}}}"

        # Handle \play directive
        elif media.startswith('\\play'):
            play_content = media.replace('\\play', '').strip()
            if play_content.startswith('\\file'):
                file_path = play_content.replace('\\file', '').strip()
                return f"\\movie[externalviewer]{{\\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{file_path}}}}}{{{file_path}}}"
            elif play_content.startswith('http'):
                return f"\\href{{{play_content}}}{{\\textcolor{{blue}}{{\\underline{{Play video}}}}}}"
            else:
                return media

        # Return as-is for other cases
        return media

    def convert_content_line_to_latex(self, line: str) -> str:
        """Convert a content line to proper LaTeX format while preserving structure"""
        line = line.strip()
        if not line:
            return line

        # Handle bullet points (lines starting with - or •)
        if line.startswith('- ') or line.startswith('• '):
            # Remove the bullet prefix and add \item
            content = line[2:].strip()
            return f"\\item {content}"

        # Handle existing LaTeX commands (they should be preserved as-is)
        if line.startswith('\\'):
            return line

        # Handle text with potential LaTeX commands inside
        # Check for common LaTeX patterns that should be preserved
        if any(cmd in line for cmd in ['\\textbf', '\\textit', '\\textcolor', '\\alert', '\\url']):
            return line

        # Plain text - wrap in appropriate environment if needed
        return line

    def get_notes_configuration(self) -> str:
        """Get the notes configuration based on current mode"""
        mode = self.notes_mode.get() if hasattr(self, 'notes_mode') else "both"

        notes_configs = {
            "slides": "\\setbeameroption{hide notes}",
            "notes": "\\setbeameroption{show only notes}",
            "both": "\\setbeameroption{show notes on second screen=right}"
        }

        config = notes_configs.get(mode, notes_configs["both"])

        return f"""
    % Notes configuration
    \\usepackage{{pgfpages}}
    {config}
    \\setbeamertemplate{{note page}}{{\\pagecolor{{yellow!5}}\\insertnote}}
    """

    def write_tex_masking_summary(self, tex_content: str):
        """Write a summary of masked content in the TeX file"""
        import re

        # Count masked lines in the generated TeX
        masked_line_count = len(re.findall(r'^%', tex_content, re.MULTILINE))
        fully_masked_slides = len(re.findall(r'% ========== FULLY MASKED SLIDE ==========', tex_content))

        if fully_masked_slides > 0 or masked_line_count > 0:
            self.write(f"\n📝 Masking preserved in TeX file:\n", "yellow")
            if fully_masked_slides > 0:
                self.write(f"  • {fully_masked_slides} fully masked slides (commented out)\n", "yellow")
            if masked_line_count > 0:
                self.write(f"  • {masked_line_count} masked content lines (commented out)\n", "yellow")
            self.write(f"  • Masked content appears as % comments in the .tex file\n", "cyan")
            self.write(f"  • Unmask to include content in final PDF\n", "cyan")

    def generate_pdf(self) -> None:
        """Generate PDF with smart error handling, auto-correction, and error editor"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first!")
            return

        try:
            # Clear terminal
            self.clear_terminal()

            # Save current state
            self.save_current_slide()

            # Get base filename without extension
            base_filename = os.path.splitext(self.current_file)[0]
            tex_file = base_filename + '.tex'
            txt_file = self.current_file

            self.write("="*60 + "\n", "cyan")
            self.write("PDF GENERATION WITH SMART ERROR HANDLING\n", "cyan")
            self.write("="*60 + "\n", "cyan")

            # Step 1: Convert text to TeX
            self.write("\nStep 1: Converting text to TeX...\n", "white")
            self.convert_to_tex()

            # Step 2: Add color information
            self.write("\nStep 2: Adding color definitions and XOR text color rules...\n", "white")

            if os.path.exists(tex_file):
                with open(tex_file, 'r', encoding='utf-8') as f:
                    tex_content = f.read()

                # Step 2.5: Ensure all required LaTeX packages are installed locally
                if hasattr(self, 'package_manager'):
                    self.write("\nStep 2.5: Checking LaTeX packages (local installation)...\n", "white")

                    # Parse tex_content for required packages
                    import re
                    required_packages = set()

                    # Find all \usepackage commands
                    usepackage_pattern = r'\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}'
                    matches = re.findall(usepackage_pattern, tex_content)
                    for match in matches:
                        for pkg in match.split(','):
                            required_packages.add(pkg.strip())

                    # Check for specific commands that need packages
                    if '\\si{' in tex_content or '\\SI{' in tex_content or 'Ω' in tex_content:
                        required_packages.add('siunitx')
                        self.write("  ℹ Detected SI units (Ω) - siunitx package required\n", "cyan")
                    if '\\textmu' in tex_content or '\\textendash' in tex_content:
                        required_packages.add('textcomp')
                        self.write("  ℹ Detected textcomp commands - textcomp package required\n", "cyan")
                    if '\\begin{tikzpicture}' in tex_content:
                        required_packages.add('tikz')
                        self.write("  ℹ Detected TikZ graphics - tikz/pgf package required\n", "cyan")
                    if '\\begin{axis}' in tex_content:
                        required_packages.add('pgfplots')
                        self.write("  ℹ Detected pgfplots - pgfplots package required\n", "cyan")
                    if '\\so{' in tex_content or '\\hl{' in tex_content or '\\ul{' in tex_content:
                        required_packages.add('soul')
                        self.write("  ℹ Detected soul commands - soul package required\n", "cyan")

                    # Install missing packages locally (no sudo required)
                    installed_packages = []
                    failed_packages = []

                    for pkg in required_packages:
                        # Check if already available (including local texmf)
                        if self.package_manager.local_installer._is_package_available(pkg, 'latex'):
                            self.write(f"  ✓ {pkg} is already available\n", "green")
                            continue

                        self.write(f"  ⚠ Missing package: {pkg}\n", "yellow")

                        # Try local installation
                        if self.package_manager.local_installer.ensure_package_available(pkg, 'latex'):
                            installed_packages.append(pkg)
                            self.write(f"  ✓ Successfully installed {pkg} locally\n", "green")
                        else:
                            failed_packages.append(pkg)
                            self.write(f"  ✗ Could not install {pkg} locally\n", "red")

                    if installed_packages:
                        self.write(f"\n✓ Installed {len(installed_packages)} package(s) locally: {', '.join(installed_packages)}\n", "green")

                    if failed_packages:
                        self.write(f"\n⚠ Could not install {len(failed_packages)} package(s): {', '.join(failed_packages)}\n", "yellow")
                        self.write(f"  The PDF may still compile if these packages are not critical.\n", "yellow")
                        self.write(f"  Manual installation instructions have been provided above.\n", "yellow")

                # Add color information to TeX content
                enhanced_content = self.add_color_info_to_output(tex_content)

                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(enhanced_content)

                self.write("✓ Added TikZ color definitions and XOR text color rules\n", "green")
            else:
                self.write("⚠ Warning: TeX file not found after conversion\n", "yellow")
                return

            # Track fixes applied and error persistence
            fixes_applied = set()
            error_history = []
            persistent_errors = {}
            max_attempts = 5

            # Step 3: Run pdflatex with smart error handling
            for attempt in range(max_attempts):
                self.write(f"\n{'='*60}\n", "white")
                self.write(f"COMPILATION ATTEMPT {attempt + 1}/{max_attempts}\n", "cyan")
                self.write(f"{'='*60}\n", "white")

                # Run compilation with detailed error capture
                result = self.run_pdflatex_with_detailed_errors(tex_file)

                # Check if PDF was created successfully
                pdf_file = base_filename + '.pdf'
                if result.get('success') and os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
                    size = os.path.getsize(pdf_file)
                    size_str = self.format_file_size(size)

                    self.write("\n" + "="*60 + "\n", "white")
                    self.write("✓ PDF GENERATED SUCCESSFULLY!\n", "green")
                    self.write("="*60 + "\n", "white")
                    self.write(f"📄 PDF File: {os.path.basename(pdf_file)}\n", "white")
                    self.write(f"📏 Size: {size_str}\n", "white")
                    self.write(f"📍 Location: {os.path.dirname(pdf_file)}\n", "white")
                    self.write(f"🔧 Fixes applied: {len(fixes_applied)}\n", "cyan")

                    if fixes_applied:
                        self.write("\nApplied fixes:\n", "cyan")
                        for fix in fixes_applied:
                            self.write(f"  • {fix}\n", "cyan")

                    self.write("\n🎨 Color Features Included:\n", "cyan")
                    self.write("  • XOR-based text color selection\n", "cyan")
                    self.write("  • Predefined airis4D color palette\n", "cyan")
                    self.write("  • Automatic black/white text contrast\n", "cyan")
                    self.write("  • TikZ color definitions\n", "cyan")

                    if messagebox.askyesno("Success",
                                         f"PDF generated successfully!\n\n"
                                         f"File: {os.path.basename(pdf_file)}\n"
                                         f"Size: {size_str}\n\n"
                                         f"Would you like to view the PDF now?"):
                        self.preview_pdf(pdf_file)
                    return

                # Check for missing package errors and try local auto-install
                if hasattr(self, 'package_manager') and result.get('errors'):
                    for error_msg in result['errors']:
                        error_context = '\n'.join(result.get('error_context', []))
                        package_info = self.package_manager.detect_missing_package(error_msg, error_context)
                        if package_info:
                            self.write(f"\n📦 Missing package detected: {package_info['name']} ({package_info['type']})\n", "yellow")

                            # Try local installation first (no sudo)
                            if self.package_manager.local_installer.ensure_package_available(package_info['name'], package_info['type']):
                                self.write("✓ Package installed locally. Recompiling...\n", "green")
                                fixes_applied.add(f"Auto-installed locally: {package_info['name']}")
                                result['fixed'] = True
                                break
                            else:
                                self.write(f"⚠ Could not install {package_info['name']} locally\n", "yellow")
                                # Don't break - try system installation as fallback
                                if self.package_manager.install_package(package_info, auto_confirm=False):
                                    self.write("✓ Package installed (system). Recompiling...\n", "green")
                                    fixes_applied.add(f"Auto-installed: {package_info['name']}")
                                    result['fixed'] = True
                                    break

                # Check for math warning that needs editor
                if result.get('has_math_warning') or (result.get('errors') and any('textendash' in str(e).lower() for e in result['errors'])):
                    self.write("\n⚠ Detected \\textendash in math mode - this requires manual fix\n", "yellow")

                    slide_num = result.get('slide_number', 0)
                    error_line = result.get('error_line', 1)

                    if messagebox.askyesno("Fix Required",
                                         f"Detected \\textendash command inside math mode.\n\n"
                                         f"Location: Slide {slide_num if slide_num > 0 else 'unknown'}\n\n"
                                         f"This must be fixed manually. Replace \\textendash with --\n"
                                         f"or move it outside $...$ math delimiters.\n\n"
                                         f"Would you like to open the Error Editor now?"):

                        editor = LaTeXErrorEditor(
                            self,
                            txt_file,
                            error_line,
                            "\\textendash invalid in math mode - replace with -- or move outside $...$",
                            result.get('error_context', []),
                            is_txt_file=True,
                            slide_num=slide_num
                        )
                        self.wait_window(editor)

                        if editor.result == 'fixed':
                            self.write("\n✓ Manual fix applied. Regenerating TeX...\n", "green")
                            fixes_applied.add(f"Fixed \\textendash in Slide {slide_num}")
                            self.update_slide_list()
                            if self.current_slide_index >= 0:
                                self.load_slide(self.current_slide_index)
                            self.convert_to_tex()
                            continue
                        elif editor.result == 'abort':
                            self.write("\n❌ Compilation aborted by user\n", "yellow")
                            return
                        else:
                            self.write("\n⚠ Continuing despite warning...\n", "yellow")
                            continue

                # Safely get analysis and its values
                analysis = result.get('analysis')
                if analysis is None:
                    analysis = {}

                error_type = analysis.get('error_type', 'unknown')
                error_line = result.get('error_line')
                error_msg = result.get('errors', ['Unknown'])[0] if result.get('errors') else 'Unknown'
                last_slide = result.get('last_successful_slide', 0)

                # Provide helpful tip if we know the last successful slide
                if last_slide > 0 and not error_line:
                    self.write(f"\n💡 Tip: The last successfully compiled slide was {last_slide}\n", "cyan")
                    self.write(f"   The error is likely in slide {last_slide + 1}\n", "cyan")

                # Track persistent errors at the same line
                if error_line:
                    error_key = f"{error_line}_{error_type}"
                    persistent_errors[error_key] = persistent_errors.get(error_key, 0) + 1

                    if persistent_errors[error_key] >= 2:
                        self.write(f"\n⚠ Same error at line {error_line} persists after auto-fix attempt.\n", "red")

                        if messagebox.askyesno("Persistent Error",
                                             f"The same error persists:\n\n"
                                             f"Error: {error_type}\n"
                                             f"Message: {error_msg[:200]}\n\n"
                                             f"Would you like to open the Error Editor to fix it manually?"):

                            editor = LaTeXErrorEditor(
                                self,
                                txt_file,
                                error_line,
                                error_msg,
                                '\n'.join(result.get('error_context', [])),
                                is_txt_file=True,
                                slide_num=result.get('slide_number', 0)
                            )
                            self.wait_window(editor)

                            if editor.result == 'fixed':
                                self.write("\n✓ Manual fix applied. Regenerating TeX...\n", "green")
                                fixes_applied.add(f"Manual fix at line {error_line}")
                                self.update_slide_list()
                                if self.current_slide_index >= 0:
                                    self.load_slide(self.current_slide_index)
                                self.convert_to_tex()
                                continue
                            elif editor.result == 'abort':
                                self.write("\n❌ Compilation aborted by user\n", "yellow")
                                return

                error_history.append({
                    'attempt': attempt + 1,
                    'error_type': error_type,
                    'error_line': error_line,
                    'error_msg': error_msg,
                    'last_successful_slide': last_slide,
                    'slide_number': result.get('slide_number', 0)
                })

                # Auto-fix for common errors
                if result.get('fixed') and persistent_errors.get(f"{error_line}_{error_type}", 0) < 2:
                    self.write("\n✓ Auto-fix applied successfully!\n", "green")
                    fixes_applied.add(f"Auto-fix: {error_type}")
                    continue

                # User-guided fix with Error Editor
                if analysis and analysis.get('error_type'):
                    if not error_line and last_slide > 0:
                        error_line = self.find_slide_line_number(tex_file, last_slide + 1)
                        if error_line:
                            self.write(f"\n⚠ Approximating error location to slide {last_slide + 1} at line {error_line}\n", "yellow")

                    if error_line:
                        self.write(f"\n⚠ Error detected: {analysis.get('error_type')}\n", "yellow")
                        self.write(f"💡 Suggestion: {analysis.get('suggestion', 'Check the error context')}\n", "cyan")

                        if result.get('error_context'):
                            self.write("\nError context:\n", "yellow")
                            for ctx_line in result['error_context'][:5]:
                                self.write(f"  {ctx_line}\n", "white")

                        response = messagebox.askquestion(
                            "Error Detected",
                            f"Error: {analysis.get('error_type')}\n\n"
                            f"Suggestion: {analysis.get('suggestion', 'Check the error context')}\n\n"
                            f"Location: Slide {result.get('slide_number', 'unknown')}, Line {error_line}\n\n"
                            f"Do you want to open the Error Editor to fix this issue?"
                        )

                        if response == 'yes':
                            editor = LaTeXErrorEditor(
                                self,
                                txt_file,
                                error_line,
                                error_msg,
                                '\n'.join(result.get('error_context', [])),
                                is_txt_file=True,
                                slide_num=result.get('slide_number', 0)
                            )
                            self.wait_window(editor)

                            if editor.result == 'fixed':
                                self.write("\n✓ Manual fix applied. Regenerating TeX...\n", "green")
                                fixes_applied.add(f"Manual fix at line {error_line}")
                                self.update_slide_list()
                                if self.current_slide_index >= 0:
                                    self.load_slide(self.current_slide_index)
                                self.convert_to_tex()
                                continue
                            elif editor.result == 'abort':
                                self.write("\n❌ Compilation aborted by user\n", "yellow")
                                return
                        else:
                            self.write("\n❌ Compilation aborted by user\n", "yellow")
                            return
                    else:
                        self.write(f"\n⚠ Error detected but location could not be determined.\n", "yellow")
                        self.write(f"💡 {analysis.get('suggestion', 'Check the error context')}\n", "cyan")

                        if messagebox.askyesno("Error Detected",
                                             f"Error: {analysis.get('error_type')}\n\n"
                                             f"Suggestion: {analysis.get('suggestion', 'Check the error context')}\n\n"
                                             f"Location could not be automatically determined.\n\n"
                                             f"Would you like to view the log file for debugging?"):
                            self.show_latex_log(tex_file)

                # Show log file as last resort
                if attempt == max_attempts - 1:
                    self.write("\n" + "="*60 + "\n", "red")
                    self.write("✗ PDF GENERATION FAILED\n", "red")
                    self.write("="*60 + "\n", "red")
                    self.write(f"   Attempts made: {max_attempts}\n", "yellow")
                    self.write(f"   Errors encountered: {len(error_history)}\n", "yellow")

                    if error_history:
                        self.write("\nError summary:\n", "yellow")
                        for err in error_history:
                            slide_info = f" (Slide {err.get('slide_number', 'unknown')})" if err.get('slide_number') else ""
                            self.write(f"  Attempt {err['attempt']}: {err['error_type']} at line {err['error_line']}{slide_info}\n", "yellow")

                    log_file = tex_file.replace('.tex', '.log')
                    if os.path.exists(log_file):
                        self.write(f"\n📋 Log file: {log_file}\n", "cyan")
                        if messagebox.askyesno("Compilation Failed",
                                             f"Failed to compile after {max_attempts} attempts.\n\n"
                                             f"Would you like to view the LaTeX log file for debugging?"):
                            self.show_latex_log(tex_file)
                    else:
                        messagebox.showerror("Compilation Failed",
                                            f"Failed to compile after {max_attempts} attempts.\n\n"
                                            f"Please check your LaTeX syntax manually.")

        except Exception as e:
            error_msg = f"\n✗ Error generating PDF: {str(e)}\n"
            self.write(error_msg, "red")
            if hasattr(e, '__traceback__'):
                self.write("\nDetailed error information:\n", "red")
                self.write(traceback.format_exc(), "red")
            messagebox.showerror("Error", f"Error generating PDF:\n{str(e)}")

    def run_pdflatex_with_detailed_errors(self, tex_file: str) -> dict:
        """Run pdflatex and capture detailed error information with precise slide-based line mapping"""
        result = {
            'success': False,
            'errors': [],
            'error_line': None,
            'error_context': [],
            'analysis': None,
            'fixed': False,
            'fix_description': '',
            'last_successful_slide': 0,
            'slide_number': 0,
            'error_line_tex': None,
            'has_math_warning': False,
            'missing_package': None
        }

        try:
            tex_dir = os.path.dirname(tex_file) or '.'
            original_dir = os.getcwd()
            os.chdir(tex_dir)

            tex_file_abs = os.path.abspath(tex_file)

            # Read the current TeX content
            with open(tex_file_abs, 'r', encoding='utf-8', errors='ignore') as f:
                tex_lines = f.readlines()
                tex_content = ''.join(tex_lines)

            # ========== AGGRESSIVE PRE-PROCESSING: Fix common issues ==========
            self.write("\n🔧 Running aggressive pre-processing to fix common LaTeX errors...\n", "cyan")

            fixed_content = tex_content
            fixes_applied = []

            # Fix 1: Fix unclosed math in titles (critical for the Open-Circuit Voltage error)
            import re

            lines = fixed_content.split('\n')
            fixed_lines = []

            for i, line in enumerate(lines):
                # Check for title with unclosed math mode
                if '\\title' in line:
                    dollar_count = line.count('$')
                    if dollar_count % 2 != 0:
                        line = line.rstrip() + '$'
                        fixes_applied.append(f"Line {i+1}: Added missing $ to close math mode in title")
                        self.write(f"  ✓ Fixed unclosed math in title at line {i+1}\n", "green")

                # Check for frame titles with unclosed math
                elif '\\begin{frame}' in line and '$' in line:
                    dollar_count = line.count('$')
                    if dollar_count % 2 != 0:
                        line = line.rstrip() + '$'
                        fixes_applied.append(f"Line {i+1}: Added missing $ to close math mode in frame title")
                        self.write(f"  ✓ Fixed unclosed math in frame title at line {i+1}\n", "green")

                fixed_lines.append(line)

            if fixes_applied:
                fixed_content = '\n'.join(fixed_lines)
                with open(tex_file_abs, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                result['fixed'] = True
                result['fix_description'] = '; '.join(fixes_applied[:5])

                # Also update the TXT file
                txt_file = tex_file_abs.replace('.tex', '.txt')
                if os.path.exists(txt_file):
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        txt_content = f.read()
                    txt_lines = txt_content.split('\n')
                    fixed_txt_lines = []
                    for line in txt_lines:
                        if '\\title' in line and line.count('$') % 2 != 0:
                            line = line.rstrip() + '$'
                        fixed_txt_lines.append(line)
                    with open(txt_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(fixed_txt_lines))
                    self.write("  ✓ Also updated TXT file with fixes\n", "green")

                # Re-read the fixed content
                with open(tex_file_abs, 'r', encoding='utf-8', errors='ignore') as f:
                    tex_lines = f.readlines()
                    tex_content = ''.join(tex_lines)

            # Build detailed slide map with line ranges
            tex_slide_map = self._build_detailed_tex_slide_map(tex_lines)

            # Also build TXT slide map for mapping back to source
            txt_file = tex_file.replace('.tex', '.txt')
            txt_slide_map = {}
            txt_lines = []
            if os.path.exists(txt_file):
                with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                    txt_lines = f.readlines()
                txt_slide_map = self._build_detailed_txt_slide_map(txt_lines)

            # Run pdflatex
            cmd = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
                   '-file-line-error', tex_file_abs]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                errors='replace'
            )

            error_lines = []
            error_context_lines = []
            in_error_context = False
            last_slide_compiled = 0
            actual_error_tex_line = None
            error_message = ""

            # Store all line numbers found in the log
            all_error_lines = []
            line_context_map = {}  # Map line number to context

            slide_pattern = r'\[(\d+)\]'

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break

                if line:
                    # Track successfully compiled slides
                    slide_match = re.search(slide_pattern, line)
                    if slide_match and ']' in line and 'pdfTeX warning' not in line:
                        slide_num = int(slide_match.group(1))
                        if slide_num > last_slide_compiled:
                            last_slide_compiled = slide_num
                            result['last_successful_slide'] = slide_num

                    # CRITICAL: Collect ALL line numbers from the log
                    line_match = re.search(r'l\.(\d+)', line)
                    if line_match:
                        found_line = int(line_match.group(1))
                        all_error_lines.append(found_line)
                        line_context_map[found_line] = line

                    # Capture error messages - look for fatal errors
                    if line.startswith('!'):
                        error_message = line.strip()
                        error_lines.append(error_message)
                        result['errors'].append(error_message)
                        in_error_context = True
                        self.write(line, "red")

                        # If this is a fatal error, this is our target
                        if 'Fatal error' in line or 'no output PDF' in line:
                            # Use the last line number collected
                            if all_error_lines:
                                actual_error_tex_line = all_error_lines[-1]  # Use the LAST line number
                                result['error_line_tex'] = actual_error_tex_line
                                self.write(f"\n⚠ Fatal error at line {actual_error_tex_line}\n", "red")

                    elif in_error_context:
                        error_context_lines.append(line.strip())
                        if len(error_context_lines) < 20:
                            self.write(line, "yellow")

                        # Stop capturing after we see the next error or end of context
                        if line.startswith('!') or 'l.' in line:
                            in_error_context = False

                    elif 'Warning' in line:
                        if 'Citation' in line:
                            self.write(line, "yellow")
                        elif 'textendash' in line:
                            self.write(line, "yellow")
                            result['has_math_warning'] = True
                        else:
                            self.write(line, "yellow")
                    elif not line.startswith('[') and not line.startswith('('):
                        self.write(line, "white")

            process.wait()

            # If we found a fatal error but no line number from the pattern, check the error message
            if actual_error_tex_line is None and all_error_lines:
                # Use the last line number found in the log
                actual_error_tex_line = all_error_lines[-1]
                result['error_line_tex'] = actual_error_tex_line
                self.write(f"\n⚠ Using last error line from log: {actual_error_tex_line}\n", "yellow")

            # Find which slide contains this line
            if actual_error_tex_line:
                error_slide_num = None
                for slide_num, slide_info in tex_slide_map.items():
                    if slide_info['start_line'] <= actual_error_tex_line <= slide_info['end_line']:
                        error_slide_num = slide_num
                        result['slide_number'] = slide_num
                        break

                if error_slide_num:
                    self.write(f"\n📍 ERROR LOCATED:", "red")
                    self.write(f" Slide {error_slide_num}", "yellow")
                    self.write(f" (TeX line {actual_error_tex_line})\n", "cyan")

                    # Get the slide content
                    slide_info = tex_slide_map[error_slide_num]
                    self.write(f"   Slide title: {slide_info['title'][:50]}\n", "cyan")

                    # Find the exact line within the slide
                    relative_line = actual_error_tex_line - slide_info['start_line']
                    self.write(f"   Relative position: line {relative_line} within slide\n", "cyan")

                    # Map to TXT file line
                    if error_slide_num in txt_slide_map:
                        txt_info = txt_slide_map[error_slide_num]
                        txt_error_line = txt_info['start_line'] + relative_line
                        if txt_error_line <= txt_info['end_line']:
                            result['error_line'] = txt_error_line
                            self.write(f"   Maps to TXT line: {txt_error_line}\n", "green")

                            # Show the problematic line from TXT
                            if 1 <= txt_error_line <= len(txt_lines):
                                problematic_line = txt_lines[txt_error_line - 1].strip()
                                self.write(f"   Problematic content: {problematic_line[:100]}\n", "yellow")

                                # Check if this is the Open-Circuit Voltage slide
                                if 'Open-Circuit Voltage' in problematic_line or 'V_{oc}' in problematic_line:
                                    self.write(f"\n💡 SPECIFIC FIX NEEDED:\n", "cyan")
                                    self.write(f"   The title has unclosed math mode.\n", "yellow")
                                    self.write(f"   Change: {problematic_line}\n", "yellow")
                                    self.write(f"   To:     {problematic_line.rstrip()}$\n", "green")

                                    # Auto-fix if possible
                                    if problematic_line.count('$') % 2 != 0:
                                        fixed_line = problematic_line.rstrip() + '$'
                                        txt_lines[txt_error_line - 1] = fixed_line + '\n'
                                        with open(txt_file, 'w', encoding='utf-8') as f:
                                            f.writelines(txt_lines)
                                        self.write(f"\n✓ Auto-fixed the TXT file!\n", "green")
                                        result['fixed'] = True

                                        # Regenerate TeX
                                        from BeamerSlideGenerator import process_input_file
                                        process_input_file(txt_file, tex_file_abs)
                                        self.write(f"✓ Regenerated TeX file\n", "green")

            # If we found an error but no slide number, try to infer
            if error_lines and result['slide_number'] == 0 and result['last_successful_slide'] > 0:
                result['slide_number'] = result['last_successful_slide'] + 1
                if result['slide_number'] in txt_slide_map:
                    result['error_line'] = txt_slide_map[result['slide_number']]['start_line']
                    self.write(f"\n⚠ Inferring error in Slide {result['slide_number']}\n", "yellow")

            # Analyze the error
            if error_lines and not result['success']:
                result['error_context'] = error_context_lines

                if 'Extra }' in error_message or 'forgotten $' in error_message:
                    result['analysis'] = {
                        'error_type': 'extra_brace_or_forgotten_dollar',
                        'suggestion': 'Extra } or forgotten $. This is often caused by unclosed math mode (e.g., $V_{oc} without closing $). Check for $ signs in titles.',
                        'auto_fixable': True,
                        'fix_type': 'fix_math_delimiters',
                        'line': result['error_line'],
                        'slide': result['slide_number']
                    }

            # Show helpful context
            if result['slide_number'] > 0 and result['error_line']:
                self.write(f"\n" + "="*60 + "\n", "cyan")
                self.write(f"HELPFUL CONTEXT:\n", "cyan")
                self.write(f"="*60 + "\n", "cyan")
                self.write(f"Error in Slide {result['slide_number']}\n", "yellow")
                self.write(f"Open your .txt file and go to line {result['error_line']}\n", "green")

            # Check if PDF was created
            pdf_file = tex_file_abs.replace('.tex', '.pdf')
            if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
                result['success'] = True
                if result.get('fixed'):
                    self.write(f"\n✓ PDF generated successfully after auto-fix!\n", "green")

            os.chdir(original_dir)
            return result

        except Exception as e:
            result['errors'].append(str(e))
            import traceback
            traceback.print_exc()
            os.chdir(original_dir)
            return result

    def _build_detailed_tex_slide_map(self, tex_lines: list) -> dict:
        """Build detailed map of slide numbers to line ranges with titles"""
        slide_map = {}
        current_slide = 0
        in_frame = False
        frame_start = None
        current_title = "Untitled"

        for i, line in enumerate(tex_lines, 1):
            # Detect frame start (not commented out)
            if '\\begin{frame}' in line and not line.strip().startswith('%'):
                current_slide += 1
                in_frame = True
                frame_start = i

                # Extract title from frame
                title_match = re.search(r'\\begin{frame}\{([^}]+)\}', line)
                if title_match:
                    current_title = title_match.group(1)
                else:
                    # Look for frametitle in subsequent lines
                    current_title = f"Slide {current_slide}"

                slide_map[current_slide] = {
                    'start_line': frame_start,
                    'end_line': None,
                    'title': current_title,
                    'content_start': None,
                    'content_end': None
                }

            elif '\\end{frame}' in line and in_frame:
                if current_slide in slide_map:
                    slide_map[current_slide]['end_line'] = i
                in_frame = False

            # Track content boundaries within frame
            elif in_frame and current_slide in slide_map:
                if slide_map[current_slide]['content_start'] is None:
                    # Content starts after the frame opening
                    if not line.strip().startswith('%'):
                        slide_map[current_slide]['content_start'] = i
                else:
                    # Update content end as we go
                    if not line.strip().startswith('%'):
                        slide_map[current_slide]['content_end'] = i

        # Fill any missing end lines
        for slide_num in slide_map:
            if slide_map[slide_num]['end_line'] is None:
                # Find next slide start or end of file
                next_start = len(tex_lines)
                for next_slide in range(slide_num + 1, len(slide_map) + 1):
                    if next_slide in slide_map:
                        next_start = slide_map[next_slide]['start_line']
                        break
                slide_map[slide_num]['end_line'] = next_start - 1

        return slide_map

    def _build_detailed_txt_slide_map(self, txt_lines: list) -> dict:
        """Build detailed map of slide numbers to line ranges in TXT file"""
        slide_map = {}
        current_slide = 0
        slide_start = None
        in_content = False
        current_title = ""

        for i, line in enumerate(txt_lines, 1):
            # Detect title line
            if re.match(r'^%?\s*\\title\s+', line):
                current_slide += 1
                slide_start = i

                # Extract title
                title_match = re.search(r'\\title\s+(.+)$', line)
                if title_match:
                    current_title = title_match.group(1).strip()
                else:
                    current_title = f"Slide {current_slide}"

                slide_map[current_slide] = {
                    'start_line': slide_start,
                    'end_line': None,
                    'title': current_title,
                    'is_masked': line.strip().startswith('%')
                }

            # Detect content block start
            elif '\\begin{Content}' in line:
                in_content = True

            # Detect content block end
            elif '\\end{Content}' in line:
                in_content = False

        # Fill end lines
        slides_list = sorted(slide_map.keys())
        for idx, slide_num in enumerate(slides_list):
            next_slide = slides_list[idx + 1] if idx + 1 < len(slides_list) else None
            if next_slide:
                slide_map[slide_num]['end_line'] = slide_map[next_slide]['start_line'] - 1
            else:
                slide_map[slide_num]['end_line'] = len(txt_lines)

        return slide_map

    def force_reload_from_file(self, file_path: str = None):
        """Force reload the current file to sync with external changes"""
        if file_path is None:
            file_path = self.current_file

        if file_path and os.path.exists(file_path):
            self.write(f"🔄 Reloading {os.path.basename(file_path)}...\n", "cyan")
            self.load_file(file_path)
            self.write(f"✓ File reloaded successfully\n", "green")
            return True
        return False

    def find_slide_line_number(self, tex_file: str, slide_number: int) -> int:
        """Find the line number of a specific slide in the TeX file"""
        try:
            with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
                tex_lines = f.readlines()

            slide_count = 0
            for i, line in enumerate(tex_lines):
                if '\\frametitle' in line or '\\begin{frame}' in line:
                    slide_count += 1
                    if slide_count == slide_number:
                        return i + 1  # Return 1-based line number

            # If exact slide not found, return a reasonable default
            return 1
        except Exception:
            return 1

    def sync_slides_from_tex(self, tex_file: str) -> None:
        """Sync the slides data structure from the TeX file after fixes"""
        try:
            # Read the TeX file
            with open(tex_file, 'r', encoding='utf-8') as f:
                tex_content = f.read()

            # Extract the document body
            import re
            doc_match = re.search(r'\\begin{document}(.*?)\\end{document}', tex_content, re.DOTALL)
            if not doc_match:
                return

            document_body = doc_match.group(1)

            # Find all frames
            frame_pattern = r'\\begin\{frame\}(?:\[[^\]]*\])?(?:\{([^}]*)\})?(.*?)\\end\{frame\}'
            frames = re.finditer(frame_pattern, document_body, re.DOTALL)

            # Update slides
            slide_idx = 0
            for frame_match in frames:
                title = frame_match.group(1) or f"Slide {slide_idx + 1}"
                frame_content = frame_match.group(2).strip()

                if slide_idx < len(self.slides):
                    # Update existing slide title
                    self.slides[slide_idx]['title'] = title
                    # Note: Content sync would be more complex; for now just update title
                slide_idx += 1

            self.update_slide_list()
            if self.current_slide_index >= 0:
                self.load_slide(self.current_slide_index)

            self.write("✓ Slides synced from fixed TeX file\n", "green")

        except Exception as e:
            self.write(f"Warning: Could not sync slides: {e}\n", "yellow")

    def apply_global_fix(self, txt_file: str, tex_file: str, error_type: str) -> bool:
        """Apply a fix globally to the entire document using LaTeXErrorAnalyzer"""
        try:
            # Read the TXT file
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Use the static method from LaTeXErrorAnalyzer
            fixed_content = LaTeXErrorAnalyzer.apply_global_fix(content, error_type)

            if fixed_content != content:
                # Write the fixed content back
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)

                self.write(f"✓ Applied global fix for '{error_type}'\n", "green")
                self.write("  Changes have been saved to the TXT file\n", "cyan")

                # Regenerate TeX from the fixed TXT file
                self.write("  Regenerating TeX file...\n", "cyan")
                self.convert_to_tex()

                return True

            self.write(f"No changes needed for global fix '{error_type}'\n", "yellow")
            return False

        except Exception as e:
            self.write(f"Global fix failed: {e}\n", "red")
            import traceback
            traceback.print_exc()
            return False

    def add_package_to_preamble(self, tex_file: str, package: str) -> bool:
        """Add a package to the TeX file preamble"""
        try:
            with open(tex_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            new_lines = []
            package_added = False
            for line in lines:
                new_lines.append(line)
                if '\\begin{document}' in line and not package_added:
                    new_lines.insert(-1, f'\\usepackage{{{package}}}\n')
                    package_added = True

            if package_added:
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                return True
            return False

        except Exception as e:
            self.write(f"Error adding package: {e}\n", "red")
            return False

    def get_custom_preamble(self) -> str:
        """Generate custom preamble with proper styling and required packages"""
        try:
            from BeamerSlideGenerator import get_beamer_preamble

            # Ensure we have non-empty values
            title = self.presentation_info.get('title', '').strip()
            subtitle = self.presentation_info.get('subtitle', '').strip()
            author = self.presentation_info.get('author', '').strip()
            institution = self.presentation_info.get('institution', 'Artificial Intelligence Research and Intelligent Systems (airis4D)')
            short_institute = self.presentation_info.get('short_institute', 'airis4D')
            date = self.presentation_info.get('date', '\\today')

            # Use defaults if empty
            if not title:
                title = "Presentation"
            if not author:
                author = "airis4D"

            # Get base preamble
            base_preamble = get_beamer_preamble(
                title, subtitle, author, institution, short_institute, date
            )

            # Additional packages needed for special characters and units
            extra_packages = r"""
    % Additional packages for special characters and units
    \usepackage{textcomp}      % For \textmu, \textendash, etc.
    \usepackage{siunitx}       % For proper units (Ω·cm², etc.)
    \usepackage{amsmath}       % Enhanced math support
    \usepackage{amssymb}       % Additional math symbols

    % Configure siunitx for proper formatting
    \sisetup{
        per-mode = symbol,
        output-decimal-marker = {.},
        group-separator = {,}
    }
    """

            # Insert extra packages before \begin{document}
            doc_pos = base_preamble.find("\\begin{document}")
            if doc_pos != -1:
                # Check if packages already exist to avoid duplicates
                if 'textcomp' not in base_preamble:
                    base_preamble = base_preamble[:doc_pos] + extra_packages + base_preamble[doc_pos:]
            else:
                # If no \begin{document}, add at the end
                base_preamble = base_preamble + extra_packages + "\n\\begin{document}\n"

            # Process logo if present
            if 'logo' in self.presentation_info and self.presentation_info['logo']:
                preamble = re.sub(r'\\logo{[^}]*}\s*\n?', '', base_preamble)
                doc_pos = preamble.find("\\begin{document}")
                if doc_pos != -1:
                    logo_command = self.presentation_info['logo'] + "\n\n"
                    preamble = preamble[:doc_pos] + logo_command + preamble[doc_pos:]
                else:
                    preamble = base_preamble + "\n" + self.presentation_info['logo'] + "\n"
            else:
                preamble = base_preamble

            return preamble

        except Exception as e:
            print(f"Error generating custom preamble: {e}")
            # Return fallback preamble with all necessary packages
            return r"""\documentclass[aspectratio=169]{beamer}
    \usepackage{graphicx}
    \usepackage{xcolor}
    \usepackage{textcomp}
    \usepackage{siunitx}
    \usepackage{amsmath}
    \usepackage{amssymb}
    \usetheme{Madrid}
    \title{Presentation}
    \author{airis4D}
    \sisetup{per-mode=symbol}
    \begin{document}
    """

    def _build_tex_slide_map(self, tex_lines: list) -> dict:
        """Build a map of slide numbers to line ranges in TeX file"""
        slide_map = {}
        current_slide = 0
        in_frame = False
        frame_start = None

        for i, line in enumerate(tex_lines, 1):
            # Detect frame start (not commented out)
            if '\\begin{frame}' in line and not line.strip().startswith('%'):
                current_slide += 1
                in_frame = True
                frame_start = i
                slide_map[current_slide] = {
                    'start_line': frame_start,
                    'end_line': None,
                    'title': self._extract_frame_title(line)
                }
            elif '\\end{frame}' in line and in_frame:
                if current_slide in slide_map:
                    slide_map[current_slide]['end_line'] = i
                in_frame = False

        # Fill any missing end lines
        for slide_num in slide_map:
            if slide_map[slide_num]['end_line'] is None:
                # Find next slide start or end of file
                next_start = len(tex_lines)
                for next_slide in range(slide_num + 1, len(slide_map) + 1):
                    if next_slide in slide_map:
                        next_start = slide_map[next_slide]['start_line']
                        break
                slide_map[slide_num]['end_line'] = next_start - 1

        return slide_map

    def _build_txt_slide_map(self, txt_lines: list) -> dict:
        """Build a map of slide numbers to line ranges in TXT file (skipping masked slides)"""
        slide_map = {}
        current_slide = 0
        slide_start = None
        in_content = False

        for i, line in enumerate(txt_lines, 1):
            # Detect title line (even if masked)
            if re.match(r'^%?\s*\\title\s+', line):
                # Check if this slide is fully masked (all content lines start with %)
                is_fully_masked = self._is_slide_fully_masked(txt_lines, i)

                if not is_fully_masked:
                    current_slide += 1
                    slide_start = i
                    slide_map[current_slide] = {
                        'start_line': slide_start,
                        'end_line': None,
                        'title': self._extract_title_from_line(line),
                        'is_masked': False
                    }
                else:
                    # Track masked slides but don't include in navigation
                    current_slide += 1
                    slide_map[current_slide] = {
                        'start_line': i,
                        'end_line': None,
                        'title': self._extract_title_from_line(line),
                        'is_masked': True
                    }

        # Fill end lines
        slides_list = sorted(slide_map.keys())
        for idx, slide_num in enumerate(slides_list):
            next_slide = slides_list[idx + 1] if idx + 1 < len(slides_list) else None
            if next_slide:
                slide_map[slide_num]['end_line'] = slide_map[next_slide]['start_line'] - 1
            else:
                slide_map[slide_num]['end_line'] = len(txt_lines)

        return slide_map

    def _is_slide_fully_masked(self, txt_lines: list, title_line_idx: int) -> bool:
        """Check if all non-empty lines in a slide start with %"""
        # Find end of this slide (next title or EOF)
        end_idx = len(txt_lines)
        for i in range(title_line_idx + 1, len(txt_lines)):
            if re.match(r'^%?\s*\\title\s+', txt_lines[i]):
                end_idx = i
                break

        # Check content lines between title and end
        for i in range(title_line_idx + 1, end_idx):
            line = txt_lines[i].strip()
            if line and not line.startswith('%'):
                return False
        return True

    def _extract_frame_title(self, line: str) -> str:
        """Extract frame title from \\begin{frame}{Title} or \\frametitle{Title}"""
        # Check for frame with title in brackets
        match = re.search(r'\\begin{frame}\{([^}]+)\}', line)
        if match:
            return match.group(1)
        return "Untitled"

    def _extract_title_from_line(self, line: str) -> str:
        """Extract title from \\title line (handling masked lines)"""
        # Remove % prefix if present
        clean_line = re.sub(r'^\s*%\s*', '', line)
        match = re.search(r'\\title\s+(.+)$', clean_line)
        if match:
            return match.group(1).strip()
        return "Untitled"

    def run_pdflatex_with_error_capture(self, tex_file: str, auto_fix: bool = True) -> dict:
        """Run pdflatex and capture errors using the LaTeXErrorAnalyzer class"""
        result = {
            'success': False,
            'errors': [],
            'error_line': None,
            'error_context': [],
            'analysis': None,
            'fixed': False,
            'fix_description': '',
            'last_successful_slide': 0
        }

        try:
            tex_dir = os.path.dirname(tex_file) or '.'
            original_dir = os.getcwd()
            os.chdir(tex_dir)

            tex_file_abs = os.path.abspath(tex_file)

            # Read the current TeX content
            with open(tex_file_abs, 'r', encoding='utf-8', errors='ignore') as f:
                tex_lines = f.readlines()

            # Find all frame titles to map slide numbers
            slide_titles = []
            frame_pattern = r'\\frametitle\{([^}]+)\}'
            for i, line in enumerate(tex_lines):
                match = re.search(frame_pattern, line)
                if match:
                    slide_titles.append({
                        'line_num': i + 1,
                        'title': match.group(1),
                        'slide_num': len(slide_titles) + 1
                    })

            # Run pdflatex
            cmd = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
                   '-file-line-error', tex_file_abs]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                errors='replace'
            )

            error_lines = []
            current_error = None
            error_line_num = None
            error_context_lines = []
            in_error_context = False
            last_slide_compiled = 0

            slide_pattern = r'\[(\d+)\]'

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break

                if line:
                    slide_match = re.search(slide_pattern, line)
                    if slide_match and ']' in line and 'pdfTeX warning' not in line:
                        slide_num = int(slide_match.group(1))
                        if slide_num > last_slide_compiled:
                            last_slide_compiled = slide_num
                            result['last_successful_slide'] = slide_num

                    if line.startswith('!'):
                        self.write(line, "red")
                        current_error = line.strip()
                        error_lines.append(current_error)
                        result['errors'].append(current_error)
                        error_context_lines = []
                        in_error_context = True
                    elif in_error_context and ('l.' in line or 'line' in line.lower()):
                        match = re.search(r'l\.(\d+)', line)
                        if match:
                            error_line_num = int(match.group(1))
                            result['error_line'] = error_line_num
                        error_context_lines.append(line.strip())
                    elif in_error_context and len(error_context_lines) < 15:
                        error_context_lines.append(line.strip())
                    elif 'Runaway argument' in line:
                        self.write(line, "red")
                        current_error = line.strip()
                        error_lines.append(current_error)
                        result['errors'].append(current_error)
                        in_error_context = True
                    elif 'Warning' in line:
                        self.write(line, "yellow")
                    elif not line.startswith('[') and not line.startswith('('):
                        self.write(line, "white")

            process.wait()

            # If we have a last successful slide but no error line, approximate
            if error_lines and not result['error_line'] and result['last_successful_slide'] > 0:
                next_slide_num = result['last_successful_slide'] + 1
                for slide_info in slide_titles:
                    if slide_info['slide_num'] == next_slide_num:
                        result['error_line'] = slide_info['line_num']
                        self.write(f"\n⚠ Assuming error is in slide {next_slide_num}: '{slide_info['title']}'\n", "yellow")
                        break

            # Analyze the error if found
            if error_lines and not result['success']:
                result['error_context'] = error_context_lines
                analysis = LaTeXErrorAnalyzer.analyze_error(
                    error_lines[0],
                    error_context_lines,
                    None,
                    result['error_line'],
                    tex_lines
                )
                result['analysis'] = analysis

                # Try auto-fix if enabled
                if auto_fix and analysis.get('auto_fixable'):
                    fixed_lines, fix_desc, fix_count = LaTeXErrorAnalyzer.apply_fix(
                        tex_lines, analysis, result['error_line']
                    )
                    if fix_count > 0:
                        with open(tex_file_abs, 'w', encoding='utf-8') as f:
                            f.writelines(fixed_lines)
                        result['fixed'] = True
                        result['fix_description'] = fix_desc
                        self.write(f"✓ Auto-fix applied: {fix_desc}\n", "green")

                        # Also fix the TXT file if it exists
                        txt_file = tex_file_abs.replace('.tex', '.txt')
                        if os.path.exists(txt_file):
                            with open(txt_file, 'r', encoding='utf-8') as f:
                                txt_lines = f.readlines()
                            fixed_txt_lines, _, _ = LaTeXErrorAnalyzer.apply_fix(
                                txt_lines, analysis, result['error_line']
                            )
                            with open(txt_file, 'w', encoding='utf-8') as f:
                                f.writelines(fixed_txt_lines)
                            self.write(f"✓ Also fixed TXT file\n", "green")

            # Check if PDF was created
            pdf_file = tex_file_abs.replace('.tex', '.pdf')
            if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
                result['success'] = True

            os.chdir(original_dir)
            return result

        except Exception as e:
            result['errors'].append(str(e))
            return result

    def analyze_latex_error(self, error_msg: str, context: list, tex_content: str,
                            line_num: int = None, tex_lines: list = None) -> dict:
        """Analyze LaTeX error and suggest fixes"""
        import re

        analysis = {
            'error_type': 'unknown',
            'suggestion': 'Unknown error. Please check the log file.',
            'auto_fixable': False,
            'fix_type': 'editor',
            'fix_data': None,
            'line': line_num
        }

        # Check for runaway argument / missing brace
        if 'Runaway argument' in error_msg or 'File ended while scanning' in error_msg:
            analysis['error_type'] = 'missing_brace'
            analysis['suggestion'] = 'Missing closing brace or math mode delimiter. Check for unmatched {, }, $, or math environment boundaries.'
            analysis['auto_fixable'] = False
            analysis['fix_type'] = 'editor'
            return analysis

        # Check for misplaced alignment tab (&) error
        if any(phrase in error_msg for phrase in [
            'Misplaced alignment tab character &',
            'Misplaced &',
            'alignment tab character &'
        ]):
            return self._analyze_ampersand_error(error_msg, tex_lines, line_num)

        # Check for missing \item error
        elif 'missing \\item' in error_msg.lower() or "perhaps a missing \\item" in error_msg:
            return self._analyze_missing_item_error(error_msg, line_num)

        # Check for undefined control sequence (missing package)
        elif 'Undefined control sequence' in error_msg:
            return self._analyze_undefined_command(error_msg, line_num)

        # Check for missing $ (math mode)
        elif 'Missing $ inserted' in error_msg:
            analysis['error_type'] = 'missing_math_mode'
            analysis['suggestion'] = 'Math mode may be missing. Add $ around math expressions like $...$ or $$...$$.'
            analysis['auto_fixable'] = False
            analysis['fix_type'] = 'editor'
            return analysis

        # Check for missing closing brace
        elif 'Missing } inserted' in error_msg:
            analysis['error_type'] = 'missing_brace'
            analysis['suggestion'] = 'Missing closing brace. Check for unmatched { characters.'
            analysis['auto_fixable'] = False
            analysis['fix_type'] = 'editor'
            return analysis

        return analysis

    def apply_auto_fix_to_tex(self, tex_file: str, tex_lines: list, analysis: dict,
                              error_line: int = None) -> bool:
        """Apply automatic fix to both TeX and TXT files"""
        try:
            fix_type = analysis.get('fix_type')
            fixed_lines = tex_lines.copy()
            fix_description = ""
            txt_file = tex_file.replace('.tex', '.txt')

            if fix_type == 'escape_ampersand':
                # Escape ampersands outside tables in TeX file
                in_table = False
                fixed_count = 0
                for i in range(len(fixed_lines)):
                    line = fixed_lines[i]
                    original_line = line

                    if '\\begin{tabular}' in line or '\\begin{array}' in line:
                        in_table = True
                    if ('\\end{tabular}' in line or '\\end{array}' in line) and in_table:
                        in_table = False

                    if not in_table and '&' in line:
                        new_line = line.replace('&', '\\&')
                        new_line = new_line.replace('\\\\&', '\\&')
                        if new_line != original_line:
                            fixed_count += 1
                            fixed_lines[i] = new_line

                if fixed_count == 0 and error_line and error_line <= len(tex_lines):
                    line = fixed_lines[error_line - 1]
                    if '&' in line and '\\&' not in line:
                        fixed_lines[error_line - 1] = line.replace('&', '\\&')
                        fixed_count = 1

                fix_description = f"Escaped {fixed_count} ampersand(s)"

                # ALSO fix the TXT file - THIS IS CRITICAL
                if os.path.exists(txt_file):
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        txt_lines = f.readlines()

                    fixed_txt_lines = []
                    in_table = False
                    for line in txt_lines:
                        if '\\begin{tabular}' in line or '\\begin{array}' in line:
                            in_table = True
                        if ('\\end{tabular}' in line or '\\end{array}' in line) and in_table:
                            in_table = False

                        if not in_table and '&' in line:
                            line = line.replace('&', '\\&')
                            line = line.replace('\\\\&', '\\&')
                        fixed_txt_lines.append(line)

                    with open(txt_file, 'w', encoding='utf-8') as f:
                        f.writelines(fixed_txt_lines)
                    self.write(f"  ✓ Also fixed ampersands in TXT file\n", "green")

            elif fix_type == 'add_item' and error_line:
                # Add \item to lines starting with - or •
                for i in range(max(0, error_line - 5), min(len(fixed_lines), error_line + 5)):
                    line = fixed_lines[i]
                    stripped = line.strip()
                    if stripped and (stripped.startswith('-') or stripped.startswith('•')):
                        fixed_lines[i] = '\\item ' + line.lstrip('-•').strip()
                        fix_description = f"Added \\item on line {i+1}"
                        break

                # Also fix TXT file
                if os.path.exists(txt_file):
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        txt_lines = f.readlines()

                    for i in range(max(0, error_line - 5), min(len(txt_lines), error_line + 5)):
                        line = txt_lines[i]
                        stripped = line.strip()
                        if stripped and (stripped.startswith('-') or stripped.startswith('•')):
                            txt_lines[i] = '\\item ' + line.lstrip('-•').strip()
                            break

                    with open(txt_file, 'w', encoding='utf-8') as f:
                        f.writelines(txt_lines)
                    self.write(f"  ✓ Also fixed TXT file\n", "green")

            elif fix_type == 'add_package':
                package = analysis.get('fix_data')
                if package:
                    new_lines = []
                    package_added = False
                    for line in fixed_lines:
                        new_lines.append(line)
                        if '\\begin{document}' in line and not package_added:
                            new_lines.insert(-1, f'\\usepackage{{{package}}}\n')
                            package_added = True
                            fix_description = f"Added \\usepackage{{{package}}}"
                    fixed_lines = new_lines

            # Write the fixed TeX content back
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)

            if fix_description:
                self.write(f"✓ Auto-fix applied: {fix_description}\n", "green")

            return True

        except Exception as e:
            self.write(f"Auto-fix failed: {str(e)}\n", "red")
            import traceback
            traceback.print_exc()
            return False

    def show_latex_log(self, tex_file: str):
        """Display the LaTeX log file for debugging"""
        log_file = tex_file.replace('.tex', '.log')
        if os.path.exists(log_file):
            dialog = ctk.CTkToplevel(self)
            dialog.title("LaTeX Compilation Log")
            dialog.geometry("800x600")
            dialog.transient(self)

            # Create text widget
            text_widget = ctk.CTkTextbox(dialog, font=("Courier", 10))
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)

            # Load log content
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()

            text_widget.insert('1.0', log_content)

            # Add buttons
            button_frame = ctk.CTkFrame(dialog)
            button_frame.pack(fill="x", padx=10, pady=10)

            ctk.CTkButton(
                button_frame,
                text="Copy to Clipboard",
                command=lambda: self.copy_text_to_clipboard(log_content)
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                button_frame,
                text="Close",
                command=dialog.destroy
            ).pack(side="right", padx=5)
        else:
            messagebox.showerror("Error", f"Log file not found: {log_file}")

    def run_pdflatex_with_auto_packages(self, tex_file: str, timeout: int = 120) -> dict:
        """Run pdflatex with automatic package installation and error capturing"""
        result = {
            'success': False,
            'errors': [],
            'warnings': [],
            'packages_installed': False,
            'installed_packages': []
        }

        try:
            tex_dir = os.path.dirname(tex_file) or '.'
            original_dir = os.getcwd()
            os.chdir(tex_dir)

            tex_file_abs = os.path.abspath(tex_file)

            # Check if tex file exists
            if not os.path.exists(tex_file_abs):
                result['errors'].append(f"TeX file not found: {tex_file_abs}")
                self.write(f"✗ TeX file not found: {tex_file_abs}\n", "red")
                return result

            # Run pdflatex and capture all output
            self.write("\nCompiling with pdflatex...\n", "white")

            cmd = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
                   '-file-line-error', tex_file_abs]

            all_errors = []

            for i in range(3):  # Three passes for references
                self.write(f"  Pass {i+1}/3...\n", "cyan")

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    errors='replace'
                )

                # Capture output
                pass_errors = []
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        # Look for errors
                        if line.startswith('!'):
                            self.write(line, "red")
                            pass_errors.append(line)
                            all_errors.append(line)
                        elif 'Error' in line or 'error' in line:
                            self.write(line, "red")
                            pass_errors.append(line)
                        elif 'Warning' in line:
                            self.write(line, "yellow")
                        elif 'no output PDF' in line:
                            self.write(line, "red")

                process.wait()

                if process.returncode != 0:
                    self.write(f"  ✗ Compilation failed on pass {i+1}\n", "red")
                    result['errors'].extend(pass_errors)

            # Check if PDF was created
            pdf_file = tex_file_abs.replace('.tex', '.pdf')
            if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
                result['success'] = True
                self.write("\n✓ PDF generated successfully!\n", "green")
            else:
                self.write("\n✗ PDF file not found after compilation\n", "red")

                # Show the log file for debugging
                log_file = tex_file_abs.replace('.tex', '.log')
                if os.path.exists(log_file):
                    self.write("\n" + "="*60 + "\n", "yellow")
                    self.write("LATEX LOG FILE (last 50 lines):\n", "yellow")
                    self.write("="*60 + "\n", "yellow")
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        log_lines = f.readlines()
                        # Show last 50 lines
                        for line in log_lines[-50:]:
                            self.write(line, "white")

                    # Also check for specific errors in the log
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()

                    # Look for common errors
                    if 'Undefined control sequence' in log_content:
                        self.write("\n🔍 Found 'Undefined control sequence' errors:\n", "red")
                        for line in log_lines:
                            if 'Undefined control sequence' in line:
                                self.write(f"  {line.strip()}\n", "red")

                    if '! LaTeX Error:' in log_content:
                        self.write("\n🔍 Found LaTeX errors:\n", "red")
                        for line in log_lines:
                            if '! LaTeX Error:' in line:
                                self.write(f"  {line.strip()}\n", "red")

                    if 'Citation' in log_content and 'undefined' in log_content:
                        self.write("\n🔍 Found undefined citations:\n", "yellow")
                        for line in log_lines:
                            if 'Citation' in line and 'undefined' in line:
                                self.write(f"  {line.strip()}\n", "yellow")

            os.chdir(original_dir)
            return result

        except Exception as e:
            self.write(f"\nProcess error: {str(e)}\n", "red")
            result['errors'].append(str(e))
            return result

    def validate_tex_file(self, tex_file: str) -> bool:
        """Validate TeX file for common issues before compilation"""
        try:
            with open(tex_file, 'r', encoding='utf-8') as f:
                content = f.read()

            issues = []

            # Check for unbalanced braces
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                issues.append(f"Unbalanced braces: {{={open_braces}, }}={close_braces}")

            # Check for unmatched \begin and \end
            begin_count = content.count('\\begin{')
            end_count = content.count('\\end{')
            if begin_count != end_count:
                issues.append(f"Unmatched environments: \\begin={{={begin_count}, \\end={{={end_count}")

            # Check for missing \end{document}
            if '\\end{document}' not in content:
                issues.append("Missing \\end{document}")

            # Check for common problematic patterns
            if '\\begin{frame}' in content and '\\end{frame}' not in content:
                issues.append("Missing \\end{frame}")

            if issues:
                self.write("\n⚠ TeX VALIDATION ISSUES:\n", "yellow")
                for issue in issues:
                    self.write(f"  • {issue}\n", "yellow")
                return False

            self.write("\n✓ TeX validation passed\n", "green")
            return True

        except Exception as e:
            self.write(f"Error validating TeX: {e}\n", "red")
            return False

    def check_latex_log_for_warnings(self, log_file: str) -> list:
        """Check LaTeX log file for warnings"""
        warnings = []
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()

            # Find all warnings
            warning_patterns = [
                r'LaTeX Warning: ([^\n]+)',
                r'Package [^\n]+ Warning: ([^\n]+)',
                r'Warning: ([^\n]+)'
            ]

            for pattern in warning_patterns:
                matches = re.findall(pattern, log_content)
                warnings.extend(matches)

            # Remove duplicates
            warnings = list(dict.fromkeys(warnings))

            return warnings[:10]  # Return first 10 warnings

        except Exception as e:
            self.write(f"Error reading log file: {e}\n", "yellow")
            return []

    def install_latex_packages(self, packages: list) -> bool:
        """
        Automatically install missing LaTeX packages using tlmgr (TeX Live) or MiKTeX
        Returns True if all packages were installed successfully
        """
        if not packages:
            return True

        self.write("\n" + "="*60 + "\n", "cyan")
        self.write("AUTOMATIC PACKAGE INSTALLATION\n", "cyan")
        self.write("="*60 + "\n", "cyan")
        self.write(f"Missing packages: {', '.join(packages)}\n\n", "yellow")

        # Detect LaTeX distribution
        tex_distribution = self.detect_latex_distribution()

        if not tex_distribution:
            self.write("⚠ Could not detect LaTeX distribution\n", "red")
            self.write("Please install missing packages manually:\n", "yellow")
            for pkg in packages:
                self.write(f"  - {pkg}\n", "yellow")
            return False

        self.write(f"Detected LaTeX distribution: {tex_distribution}\n", "green")

        # Ask user for permission
        if not messagebox.askyesno("Install Packages",
                                   f"The following LaTeX packages are missing:\n\n"
                                   f"{', '.join(packages)}\n\n"
                                   f"Would you like to install them automatically?\n\n"
                                   f"This requires an internet connection and may take a moment."):
            self.write("Package installation cancelled by user\n", "yellow")
            return False

        success_count = 0

        for pkg in packages:
            self.write(f"\nInstalling package: {pkg}...\n", "white")

            if tex_distribution == 'texlive':
                success = self.install_texlive_package(pkg)
            elif tex_distribution == 'miktex':
                success = self.install_miktex_package(pkg)
            else:
                success = False

            if success:
                success_count += 1
                self.write(f"  ✓ Installed {pkg}\n", "green")
            else:
                self.write(f"  ✗ Failed to install {pkg}\n", "red")

        self.write(f"\nInstalled {success_count}/{len(packages)} packages\n",
                   "green" if success_count == len(packages) else "yellow")

        return success_count == len(packages)

    def handle_missing_package_error(self, error_message: str) -> list:
        """Parse error message to identify missing packages"""
        import re

        missing_packages = []

        # Pattern for missing .sty files
        sty_pattern = r'File `([^\.]+)\.sty\' not found'
        matches = re.findall(sty_pattern, error_message)
        missing_packages.extend(matches)

        # Pattern for missing package errors
        pkg_pattern = r'package\s+([^\s]+)\s+not found'
        matches = re.findall(pkg_pattern, error_message, re.IGNORECASE)
        missing_packages.extend(matches)

        # Pattern for LaTeX Error: Missing package
        missing_pattern = r'! LaTeX Error: Missing\s+([^\s]+)\s+package'
        matches = re.findall(missing_pattern, error_message, re.IGNORECASE)
        missing_packages.extend(matches)

        return list(set(missing_packages))  # Remove duplicates

    def detect_latex_distribution(self) -> str:
        """Detect which LaTeX distribution is installed"""
        # Check for TeX Live
        if shutil.which('tlmgr'):
            try:
                result = subprocess.run(['tlmgr', '--version'],
                                      capture_output=True, text=True, timeout=5)
                if 'TeX Live' in result.stdout:
                    return 'texlive'
            except:
                pass

        # Check for MiKTeX
        if sys.platform == 'win32':
            miktex_paths = [
                r'C:\Program Files\MiKTeX\miktex\bin\x64\miktex-console.exe',
                r'C:\Program Files\MiKTeX\miktex\bin\x64\mpm.exe'
            ]
            for path in miktex_paths:
                if os.path.exists(path):
                    return 'miktex'
        else:
            if shutil.which('miktex'):
                return 'miktex'

        # Check for MacTeX (uses tlmgr)
        if sys.platform == 'darwin':
            if shutil.which('tlmgr'):
                return 'texlive'

        return None

    def install_texlive_package(self, package: str) -> bool:
        """Install a package using TeX Live's tlmgr"""
        try:
            # First, update package database
            self.write("    Updating package database...\n", "cyan")
            subprocess.run(['tlmgr', 'update', '--list'],
                          capture_output=True, timeout=30, check=False)

            # Install the package
            self.write(f"    Installing {package}...\n", "cyan")
            result = subprocess.run(['tlmgr', 'install', '--reinstall', package],
                                   capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                return True
            else:
                # Try with sudo if needed
                if 'permission' in result.stderr.lower() or 'cannot' in result.stderr.lower():
                    self.write("    Need permissions, trying with sudo...\n", "yellow")
                    result = subprocess.run(['sudo', 'tlmgr', 'install', package],
                                           capture_output=True, text=True, timeout=120)
                    return result.returncode == 0
                return False

        except subprocess.TimeoutExpired:
            self.write("    ✗ Installation timed out\n", "red")
            return False
        except Exception as e:
            self.write(f"    ✗ Error: {str(e)}\n", "red")
            return False

    def install_miktex_package(self, package: str) -> bool:
        """Install a package using MiKTeX's package manager"""
        try:
            if sys.platform == 'win32':
                # Use MiKTeX Console command line
                miktex_console = r'C:\Program Files\MiKTeX\miktex\bin\x64\miktex-console.exe'
                if os.path.exists(miktex_console):
                    result = subprocess.run(
                        [miktex_console, 'install', package],
                        capture_output=True, text=True, timeout=120
                    )
                    return result.returncode == 0

                # Alternative: Use mpm (MiKTeX Package Manager)
                mpm = r'C:\Program Files\MiKTeX\miktex\bin\x64\mpm.exe'
                if os.path.exists(mpm):
                    result = subprocess.run(
                        [mpm, '--install', package],
                        capture_output=True, text=True, timeout=120
                    )
                    return result.returncode == 0
            else:
                # Linux/macOS MiKTeX
                if shutil.which('miktex'):
                    result = subprocess.run(
                        ['miktex', 'packages', 'install', package],
                        capture_output=True, text=True, timeout=120
                    )
                    return result.returncode == 0

            return False

        except subprocess.TimeoutExpired:
            self.write("    ✗ Installation timed out\n", "red")
            return False
        except Exception as e:
            self.write(f"    ✗ Error: {str(e)}\n", "red")
            return False

    def add_color_info_to_output(self, tex_content):
        """Add color information and XOR rules to TeX output"""

        # Color information to add
        color_info = """
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %% COLOR DEFINITIONS FOR TIKZ FIGURES
    %% XOR Rule: Automatic text color selection based on background
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    \\usepackage{xcolor}  % Required for color support

    %% Predefined color palette with optimal text colors
    \\definecolor{airis4d_blue}{RGB}{41,128,185}    % Dark → Use text=white
    \\definecolor{airis4d_green}{RGB}{39,174,96}    % Light → Use text=black
    \\definecolor{airis4d_orange}{RGB}{243,156,18}  % Light → Use text=black
    \\definecolor{airis4d_red}{RGB}{231,76,60}      % Dark → Use text=white
    \\definecolor{airis4d_purple}{RGB}{155,89,182}  % Dark → Use text=white
    \\definecolor{airis4d_teal}{RGB}{26,188,156}    % Dark → Use text=white
    \\definecolor{airis4d_gray}{RGB}{149,165,166}   % Light → Use text=black

    %% Additional utility colors
    \\definecolor{airis4d_lightblue}{RGB}{173,216,230}  % Light → text=black
    \\definecolor{airis4d_darkblue}{RGB}{0,0,139}       % Dark → text=white
    \\definecolor{airis4d_lightgreen}{RGB}{144,238,144} % Light → text=black
    \\definecolor{airis4d_darkgreen}{RGB}{0,100,0}      % Dark → text=white

    %% XOR TEXT COLOR RULE
    %%
    %% For TikZ figures with colored backgrounds:
    %% 1. Calculate background luminance: L = 0.2126*R + 0.7152*G + 0.0722*B
    %% 2. If L > 0.179: Use text=black (light backgrounds)
    %% 3. If L <= 0.179: Use text=white (dark backgrounds)
    %%
    %% Example usage in TikZ:
    %% \\node[fill=airis4d_blue, text=white, minimum width=3cm] {White text on blue};
    %% \\node[fill=airis4d_orange, text=black, minimum width=3cm] {Black text on orange};
    %%
    %% For custom colors, use the get_xor_text_color() function to determine
    %% the optimal text color for any background.

    %% Color helper macros
    \\newcommand{\\airisblue}[1]{\\textcolor{airis4d_blue}{#1}}
    \\newcommand{\\airisgreen}[1]{\\textcolor{airis4d_green}{#1}}
    \\newcommand{\\airisorange}[1]{\\textcolor{airis4d_orange}{#1}}
    \\newcommand{\\airisred}[1]{\\textcolor{airis4d_red}{#1}}
    \\newcommand{\\airispurple}[1]{\\textcolor{airis4d_purple}{#1}}

    %% Color box environments
    \\newenvironment{airisbluebox}{%
        \\begin{tcolorbox}[colback=airis4d_blue!10,colframe=airis4d_blue,title={\\airisblue{Information}}]
    }{\\end{tcolorbox}}

    \\newenvironment{airisgreenbox}{%
        \\begin{tcolorbox}[colback=airis4d_green!10,colframe=airis4d_green,title={\\airisgreen{Note}}]
    }{\\end{tcolorbox}}

    \\newenvironment{airisredbox}{%
        \\begin{tcolorbox}[colback=airis4d_red!10,colframe=airis4d_red,title={\\airisred{Warning}}]
    }{\\end{tcolorbox}}

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    """

        # Insert color info after documentclass but before begin{document}
        if "\\documentclass" in tex_content:
            # Find the position after documentclass and any packages
            docclass_end = tex_content.find("\\begin{document}")

            if docclass_end != -1:
                # Insert color info right before begin{document}
                new_content = tex_content[:docclass_end] + color_info + tex_content[docclass_end:]
                return new_content

        # Fallback: prepend if we can't find the right position
        return color_info + tex_content

    def generate_color_report(self, tex_file):
        """Generate a report of color usage in the document"""
        try:
            with open(tex_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Count color occurrences
            colors = {
                'airis4d_blue': content.count('airis4d_blue'),
                'airis4d_green': content.count('airis4d_green'),
                'airis4d_orange': content.count('airis4d_orange'),
                'airis4d_red': content.count('airis4d_red'),
                'airis4d_purple': content.count('airis4d_purple'),
                'airis4d_teal': content.count('airis4d_teal'),
                'airis4d_gray': content.count('airis4d_gray'),
            }

            total_colors = sum(colors.values())

            if total_colors > 0:
                self.write("\n📊 Color Usage Report:\n", "cyan")
                for color, count in colors.items():
                    if count > 0:
                        # Determine recommended text color
                        text_color = get_xor_text_color(color)
                        self.write(f"  • {color}: {count} uses → text={text_color}\n", "cyan")

                self.write(f"  Total color references: {total_colors}\n", "cyan")

        except Exception as e:
            self.write(f"⚠ Could not generate color report: {str(e)}\n", "yellow")

    def view_color_definitions(self, tex_file):
        """Open a window to view color definitions"""
        try:
            with open(tex_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract color definitions section
            import re
            color_section_match = re.search(r'%%%% COLOR DEFINITIONS FOR TIKZ FIGURES(.*?)(?=%%%%|$)',
                                           content, re.DOTALL)

            if color_section_match:
                color_text = color_section_match.group(1).strip()

                # Create a dialog to show color definitions
                dialog = ctk.CTkToplevel(self)
                dialog.title("Color Definitions in TeX File")
                dialog.geometry("700x500")

                # Center dialog
                dialog.transient(self)

                # Create text widget with syntax highlighting
                text_widget = ctk.CTkTextbox(dialog, font=("Courier", 10))
                text_widget.pack(fill="both", expand=True, padx=10, pady=10)

                # Insert color definitions
                text_widget.insert('1.0', color_text)

                # Add copy button
                button_frame = ctk.CTkFrame(dialog)
                button_frame.pack(fill="x", padx=10, pady=10)

                ctk.CTkButton(
                    button_frame,
                    text="Copy to Clipboard",
                    command=lambda: self.copy_text_to_clipboard(color_text)
                ).pack(side="left", padx=5)

                ctk.CTkButton(
                    button_frame,
                    text="Close",
                    command=dialog.destroy
                ).pack(side="right", padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"Could not view color definitions: {str(e)}")

    def copy_text_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Color definitions copied to clipboard")

    def check_latex_log(self, log_file: str) -> None:
        """Check LaTeX log file for warnings and errors"""
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()

            # Check for common issues
            warnings = []
            errors = []

            warning_patterns = [
                r'Warning: ([^\n]+)',
                r'LaTeX Warning: ([^\n]+)',
                r'Package [^\n]+ Warning: ([^\n]+)'
            ]

            error_patterns = [
                r'! ([^\n]+)',
                r'Error: ([^\n]+)',
                r'! LaTeX Error: ([^\n]+)'
            ]

            for pattern in warning_patterns:
                for match in re.finditer(pattern, log_content):
                    warnings.append(match.group(1))

            for pattern in error_patterns:
                for match in re.finditer(pattern, log_content):
                    errors.append(match.group(1))

            if warnings or errors:
                self.write("\nCompilation Report:\n", "yellow")

                if errors:
                    self.write("\nErrors:\n", "red")
                    for error in errors:
                        self.write(f"• {error}\n", "red")

                if warnings:
                    self.write("\nWarnings:\n", "yellow")
                    for warning in warnings:
                        self.write(f"• {warning}\n", "yellow")

        except Exception as e:
            self.write(f"\nError reading log file: {str(e)}\n", "red")

    def write(self, text: str, color: str = "white") -> None:
        """Write text to terminal with color support"""
        try:
            if hasattr(self, 'terminal'):
                self.terminal.write(text, color)
        except Exception as e:
            print(f"Error writing to terminal: {str(e)}", file=sys.__stdout__)

    def run_pdflatex(self, tex_file: str, timeout: int = 60) -> dict:
        """
        Run pdflatex with interactive error editor that pinpoints exact errors.
        After fixing, saves the file, reloads it, regenerates TeX, and recompiles.
        """
        result = {
            'success': False,
            'errors': [],
            'warnings': [],
            'pdf_path': None,
            'fatal_error': False,
            'aborted': False
        }

        original_dir = os.getcwd()
        max_attempts = 5
        attempt = 0
        last_error_key = None

        try:
            tex_dir = os.path.dirname(tex_file) or '.'
            os.chdir(tex_dir)

            # Make sure tex_file is absolute path
            tex_file_abs = os.path.abspath(tex_file)
            txt_file_abs = tex_file_abs.replace('.tex', '.txt')

            while attempt < max_attempts and not result['aborted']:
                attempt += 1

                self.write("\n" + "="*60 + "\n", "cyan")
                self.write(f"RUNNING PDFLATEX (Attempt {attempt})\n", "cyan")
                self.write(f"TeX File: {tex_file_abs}\n", "cyan")
                self.write(f"TXT File: {txt_file_abs}\n", "cyan")
                self.write("="*60 + "\n\n", "cyan")

                # First, ensure the tex file exists (generate from txt if needed)
                if not os.path.exists(tex_file_abs) and os.path.exists(txt_file_abs):
                    self.write("Regenerating TeX file from TXT...\n", "yellow")
                    try:
                        from BeamerSlideGenerator import process_input_file
                        process_input_file(txt_file_abs, tex_file_abs)
                        self.write("✓ TeX file regenerated\n", "green")
                    except Exception as e:
                        self.write(f"✗ Error regenerating TeX: {e}\n", "red")

                # Run pdflatex
                cmd = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
                       '-file-line-error', tex_file_abs]

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    errors='replace'
                )

                output_lines = []
                error_found = False
                error_line_num = None
                error_message = ""
                error_context = []

                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break

                    if line:
                        output_lines.append(line.rstrip())

                        if line.startswith('!'):
                            self.write(line, "red")
                            error_found = True
                            # Try to extract line number from the error line
                            line_match = re.search(r'l\.(\d+)', line)
                            if line_match:
                                error_line_num = int(line_match.group(1))
                        elif 'Warning' in line:
                            result['warnings'].append(line)
                        elif not error_found:
                            if not any(ignore in line for ignore in ['Overfull', 'Underfull', 'pdfTeX warning']):
                                self.write(line, "white")

                # Check if compilation was successful
                pdf_file = tex_file_abs.replace('.tex', '.pdf')
                if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
                    log_file = tex_file_abs.replace('.tex', '.log')
                    if os.path.exists(log_file):
                        with open(log_file, 'r') as f:
                            log_content = f.read()
                            if 'Fatal error' not in log_content:
                                result['success'] = True
                                result['pdf_path'] = pdf_file
                                size = os.path.getsize(pdf_file)
                                self.write(f"\n✓ PDF generated: {os.path.basename(pdf_file)} ({self.format_file_size(size)})\n", "green")
                                return result
                    else:
                        result['success'] = True
                        result['pdf_path'] = pdf_file
                        size = os.path.getsize(pdf_file)
                        self.write(f"\n✓ PDF generated: {os.path.basename(pdf_file)} ({self.format_file_size(size)})\n", "green")
                        return result

                # If no error detected but PDF not created, check log file
                if not error_found:
                    log_file = tex_file_abs.replace('.tex', '.log')
                    if os.path.exists(log_file):
                        exact_error_line, error_message, error_context = self.parse_latex_log(log_file)
                        if exact_error_line:
                            error_line_num = exact_error_line
                            error_found = True
                            self.write(f"\n⚠ Found error in log at line {error_line_num}: {error_message}\n", "red")
                        else:
                            self.write("\n✗ Compilation failed but no specific error found.\n", "red")
                            self.write("Check the log file for details.\n", "yellow")
                            result['fatal_error'] = True
                            return result

                if not error_found:
                    self.write("\n✗ Compilation failed with unknown error.\n", "red")
                    result['fatal_error'] = True
                    return result

                # Check for repeated error
                error_key = f"{error_message[:50]}_{error_line_num}"
                if last_error_key == error_key:
                    self.write(f"\n⚠ Same error persists after fix attempt.\n", "red")
                    self.write(f"  Error: {error_message[:200]}\n", "yellow")
                    if error_line_num:
                        self.write(f"  Line: {error_line_num}\n", "yellow")

                    response = messagebox.askyesno("Error Persists",
                                                 f"The same error persists.\n\n"
                                                 f"Error: {error_message[:200]}\n"
                                                 f"Line: {error_line_num if error_line_num else 'Unknown'}\n\n"
                                                 f"Do you want to open the editor again?")
                    if not response:
                        result['fatal_error'] = True
                        return result

                last_error_key = error_key

                # Get the exact line content for context from the TXT file
                line_content = ""
                if error_line_num:
                    try:
                        # Try to get the corresponding line from TXT file
                        if os.path.exists(txt_file_abs):
                            with open(txt_file_abs, 'r', encoding='utf-8', errors='ignore') as f:
                                txt_lines = f.readlines()
                                # Map TeX line number to approximate TXT line number
                                # Since structures are different, we'll show context from both
                                if 1 <= error_line_num <= len(txt_lines):
                                    line_content = txt_lines[error_line_num - 1].strip()
                                    self.write(f"Error line content (TXT): {line_content}\n", "yellow")
                                else:
                                    self.write(f"Note: Line {error_line_num} may correspond to different location in TXT\n", "yellow")
                        else:
                            self.write(f"Warning: TXT file not found: {txt_file_abs}\n", "yellow")
                    except Exception as e:
                        self.write(f"Could not read line {error_line_num}: {e}\n", "yellow")

                # Launch error editor - EDIT THE TXT FILE DIRECTLY
                self.write("\n" + "="*60 + "\n", "yellow")
                self.write("LAUNCHING ERROR EDITOR\n", "yellow")
                self.write("="*60 + "\n", "yellow")
                self.write(f"Error at line {error_line_num if error_line_num else 'unknown'} (in TeX)\n", "white")
                self.write("The error editor will open the TXT file. Fix the issue, save, and close.\n", "white")
                self.write("Options: Fix & Recompile | Skip Error | Abort\n\n", "white")

                # Get the parent window safely
                parent_window = None
                if hasattr(self, 'root') and self.root:
                    parent_window = self.root
                elif hasattr(self, 'master') and self.master:
                    parent_window = self.master
                elif hasattr(self, 'winfo_toplevel'):
                    parent_window = self
                else:
                    parent_window = tk.Tk()
                    parent_window.withdraw()

                # Create editor with TXT file (NOT the TeX file)
                editor = LaTeXErrorEditor(
                    parent_window,
                    txt_file_abs,  # Pass the TXT file path
                    error_line_num or 1,
                    error_message,
                    '\n'.join(error_context),
                    '\n'.join(output_lines[-100:]),
                    exact_line_content=line_content,
                    is_txt_file=True  # This tells the editor it's editing a TXT file
                )

                # Wait for editor to close
                try:
                    if hasattr(parent_window, 'wait_window'):
                        parent_window.wait_window(editor)
                    else:
                        editor.wait_window()
                except:
                    pass

                # Handle editor result
                if editor.result == 'fixed':
                    self.write("\n✓ User fixed the TXT file.\n", "green")

                    # CRITICAL: RELOAD THE TXT FILE INTO THE IDE
                    self.write("Reloading file into IDE...\n", "cyan")
                    try:
                        # Save current state first
                        self.save_current_slide()

                        # Reload the file - this will update all internal data structures
                        self.load_file(txt_file_abs)

                        self.write("✓ File reloaded successfully\n", "green")

                        # Regenerate TeX from the updated TXT file
                        self.write("Regenerating TeX file...\n", "cyan")
                        from BeamerSlideGenerator import process_input_file
                        process_input_file(txt_file_abs, tex_file_abs)
                        self.write("✓ TeX file regenerated from updated TXT\n", "green")

                    except Exception as e:
                        self.write(f"✗ Error reloading/regenerating: {e}\n", "red")
                        import traceback
                        traceback.print_exc()
                        result['fatal_error'] = True
                        return result

                    continue  # Recompile with the updated files

                elif editor.result == 'skip':
                    self.write("\n⚠ Skipping error. TeX will be regenerated...\n", "yellow")
                    # Regenerate TeX from the (possibly modified) TXT file
                    try:
                        from BeamerSlideGenerator import process_input_file
                        process_input_file(txt_file_abs, tex_file_abs)
                        self.write("✓ TeX file regenerated\n", "green")
                    except Exception as e:
                        self.write(f"✗ Error regenerating TeX: {e}\n", "red")
                    continue

                elif editor.result == 'abort':
                    self.write("\n✗ Compilation aborted by user\n", "red")
                    result['aborted'] = True
                    result['fatal_error'] = True
                    return result

            if attempt >= max_attempts:
                self.write(f"\n✗ Too many attempts ({max_attempts}). Compilation aborted.\n", "red")
                result['fatal_error'] = True

            return result

        except Exception as e:
            self.write(f"\nProcess error: {str(e)}\n", "red")
            result['errors'].append(str(e))
            result['fatal_error'] = True
            return result

        finally:
            try:
                os.chdir(original_dir)
            except:
                pass

    def find_error_line_in_log(self, tex_file: str, error_message: str) -> int:
        """
        Find the error line number by examining the LaTeX log file.
        """
        log_file = tex_file.replace('.tex', '.log')
        if not os.path.exists(log_file):
            return None

        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()

            # Look for line number markers
            line_matches = re.findall(r'l\.(\d+)', log_content)
            if line_matches:
                return int(line_matches[0])

            # Look for file:line format
            file_line_matches = re.findall(r'\./(?:[^:]+):(\d+):', log_content)
            if file_line_matches:
                return int(file_line_matches[0])

            return None

        except Exception:
            return None

    def comment_out_line_in_file(self, tex_file_path, line_num):
        """
        Automatically comment out a specific line in the tex file.
        Returns True if successful, False otherwise.
        """
        try:
            with open(tex_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if 1 <= line_num <= len(lines):
                original_line = lines[line_num - 1]
                # Check if already commented
                if not original_line.strip().startswith('%'):
                    lines[line_num - 1] = f'% {original_line.rstrip()}  % Auto-commented by error handler\n'

                    with open(tex_file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    self.write(f"  Commented: {original_line[:80].strip()}\n", "yellow")
                    return True
                else:
                    self.write(f"  Line {line_num} already commented\n", "yellow")
                    return True
            else:
                self.write(f"  Invalid line number: {line_num}\n", "red")
                return False

        except Exception as e:
            self.write(f"  Error commenting line: {e}\n", "red")
            return False

    def handle_pdf_completion(self, pdf_file: str, size_str: str) -> None:
        """Handle successful PDF generation"""
        if messagebox.askyesno("Success",
                              f"PDF generated successfully!\nSize: {size_str}\n\nWould you like to view it now?"):
            self.preview_pdf()

    def handle_compilation_error(self, error: Exception) -> None:
        """Handle compilation errors"""
        error_msg = f"Error generating PDF: {str(error)}\n"
        self.write_to_terminal(f"\n✗ {error_msg}", "red")

        # Add detailed error information to terminal
        if hasattr(error, '__traceback__'):
            self.write_to_terminal("\nDetailed error information:\n", "red")
            self.write_to_terminal(traceback.format_exc(), "red")

        messagebox.showerror("Error", f"Error generating PDF:\n{str(error)}")

#------------------------------------------------------------------------------------------------------------------
    def compile_presentation(self, mode: str = "both") -> None:
        """
        Compile presentation with specified notes mode.
        """
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first!")
            return

        try:
            # Save current state
            self.save_current_slide()
            self.save_file()

            # Get base filename
            base_filename = os.path.splitext(self.current_file)[0]
            tex_file = base_filename + '.tex'

            # Clear terminal
            self.clear_terminal()

            # Convert to TEX if needed
            if not os.path.exists(tex_file):
                self.write("Converting text to TEX...\n", "white")
                self.convert_to_tex()

            # Compile with specified mode
            self.write(f"\nCompiling presentation in {mode} mode...\n", "white")
            try:
                pdf_file = compile_with_notes_mode(tex_file, mode)

                if os.path.exists(pdf_file):
                    size = os.path.getsize(pdf_file)
                    size_str = self.format_file_size(size)

                    self.write(f"\n✓ PDF generated successfully ({size_str})\n", "green")

                    if messagebox.askyesno("Success",
                        f"PDF generated successfully in {mode} mode!\n"
                        f"Size: {size_str}\n\n"
                        "Would you like to view it now?"):
                        self.preview_pdf(pdf_file)
                else:
                    self.write("\n✗ Error: PDF file not found after compilation\n", "red")

            except Exception as e:
                self.write(f"\n✗ Error in compilation: {str(e)}\n", "red")
                messagebox.showerror("Error", f"Error compiling PDF:\n{str(e)}")

        except Exception as e:
            self.write(f"\n✗ Error: {str(e)}\n", "red")
            messagebox.showerror("Error", f"Error generating PDF:\n{str(e)}")

    def set_notes_mode(self, mode: str) -> None:
        """Set notes mode and update UI"""
        self.notes_mode.set(mode)
        self.update_notes_buttons(mode)

        # Update preview if available
        if self.current_file:
            self.compile_presentation(mode)

    def preview_pdf(self, pdf_file: str = None) -> None:
        """Preview generated PDF using system default PDF viewer"""
        if not pdf_file:
            if not self.current_file:
                messagebox.showwarning("Warning", "Please save and generate PDF first!")
                return

            # Use default PDF name
            pdf_file = os.path.splitext(self.current_file)[0] + '.pdf'

        if os.path.exists(pdf_file):
            if sys.platform.startswith('win'):
                os.startfile(pdf_file)
            elif sys.platform.startswith('darwin'):
                subprocess.run(['open', pdf_file])
            else:
                subprocess.run(['xdg-open', pdf_file])
        else:
            messagebox.showwarning("Warning", "PDF file not found. Generate it first!")

#------------------------------------------------------------------------------------------------------------------

    def new_slide(self) -> None:
        """Create new slide, preserving content if editing first slide"""
        # Check if we're editing the initial slide without saving
        if (self.current_slide_index == 0 and
            self.slides[0]['title'] == 'Presentation Title' and
            len(self.slides[0]['content']) == 1 and
            self.slides[0]['content'][0] == '- First bullet point'):

            # This is the initial template slide, save current content first
            self.save_current_slide()

        # Proceed with creating new slide
        new_slide = {
            'title': 'New Slide',
            'media': '',
            'content': [],
            'notes': []
        }

        self.slides.append(new_slide)
        self.current_slide_index = len(self.slides) - 1
        self.update_slide_list()
        self.load_slide(self.current_slide_index)

        # Focus title entry for immediate editing
        self.title_entry.focus_set()
        self.title_entry.select_range(0, 'end')


    def move_slide(self, direction: int) -> None:
        """Move current slide up or down"""
        if not self.slides or self.current_slide_index < 0:
            return

        new_index = self.current_slide_index + direction
        if 0 <= new_index < len(self.slides):
            self.save_current_slide()
            self.slides[self.current_slide_index], self.slides[new_index] = \
                self.slides[new_index], self.slides[self.current_slide_index]
            self.current_slide_index = new_index
            self.update_slide_list()
            self.load_slide(self.current_slide_index)



    def on_slide_select(self, event) -> None:
        """Handle slide selection from list"""
        index = self.slide_list.index("@%d,%d" % (event.x, event.y)).split('.')[0]
        index = int(index)
        if 0 <= index < len(self.slides):
            self.save_current_slide()
            self.current_slide_index = index
            self.load_slide(index)
            self.update_slide_list()

    def save_current_slide(self):
        r"""Save current slide data while preserving hidden status and \None handling"""
        if not hasattr(self, 'slides') or not self.slides:
            self.slides = []
            self.current_slide_index = -1
            return

        if self.current_slide_index < 0:
            title = self.title_entry.get().strip()
            media = self.media_entry.get().strip()

            # CRITICAL FIX: Handle \None properly when saving new slide
            media_masked = False
            if media.startswith('%'):
                media_masked = True
                media = media.lstrip('%').lstrip()

            # If media is "\None" or empty, store as empty string
            if media == "\\None" or not media:
                media = ""
                # Preserve masking state even for empty media

            # Get content with hidden status tracking
            content_with_hidden = []
            hidden_content_indices = []
            content_text = self.content_editor.get('1.0', 'end-1c')
            content_lines = content_text.split('\n')

            for i, line in enumerate(content_lines):
                line = line.rstrip()
                if not line:
                    continue

                # Check if line is hidden (starts with %)
                # Use strip() to check for % at beginning after whitespace
                stripped = line.lstrip()
                is_hidden = stripped.startswith('%')

                # Remove the % prefix and any following spaces
                if is_hidden:
                    # Remove the first % and any spaces after it
                    clean_line = re.sub(r'^\s*%\s*', '', line)
                else:
                    clean_line = line

                if clean_line:  # Only add non-empty lines
                    content_with_hidden.append(clean_line)
                    if is_hidden:
                        hidden_content_indices.append(len(content_with_hidden) - 1)

            # Get notes with hidden status tracking
            notes_with_hidden = []
            hidden_note_indices = []
            notes_text = self.notes_editor.get('1.0', 'end-1c')
            notes_lines = notes_text.split('\n')

            for i, line in enumerate(notes_lines):
                line = line.rstrip()
                if not line:
                    continue

                stripped = line.lstrip()
                is_hidden = stripped.startswith('%')

                if is_hidden:
                    clean_line = re.sub(r'^\s*%\s*', '', line)
                else:
                    clean_line = line

                if clean_line:
                    notes_with_hidden.append(clean_line)
                    if is_hidden:
                        hidden_note_indices.append(len(notes_with_hidden) - 1)

            if title or media or content_with_hidden or notes_with_hidden:
                new_slide = {
                    'title': title or 'New Slide',
                    'media': media,
                    'content': content_with_hidden,
                    'notes': notes_with_hidden,
                    '_hidden_content_indices': hidden_content_indices,
                    '_hidden_note_indices': hidden_note_indices,
                    '_media_masked': media_masked,
                    '_fully_masked': False
                }
                self.slides.append(new_slide)
                self.current_slide_index = len(self.slides) - 1
                self.update_slide_list()
            return

        # Normal slide save for existing slides
        title = self.title_entry.get().strip()
        media = self.media_entry.get().strip()

        # CRITICAL FIX: Handle \None properly when saving existing slide
        media_masked = False
        if media.startswith('%'):
            media_masked = True
            media = media.lstrip('%').lstrip()

        # If media is "\None" or empty, store as empty string
        if media == "\\None" or not media:
            media = ""
            # Preserve masking state even for empty media

        # Get content with hidden status tracking
        content_with_hidden = []
        hidden_content_indices = []
        content_text = self.content_editor.get('1.0', 'end-1c')
        content_lines = content_text.split('\n')

        for i, line in enumerate(content_lines):
            line = line.rstrip()
            if not line:
                continue

            stripped = line.lstrip()
            is_hidden = stripped.startswith('%')

            if is_hidden:
                clean_line = re.sub(r'^\s*%\s*', '', line)
            else:
                clean_line = line

            if clean_line:
                content_with_hidden.append(clean_line)
                if is_hidden:
                    hidden_content_indices.append(len(content_with_hidden) - 1)

        # Get notes with hidden status tracking
        notes_with_hidden = []
        hidden_note_indices = []
        notes_text = self.notes_editor.get('1.0', 'end-1c')
        notes_lines = notes_text.split('\n')

        for i, line in enumerate(notes_lines):
            line = line.rstrip()
            if not line:
                continue

            stripped = line.lstrip()
            is_hidden = stripped.startswith('%')

            if is_hidden:
                clean_line = re.sub(r'^\s*%\s*', '', line)
            else:
                clean_line = line

            if clean_line:
                notes_with_hidden.append(clean_line)
                if is_hidden:
                    hidden_note_indices.append(len(notes_with_hidden) - 1)

        # Update the slide - preserve hidden status
        if 0 <= self.current_slide_index < len(self.slides):
            self.slides[self.current_slide_index] = {
                'title': title,
                'media': media,
                'content': content_with_hidden,
                'notes': notes_with_hidden,
                '_hidden_content_indices': hidden_content_indices,
                '_hidden_note_indices': hidden_note_indices,
                '_media_masked': media_masked,
                '_fully_masked': self.slides[self.current_slide_index].get('_fully_masked', False)
            }

            # Log the save for debugging
            logger.info(f"Saved slide {self.current_slide_index + 1}: title='{title[:50]}', "
                       f"media='{media[:30] if media else 'None'}', "
                       f"media_masked={media_masked}, content_lines={len(content_with_hidden)}, "
                       f"notes_lines={len(notes_with_hidden)}")

    def mask_line_in_editor(self, event=None):
        """Mask/unmask the current line in the focused editor (Ctrl+Delete in editors)"""
        focused_widget = self.focus_get()

        editor = None
        editor_name = ""
        is_content = False
        is_notes = False

        if focused_widget == self.content_editor._textbox:
            editor = self.content_editor._textbox
            editor_name = "content"
            is_content = True
            # Save state before change
            self.last_content_state = self.content_editor.get('1.0', 'end-1c')
            if self.last_content_state:
                self.content_undo_stack.append(self.last_content_state)
        elif focused_widget == self.notes_editor._textbox:
            editor = self.notes_editor._textbox
            editor_name = "notes"
            is_notes = True
            # Save state before change
            self.last_notes_state = self.notes_editor.get('1.0', 'end-1c')
            if self.last_notes_state:
                self.notes_undo_stack.append(self.last_notes_state)
        else:
            self.write("Click in content or notes editor first to mask lines\n", "yellow")
            return "break"

        try:
            # Get current cursor position and line
            current_pos = editor.index("insert")
            line_num = int(current_pos.split('.')[0])
            line_start = editor.index(f"{line_num}.0")
            line_end = editor.index(f"{line_num}.end")

            # Get the line content
            line_content = editor.get(line_start, line_end)

            if not line_content.strip():
                self.write("Cannot mask empty line\n", "yellow")
                return "break"

            # Check if line is already masked
            is_masked = line_content.lstrip().startswith('%')

            if is_masked:
                # Unmask: remove the % prefix
                clean_line = re.sub(r'^\s*%\s*', '', line_content)
                editor.delete(line_start, line_end)
                editor.insert(line_start, clean_line)
                self.write(f"✓ Unmasked line {line_num} in {editor_name} editor\n", "green")

                # Update the hidden indices for this slide
                if 0 <= self.current_slide_index < len(self.slides):
                    slide = self.slides[self.current_slide_index]
                    if is_content:
                        content_line_idx = line_num - 1
                        if content_line_idx in slide.get('_hidden_content_indices', []):
                            slide['_hidden_content_indices'].remove(content_line_idx)
                            slide['_hidden_content_indices'].sort()
                    elif is_notes:
                        note_line_idx = line_num - 1
                        if note_line_idx in slide.get('_hidden_note_indices', []):
                            slide['_hidden_note_indices'].remove(note_line_idx)
                            slide['_hidden_note_indices'].sort()
            else:
                # Mask: add % at beginning
                indent_match = re.match(r'^(\s*)', line_content)
                indent = indent_match.group(1) if indent_match else ""
                rest = line_content[len(indent):]
                masked_line = f"{indent}% {rest}"
                editor.delete(line_start, line_end)
                editor.insert(line_start, masked_line)
                self.write(f"✓ Masked line {line_num} in {editor_name} editor\n", "yellow")

                # Update the hidden indices for this slide
                if 0 <= self.current_slide_index < len(self.slides):
                    slide = self.slides[self.current_slide_index]
                    if is_content:
                        content_line_idx = line_num - 1
                        if '_hidden_content_indices' not in slide:
                            slide['_hidden_content_indices'] = []
                        if content_line_idx not in slide['_hidden_content_indices']:
                            slide['_hidden_content_indices'].append(content_line_idx)
                            slide['_hidden_content_indices'].sort()
                    elif is_notes:
                        note_line_idx = line_num - 1
                        if '_hidden_note_indices' not in slide:
                            slide['_hidden_note_indices'] = []
                        if note_line_idx not in slide['_hidden_note_indices']:
                            slide['_hidden_note_indices'].append(note_line_idx)
                            slide['_hidden_note_indices'].sort()

            # Clear redo stacks after new action
            if is_content:
                self.content_redo_stack.clear()
            else:
                self.notes_redo_stack.clear()

            # FIX: Move to the next line WITHOUT skipping
            # Get the next line number
            next_line_num = line_num + 1
            # Check if next line exists
            next_line_end = editor.index(f"{next_line_num}.end")
            if next_line_end and next_line_end != editor.index("end"):
                # Move cursor to the beginning of the next line
                editor.mark_set("insert", f"{next_line_num}.0")
            else:
                # Stay at current line if it's the last line
                editor.mark_set("insert", f"{line_num}.0")

            # Update syntax highlighting
            if hasattr(self, 'syntax_highlighter') and self.syntax_highlighter.active:
                self.syntax_highlighter.highlight()

            # Save the changes
            self.save_current_slide()

        except Exception as e:
            self.write(f"Error masking line: {str(e)}\n", "red")
            import traceback
            traceback.print_exc()

        return "break"

    def clear_editor(self) -> None:
        """Clear editor fields"""
        self.title_entry.delete(0, 'end')
        self.media_entry.delete(0, 'end')
        self.content_editor.delete('1.0', 'end')

    # Media Handling
    def browse_media(self) -> None:
        """Browse media files with thumbnail preview"""
        def on_file_selected(media_path):
            self.media_entry.delete(0, 'end')
            self.media_entry.insert(0, media_path)

        browser = FileThumbnailBrowser(self, callback=on_file_selected)
        browser.transient(self)
        browser.grab_set()
        self.wait_window(browser)

    def youtube_dialog(self) -> None:
        """Handle YouTube video insertion"""
        dialog = ctk.CTkInputDialog(
            text="Enter YouTube URL:",
            title="Add YouTube Video"
        )
        url = dialog.get_input()
        if url:
            if 'youtube.com' in url or 'youtu.be' in url:
                self.media_entry.delete(0, 'end')
                self.media_entry.insert(0, f"\\play {url}")
            else:
                messagebox.showwarning("Invalid URL", "Please enter a valid YouTube URL")

    def search_images(self) -> None:
        """Open image search for current slide"""
        query = construct_search_query(
            self.title_entry.get(),
            self.content_editor.get("1.0", "end").split('\n')
        )
        open_google_image_search(query)

    def generate_tex_content(self) -> str:
        """Generate complete tex file content with proper notes handling"""
        # Get base content
        if hasattr(self, 'custom_preamble'):
            content = self.custom_preamble
        else:
            content = get_beamer_preamble(
                self.presentation_info['title'],
                self.presentation_info['subtitle'],
                self.presentation_info['author'],
                self.presentation_info['institution'],
                self.presentation_info['short_institute'],
                self.presentation_info['date']
            )

        # Modify preamble for notes configuration
        content = self.modify_preamble_for_notes(content)
        print(content)
        # Add slides with appropriate notes handling
        for slide in self.slides:
            content += f"\\begin{frame}\n"
            content += f"\\frametitle{{{slide['title']}}}\n"

            if slide['media']:
                content += f"{slide['media']}\n"

            for item in slide['content']:
                if item.strip():
                    content += f"{item}\n"

            content += "\\end{frame}\n"

            # Add notes if not in slides_only mode
            if self.notes_mode.get() != "slides_only" and 'notes' in slide and slide['notes']:
                content += "\\note{\n\\begin{itemize}\n"
                for note in slide['notes']:
                    if note.strip():
                        note = note.lstrip('•- ').strip()
                        content += f"\\item {note}\n"
                content += "\\end{itemize}\n}\n"
            note=""
            content += "\n"

        content += "\\end{document}\n"
        return content

    def modify_preamble_for_notes(self, tex_content: str) -> str:
        """Modify the preamble based on current notes mode"""
        mode = self.notes_mode.get()
        print(mode)
        # Define the notes configuration based on mode
        notes_configs = {
            "slides": "\\setbeameroption{hide notes}",
            "notes": "\\setbeameroption{show only notes}",
            "both": "\\setbeameroption{show notes on second screen=right}"
        }

        # First, remove any existing notes configurations
        tex_content = re.sub(r'%.*\\setbeameroption{[^}]*}.*\n', '', tex_content)
        tex_content = re.sub(r'\\setbeameroption{[^}]*}', '', tex_content)

        # Ensure pgfpages package is present
        if "\\usepackage{pgfpages}" not in tex_content:
            package_line = "\\usepackage{pgfpages}\n"
        else:
            package_line = ""

        # Get the appropriate notes configuration
        notes_config = notes_configs[mode]

        # Add the configuration just before \begin{document}
        doc_pos = tex_content.find("\\begin{document}")
        if doc_pos != -1:
            insert_text = f"{package_line}% Notes configuration\n{notes_config}\n\\setbeamertemplate{{note page}}{{\\pagecolor{{yellow!5}}\\insertnote}}\n\n"
            tex_content = tex_content[:doc_pos] + insert_text + tex_content[doc_pos:]

        return tex_content

    def save_file(self) -> None:
        """Save presentation preserving custom preamble and line-level masking"""

        # Declare global at the beginning
        global working_folder

        # Determine the filename to save
        filename = None

        # Case 1: We have a current_file (file was loaded or previously saved)
        if self.current_file and os.path.exists(self.current_file):
            # Ask if user wants to overwrite or save as new
            response = messagebox.askyesno(
                "Save File",
                f"File: {os.path.basename(self.current_file)}\n\n"
                "Do you want to overwrite this file?\n"
                "Click 'Yes' to overwrite, 'No' to save as a new file."
            )
            if response:
                # Overwrite existing file
                filename = self.current_file
            else:
                # Save as new file - use the current filename as base
                base_name = os.path.splitext(os.path.basename(self.current_file))[0]
                save_dir = os.path.dirname(self.current_file) or working_folder

                filename = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    initialfile=f"{base_name}.txt",
                    initialdir=save_dir,
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                )
                if not filename:
                    return
                self.current_file = filename
        else:
            # Case 2: No current_file (brand new unsaved document)
            # Use the title as default filename, but don't force it
            default_name = "presentation"

            # Only use title if it's not the default placeholder
            if hasattr(self, 'title_entry') and self.title_entry.get():
                title_text = self.title_entry.get().strip()
                if title_text and title_text != "Presentation Title":
                    # Sanitize title for filename
                    default_name = re.sub(r'[<>:"/\\|?*]', '', title_text)
                    default_name = default_name.replace(' ', '_')
                    if not default_name:
                        default_name = "presentation"

            # Use the last working directory or Documents folder
            save_dir = working_folder
            if save_dir == "~" or not os.path.exists(save_dir):
                # Try to find Documents folder
                possible_docs = [
                    Path.home() / 'Documents',
                    Path.home() / 'documents',
                    Path(os.path.expandvars('%USERPROFILE%\\Documents'))
                ]
                for doc_path in possible_docs:
                    if doc_path.exists() and doc_path.is_dir():
                        save_dir = str(doc_path)
                        break
                else:
                    save_dir = str(Path.home())

            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile=f"{default_name}.txt",
                initialdir=save_dir,
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if not filename:
                return
            self.current_file = filename

        # Update global working folder and terminal
        working_folder = os.path.dirname(filename) or '.'
        os.chdir(working_folder)
        if hasattr(self, 'terminal'):
            self.terminal.set_working_directory(working_folder)

        # Save current slide before generating content
        self.save_current_slide()

        try:
            # Get custom preamble with logo
            content = self.get_custom_preamble()

            # Track counts
            masked_count = 0
            total_hidden_lines = 0

            # Define layout directives
            layout_directives = [
                '\\begin{columns}', '\\end{columns}', '\\column',
                '\\begin{itemize}', '\\end{itemize}', '\\begin{enumerate}', '\\end{enumerate}',
                '\\begin{block}', '\\end{block}', '\\begin{alertblock}', '\\end{alertblock}',
                '\\begin{exampleblock}', '\\end{exampleblock}',
                '\\begin{figure}', '\\end{figure}', '\\begin{table}', '\\end{table}',
                '\\begin{tikzpicture}', '\\end{tikzpicture}',
                '\\ff', '\\wm', '\\pip', '\\split', '\\hl', '\\bg', '\\tb', '\\ol', '\\corner', '\\mosaic'
            ]

            # Add slides
            for idx, slide in enumerate(self.slides):
                is_fully_masked = slide.get('_fully_masked', False) or self.is_slide_masked(idx)
                hidden_content_indices = set(slide.get('_hidden_content_indices', []))
                hidden_note_indices = set(slide.get('_hidden_note_indices', []))
                media_masked = slide.get('_media_masked', False)

                if is_fully_masked:
                    masked_count += 1
                    content += "\n\n% ========== MASKED SLIDE (DELETED) ==========\n"

                content += "\n\n"

                # Handle title
                title = slide.get('title', 'Untitled')
                clean_title = re.sub(r'^\[DELETED\]\s*', '', title)

                if is_fully_masked:
                    content += f"% \\title {clean_title}\n"
                    content += "% \\begin{Content}\n"
                else:
                    content += f"\\title {clean_title}\n"
                    content += "\\begin{Content}\n"

                # Handle media
                media = slide.get('media', '')
                content_items = slide.get('content', [])

                # Write media line
                if is_fully_masked or media_masked:
                    if media:
                        content += f"% {media}\n"
                    else:
                        content += "% \\None\n"
                else:
                    if media and media != "\\None":
                        content += f"{media}\n"
                    else:
                        content += "\\None\n"

                # Write content items
                for i, item in enumerate(content_items):
                    if item and item.strip():
                        is_line_hidden = i in hidden_content_indices

                        if is_fully_masked or is_line_hidden:
                            if not item.strip().startswith('%'):
                                content += f"% {item}\n"
                                total_hidden_lines += 1
                            else:
                                content += f"{item}\n"
                        else:
                            content += f"{item}\n"

                # End Content block
                if is_fully_masked:
                    content += "% \\end{Content}\n\n"
                else:
                    content += "\\end{Content}\n\n"

                # Handle notes
                if is_fully_masked:
                    content += "% \\begin{Notes}\n"
                    if 'notes' in slide and slide['notes']:
                        for i, note in enumerate(slide['notes']):
                            if note and note.strip():
                                is_note_hidden = i in hidden_note_indices
                                if is_note_hidden:
                                    if not note.strip().startswith('%'):
                                        content += f"% {note}\n"
                                        total_hidden_lines += 1
                                    else:
                                        content += f"{note}\n"
                                else:
                                    content += f"% {note}\n"
                    content += "% \\end{Notes}\n"
                else:
                    if 'notes' in slide and slide['notes']:
                        content += "\\begin{Notes}\n"
                        for i, note in enumerate(slide['notes']):
                            if note and note.strip():
                                is_note_hidden = i in hidden_note_indices
                                if is_note_hidden:
                                    content += f"% {note}\n"
                                    total_hidden_lines += 1
                                else:
                                    content += f"{note}\n"
                        content += "\\end{Notes}\n"
                    else:
                        content += "\\begin{Notes}\n"
                        content += "\\end{Notes}\n"

            content += "\\end{document}"

            # Save to text file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

            self.write(f"✓ File saved successfully: {filename}\n", "green")

            # Show summary
            summary_parts = []
            if masked_count > 0:
                summary_parts.append(f"{masked_count} fully masked slide(s)")
            if total_hidden_lines > 0:
                summary_parts.append(f"{total_hidden_lines} hidden line(s)")

            if summary_parts:
                self.write(f"ℹ Saved with: {', '.join(summary_parts)}\n", "yellow")

            # Update recent files list
            if hasattr(self, 'session_manager') and self.session_manager:
                if filename not in self.session_data['recent_files']:
                    self.session_data['recent_files'].append(filename)
                    if len(self.session_data['recent_files']) > 10:
                        self.session_data['recent_files'].pop(0)
                    self.session_manager.save_session(self.session_data)

            return True

        except Exception as e:
            self.write(f"✗ Error saving file: {str(e)}\n", "red")
            messagebox.showerror("Error", f"Error saving file:\n{str(e)}")
            return False

    def load_file(self, filename: str) -> None:
        """Load presentation from file with full preservation of masked content"""
        try:
            logger.info(f"Loading file: {filename}")

            # CRITICAL: Set current_file BEFORE any other operations
            self.current_file = filename
            # Update working directory
            global working_folder
            working_folder = os.path.dirname(filename) or '.'
            os.chdir(working_folder)
            if hasattr(self, 'terminal'):
                self.terminal.set_working_directory(working_folder)

            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            self.slides = []
            self.current_slide_index = -1

            # Extract presentation info
            import re
            for key in self.presentation_info:
                pattern = f"\\\\{key}{{(.*?)}}"
                match = re.search(pattern, content)
                if match:
                    self.presentation_info[key] = match.group(1)

            # Split into slides by finding all title lines
            lines = content.split('\n')

            slides_raw = []
            current_slide_lines = []

            for line in lines:
                if re.match(r'^%?\s*\\title\s+', line):
                    if current_slide_lines:
                        slides_raw.append(current_slide_lines)
                    current_slide_lines = [line]
                else:
                    current_slide_lines.append(line)

            if current_slide_lines:
                slides_raw.append(current_slide_lines)

            logger.info(f"Found {len(slides_raw)} slide blocks")

            masked_slides_count = 0
            total_masked_lines = 0

            for slide_idx, slide_lines in enumerate(slides_raw):
                # Check if slide is fully masked
                non_empty = [l for l in slide_lines if l.strip()]
                is_fully_masked = False

                if non_empty:
                    first_line = non_empty[0].strip()
                    if first_line.startswith('%') and '\\title' in first_line:
                        is_fully_masked = all(l.strip().startswith('%') for l in non_empty)

                # Extract title - preserve the original line including % if masked
                title_line = None
                title_raw = None
                for line in slide_lines:
                    title_match = re.search(r'(%?\s*\\title\s+)(.+)$', line)
                    if title_match:
                        title_raw = line  # Keep the raw line with potential %
                        title_line = title_match.group(2).strip()
                        break

                if title_line is None:
                    logger.warning(f"No title found in slide block {slide_idx}")
                    continue

                title = title_line

                if is_fully_masked and not title.startswith('[DELETED]'):
                    title = f"[DELETED] {title}"
                    masked_slides_count += 1

                # Parse content and notes blocks - PRESERVE ALL LINES INCLUDING MASKED ONES
                in_content = False
                in_notes = False
                content_lines = []
                notes_lines = []
                hidden_content_indices = []
                hidden_note_indices = []
                media = ""
                media_masked = False
                found_media = False
                content_line_index = 0
                is_first_content_line = True  # Track first line of content block

                for line in slide_lines:
                    # Skip the title line itself
                    if line == title_raw:
                        continue

                    # Check for Content block boundaries
                    if re.match(r'^%?\s*\\begin{Content}\s*$', line):
                        in_content = True
                        in_notes = False
                        is_first_content_line = True  # Reset for new content block
                        continue
                    elif re.match(r'^%?\s*\\end{Content}\s*$', line):
                        in_content = False
                        continue

                    # Check for Notes block boundaries
                    if re.match(r'^%?\s*\\begin{Notes}\s*$', line):
                        in_notes = True
                        in_content = False
                        continue
                    elif re.match(r'^%?\s*\\end{Notes}\s*$', line):
                        in_notes = False
                        continue

                    # Process content lines - PRESERVE EVERY LINE including masked ones
                    if in_content:
                        # Check if this line is masked (starts with % after optional whitespace)
                        is_masked = line.lstrip().startswith('%')

                        # Clean the line for storage (remove the % prefix for masked lines)
                        if is_masked:
                            clean_line = re.sub(r'^\s*%\s*', '', line)
                        else:
                            clean_line = line

                        # Store the line (even if empty, but skip completely empty)
                        if clean_line.strip() or (is_masked and clean_line):
                            # First non-empty line is media
                            if not found_media:
                                found_media = True
                                media_value = clean_line.strip()

                                # CRITICAL FIX: Handle \None marker properly
                                if media_value == "\\None":
                                    media = ""  # Empty string for no media
                                    media_masked = is_masked
                                    logger.info(f"  Media: None (explicit \\None marker, masked={media_masked})")
                                else:
                                    media = media_value
                                    media_masked = is_masked
                                    if is_masked and media != "\\None":
                                        total_masked_lines += 1
                                    logger.info(f"  Media found: '{media}' (masked={media_masked})")

                                is_first_content_line = False
                            else:
                                # Regular content line
                                # Skip if it's an empty line that was just a marker
                                if clean_line.strip() or (is_masked and clean_line.strip()):
                                    content_lines.append(clean_line.rstrip())
                                    if is_masked:
                                        hidden_content_indices.append(content_line_index)
                                        total_masked_lines += 1
                                        logger.info(f"  Masked content line {content_line_index + 1}: '{clean_line[:50]}'")
                                    else:
                                        logger.info(f"  Visible content line {content_line_index + 1}: '{clean_line[:50]}'")
                                    content_line_index += 1

                    # Process notes lines - PRESERVE EVERY LINE including masked ones
                    if in_notes:
                        is_masked = line.lstrip().startswith('%')

                        if is_masked:
                            clean_line = re.sub(r'^\s*%\s*', '', line)
                        else:
                            clean_line = line

                        if clean_line.strip():
                            notes_lines.append(clean_line.rstrip())
                            if is_masked:
                                hidden_note_indices.append(len(notes_lines) - 1)
                                total_masked_lines += 1
                                logger.info(f"  Masked note line {len(notes_lines)}: '{clean_line[:50]}'")

                # If no media was found, set to empty string
                if not found_media:
                    media = ""
                    media_masked = False
                    logger.info(f"  No media found in slide")

                # Create slide with preserved masking
                slide = {
                    'title': title,
                    'media': media,
                    'content': content_lines,
                    'notes': notes_lines,
                    '_hidden_content_indices': hidden_content_indices,
                    '_hidden_note_indices': hidden_note_indices,
                    '_media_masked': media_masked,
                    '_fully_masked': is_fully_masked
                }

                self.slides.append(slide)
                logger.info(f"Slide {len(self.slides)}: '{title[:50]}' (media='{media[:30] if media else 'None'}', "
                           f"fully_masked={is_fully_masked}, content_lines={len(content_lines)}, "
                           f"hidden_content={len(hidden_content_indices)})")

            if self.slides:
                self.current_slide_index = 0
                self.load_slide(0)
            else:
                logger.error("No slides were loaded!")
                messagebox.showerror("Error", "No slides could be loaded from the file!")
                return

            self.update_slide_list()

            # Show loading summary
            summary_parts = [f"✓ Loaded {len(self.slides)} slides"]
            if masked_slides_count > 0:
                summary_parts.append(f"{masked_slides_count} fully masked")
            if total_masked_lines > 0:
                summary_parts.append(f"{total_masked_lines} masked lines")

            self.write(" | ".join(summary_parts) + "\n", "green")

            if masked_slides_count > 0 or total_masked_lines > 0:
                self.write("ℹ Masked content is shown with strikethrough\n", "yellow")
                self.write("  • Click on masked line + Ctrl+Delete to unmask\n", "cyan")

        except Exception as e:
            error_msg = f"Error loading file: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.write(f"✗ {error_msg}\n", "red")
            messagebox.showerror("Error", f"Error loading file:\n{str(e)}")

    def _apply_masking_to_slide(self, slide_index: int) -> None:
        """Apply masking to a slide (mark as deleted)"""
        if 0 <= slide_index < len(self.slides):
            slide = self.slides[slide_index]

            # Add marker to title
            if not slide['title'].startswith('[DELETED]'):
                slide['title'] = f"[DELETED] {slide['title']}"

            # Note: We don't modify content here because it's already loaded
            # The is_slide_masked method will check for the title marker

            # Update the slide list display
            self.update_slide_list()

    def is_slide_masked(self, slide_index: int) -> bool:
        """Check if a slide is masked (deleted)"""
        if not 0 <= slide_index < len(self.slides):
            return False

        slide = self.slides[slide_index]

        # Check title for deletion marker
        if slide.get('title', '').startswith('[DELETED]'):
            return True

        # Check if all content is commented
        content_items = slide.get('content', [])
        if content_items:
            # If all non-empty content lines start with %, it's masked
            non_empty_items = [item for item in content_items if item.strip()]
            if non_empty_items:
                all_commented = all(item.strip().startswith('%') for item in non_empty_items)
                if all_commented:
                    return True

        return False

    def show_settings_dialog(self) -> None:
        """Show presentation settings dialog with logo handling"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Presentation Settings")
        dialog.geometry("500x450")

        # Make dialog modal but wait until it's visible
        dialog.transient(self)

        # Center the dialog on parent window
        def center_dialog():
            dialog.update_idletasks()  # Make sure dialog is fully created
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            window_width = dialog.winfo_width()
            window_height = dialog.winfo_height()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            dialog.geometry(f"+{x}+{y}")

            # Set grab after dialog is visible
            dialog.after(100, lambda: dialog.grab_set())

        # Container frame for settings
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create entry fields for presentation metadata
        entries = {}
        row = 0
        for key, value in self.presentation_info.items():
            if key != 'logo':  # Handle logo separately
                label = ctk.CTkLabel(main_frame, text=key.title() + ":")
                label.grid(row=row, column=0, padx=5, pady=5, sticky="e")

                entry = ctk.CTkEntry(main_frame, width=300)
                entry.insert(0, value)
                entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
                entries[key] = entry
                row += 1

        # Add logo selection
        logo_label = ctk.CTkLabel(main_frame, text="Logo:")
        logo_label.grid(row=row, column=0, padx=5, pady=5, sticky="e")

        logo_frame = ctk.CTkFrame(main_frame)
        logo_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        logo_entry = ctk.CTkEntry(logo_frame, width=240)
        logo_entry.pack(side="left", padx=(0, 5), fill="x", expand=True)

        # Insert existing logo path if present
        if 'logo' in self.presentation_info:
            logo_path = self.presentation_info['logo']
            # Extract path from logo command if present
            if '\\includegraphics' in logo_path:
                match = re.search(r'\\includegraphics\[.*?\]{(.*?)}', logo_path)
                if match:
                    logo_entry.insert(0, match.group(1))
            else:
                logo_entry.insert(0, logo_path)

        def browse_logo():
            """Handle logo file selection"""
            filename = filedialog.askopenfilename(
                title="Select Logo Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.pdf"),
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg *.jpeg"),
                    ("PDF files", "*.pdf"),
                    ("All files", "*.*")
                ],
                parent=dialog  # Set parent for proper modal behavior
            )
            if filename:
                logo_entry.delete(0, 'end')
                logo_entry.insert(0, filename)

        ctk.CTkButton(logo_frame, text="Browse",
                      command=browse_logo).pack(side="left", padx=5)

        def save_settings():
            """Save settings including logo"""
            try:
                # Save regular metadata
                for key, entry in entries.items():
                    self.presentation_info[key] = entry.get()

                # Save logo if specified
                logo_path = logo_entry.get().strip()
                if logo_path:
                    if os.path.exists(logo_path):
                        # Save logo path with LaTeX formatting
                        self.presentation_info['logo'] = f"\\logo{{\\includegraphics[height=1cm]{{{logo_path}}}}}"
                    else:
                        messagebox.showerror("Error",
                                           f"Logo file not found:\n{logo_path}",
                                           parent=dialog)
                        return
                else:
                    # Remove logo if entry is empty
                    self.presentation_info.pop('logo', None)

                dialog.grab_release()
                dialog.destroy()

            except Exception as e:
                messagebox.showerror("Error",
                                   f"Error saving settings:\n{str(e)}",
                                   parent=dialog)

        def on_cancel():
            """Handle dialog cancellation"""
            dialog.grab_release()
            dialog.destroy()

        # Add buttons frame
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.grid(row=row + 1, column=0, columnspan=2, pady=20)

        # Add Save and Cancel buttons
        ctk.CTkButton(buttons_frame, text="Save Settings",
                      command=save_settings).pack(side="left", padx=10)

        ctk.CTkButton(buttons_frame, text="Cancel",
                      command=on_cancel).pack(side="left", padx=10)

        # Configure grid
        main_frame.columnconfigure(1, weight=1)

        # Handle dialog close button
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        # Center and show dialog
        dialog.after(10, center_dialog)

        # Lift dialog to top
        dialog.lift()

    def debug_slide_data(self):
        """Debug function to print slide data structure"""
        print("\n=== DEBUG: Current Slide Data ===")
        for idx, slide in enumerate(self.slides):
            print(f"\nSlide {idx + 1}:")
            print(f"  Title: {slide.get('title')}")
            print(f"  Media: {slide.get('media')}")
            print(f"  Media masked: {slide.get('_media_masked')}")
            print(f"  Content: {slide.get('content')}")
            print(f"  Hidden content indices: {slide.get('_hidden_content_indices')}")
            print(f"  Notes: {slide.get('notes')}")
            print(f"  Hidden note indices: {slide.get('_hidden_note_indices')}")
            print(f"  Fully masked: {slide.get('_fully_masked')}")
        print("=" * 40)

    def edit_preamble(self):
        """Open preamble editor with logo support"""
        # Get current preamble including logo
        current_preamble = self.get_custom_preamble()

        # Open preamble editor
        new_preamble = PreambleEditor.edit_preamble(self, current_preamble)

        if new_preamble is not None:
            # Store the custom preamble
            self.custom_preamble = new_preamble
            messagebox.showinfo("Success", "Preamble updated successfully!")

    def present_with_notes(self) -> None:
        """Present PDF using pympress for dual-screen display with notes"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save your file first!")
            return

        try:
            # Get absolute paths
            base_filename = os.path.splitext(self.current_file)[0]
            pdf_file = base_filename + '.pdf'
            abs_pdf_path = os.path.abspath(pdf_file)

            # Check if PDF exists and generate if needed
            if not os.path.exists(abs_pdf_path):
                self.write_to_terminal("PDF not found. Generating...")
                self.generate_pdf()

                if not os.path.exists(abs_pdf_path):
                    messagebox.showerror("Error", "Failed to generate PDF presentation.")
                    return

            # Use system pympress
            self.write_to_terminal("Launching pympress presentation viewer...")

            # Try different possible pympress locations
            pympress_paths = [
                shutil.which('pympress'),
                '/usr/local/bin/pympress',
                '/usr/bin/pympress',
                os.path.expanduser('~/.local/bin/pympress')
            ]

            launched = False
            for path in pympress_paths:
                if path and os.path.exists(path):
                    subprocess.Popen([path, abs_pdf_path])
                    launched = True
                    break

            if not launched:
                # Try using python -m pympress
                try:
                    subprocess.Popen([sys.executable, "-m", "pympress", abs_pdf_path])
                    launched = True
                except:
                    pass

            if launched:
                self.write_to_terminal("✓ Presentation launched successfully\n", "green")
                self.write_to_terminal("\nPympress Controls:\n")
                self.write_to_terminal("- Right Arrow/Space/Page Down: Next slide\n")
                self.write_to_terminal("- Left Arrow/Page Up: Previous slide\n")
                self.write_to_terminal("- Escape: Exit presentation\n")
                self.write_to_terminal("- F11: Toggle fullscreen\n")
                self.write_to_terminal("- N: Toggle notes\n")
                self.write_to_terminal("- P: Pause/unpause timer\n")
            else:
                self.write_to_terminal("✗ pympress not found. Please install it:\n", "red")
                self.write_to_terminal("  pip install pympress\n", "yellow")

        except Exception as e:
            self.write_to_terminal(f"✗ Error launching presentation: {str(e)}\n", "red")
            messagebox.showerror("Error", f"Error launching presentation:\n{str(e)}")

    def add_tikz_color_helper(self):
        """Add TikZ color helper button to toolbar"""
        # Add to existing toolbar
        if hasattr(self, 'toolbar'):
            tikz_button = ctk.CTkButton(
                self.toolbar,
                text="🎨 TikZ Colors",
                command=self.show_tikz_color_helper,
                width=100,
                fg_color="#9b59b6",
                hover_color="#8e44ad"
            )
            tikz_button.pack(side="left", padx=5)
            self.create_tooltip(tikz_button, "TikZ Color Helper with XOR text coloring")

    def show_tikz_color_helper(self):
        """Show TikZ color helper dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("TikZ Color Helper")
        dialog.geometry("600x500")

        # Center dialog
        dialog.transient(self)
        dialog.grab_set()

        # Create notebook for tabs
        notebook = ctk.CTkTabview(dialog)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Color Picker
        color_tab = notebook.add("Color Picker")
        self.create_color_picker_tab(color_tab)

        # Tab 2: Color Definitions
        definitions_tab = notebook.add("Color Definitions")
        self.create_definitions_tab(definitions_tab)

        # Tab 3: Examples
        examples_tab = notebook.add("Examples")
        self.create_examples_tab(examples_tab)

    def create_color_picker_tab(self, parent):
        """Create color picker tab"""
        # Initialize color helper
        self.tikz_color_helper = TikZColorHelper()

        # Instructions
        instructions = ctk.CTkLabel(
            parent,
            text="Select a background color. Text color will be automatically chosen using XOR rule.",
            wraplength=550,
            font=("Arial", 11)
        )
        instructions.pack(pady=10)

        # Color input frame
        input_frame = ctk.CTkFrame(parent)
        input_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(input_frame, text="Background Color:").pack(side="left", padx=5)
        self.bg_color_entry = ctk.CTkEntry(input_frame, width=150)
        self.bg_color_entry.pack(side="left", padx=5)
        self.bg_color_entry.insert(0, "airis4d_blue")

        # Preview button
        preview_btn = ctk.CTkButton(
            input_frame,
            text="Preview",
            command=self.preview_tikz_colors,
            width=80
        )
        preview_btn.pack(side="left", padx=5)

        # Pick color button
        pick_btn = ctk.CTkButton(
            input_frame,
            text="🎨 Pick Color",
            command=self.pick_tikz_color,
            width=100,
            fg_color="#3498db"
        )
        pick_btn.pack(side="left", padx=5)

        # Preview area
        self.tikz_preview_frame = ctk.CTkFrame(parent, height=150)
        self.tikz_preview_frame.pack(fill="x", padx=10, pady=10)
        self.tikz_preview_frame.pack_propagate(False)

        self.tikz_preview_label = ctk.CTkLabel(
            self.tikz_preview_frame,
            text="TikZ Color Preview",
            font=("Arial", 14),
            height=140,
            corner_radius=10
        )
        self.tikz_preview_label.pack(pady=5)

        # Generated code area
        code_frame = ctk.CTkFrame(parent)
        code_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(code_frame, text="Generated TikZ Code:").pack(anchor="w", padx=5, pady=5)

        self.tikz_code_text = ctk.CTkTextbox(code_frame, height=100)
        self.tikz_code_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Insert button
        insert_btn = ctk.CTkButton(
            parent,
            text="Insert into Content",
            command=self.insert_tikz_code,
            width=150,
            fg_color="#2ecc71"
        )
        insert_btn.pack(pady=10)

    def pick_tikz_color(self):
        """Pick a color using color picker"""
        result = ColorPickerDialog.pick_color(self)
        if result:
            self.bg_color_entry.delete(0, 'end')
            self.bg_color_entry.insert(0, result['name'])

            # Add to color helper
            self.tikz_color_helper.define_color(result['name'], result['rgb'])

            self.preview_tikz_colors()

    def preview_tikz_colors(self):
        """Preview TikZ colors"""
        bg_color = self.bg_color_entry.get().strip()

        if not bg_color:
            messagebox.showwarning("Warning", "Please enter a background color")
            return

        # Get text color
        text_color = self.tikz_color_helper.get_text_color(bg_color)

        # Update preview
        try:
            # Try to set background color in preview
            if bg_color in self.tikz_color_helper.color_definitions:
                rgb = self.tikz_color_helper.color_definitions[bg_color]
                hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            elif bg_color in self.tikz_color_helper.default_colors:
                rgb = self.tikz_color_helper.default_colors[bg_color]
                hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            else:
                # Assume it's a valid color name
                hex_color = bg_color

            self.tikz_preview_label.configure(
                text=f"Background: {bg_color}\nText Color: {text_color}",
                fg_color=hex_color,
                text_color="white" if text_color == "white" else "black"
            )

            # Generate TikZ code
            tikz_code = f"""
    % TikZ node with automatic text color
    \\definecolor{{{bg_color}}}{{RGB}}{{{rgb[0]},{rgb[1]},{rgb[2]}}}
    \\node[fill={bg_color}, text={text_color}, minimum width=3cm, minimum height=1cm] {{{text_color.upper()} text on {bg_color}}};
    """

            self.tikz_code_text.delete('1.0', 'end')
            self.tikz_code_text.insert('1.0', tikz_code.strip())

        except Exception as e:
            messagebox.showerror("Error", f"Could not preview color: {str(e)}")

    def insert_tikz_code(self):
        """Insert TikZ code into content editor"""
        code = self.tikz_code_text.get('1.0', 'end-1c')
        if code:
            self.content_editor.insert('insert', f"\n{code}\n")

    def create_definitions_tab(self, parent):
        """Create color definitions tab"""
        text = ctk.CTkTextbox(parent)
        text.pack(fill="both", expand=True, padx=10, pady=10)

        definitions = self.tikz_color_helper.generate_tikz_color_definitions()

        text.insert('1.0', "% TikZ Color Definitions (add to preamble)\n")
        text.insert('end', definitions)

        # Add copy button
        copy_btn = ctk.CTkButton(
            parent,
            text="Copy to Clipboard",
            command=lambda: self.copy_to_clipboard(definitions),
            width=150
        )
        copy_btn.pack(pady=10)

    def create_examples_tab(self, parent):
        """Create examples tab"""
        text = ctk.CTkTextbox(parent)
        text.pack(fill="both", expand=True, padx=10, pady=10)

        examples = """
    % Example 1: Basic colored node
    \\node[fill=airis4d_blue, text=white, draw=black, thick, minimum width=2cm] {White Text};

    % Example 2: Multiple nodes with different colors
    \\begin{tikzpicture}
        \\node[fill=airis4d_green, text=black, circle] at (0,0) {A};
        \\node[fill=airis4d_red, text=white, circle] at (2,0) {B};
        \\node[fill=airis4d_orange, text=black, circle] at (4,0) {C};
    \\end{tikzpicture}

    % Example 3: Using the create_colored_node helper
    % (Include the TikZColorHelper class in your document preamble)
    """

        text.insert('1.0', examples)

    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Color definitions copied to clipboard")

    def add_color_info_to_output(self, content):
        """Add color information to generated output"""
        color_info = """
    % Color Information for TikZ Figures
    % Use these color definitions for consistent theming
    % Text colors are automatically chosen using XOR rule

    % Default color palette
    \\definecolor{airis4d_blue}{RGB}{41,128,185}
    \\definecolor{airis4d_green}{RGB}{39,174,96}
    \\definecolor{airis4d_orange}{RGB}{243,156,18}
    \\definecolor{airis4d_red}{RGB}{231,76,60}
    \\definecolor{airis4d_purple}{RGB}{155,89,182}
    \\definecolor{airis4d_teal}{RGB}{26,188,156}
    \\definecolor{airis4d_gray}{RGB}{149,165,166}

    % XOR Rule for text colors:
    % - Use text=white on dark backgrounds (luminance < 0.179)
    % - Use text=black on light backgrounds (luminance > 0.179)

    % Example usage:
    % \\node[fill=airis4d_blue, text=white] {White text on blue};
    % \\node[fill=airis4d_orange, text=black] {Black text on orange};
    """

        # Insert color info after the document class
        if "\\documentclass" in content:
            parts = content.split("\\documentclass", 1)
            new_content = parts[0] + "\\documentclass" + parts[1].replace(
                "\\begin{document}",
                color_info + "\n\\begin{document}",
                1
            )
            return new_content

        return color_info + "\n" + content

    def _generate_layout_latex(self, layout_type: str, layout_params: str, content: list, title: str) -> str:
        """
        Generate LaTeX code for various layout directives.
        Supports: mosaic, split, pip, watermark, fullframe, highlight, background, topbottom, overlay, corner, table
        """
        frame_title = self.clean_frame_title_for_latex(title)

        # Check if this is a table layout (detect from params or content)
        is_table = False
        if layout_type == 'table':
            is_table = True
        elif layout_params and ('\\begin{tabular}' in layout_params or '\\hline' in layout_params):
            is_table = True
            layout_type = 'table'
        elif content and any('\\begin{tabular}' in line for line in content):
            is_table = True
            layout_type = 'table'

        # Route to appropriate layout handler
        if is_table or layout_type == 'table':
            return self._generate_table_layout(layout_params, content, frame_title)
        elif layout_type == 'mosaic':
            return self._generate_mosaic_layout(layout_params, content, frame_title)
        elif layout_type == 'split':
            return self._generate_split_layout(layout_params, content, frame_title)
        elif layout_type == 'pip':
            return self._generate_pip_layout(layout_params, content, frame_title)
        elif layout_type == 'watermark':
            return self._generate_watermark_layout(layout_params, content, frame_title)
        elif layout_type == 'fullframe':
            return self._generate_fullframe_layout(layout_params, content, frame_title)
        elif layout_type == 'highlight':
            return self._generate_highlight_layout(layout_params, content, frame_title)
        elif layout_type == 'background':
            return self._generate_background_layout(layout_params, content, frame_title)
        elif layout_type == 'topbottom':
            return self._generate_topbottom_layout(layout_params, content, frame_title)
        elif layout_type == 'overlay':
            return self._generate_overlay_layout(layout_params, content, frame_title)
        elif layout_type == 'corner':
            return self._generate_corner_layout(layout_params, content, frame_title)
        else:
            # Fallback to default layout
            return self._generate_default_layout(layout_params, content, frame_title)

    def _split_bibliography_across_frames(self, content_lines: list, frame_title: str) -> list:
        """
        Split long bibliography across multiple frames with back-references.
        PRESERVES original bibitem numbering and full content.
        Returns list of frame LaTeX strings.
        """
        import re

        frames = []
        items_per_frame = 12  # Number of references per page

        # Parse the bibliography items - PRESERVE FULL CONTENT
        bib_items = []
        in_thebibliography = False
        bib_options = "99"
        bib_header = ""
        bib_footer = ""

        # First, find the entire bibliography content as a single block
        full_bib_content = []
        for line in content_lines:
            full_bib_content.append(line)

        # Join to get the complete bibliography
        complete_bib = '\n'.join(full_bib_content)

        # Find all bibitem entries with their full content
        # Pattern matches: \bibitem{key} rest of the reference until next \bibitem or \end{thebibliography}
        bib_pattern = r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem\{|\\end\{thebibliography\})'
        matches = re.findall(bib_pattern, complete_bib, re.DOTALL)

        if not matches:
            # Fallback: try simpler pattern
            lines = complete_bib.split('\n')
            current_item = []
            in_item = False
            current_key = None

            for line in lines:
                if '\\bibitem{' in line:
                    if current_item and current_key:
                        bib_items.append((current_key, '\n'.join(current_item)))
                    # Extract key
                    key_match = re.search(r'\\bibitem\{([^}]+)\}', line)
                    if key_match:
                        current_key = key_match.group(1)
                        # Get the rest of the line after the bibitem
                        rest = line[key_match.end():]
                        current_item = [rest] if rest.strip() else []
                    else:
                        current_item = [line]
                    in_item = True
                elif in_item:
                    current_item.append(line)

            if current_item and current_key:
                bib_items.append((current_key, '\n'.join(current_item)))
        else:
            # Process matches
            for key, content in matches:
                # Clean up the content
                content = content.strip()
                bib_items.append((key, content))

        if not bib_items:
            self.write(f"  ⚠ No bibitems found in bibliography slide\n", "yellow")
            return [self._generate_bibliography_frame(content_lines, frame_title)]

        self.write(f"  ✓ Found {len(bib_items)} bibliography items\n", "green")

        # Extract the header and footer
        header_match = re.search(r'(\\begin\{thebibliography\}\{[^}]+\})', complete_bib)
        if header_match:
            bib_header = header_match.group(1)
        else:
            bib_header = "\\begin{thebibliography}{99}"

        footer_match = re.search(r'(\\end\{thebibliography\})', complete_bib)
        if footer_match:
            bib_footer = footer_match.group(1)
        else:
            bib_footer = "\\end{thebibliography}"

        # Split items across frames
        total_items = len(bib_items)
        num_frames = (total_items + items_per_frame - 1) // items_per_frame

        for frame_num in range(num_frames):
            start_idx = frame_num * items_per_frame
            end_idx = min(start_idx + items_per_frame, total_items)
            frame_items = bib_items[start_idx:end_idx]

            # Build frame content
            frame_content = []
            if num_frames > 1:
                title_with_page = f"{frame_title} (Page {frame_num + 1}/{num_frames})"
            else:
                title_with_page = frame_title

            # Clean the title for LaTeX
            clean_title = self.clean_frame_title_for_latex(title_with_page)

            frame_content.append(f"\\begin{{frame}}[allowframebreaks]{{{clean_title}}}")
            frame_content.append(f"\\frametitle{{{clean_title}}}")
            frame_content.append(bib_header)

            for key, content in frame_items:
                # Add back-references to each bibitem
                processed_item = self._add_back_references_to_bibitem_content(key, content)
                frame_content.append(processed_item)

            frame_content.append(bib_footer)
            frame_content.append("\\end{frame}")

            frames.append('\n'.join(frame_content))

        return frames

    def _add_back_references_to_bibitem_content(self, citation_key: str, content: str) -> str:
        """
        Add back-references to a bibliography item showing where it was cited.
        PRESERVES the original bibitem format.
        """
        import re

        # Find where this citation appears in the slides
        slide_numbers = []
        for idx, slide in enumerate(self.slides, 1):
            # Skip fully masked slides
            if slide.get('_fully_masked', False):
                continue

            # Check content for \cite{citation_key}
            for content_line in slide.get('content', []):
                if f'\\cite{{{citation_key}}}' in content_line or f'\\cite{{{citation_key}' in content_line:
                    if idx not in slide_numbers:
                        slide_numbers.append(idx)
                    break
            # Check notes
            for note_line in slide.get('notes', []):
                if f'\\cite{{{citation_key}}}' in note_line or f'\\cite{{{citation_key}' in note_line:
                    if idx not in slide_numbers:
                        slide_numbers.append(idx)
                    break

        # Build the complete bibitem
        if slide_numbers:
            back_refs = ', '.join([f"{num}" for num in slide_numbers])
            back_ref_text = f" \\hfill\\textcolor{{gray}}{{\\tiny [Cited on slides: {back_refs}]}}"
            # Add back-reference at the end of the content
            content = content.rstrip() + back_ref_text

        return f"\\bibitem{{{citation_key}}} {content}"

    def _ensure_bibliography_numbering_list(self, bib_items: list) -> list:
        """
        Ensure bibliography items have clear enumerated numbers.
        Returns list of processed bibitem strings.
        """
        import re

        processed_items = []
        counter = 1

        for item in bib_items:
            # Check if item already has explicit numbering
            if '\\bibitem[' not in item and not re.search(r'\\bibitem\[?\d+\]?', item):
                # Add explicit number
                match = re.search(r'\\bibitem\{([^}]+)\}', item)
                if match:
                    key = match.group(1)
                    item = item.replace(f'\\bibitem{{{key}}}', f'\\bibitem[{counter}]{{{key}}}')
            processed_items.append(item)
            counter += 1

        return processed_items

    def _add_back_references_to_bibitem(self, bibitem_content: str) -> str:
        """
        Add back-references to a bibliography item showing where it was cited.
        PRESERVES the original bibitem format - does not change numbering.
        """
        import re

        # Extract the citation key from \bibitem{key} (preserve original)
        match = re.search(r'\\bibitem\{([^}]+)\}', bibitem_content)
        if not match:
            return bibitem_content

        citation_key = match.group(1)

        # Find where this citation appears in the slides
        slide_numbers = []
        for idx, slide in enumerate(self.slides, 1):
            # Skip fully masked slides
            if slide.get('_fully_masked', False):
                continue

            # Check content for \cite{citation_key}
            for content_line in slide.get('content', []):
                if f'\\cite{{{citation_key}}}' in content_line or f'\\cite{{{citation_key}' in content_line:
                    if idx not in slide_numbers:
                        slide_numbers.append(idx)
                    break
            # Check notes
            for note_line in slide.get('notes', []):
                if f'\\cite{{{citation_key}}}' in note_line or f'\\cite{{{citation_key}' in note_line:
                    if idx not in slide_numbers:
                        slide_numbers.append(idx)
                    break

        # Build back-reference text - insert BEFORE the closing of the bibitem
        if slide_numbers:
            back_refs = ', '.join([f"{num}" for num in slide_numbers])
            back_ref_text = f" \\hfill\\textcolor{{gray}}{{\\tiny [Cited on slides: {back_refs}]}}"

            # Insert back-reference at the end of the bibitem content
            # Find where the bibitem content ends (after the closing brace of the key)
            # Format: \bibitem{key} content here
            key_match = re.search(r'\\bibitem\{[^}]+\}', bibitem_content)
            if key_match:
                key_end = key_match.end()
                # Insert after the key, before any newline or at the end
                if key_end < len(bibitem_content):
                    bibitem_content = bibitem_content[:key_end] + back_ref_text + bibitem_content[key_end:]
                else:
                    bibitem_content = bibitem_content + back_ref_text

        return bibitem_content

    def _generate_bibliography_frame(self, content_lines: list, frame_title: str) -> str:
        """
        Generate a single bibliography frame (fallback when splitting fails).
        PRESERVES original bibitem formatting.
        """
        clean_title = self.clean_frame_title_for_latex(frame_title)

        # Join all content lines
        complete_bib = '\n'.join(content_lines)

        # Find all bibitem entries
        bib_pattern = r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem\{|\\end\{thebibliography\})'
        matches = re.findall(bib_pattern, complete_bib, re.DOTALL)

        latex = f"\\begin{{frame}}[allowframebreaks]{{{clean_title}}}\n"
        latex += f"\\frametitle{{{clean_title}}}\n"

        # Extract header
        header_match = re.search(r'(\\begin\{thebibliography\}\{[^}]+\})', complete_bib)
        if header_match:
            latex += header_match.group(1) + "\n"
        else:
            latex += "\\begin{thebibliography}{99}\n"

        # Process each bibitem
        for key, content in matches:
            content = content.strip()
            # Add back-references
            processed_item = self._add_back_references_to_bibitem_content(key, content)
            latex += processed_item + "\n"

        latex += "\\end{thebibliography}\n"
        latex += "\\end{frame}\n"

        return latex

    def _add_citation_back_references_to_slides(self, tex_content: str) -> str:
        """
        Add clickable back-references from citations to bibliography entries.
        Call this when generating final TeX output.
        """
        import re

        # Build a mapping of citation keys to slide numbers
        citation_map = {}
        for idx, slide in enumerate(self.slides, 1):
            if slide.get('_fully_masked', False):
                continue

            for content_line in slide.get('content', []):
                # Find all citations in this slide
                cites = re.findall(r'\\cite\{([^}]+)\}', content_line)
                for cite_key in cites:
                    if cite_key not in citation_map:
                        citation_map[cite_key] = []
                    if idx not in citation_map[cite_key]:
                        citation_map[cite_key].append(idx)

            for note_line in slide.get('notes', []):
                cites = re.findall(r'\\cite\{([^}]+)\}', note_line)
                for cite_key in cites:
                    if cite_key not in citation_map:
                        citation_map[cite_key] = []
                    if idx not in citation_map[cite_key]:
                        citation_map[cite_key].append(idx)

        # Add hyperref package if not present
        if '\\usepackage{hyperref}' not in tex_content:
            # Find the best place to insert hyperref (after documentclass)
            if '\\documentclass' in tex_content:
                docclass_end = tex_content.find('\\begin{document}')
                if docclass_end != -1:
                    hyperref_insert = '\n\\usepackage{hyperref}\n'
                    tex_content = tex_content[:docclass_end] + hyperref_insert + tex_content[docclass_end:]
            else:
                tex_content = '\\usepackage{hyperref}\n' + tex_content

        # Add hyperref configuration for better citation links
        hyperref_config = """
    % Configure hyperref for better citation links
    \\hypersetup{
        colorlinks=true,
        linkcolor=blue,
        citecolor=blue,
        urlcolor=blue,
        linktoc=all,
        pdfborder={0 0 0}
    }
    """
        if '\\hypersetup' not in tex_content:
            tex_content = tex_content.replace('\\usepackage{hyperref}', '\\usepackage{hyperref}\n' + hyperref_config)

        return tex_content

    def _add_bibliography_navigation(self, frames: list, total_frames: int) -> list:
        """
        Add navigation links between bibliography frames.
        """
        for i, frame in enumerate(frames):
            nav_links = []

            # Add previous page link
            if i > 0:
                nav_links.append(f"\\hyperlink{{page.{i}}}{{\\textcolor{{blue}}{{\\small ← Previous}}}}")

            # Add page indicator
            nav_links.append(f"\\textcolor{{gray}}{{\\small Page {i+1}/{total_frames}}}")

            # Add next page link
            if i < total_frames - 1:
                nav_links.append(f"\\hyperlink{{page.{i+2}}}{{\\textcolor{{blue}}{{\\small Next →}}}}")

            nav_bar = " \\hfill ".join(nav_links)

            # Insert navigation before \end{frame}
            frame = frame.replace(
                '\\end{frame}',
                f'\\vspace{{0.5em}}\\hfill {nav_bar} \\hfill\\end{{frame}}'
            )
            frames[i] = frame

        return frames

    def _generate_default_layout(self, params: str, content: list, frame_title: str) -> str:
        """
        Generate default layout with automatic two-column split when first line is an image.

        SUPPORTED FEATURES:
        1. Bibliography/References with multi-page splitting and back-references
        2. Columns environment (preserved exactly with user-specified widths)
        3. Mosaic directives (converted to tabular grids)
        4. Math expressions (quote-bracket notation and standard LaTeX)
        5. YouTube videos (converted to movie commands)
        6. URL images (downloaded and embedded)
        7. Local images (file paths)
        8. Tables (tabular environments)
        9. Itemize/Enumerate lists
        10. Bullet points (converted to itemize)
        11. Text formatting (textbf, textcolor, etc.)
        12. Play directives for videos
        13. Two-column layout (image + content) - preserves user widths
        14. Single image layout (centered)
        15. Single content layout
        """

        # ========== 1. BIBLIOGRAPHY/REFERENCES HANDLING ==========
        is_bibliography = False
        bib_content = []
        in_bibliography = False

        for line in content:
            if '\\begin{thebibliography}' in line:
                is_bibliography = True
                in_bibliography = True
                bib_content.append(line)
            elif '\\end{thebibliography}' in line:
                in_bibliography = False
                bib_content.append(line)
            elif in_bibliography:
                bib_content.append(line)

        if is_bibliography and bib_content:
            frames = self._split_bibliography_across_frames(bib_content, frame_title)
            if frames:
                if len(frames) == 1:
                    return frames[0]
                else:
                    frames = self._add_bibliography_navigation(frames, len(frames))
                    return '\n\n'.join(frames)

        # ========== 2. PREPARE CONTENT ==========
        clean_title = self.clean_frame_title_for_latex(frame_title)
        full_content = '\n'.join(content)

        import re
        import hashlib

        # ========== 3. PROTECT ALL MATH EXPRESSIONS WITH PLACEHOLDERS ==========
        math_placeholders = {}
        placeholder_counter = 0

        def protect_math(match):
            nonlocal placeholder_counter
            expr = match.group(0)
            placeholder = f"<<<MATH_PLACEHOLDER_{placeholder_counter}>>>"
            math_placeholders[placeholder] = expr
            placeholder_counter += 1
            return placeholder

        # Protect inline math $...$
        full_content = re.sub(r'\$[^\$]+\$', protect_math, full_content, flags=re.DOTALL)
        # Protect display math \[...\]
        full_content = re.sub(r'\\\[.*?\\\]', protect_math, full_content, flags=re.DOTALL)
        # Protect quote-bracket math '[...]' and "[...]"
        full_content = re.sub(r'[\'"]\[.*?[\'"]\]', protect_math, full_content, flags=re.DOTALL)
        # Protect math environments
        full_content = re.sub(r'\\begin\{align\*?\}.*?\\end\{align\*?\}', protect_math, full_content, flags=re.DOTALL)
        full_content = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}', protect_math, full_content, flags=re.DOTALL)

        # Convert any remaining unprotected quote-bracket math to display math
        def convert_math_expression(match):
            math_content = match.group(1).strip()
            if '\\\\' in math_content:
                lines = math_content.split('\\\\')
                aligned_lines = []
                for line in lines:
                    line = line.strip()
                    if line:
                        if '&' not in line:
                            line = f"& {line}"
                        aligned_lines.append(line)
                return "\\begin{align*}\n" + "\\\\\n".join(aligned_lines) + "\n\\end{align*}"
            else:
                return f"\\[{math_content}\\]"

        full_content = re.sub(r'[\'"]\[(.*?)[\'"]\]', convert_math_expression, full_content, flags=re.DOTALL)

        # ========== 4. YOUTUBE VIDEO CONVERSION ==========
        def convert_youtube_to_movie(match):
            url = match.group(1).strip()
            video_id = None
            if 'youtube.com/watch?v=' in url:
                video_id = url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[1].split('?')[0]

            if video_id:
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
                return f"\\movie[externalviewer]{{\\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{thumbnail_url}}}}}{{{url}}}"
            else:
                return f"\\href{{{url}}}{{\\textcolor{{blue}}{{\\underline{{Play Video}}}}}}"

        youtube_patterns = [
            r'\\play\s+(https?://(?:www\.)?youtube\.com/watch\?v=[^\s\n]+)',
            r'\\play\s+(https?://(?:www\.)?youtu\.be/[^\s\n]+)',
        ]

        for pattern in youtube_patterns:
            full_content = re.sub(pattern, convert_youtube_to_movie, full_content)

        # ========== 5. URL IMAGE CONVERSION ==========
        def convert_url_image(match):
            url = match.group(1).strip()
            url_hash = hashlib.md5(url.encode()).hexdigest()[:16]
            extension = url.split('.')[-1].split('?')[0].lower()
            if extension not in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                extension = 'png'
            filename = f"url_image_{url_hash}.{extension}"
            filepath = f"media_files/{filename}"
            return f"\\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{filepath}}}"

        url_image_pattern = r'\\file\s+(https?://[^\s\n]+\.(?:png|jpg|jpeg|gif|webp))'
        full_content = re.sub(url_image_pattern, convert_url_image, full_content)

        # ========== 6. MOSAIC DIRECTIVE CONVERSION ==========
        def convert_mosaic_to_tabular(match, col_width=0.47):
            rows = int(match.group(1))
            cols = int(match.group(2))
            images = [img.strip() for img in match.group(3).split(',')]

            tabular = "\\begin{center}\n"
            tabular += f"\\begin{{tabular}}{{{'c' * cols}}}\n"
            tabular += "\\hline\n"

            for idx, img in enumerate(images):
                img = img.strip()
                if img.startswith('http'):
                    url_hash = hashlib.md5(img.encode()).hexdigest()[:16]
                    img_path = f"media_files/url_image_{url_hash}.png"
                elif not img.startswith(('media_files/', './', '/')):
                    img_path = f"media_files/{img}"
                else:
                    img_path = img

                tabular += f"\\includegraphics[width={col_width}\\textwidth,height=0.25\\textheight,keepaspectratio]{{{img_path}}}"

                if (idx + 1) % cols == 0:
                    if idx < len(images) - 1:
                        tabular += "\\\\ \\hline\n"
                else:
                    tabular += " & "

            if not tabular.endswith('\\hline\n'):
                tabular += "\\\\ \\hline\n"
            tabular += "\\end{tabular}\n"
            tabular += "\\end{center}"
            return tabular

        # ========== 7. PLAY DIRECTIVE CONVERSION ==========
        def convert_play_directive(match):
            file_path = match.group(1).strip()
            if not file_path.startswith(('media_files/', './', '/')):
                file_path = f"media_files/{file_path}"
            return f"\\movie[externalviewer]{{\\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{file_path}}}}}{{{file_path}}}"

        # ========== 8. CHECK FOR COLUMNS ENVIRONMENT - PRESERVE EXACTLY ==========
        # IMPORTANT: If columns exist, preserve them EXACTLY without modifying column widths
        if '\\begin{columns}' in full_content and '\\end{columns}' in full_content:
            # Extract columns content
            columns_pattern = r'(\\begin\{columns\}(?:\[[^\]]*\])?\s*\n(.*?)\\end\{columns\})'
            columns_match = re.search(columns_pattern, full_content, re.DOTALL)

            if columns_match:
                columns_content = columns_match.group(1)

                # Only convert mosaic directives inside columns (preserve everything else)
                columns_content = re.sub(
                    r'\\mosaic\{(\d+),(\d+)\}\{([^}]+)\}',
                    lambda m: convert_mosaic_to_tabular(m, col_width=0.47),
                    columns_content
                )

                # Convert YouTube inside columns
                for pattern in youtube_patterns:
                    columns_content = re.sub(pattern, convert_youtube_to_movie, columns_content)

                # Convert URL images inside columns
                columns_content = re.sub(url_image_pattern, convert_url_image, columns_content)

                # Convert play directives inside columns
                columns_content = re.sub(r'\\play\s+\\file\s+([^\s\n]+)', convert_play_directive, columns_content)

                # Restore math placeholders inside columns
                for placeholder, math_expr in math_placeholders.items():
                    columns_content = columns_content.replace(placeholder, math_expr)

                # Build frame with preserved columns (including user-specified widths)
                latex = f"\\begin{{frame}}{{{clean_title}}}\n"
                latex += f"\\frametitle{{{clean_title}}}\n"
                latex += columns_content + "\n"
                latex += "\\end{frame}\n"
                return latex

        # ========== 9. PROCESS NON-COLUMNS CONTENT ==========
        # Convert mosaic directives
        full_content = re.sub(r'\\mosaic\{(\d+),(\d+)\}\{([^}]+)\}',
                             lambda m: convert_mosaic_to_tabular(m, col_width=0.7),
                             full_content)

        # Convert play directives
        full_content = re.sub(r'\\play\s+\\file\s+([^\s\n]+)', convert_play_directive, full_content)

        # ========== 10. IMAGE DETECTION ==========
        has_image = False
        image_path = None

        # Check params for image
        if params and params != "\\None":
            if any(x in params for x in ['\\includegraphics', '.png', '.jpg', '.jpeg', '.pdf', '.gif', '.webp']):
                has_image = True
                image_path = params.strip()
                if image_path.startswith('\\file'):
                    image_path = image_path.replace('\\file', '').strip()
                if image_path.startswith('http'):
                    url_hash = hashlib.md5(image_path.encode()).hexdigest()[:16]
                    image_path = f"media_files/url_image_{url_hash}.png"
                elif not image_path.startswith(('media_files/', './', '/')):
                    image_path = f"media_files/{image_path}"

        # Check content for image (first non-empty line)
        if not has_image:
            lines_for_image = full_content.split('\n')
            for line in lines_for_image:
                line_stripped = line.strip()
                if line_stripped and not line_stripped.startswith('%'):
                    if (line_stripped.startswith('\\file') and
                        any(ext in line_stripped.lower() for ext in ['.png', '.jpg', '.jpeg', '.pdf', '.gif', '.webp'])):
                        has_image = True
                        image_path = line_stripped
                        if image_path.startswith('\\file'):
                            image_path = image_path.replace('\\file', '').strip()
                        if image_path.startswith('http'):
                            url_hash = hashlib.md5(image_path.encode()).hexdigest()[:16]
                            image_path = f"media_files/url_image_{url_hash}.png"
                        elif not image_path.startswith(('media_files/', './', '/')):
                            image_path = f"media_files/{image_path}"
                        # Remove the image line from content
                        full_content = re.sub(r'^\\file\s+[^\n]+\n?', '', full_content, flags=re.MULTILINE)
                        break

        # ========== 11. BULLET POINT PROCESSING ==========
        def process_bullet_points(text):
            """Convert bullet points to itemize environment."""
            lines = text.split('\n')
            result_lines = []
            in_itemize = False

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    result_lines.append(line)
                    continue

                if stripped.startswith(('-', '•')):
                    if not in_itemize:
                        result_lines.append("\\begin{itemize}")
                        in_itemize = True
                    bullet_content = re.sub(r'^[-•]\s*', '', stripped)
                    result_lines.append(f"\\item {bullet_content}")
                else:
                    if in_itemize:
                        result_lines.append("\\end{itemize}")
                        in_itemize = False
                    result_lines.append(line)

            if in_itemize:
                result_lines.append("\\end{itemize}")

            return '\n'.join(result_lines)

        has_tabular = '\\begin{tabular}' in full_content
        has_itemize = '\\begin{itemize}' in full_content or '\\begin{enumerate}' in full_content

        if not has_tabular and not has_itemize:
            full_content = process_bullet_points(full_content)

        # ========== 12. RESTORE ALL MATH EXPRESSIONS ==========
        for placeholder, math_expr in math_placeholders.items():
            full_content = full_content.replace(placeholder, math_expr)

        # ========== 13. BUILD THE FRAME ==========
        latex = f"\\begin{{frame}}{{{clean_title}}}\n"
        latex += f"\\frametitle{{{clean_title}}}\n"

        if has_image and full_content.strip():
            # Two-column layout - preserve user-specified widths or use defaults
            latex += "\\begin{columns}[T]\n"
            latex += "\\column{0.45\\textwidth}\n"
            latex += "\\begin{center}\n"
            latex += f"\\includegraphics[width=\\textwidth,keepaspectratio]{{{image_path}}}\n"
            latex += "\\end{center}\n"
            latex += "\\column{0.5\\textwidth}\n"
            latex += full_content + "\n"
            latex += "\\end{columns}\n"
        elif has_image:
            latex += "\\begin{center}\n"
            latex += f"\\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{image_path}}}\n"
            latex += "\\end{center}\n"
        else:
            if full_content.strip():
                latex += full_content + "\n"

        latex += "\\end{frame}\n"
        return latex

    def _generate_table_layout(self, params: str, content: list, frame_title: str) -> str:
        """
        Generate table layout - preserves LaTeX tabular environments exactly as they appear.
        Automatically creates two-column layout when first line is an image.
        """
        # Clean the frame title
        clean_title = self.clean_frame_title_for_latex(frame_title)

        latex = f"\\begin{{frame}}{{{clean_title}}}\n"
        latex += f"\\frametitle{{{clean_title}}}\n"

        # Initialize containers
        has_image = False
        image_path = None
        table_content = []
        regular_content = []
        in_table = False
        is_first_line_image = False

        # Check params for image
        if params and params != "\\None":
            if any(x in params for x in ['\\includegraphics', '.png', '.jpg', '.jpeg', '.pdf', '.gif']):
                has_image = True
                image_path = params.strip()
                if image_path.startswith('\\file'):
                    image_path = image_path.replace('\\file', '').strip()
                if not image_path.startswith(('media_files/', './', '/')):
                    image_path = f"media_files/{image_path}"

        # Parse content
        if content:
            first_line = True
            for line in content:
                line_stripped = line.strip()

                # Check if first line is an image
                if first_line:
                    first_line = False
                    if not has_image:
                        if (line_stripped.startswith('\\file') and
                            any(ext in line_stripped.lower() for ext in ['.png', '.jpg', '.jpeg', '.pdf', '.gif'])):
                            is_first_line_image = True
                            has_image = True
                            image_path = line_stripped
                            if image_path.startswith('\\file'):
                                image_path = image_path.replace('\\file', '').strip()
                            if not image_path.startswith(('media_files/', './', '/')):
                                image_path = f"media_files/{image_path}"
                            continue

                # Detect table
                if '\\begin{tabular}' in line_stripped:
                    in_table = True
                    table_content.append(line)
                    continue
                elif '\\end{tabular}' in line_stripped:
                    in_table = False
                    table_content.append(line)
                    continue

                # Detect other images
                if not in_table and not has_image:
                    if (line_stripped.startswith('\\file') and
                        any(ext in line_stripped.lower() for ext in ['.png', '.jpg', '.jpeg', '.pdf', '.gif'])):
                        has_image = True
                        image_path = line_stripped
                        if image_path.startswith('\\file'):
                            image_path = image_path.replace('\\file', '').strip()
                        if not image_path.startswith(('media_files/', './', '/')):
                            image_path = f"media_files/{image_path}"
                        continue

                # Collect content
                if in_table:
                    if '\\\\' in line and line.endswith('\\\\'):
                        line = line.rstrip('\\')
                    table_content.append(line)
                elif line_stripped and not line_stripped.startswith('\\file'):
                    regular_content.append(line)

        # Fix table formatting
        if table_content:
            table_content = self._fix_table_formatting(table_content)

        # Determine layout
        if has_image and (table_content or regular_content):
            # Two-column: image on left, content on right
            latex += "\\begin{columns}[T]\n"
            latex += "\\column{0.45\\textwidth}\n"
            latex += "\\begin{center}\n"
            latex += f"\\includegraphics[width=\\textwidth,keepaspectratio]{{{image_path}}}\n"
            latex += "\\end{center}\n"
            latex += "\\column{0.5\\textwidth}\n"

            if table_content:
                table_text = '\n'.join(table_content)
                latex += table_text + "\n"

            if regular_content:
                has_bullets = any(line.strip().startswith(('-', '•')) for line in regular_content)
                if has_bullets or len(regular_content) > 1:
                    content_items = self._format_content_items(regular_content)
                    if content_items:
                        latex += content_items + "\n"
                else:
                    latex += '\n'.join(regular_content) + "\n"

            latex += "\\end{columns}\n"
        elif has_image:
            # Just image centered
            latex += "\\begin{center}\n"
            latex += f"\\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{image_path}}}\n"
            latex += "\\end{center}\n"
        elif table_content:
            # Just table
            table_text = '\n'.join(table_content)
            latex += table_text + "\n"
        elif regular_content:
            # Just text
            has_bullets = any(line.strip().startswith(('-', '•')) for line in regular_content)
            if has_bullets or len(regular_content) > 1:
                content_items = self._format_content_items(regular_content)
                if content_items:
                    latex += content_items + "\n"
            else:
                latex += '\n'.join(regular_content) + "\n"

        latex += "\\end{frame}\n"
        return latex

    def _fix_table_formatting(self, table_lines: list) -> list:
        """
        Fix table formatting issues including:
        - Missing \hline at the beginning
        - Escaped newline issues (\\hline\\)
        - Proper column separators
        """
        fixed_lines = []
        in_table = False
        hline_added = False

        for line in table_lines:
            line_stripped = line.rstrip()

            # Check for table start
            if '\\begin{tabular}' in line_stripped:
                in_table = True
                hline_added = False
                fixed_lines.append(line_stripped)
                continue

            # Check for table end
            if '\\end{tabular}' in line_stripped:
                in_table = False
                fixed_lines.append(line_stripped)
                continue

            if in_table:
                # Fix escaped newlines: convert \\hline\\ to \hline
                if '\\\\hline\\\\' in line_stripped:
                    line_stripped = line_stripped.replace('\\\\hline\\\\', '\\hline')
                elif '\\\\hline' in line_stripped:
                    line_stripped = line_stripped.replace('\\\\hline', '\\hline')

                # Remove trailing backslashes if they're not needed
                if line_stripped.endswith('\\\\') and '\\hline' not in line_stripped:
                    # Check if this is a row separator that needs the backslashes
                    if line_stripped.count('&') > 0:
                        # This is a data row, keep the backslashes
                        pass
                    else:
                        line_stripped = line_stripped.rstrip('\\')

                # Add missing initial \hline if needed
                if not hline_added and (line_stripped.startswith('\\textbf') or
                                         (line_stripped and line_stripped[0].isalpha())):
                    # This is the first row of data, add \hline before it
                    fixed_lines.append('\\hline')
                    hline_added = True

                fixed_lines.append(line_stripped)
            else:
                fixed_lines.append(line_stripped)

        return fixed_lines

    def _generate_mosaic_layout(self, params: str, content: list, frame_title: str) -> str:
        """Generate mosaic layout with dynamic grid sizing and proper scaling, including table support"""
        import re

        # Clean the frame title
        clean_title = self.clean_frame_title_for_latex(frame_title)

        # Parse mosaic parameters: \mosaic{rows,cols}{image1, image2, ...}
        mosaic_match = re.search(r'\{(\d+),(\d+)\}\{(.*?)\}', params)

        if not mosaic_match:
            # Try to fix malformed mosaic (missing braces)
            if params.strip() and not params.startswith('{'):
                # Assume it's just a list of images, use auto-layout
                images = [img.strip() for img in params.split(',') if img.strip()]
                if images:
                    # Auto-calculate grid (prefer 3 columns, max 4)
                    cols = min(4, max(2, (len(images) + 2) // 3))
                    rows = (len(images) + cols - 1) // cols
                    self.write(f"  ℹ Auto-detected mosaic: {rows}x{cols} for {len(images)} images\n", "cyan")
                    return self._render_mosaic_grid(images, rows, cols, content, clean_title)

            # Check if this might be a table directive
            if params.strip().startswith('{') and 'rows' in params.lower():
                self.write("  ℹ Detected table format, using table layout\n", "cyan")
                return self._generate_table_layout(params, content, clean_title)

            self.write("  ⚠ Invalid mosaic format, using default layout\n", "yellow")
            return self._generate_default_layout(params, content, clean_title)

        rows = int(mosaic_match.group(1))
        cols = int(mosaic_match.group(2))
        images = [img.strip() for img in mosaic_match.group(3).split(',') if img.strip()]

        # Remove any 'media_files/' prefix that might be duplicated
        cleaned_images = []
        for img in images:
            if img.startswith('media_files/media_files/'):
                img = img.replace('media_files/media_files/', 'media_files/')
            cleaned_images.append(img)

        return self._render_mosaic_grid(cleaned_images, rows, cols, content, clean_title)

    def _render_mosaic_grid(self, images: list, rows: int, cols: int, content: list, frame_title: str) -> str:
        """Render the mosaic grid with proper scaling, blank cells, and auto-expansion"""

        # Clean the frame title for LaTeX
        clean_title = self.clean_frame_title_for_latex(frame_title)

        # Check if any image contains table-like content
        has_table_like = any(',' in img and ('rows' in img.lower() or 'cols' in img.lower()) for img in images)
        if has_table_like:
            self.write("  ℹ Detected table-like content in mosaic, using table layout\n", "cyan")
            # Extract the table parameters from the images list
            table_params = ','.join(images)
            return self._generate_table_layout(table_params, content, clean_title)

        # Calculate optimal grid if needed
        total_images = len(images)
        total_cells = rows * cols

        # Auto-expand if more images than cells
        if total_images > total_cells:
            new_rows = (total_images + cols - 1) // cols
            self.write(f"  ℹ Expanding mosaic: {rows}x{cols} → {new_rows}x{cols} for {total_images} images\n", "cyan")
            rows = new_rows
            total_cells = rows * cols

        # Pad images list with empty strings to fill the grid
        padded_images = images + [''] * (total_cells - len(images))

        # Calculate available width per column
        col_width = 0.94 / cols

        latex = f"\\begin{{frame}}{{{clean_title}}}\n"
        latex += f"\\frametitle{{{clean_title}}}\n"

        # Check if we're inside a columns environment (content contains column markers)
        has_existing_columns = any('\\begin{columns}' in line for line in content) if content else False

        if has_existing_columns:
            # Extract left column content and right column content separately
            left_content = []
            right_content = []
            in_columns = False
            in_left = False
            in_right = False

            for line in content:
                if '\\begin{columns}' in line:
                    in_columns = True
                    continue
                elif '\\end{columns}' in line:
                    in_columns = False
                    continue
                elif in_columns and '\\column' in line:
                    # Determine which column
                    if '0.5' in line or '0.48' in line:
                        in_left = True
                        in_right = False
                    else:
                        in_left = False
                        in_right = True
                    continue
                elif in_columns and in_left:
                    left_content.append(line)
                elif in_columns and in_right:
                    right_content.append(line)

            # Build the columns structure
            latex += "\\begin{columns}[T]\n"

            # Left column - original text content
            latex += "\\column{0.48\\textwidth}\n"
            for line in left_content:
                if line.strip():
                    # Process bullet points
                    if line.strip().startswith(('-', '•')):
                        bullet_content = re.sub(r'^[-•]\s*', '', line.strip())
                        latex += f"\\item {bullet_content}\n"
                    else:
                        latex += line + "\n"

            # Right column - mosaic grid
            latex += "\\column{0.48\\textwidth}\n"
            latex += self._generate_mosaic_grid_only(padded_images, rows, cols)

            latex += "\\end{columns}\n"

        else:
            # No existing columns - just add content then mosaic
            if content:
                content_items = self._format_content_items(content)
                if content_items:
                    latex += content_items + "\n"
                    latex += "\\vspace{0.5em}\n"

            # Add the mosaic grid
            latex += self._generate_mosaic_grid_only(padded_images, rows, cols)

        latex += "\\end{frame}\n"
        return latex

    def _generate_mosaic_grid_only(self, images: list, rows: int, cols: int) -> str:
        """Generate just the mosaic grid table (without frame wrapper)"""

        total_cells = rows * cols
        padded_images = images + [''] * (total_cells - len(images))

        # Calculate available width per column
        col_width = 0.94 / cols

        # Check if any image contains a table or list
        has_list_content = any(',' in img and ('item' in img.lower() or 'bullet' in img.lower()) for img in padded_images)

        if has_list_content:
            # Use tabular with paragraph columns for list content
            latex = "\\begin{center}\n"
            latex += f"\\begin{{tabular}}{{{'p{' + str(col_width) + '\\textwidth}' * cols}}}\n"
            latex += "\\hline\n"

            for idx, img_path in enumerate(padded_images):
                if idx > 0 and idx % cols == 0:
                    latex = latex.rstrip('& ') + "\\\\ \\hline\n"

                if img_path:
                    clean_path = img_path
                    if not clean_path.startswith(('media_files/', './', '/')):
                        clean_path = f"media_files/{clean_path}"

                    # Check if this contains list items
                    if '\\item' in clean_path or '•' in clean_path or '-' in clean_path:
                        # Format as itemized list
                        items = re.split(r'[,;]', clean_path)
                        items = [item.strip() for item in items if item.strip()]
                        if items:
                            cell_content = "\\begin{itemize}\n"
                            for item in items:
                                item = re.sub(r'^[-•]\\s*', '', item)
                                cell_content += f"\\item {item}\n"
                            cell_content += "\\end{itemize}"
                            latex += f" {cell_content} &"
                        else:
                            latex += f" \\includegraphics[width={col_width}\\textwidth,height=0.25\\textheight,keepaspectratio]{{{clean_path}}} &"
                    else:
                        # Regular image
                        latex += f" \\includegraphics[width={col_width}\\textwidth,height=0.25\\textheight,keepaspectratio]{{{clean_path}}} &"
                else:
                    # Empty cell placeholder
                    latex += f" \\textcolor{{gray}}{{\\rule{{{col_width}\\textwidth}}{{0.2\\textheight}}}} &"

            latex = latex.rstrip('& ') + "\\\\ \\hline\n"
            latex += "\\end{tabular}\n"
            latex += "\\end{center}\n"
        else:
            # Use standard tabular for images
            latex = "\\begin{center}\n"
            latex += f"\\begin{{tabular}}{{{'c' * cols}}}\n"
            latex += "\\hline\n"

            for idx, img_path in enumerate(padded_images):
                if idx > 0 and idx % cols == 0:
                    latex = latex.rstrip('& ') + "\\\\ \\hline\n"

                if img_path:
                    clean_path = img_path
                    if not clean_path.startswith(('media_files/', './', '/')):
                        clean_path = f"media_files/{clean_path}"
                    latex += f" \\includegraphics[width={col_width}\\textwidth,height=0.25\\textheight,keepaspectratio]{{{clean_path}}} &"
                else:
                    # Empty cell placeholder
                    latex += f" \\textcolor{{gray}}{{\\rule{{{col_width}\\textwidth}}{{0.2\\textheight}}}} &"

            latex = latex.rstrip('& ') + "\\\\ \\hline\n"
            latex += "\\end{tabular}\n"
            latex += "\\end{center}\n"

        blank_count = padded_images.count('')
        if blank_count > 0:
            latex += "\n\\vspace{0.3em}\n"
            latex += f"\\begin{{center}}\\textcolor{{gray}}{{\\footnotesize {blank_count} placeholder(s) for missing images}}\\end{{center}}\n"

        return latex




    def _render_table_grid(self, cell_data: list, rows: int, cols: int, content_mode: str) -> str:
        """
        Render the table grid with proper cell formatting.
        Supports both images and text items.
        """
        # Calculate column width based on number of columns
        col_width = 0.9 / cols

        latex = "\\begin{center}\n"
        latex += f"\\begin{{tabular}}{{{'p{' + str(col_width) + '\\textwidth}' * cols}}}\n"
        latex += "\\hline\n"

        for i, row in enumerate(cell_data):
            row_latex = ""
            for j, cell in enumerate(row):
                if cell.strip():
                    # Check if this cell contains an image
                    if content_mode == "images" or ('\\includegraphics' in cell or cell.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf'))):
                        # Handle image cell
                        clean_path = cell.strip()
                        if not clean_path.startswith(('media_files/', './', '/')) and '\\includegraphics' not in clean_path:
                            clean_path = f"media_files/{clean_path}"

                        # Remove any existing \includegraphics wrapper
                        img_match = re.search(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', clean_path)
                        if img_match:
                            clean_path = img_match.group(1)

                        # Create centered image cell
                        cell_content = f"\\begin{{center}}\\includegraphics[width={col_width}\\textwidth,keepaspectratio]{{{clean_path}}}\\end{{center}}"
                    else:
                        # Handle text cell - convert to itemized list if multiple items
                        if '\n' in cell or ';' in cell:
                            # Multiple items - create itemize
                            items = re.split(r'[;\n]', cell)
                            items = [item.strip() for item in items if item.strip()]
                            if items:
                                cell_content = "\\begin{itemize}\n"
                                for item in items:
                                    # Clean up the item
                                    item = re.sub(r'^[-•]\s*', '', item)
                                    cell_content += f"\\item {item}\n"
                                cell_content += "\\end{itemize}"
                            else:
                                cell_content = cell.strip()
                        else:
                            # Single item - remove bullet if present
                            cell_content = re.sub(r'^[-•]\s*', '', cell.strip())
                            if not cell_content:
                                cell_content = "\\textcolor{gray}{---}"

                    row_latex += f" {cell_content} &"
                else:
                    # Empty cell
                    row_latex += f" \\textcolor{{gray}}{{\\rule{{{col_width}\\textwidth}}{{1cm}}}} &"

            # Remove trailing '&' and add row separator
            row_latex = row_latex.rstrip('&') + "\\\\ \\hline\n"
            latex += row_latex

        latex += "\\end{tabular}\n"
        latex += "\\end{center}\n"

        return latex

    def balance_braces(self, text: str) -> str:
        """Balance braces in a string to prevent LaTeX errors"""
        if not text:
            return text

        open_count = text.count('{')
        close_count = text.count('}')

        if open_count > close_count:
            text += '}' * (open_count - close_count)
        elif close_count > open_count:
            # Remove extra closing braces from the end
            while text.endswith('}') and text.count('}') > text.count('{'):
                text = text[:-1]

        return text

    def clean_frame_title_for_latex(self, title: str) -> str:
        """Clean frame title to prevent LaTeX compilation errors"""
        if not title:
            return "Untitled"

        # Remove all braces from titles (they cause issues)
        title = str(title)
        title = title.replace('\\{', '').replace('\\}', '')
        title = title.replace('{', '').replace('}', '')

        # Escape special characters
        title = title.replace('&', '\\&')
        title = title.replace('%', '\\%')
        title = title.replace('#', '\\#')
        title = title.replace('_', '\\_')
        title = title.replace('$', '\\$')

        return title.strip() or "Untitled"


    def _generate_mosaic_from_list(self, images: list, rows: int, cols: int, content: list, frame_title: str) -> str:
        """Generate mosaic from a list of images with specified grid dimensions"""

        # Clean the frame title
        clean_title = frame_title.replace('\\\\', '\\').replace('\\&', '&')

        latex = f"\\begin{{frame}}{{{clean_title}}}\n"
        latex += f"\\frametitle{{{clean_title}}}\n"

        # Calculate column width
        col_width = 0.95 / cols

        # Create the mosaic grid
        latex += "\\begin{center}\n"
        latex += f"\\begin{{tabular}}{{{'c' * cols}}}\n"
        latex += "\\hline\n"

        for idx, img_path in enumerate(images):
            # Add row separator every 'cols' images
            if idx > 0 and idx % cols == 0:
                latex = latex.rstrip('& ') + "\\\\ \\hline\n"

            # Ensure image path is correct
            clean_path = img_path
            if not clean_path.startswith(('media_files/', './', '/')):
                clean_path = f"media_files/{clean_path}"

            latex += f"\\includegraphics[width={col_width}\\textwidth,keepaspectratio]{{{clean_path}}} & "

        # Close the last row
        latex = latex.rstrip('& ') + "\\\\ \\hline\n"
        latex += "\\end{tabular}\n"
        latex += "\\end{center}\n"

        # Extract and format content from inside columns environment
        extracted_content = self._extract_and_format_content_from_columns(content)

        # Add formatted content
        if extracted_content:
            latex += "\n\\vspace{0.5em}\n"
            latex += extracted_content

        latex += "\\end{frame}\n"
        return latex

    def _extract_and_format_content_from_columns(self, content: list) -> str:
        """
        Extract content from inside columns environment and format it properly.
        Preserves itemize environments and converts bullet points to \item commands.
        """
        if not content:
            return ""

        result = []
        in_columns = False
        in_itemize = False

        for line in content:
            stripped = line.strip()

            # Track columns environment boundaries
            if '\\begin{columns}' in stripped:
                in_columns = True
                continue
            elif '\\end{columns}' in stripped:
                in_columns = False
                continue

            # Skip \column commands
            if stripped.startswith('\\column'):
                continue

            # If we're inside columns, process the content
            if in_columns and stripped:
                # Handle itemize environment start
                if '\\begin{itemize}' in stripped:
                    in_itemize = True
                    result.append(stripped)
                    continue

                # Handle itemize environment end
                if '\\end{itemize}' in stripped:
                    in_itemize = False
                    result.append(stripped)
                    continue

                # Handle bullet points inside itemize (lines starting with -)
                if in_itemize and stripped.startswith('-'):
                    # Convert - to \item
                    item_content = stripped[1:].strip()
                    result.append(f"\\item {item_content}")
                else:
                    # Regular content
                    result.append(line)

        return '\n'.join(result)

    def _extract_content_from_columns(self, content: list) -> list:
        """
        Extract content from inside columns environment.
        Removes the \begin{columns}, \end{columns}, and \column commands
        but preserves the actual content.
        """
        if not content:
            return []

        extracted = []
        in_columns = False
        skip_until_next_column = False
        current_column_content = []

        for line in content:
            stripped = line.strip()

            # Track columns environment boundaries
            if '\\begin{columns}' in stripped:
                in_columns = True
                continue
            elif '\\end{columns}' in stripped:
                in_columns = False
                # Add the last column's content
                if current_column_content:
                    extracted.extend(current_column_content)
                    current_column_content = []
                continue

            # Skip \column commands but keep their content
            if stripped.startswith('\\column'):
                # If we have accumulated content from previous column, add it
                if current_column_content:
                    extracted.extend(current_column_content)
                    current_column_content = []
                continue

            # If we're inside columns, collect the content
            if in_columns:
                # Don't add empty lines
                if stripped:
                    current_column_content.append(line)
            else:
                # Outside columns, add directly (shouldn't happen in normal case)
                if stripped:
                    extracted.append(line)

        # Add any remaining content
        if current_column_content:
            extracted.extend(current_column_content)

        return extracted

    def _format_content_items(self, content_list):
        """Format content items into proper LaTeX structure with correct nesting"""
        if not content_list:
            return ""

        result = []
        in_list = False
        list_type = None
        list_stack = []  # Track nested list types
        in_alertblock = False
        in_block = False
        current_block_type = None

        i = 0
        while i < len(content_list):
            item = content_list[i]
            if not item or not item.strip():
                i += 1
                continue

            stripped = item.strip()

            # Handle alertblock environment
            if stripped.startswith('\\begin{alertblock}'):
                in_alertblock = True
                result.append(stripped)
                i += 1
                continue
            elif stripped.startswith('\\end{alertblock}'):
                in_alertblock = False
                result.append(stripped)
                i += 1
                continue

            # Handle block environment
            if stripped.startswith('\\begin{block}'):
                in_block = True
                current_block_type = 'block'
                result.append(stripped)
                i += 1
                continue
            elif stripped.startswith('\\end{block}'):
                in_block = False
                current_block_type = None
                result.append(stripped)
                i += 1
                continue

            # Handle itemize environment start
            if '\\begin{itemize}' in stripped:
                list_stack.append('itemize')
                result.append(stripped)
                i += 1
                continue

            # Handle itemize environment end
            if '\\end{itemize}' in stripped:
                if list_stack:
                    list_stack.pop()
                result.append(stripped)
                i += 1
                continue

            # Handle enumerate environment
            if '\\begin{enumerate}' in stripped:
                list_stack.append('enumerate')
                result.append(stripped)
                i += 1
                continue
            elif '\\end{enumerate}' in stripped:
                if list_stack:
                    list_stack.pop()
                result.append(stripped)
                i += 1
                continue

            # Handle bullet points (convert - to \item)
            if stripped.startswith(('- ', '• ')):
                bullet_content = re.sub(r'^[-•]\s*', '', stripped)
                bullet_content = self._fix_alert_commands(bullet_content)

                # If not already in a list, start one
                if not list_stack:
                    result.append("\\begin{itemize}")
                    result.append(f"\\item {bullet_content}")
                    # Don't close immediately - might have more items
                    list_stack.append('itemize')
                else:
                    result.append(f"\\item {bullet_content}")
                i += 1
                continue

            # Handle standalone \item commands
            if stripped.startswith('\\item'):
                # Fix any malformed \alert commands
                item_content = self._fix_alert_commands(stripped)
                if not list_stack:
                    result.append("\\begin{itemize}")
                    result.append(item_content)
                    list_stack.append('itemize')
                else:
                    result.append(item_content)
                i += 1
                continue

            # Handle \pause commands
            if stripped.startswith('\\pause'):
                result.append(stripped)
                i += 1
                continue

            # Handle column commands
            if stripped.startswith('\\column'):
                result.append(stripped)
                i += 1
                continue

            # Handle \hline commands
            if stripped == '\\hline':
                result.append(stripped)
                i += 1
                continue

            # Handle \centering
            if stripped == '\\centering':
                result.append(stripped)
                i += 1
                continue

            # Handle plain text content
            if stripped:
                # Fix alert commands in text
                stripped = self._fix_alert_commands(stripped)

                # If we're in a list but this isn't an item, we need to close the list
                if list_stack and not stripped.startswith('\\item'):
                    # Close all open lists
                    for _ in range(len(list_stack)):
                        if list_stack[-1] == 'itemize':
                            result.append("\\end{itemize}")
                        elif list_stack[-1] == 'enumerate':
                            result.append("\\end{enumerate}")
                        list_stack.pop()
                    result.append(stripped)
                else:
                    result.append(stripped)

            i += 1

        # Close any remaining open lists
        while list_stack:
            if list_stack[-1] == 'itemize':
                result.append("\\end{itemize}")
            elif list_stack[-1] == 'enumerate':
                result.append("\\end{enumerate}")
            list_stack.pop()

        return '\n'.join(result)

    def _fix_alert_commands(self, text):
        """
        Fix malformed \alert commands to ensure they have proper braces.
        Converts \alert text -> \alert{text}
        Converts \alert{text} -> \alert{text} (unchanged)
        """
        import re

        # Fix \alert without braces: \alert text -> \alert{text}
        # Match \alert followed by space and then content until space, newline, or end
        text = re.sub(r'\\alert\s+([^{\\\s][^\\\n]*?)(?=\s*$|\s*\\|$)', r'\\alert{\1}', text)

        # Fix \alert with missing opening brace: \alert text} -> \alert{text}
        text = re.sub(r'\\alert\s+([^{][^}]*?)\}', r'\\alert{\1}', text)

        # Fix \alert with no braces at all
        text = re.sub(r'\\alert\s+([a-zA-Z][a-zA-Z\s]*?)(?=\s|$|\\|\.|,|;|:)', r'\\alert{\1}', text)

        return text

    def _generate_split_layout(self, params: str, content: list, frame_title: str) -> str:
        """Generate split layout: image on left, content on right"""
        latex = f"\\begin{{frame}}{{{frame_title}}}\n"
        latex += f"\\frametitle{{{frame_title}}}\n"
        latex += "\\begin{columns}[T]\n"
        latex += "\\begin{column}{0.48\\textwidth}\n"

        # Handle image path
        clean_path = params.strip()
        if not clean_path.startswith(('media_files/', './', '/')):
            clean_path = f"media_files/{clean_path}"

        latex += f"\\includegraphics[width=\\textwidth,keepaspectratio]{{{clean_path}}}\n"
        latex += "\\end{column}\n"
        latex += "\\begin{column}{0.48\\textwidth}\n"

        if content:
            content_items = self._format_content_items(content)
            if content_items:
                latex += content_items + "\n"

        latex += "\\end{column}\n"
        latex += "\\end{columns}\n"
        latex += "\\end{frame}\n"
        return latex

    def _generate_pip_layout(self, params: str, content: list, frame_title: str) -> str:
        """Generate picture-in-picture layout: content on left, small image on right"""
        latex = f"\\begin{{frame}}{{{frame_title}}}\n"
        latex += f"\\frametitle{{{frame_title}}}\n"
        latex += "\\begin{columns}[T]\n"
        latex += "\\begin{column}{0.68\\textwidth}\n"

        if content:
            content_items = self._format_content_items(content)
            if content_items:
                latex += content_items + "\n"

        latex += "\\end{column}\n"
        latex += "\\begin{column}{0.28\\textwidth}\n"
        latex += "\\vspace{1em}\n"

        # Handle image path
        clean_path = params.strip()
        if not clean_path.startswith(('media_files/', './', '/')):
            clean_path = f"media_files/{clean_path}"

        latex += f"\\includegraphics[width=\\textwidth,keepaspectratio]{{{clean_path}}}\n"
        latex += "\\end{column}\n"
        latex += "\\end{columns}\n"
        latex += "\\end{frame}\n"
        return latex

    def _generate_watermark_layout(self, params: str, content: list, frame_title: str) -> str:
        """Generate watermark layout: image as background watermark"""
        clean_path = params.strip()
        if not clean_path.startswith(('media_files/', './', '/')):
            clean_path = f"media_files/{clean_path}"

        latex = f"\\begin{{frame}}{{{frame_title}}}\n"
        latex += f"\\frametitle{{{frame_title}}}\n"
        latex += "\\setbeamertemplate{background}{\n"
        latex += "\\begin{tikzpicture}[remember picture,overlay]\n"
        latex += f"\\node[opacity=0.15] at (current page.center) {{\\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{{{clean_path}}}}};\n"
        latex += "\\end{tikzpicture}\n"
        latex += "}\n\n"

        if content:
            content_items = self._format_content_items(content)
            if content_items:
                latex += content_items + "\n"

        latex += "\\end{frame}\n"
        return latex

    def _generate_fullframe_layout(self, params: str, content: list, frame_title: str) -> str:
        """Generate fullframe layout: image takes entire frame"""
        clean_path = params.strip()
        if not clean_path.startswith(('media_files/', './', '/')):
            clean_path = f"media_files/{clean_path}"

        latex = f"\\begin{{frame}}{{{frame_title}}}\n"
        latex += "\\setbeamertemplate{background}{\n"
        latex += "\\begin{tikzpicture}[remember picture,overlay]\n"
        latex += f"\\node at (current page.center) {{\\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{{{clean_path}}}}};\n"
        latex += "\\end{tikzpicture}\n"
        latex += "}\n"
        latex += "\\frametitle{{{frame_title}}}\n\n"

        if content:
            content_items = self._format_content_items(content)
            if content_items:
                latex += "\\begin{textblock}{0.8}(0.1,0.7)\n"
                latex += content_items + "\n"
                latex += "\\end{textblock}\n"

        latex += "\\end{frame}\n"
        return latex

    def _generate_highlight_layout(self, params: str, content: list, frame_title: str) -> str:
        """Generate highlight layout: image with highlighted content overlay"""
        clean_path = params.strip()
        if not clean_path.startswith(('media_files/', './', '/')):
            clean_path = f"media_files/{clean_path}"

        latex = f"\\begin{{frame}}{{{frame_title}}}\n"
        latex += f"\\frametitle{{{frame_title}}}\n"
        latex += "\\begin{columns}[T]\n"
        latex += "\\begin{column}{0.6\\textwidth}\n"
        latex += f"\\includegraphics[width=\\textwidth,keepaspectratio]{{{clean_path}}}\n"
        latex += "\\end{column}\n"
        latex += "\\begin{column}{0.36\\textwidth}\n"

        if content:
            content_items = self._format_content_items(content)
            if content_items:
                latex += "\\colorbox{yellow!20}{\n"
                latex += "\\begin{minipage}{\\textwidth}\n"
                latex += content_items + "\n"
                latex += "\\end{minipage}\n"
                latex += "}\n"

        latex += "\\end{column}\n"
        latex += "\\end{columns}\n"
        latex += "\\end{frame}\n"
        return latex

    def _generate_background_layout(self, params: str, content: list, frame_title: str) -> str:
        """Generate background layout: image as background with content overlay"""
        clean_path = params.strip()
        if not clean_path.startswith(('media_files/', './', '/')):
            clean_path = f"media_files/{clean_path}"

        latex = f"\\begin{{frame}}{{{frame_title}}}\n"
        latex += f"\\frametitle{{{frame_title}}}\n"
        latex += "\\setbeamertemplate{background}{\n"
        latex += "\\begin{tikzpicture}[remember picture,overlay]\n"
        latex += f"\\node[opacity=0.3] at (current page.center) {{\\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{{{clean_path}}}}};\n"
        latex += "\\end{tikzpicture}\n"
        latex += "}\n\n"

        if content:
            content_items = self._format_content_items(content)
            if content_items:
                latex += "\\begin{beamercolorbox}[wd=\\paperwidth,ht=\\paperheight,center]{}\n"
                latex += content_items + "\n"
                latex += "\\end{beamercolorbox}\n"

        latex += "\\end{frame}\n"
        return latex

    def _generate_topbottom_layout(self, params: str, content: list, frame_title: str) -> str:
        """Generate top-bottom layout: image at top, content at bottom"""
        clean_path = params.strip()
        if not clean_path.startswith(('media_files/', './', '/')):
            clean_path = f"media_files/{clean_path}"

        latex = f"\\begin{{frame}}{{{frame_title}}}\n"
        latex += f"\\frametitle{{{frame_title}}}\n"
        latex += "\\begin{center}\n"
        latex += f"\\includegraphics[width=0.8\\textwidth,keepaspectratio]{{{clean_path}}}\n"
        latex += "\\end{center}\n"
        latex += "\\vspace{0.5em}\n"

        if content:
            content_items = self._format_content_items(content)
            if content_items:
                latex += content_items + "\n"

        latex += "\\end{frame}\n"
        return latex

    def _generate_overlay_layout(self, params: str, content: list, frame_title: str) -> str:
        """Generate overlay layout: image with overlaid text blocks"""
        # Parse overlay parameters: image_path|x_pos,y_pos|text|x_pos,y_pos|text...
        parts = params.split('|')
        image_path = parts[0].strip()
        if not image_path.startswith(('media_files/', './', '/')):
            image_path = f"media_files/{image_path}"

        latex = f"\\begin{{frame}}{{{frame_title}}}\n"
        latex += f"\\frametitle{{{frame_title}}}\n"
        latex += "\\begin{tikzpicture}[remember picture,overlay]\n"
        latex += f"\\node at (current page.center) {{\\includegraphics[width=\\paperwidth,keepaspectratio]{{{image_path}}}}};\n"

        # Add overlay text blocks
        for i in range(1, len(parts)):
            if '|' not in parts[i]:
                continue
            coords, text = parts[i].split('|', 1)
            x, y = coords.split(',')
            latex += f"\\node[fill=black!70, text=white, rounded corners, anchor=north west] at ({x},{y}) {{\\textbf{{{text}}}}};\n"

        latex += "\\end{tikzpicture}\n"
        latex += "\\end{frame}\n"
        return latex

    def _generate_corner_layout(self, params: str, content: list, frame_title: str) -> str:
        """Generate corner layout: image in corner with content"""
        # Parse corner parameters: image_path|corner (tl, tr, bl, br)
        parts = params.split('|')
        image_path = parts[0].strip()
        corner = parts[1].strip() if len(parts) > 1 else 'br'

        if not image_path.startswith(('media_files/', './', '/')):
            image_path = f"media_files/{image_path}"

        # Position mapping
        positions = {
            'tl': ('0.05\\textwidth', '0.05\\textheight', 'north west'),
            'tr': ('0.95\\textwidth', '0.05\\textheight', 'north east'),
            'bl': ('0.05\\textwidth', '0.95\\textheight', 'south west'),
            'br': ('0.95\\textwidth', '0.95\\textheight', 'south east')
        }
        x, y, anchor = positions.get(corner, positions['br'])

        latex = f"\\begin{{frame}}{{{frame_title}}}\n"
        latex += f"\\frametitle{{{frame_title}}}\n"
        latex += "\\begin{tikzpicture}[remember picture,overlay]\n"
        latex += f"\\node[anchor={anchor}] at ({x},{y}) {{\\includegraphics[width=0.25\\textwidth,keepaspectratio]{{{image_path}}}}};\n"
        latex += "\\end{tikzpicture}\n\n"

        if content:
            content_items = self._format_content_items(content)
            if content_items:
                latex += content_items + "\n"

        latex += "\\end{frame}\n"
        return latex



    def parse_latex_log(self, log_file: str) -> tuple:
        """
        Parse LaTeX log file to find exact error line and message.
        Handles various error types including "Undefined control sequence".
        """
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()

            line_num = None
            error_msg = ""
            error_context = []

            # Pattern 1: Undefined control sequence error
            undefined_ctrl_match = re.search(
                r'Undefined control sequence\.\s*<argument>\s*(.*?)\s*l\.(\d+)',
                log_content,
                re.DOTALL
            )
            if undefined_ctrl_match:
                line_num = int(undefined_ctrl_match.group(2))
                error_msg = f"Undefined control sequence: {undefined_ctrl_match.group(1).strip()[:100]}"
                print(f"Found undefined control sequence error at line {line_num}: {error_msg}")
                return line_num, error_msg, self._get_error_context(log_content, line_num)

            # Pattern 2: Missing \item error
            missing_item_match = re.search(
                r'LaTeX Error: Something\'s wrong--perhaps a missing \\item\..*?l\.(\d+)',
                log_content,
                re.DOTALL
            )
            if missing_item_match:
                line_num = int(missing_item_match.group(1))
                error_msg = "Missing \\item in list environment"
                print(f"Found missing \\item error at line {line_num}")
                return line_num, error_msg, self._get_error_context(log_content, line_num)

            # Pattern 3: "Not allowed in LR mode" error
            lr_mode_match = re.search(
                r'LaTeX Error: Not allowed in LR mode\..*?l\.(\d+)',
                log_content,
                re.DOTALL
            )
            if lr_mode_match:
                line_num = int(lr_mode_match.group(1))
                error_msg = "Not allowed in LR mode - verbatim or special command in wrong place"
                print(f"Found LR mode error at line {line_num}")
                return line_num, error_msg, self._get_error_context(log_content, line_num)

            # Pattern 4: Extra } or forgotten \endgroup
            extra_brace_match = re.search(
                r'Extra \}, or forgotten \\endgroup\.\s*l\.(\d+)',
                log_content,
                re.DOTALL
            )
            if extra_brace_match:
                line_num = int(extra_brace_match.group(1))
                error_msg = "Extra } or forgotten \\endgroup - check for unbalanced braces"
                print(f"Found brace error at line {line_num}")
                return line_num, error_msg, self._get_error_context(log_content, line_num)

            # Pattern 5: Standard LaTeX error format
            error_pattern = r'! (.*?)\nl\.(\d+)\s*\n(.*?)(?=\n! |\n\*\*\* |$)'
            matches = list(re.finditer(error_pattern, log_content, re.DOTALL))

            if matches:
                last_match = matches[-1]
                error_msg = last_match.group(1).strip()
                line_num = int(last_match.group(2))
                error_context = last_match.group(3).strip().split('\n')
                print(f"Found standard error at line {line_num}: {error_msg[:100]}")
                return line_num, error_msg, error_context

            # Pattern 6: File:line format
            file_line_pattern = r'\./([^:]+):(\d+):\s*(.*?)$'
            matches = list(re.finditer(file_line_pattern, log_content, re.MULTILINE))
            if matches:
                last_match = matches[-1]
                line_num = int(last_match.group(2))
                error_msg = last_match.group(3).strip()
                print(f"Found file-line error at line {line_num}: {error_msg[:100]}")
                return line_num, error_msg, self._get_error_context(log_content, line_num)

            # Pattern 7: Look for any line number reference in fatal error
            fatal_pattern = r'==> Fatal error occurred.*?l\.(\d+)'
            fatal_match = re.search(fatal_pattern, log_content, re.DOTALL)
            if fatal_match:
                line_num = int(fatal_match.group(1))
                # Try to find error message before this
                error_match = re.search(r'! (.*?)(?=\n)', log_content)
                if error_match:
                    error_msg = error_match.group(1).strip()
                else:
                    error_msg = "Fatal LaTeX error"
                print(f"Found fatal error at line {line_num}: {error_msg[:100]}")
                return line_num, error_msg, self._get_error_context(log_content, line_num)

            # Pattern 8: Generic error detection - find the last error in the log
            error_lines = re.findall(r'^! (.*?)$.*?l\.(\d+)', log_content, re.MULTILINE | re.DOTALL)
            if error_lines:
                last_error = error_lines[-1]
                error_msg = last_error[0].strip()
                line_num = int(last_error[1])
                print(f"Found generic error at line {line_num}: {error_msg[:100]}")
                return line_num, error_msg, self._get_error_context(log_content, line_num)

            print("No error pattern matched in log file")
            return None, "", []

        except Exception as e:
            print(f"Error parsing log file: {e}")
            import traceback
            traceback.print_exc()
            return None, "", []

    def _get_error_context(self, log_content: str, line_num: int) -> list:
        """Extract context around the error line from log content"""
        try:
            lines = log_content.split('\n')
            context = []

            for i, line in enumerate(lines):
                if f'l.{line_num}' in line:
                    start = max(0, i - 5)
                    end = min(len(lines), i + 10)
                    context = lines[start:end]
                    break

            return context
        except Exception as e:
            print(f"Error getting context: {e}")
            return []

    def reload_txt_from_tex(self, tex_file_path):
        """Reload the corresponding txt file from the updated tex file"""
        try:
            txt_file = tex_file_path.replace('.tex', '.txt')
            if os.path.exists(txt_file):
                # Reload the txt file to update the IDE
                self.load_file(txt_file)
                self.write(f"✓ Reloaded {os.path.basename(txt_file)} from updated TeX file\n", "green")
        except Exception as e:
            self.write(f"✗ Error reloading txt file: {str(e)}\n", "red")

    def _handle_bibliography_slide(self, content_lines: list, frame_title: str, slide_index: int) -> str:
        """Professionally handle a bibliography slide with clickable back-references."""
        import re

        config = BibliographyConfig()

        # Parse the bibliography
        full_content = '\n'.join(content_lines)

        # Extract header
        header_match = re.search(r'(\\begin\{thebibliography\}(?:\[[^\]]*\])?\{[^}]+\})', full_content)
        header = header_match.group(1) if header_match else "\\begin{thebibliography}{99}"

        # Extract footer
        footer = "\\end{thebibliography}"

        # Extract bibitems with their content
        pattern = r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem\{|\\end\{thebibliography\})'
        matches = re.findall(pattern, full_content, re.DOTALL)

        bib_items = []
        for key, content in matches:
            content = content.strip()
            raw_text = f"\\bibitem{{{key}}} {content}"
            bib_items.append(BibliographyItem(key, content, raw_text))

        if not bib_items:
            return self._generate_bibliography_fallback(content_lines, frame_title)

        # Build citation map - find where each citation appears
        for item in bib_items:
            slide_numbers = []
            for idx, slide in enumerate(self.slides, 1):
                if slide.get('_fully_masked', False):
                    continue

                # Search in content
                for content_line in slide.get('content', []):
                    if f'\\cite{{{item.citation_key}}}' in content_line:
                        if idx not in slide_numbers:
                            slide_numbers.append(idx)
                        break

                # Search in notes
                for note_line in slide.get('notes', []):
                    if f'\\cite{{{item.citation_key}}}' in note_line:
                        if idx not in slide_numbers:
                            slide_numbers.append(idx)
                        break

            for slide_num in slide_numbers:
                item.add_slide_reference(slide_num)

            # Log for debugging
            if slide_numbers:
                self.write(f"    • {item.citation_key}: cited on slides {slide_numbers}\n", "cyan")

        # Generate output
        total_items = len(bib_items)
        if total_items <= config.items_per_page:
            return self._generate_single_bibliography_frame(header, bib_items, footer, frame_title, config)
        else:
            return self._generate_multi_page_bibliography(header, bib_items, footer, frame_title, config, total_items)

    def _build_citation_map(self, bib_items: list):
        """
        Build a mapping of citation keys to slide numbers.
        This is called once per bibliography slide.
        """
        # Clear existing citation map for this bibliography
        self._current_citation_map = {}

        for item in bib_items:
            key = item.citation_key
            slide_numbers = []

            # Search through all slides for citations
            for idx, slide in enumerate(self.slides, 1):
                if slide.get('_fully_masked', False):
                    continue

                # Check content
                for content_line in slide.get('content', []):
                    if f'\\cite{{{key}}}' in content_line or f'\\cite{{{key}' in content_line:
                        if idx not in slide_numbers:
                            slide_numbers.append(idx)
                        break

                # Check notes
                for note_line in slide.get('notes', []):
                    if f'\\cite{{{key}}}' in note_line or f'\\cite{{{key}' in note_line:
                        if idx not in slide_numbers:
                            slide_numbers.append(idx)
                        break

            # Store the slide references in the bibliography item
            for slide_num in slide_numbers:
                item.add_slide_reference(slide_num)

            self._current_citation_map[key] = slide_numbers

    def _generate_single_bibliography_frame(self, header: str, bib_items: list, footer: str, frame_title: str, config) -> str:
        """Generate a single bibliography frame with clickable back-links."""
        clean_title = self.clean_frame_title_for_latex(frame_title)

        lines = [f"\\begin{{frame}}[allowframebreaks]{{{clean_title}}}"]
        lines.append(f"\\frametitle{{{clean_title}}}")
        lines.append(header)
        for item in bib_items:
            # Generate clickable back-links
            processed_item = self._add_clickable_back_references(item, config)
            lines.append(processed_item)
        lines.append(footer)
        lines.append("\\end{frame}")

        return '\n'.join(lines)

    def _generate_multi_page_bibliography(self, header: str, bib_items: list, footer: str, frame_title: str, config, total_items: int) -> str:
        """Generate multiple bibliography frames with clickable back-links and navigation."""
        items_per_page = config.items_per_page
        num_frames = (total_items + items_per_page - 1) // items_per_page

        all_frames = []
        for frame_num in range(num_frames):
            start_idx = frame_num * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)
            frame_items = bib_items[start_idx:end_idx]

            if num_frames > 1:
                page_title = f"{frame_title} (Page {frame_num + 1}/{num_frames})"
            else:
                page_title = frame_title

            clean_title = self.clean_frame_title_for_latex(page_title)

            lines = [f"\\begin{{frame}}[allowframebreaks]{{{clean_title}}}"]
            lines.append(f"\\frametitle{{{clean_title}}}")
            lines.append(header)
            for item in frame_items:
                # Generate clickable back-links
                processed_item = self._add_clickable_back_references(item, config)
                lines.append(processed_item)
            lines.append(footer)
            lines.append("\\end{frame}")

            all_frames.append('\n'.join(lines))

        if config.enable_navigation and num_frames > 1:
            all_frames = self._add_bibliography_navigation_links(all_frames, num_frames)

        return '\n\n'.join(all_frames)

    def _add_clickable_back_references(self, bib_item, config) -> str:
        """
        Add clickable back-references to a bibliography item.
        Creates hyperlinks from the slide numbers back to the actual slides.
        """
        if not bib_item.slide_references or not config.enable_back_references:
            return bib_item.raw_text

        # Create clickable hyperlinks for each slide number
        clickable_links = []
        for slide_num in bib_item.slide_references:
            # \hyperlink{page.X}{X} creates a clickable link to page X
            clickable_links.append(f"\\hyperlink{{page.{slide_num}}}{{{slide_num}}}")

        if len(clickable_links) > config.max_back_references_display:
            display_links = clickable_links[:config.max_back_references_display]
            remaining = len(clickable_links) - config.max_back_references_display
            links_text = ', '.join(display_links)
            back_ref = f"{links_text} +{remaining} more"
        else:
            back_ref = ', '.join(clickable_links)

        back_ref_text = f" \\hfill\\textcolor{{gray}}{{\\tiny [Cited on slides: {back_ref}]}}"

        # Add the back-reference to the raw text
        if bib_item.raw_text.endswith('\n'):
            return bib_item.raw_text.rstrip() + back_ref_text + '\n'
        else:
            return bib_item.raw_text.rstrip() + back_ref_text

    def _add_bibliography_navigation_links(self, frames: list, total_frames: int) -> list:
        """
        Add navigation links between bibliography frames.

        Args:
            frames: List of frame LaTeX strings
            total_frames: Total number of frames

        Returns:
            Modified frames with navigation links
        """
        import re

        result_frames = []

        for i, frame in enumerate(frames):
            # Extract the frametitle to add navigation after it
            nav_links = []

            # Previous page link
            if i > 0:
                nav_links.append(f"\\hyperlink{{page.{i}}}{{\\textcolor{{blue}}{{\\small ← Previous Page}}}}")

            # Page indicator
            nav_links.append(f"\\textcolor{{gray}}{{\\small Page {i+1}/{total_frames}}}")

            # Next page link
            if i < total_frames - 1:
                nav_links.append(f"\\hyperlink{{page.{i+2}}}{{\\textcolor{{blue}}{{\\small Next Page →}}}}")

            nav_bar = " \\hfill ".join(nav_links)

            # Insert navigation after the frametitle
            # Find the position after \frametitle
            frametitle_pattern = r'(\\frametitle\{[^}]*\})'
            match = re.search(frametitle_pattern, frame)

            if match:
                insert_pos = match.end()
                modified_frame = (
                    frame[:insert_pos] +
                    f"\n\\vspace{{0.5em}}\\begin{{center}}{nav_bar}\\end{{center}}\n" +
                    frame[insert_pos:]
                )
            else:
                # Fallback: add at the beginning of the frame content
                modified_frame = frame.replace(
                    f"\\begin{{frame}}",
                    f"\\begin{{frame}}\n\\vspace{{0.5em}}\\begin{{center}}{nav_bar}\\end{{center}}\n"
                )

            result_frames.append(modified_frame)

        return result_frames

    def _generate_bibliography_fallback(self, content_lines: list, frame_title: str) -> str:
        """
        Fallback method for when bibliography parsing fails.
        Preserves original content but adds allowframebreaks.
        """
        clean_title = self.clean_frame_title_for_latex(frame_title)

        lines = []
        lines.append(f"\\begin{{frame}}[allowframebreaks]{{{clean_title}}}")
        lines.append(f"\\frametitle{{{clean_title}}}")

        for line in content_lines:
            lines.append(line)

        lines.append("\\end{frame}")

        return '\n'.join(lines)

    def download_url_image(self, url: str) -> str:
        """Download image from URL and save to media_files directory"""
        import urllib.request
        import hashlib

        os.makedirs('media_files', exist_ok=True)

        # Create unique filename from URL
        url_hash = hashlib.md5(url.encode()).hexdigest()[:16]
        extension = url.split('.')[-1].split('?')[0].lower()
        if extension not in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
            extension = 'png'

        filename = f"url_image_{url_hash}.{extension}"
        filepath = os.path.join('media_files', filename)

        if not os.path.exists(filepath):
            try:
                urllib.request.urlretrieve(url, filepath)
                self.write(f"✓ Downloaded image from URL: {filename}\n", "green")
            except Exception as e:
                self.write(f"✗ Failed to download image: {e}\n", "red")
                return ""

        return filepath

# Add these classes right after the imports and before the BeamerSlideEditor class

class ScreenCaptureMethod:
    """Detect and manage screen capture methods for different environments"""

    WAYLAND = "wayland"
    X11 = "x11"
    UNKNOWN = "unknown"

    @classmethod
    def detect(cls):
        """Detect current display server and available capture methods"""
        session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        wayland_display = os.environ.get('WAYLAND_DISPLAY', '')
        x11_display = os.environ.get('DISPLAY', '')

        available_methods = []

        if session_type == 'wayland' or wayland_display:
            session_type = cls.WAYLAND
            if shutil.which('grim'):
                available_methods.append('grim')
            if shutil.which('slurp'):
                available_methods.append('slurp')
            if shutil.which('import'):
                available_methods.append('import_wayland')
        elif x11_display:
            session_type = cls.X11
            if shutil.which('import'):
                available_methods.append('import')
            if shutil.which('ffmpeg'):
                available_methods.append('ffmpeg')
        else:
            session_type = cls.UNKNOWN

        available_methods.append('pil_fallback')
        return session_type, available_methods


class WaylandScreenCapture:
    """Screen capture for Wayland using grim/slurp"""

    def __init__(self, parent=None, verbose=True):
        self.parent = parent
        self.verbose = verbose

    def write(self, text, color="white"):
        if self.parent and hasattr(self.parent, 'write'):
            self.parent.write(text, color)
        elif self.verbose:
            print(text)

    def capture_region(self, bbox, output_path):
        """Capture region using PIL ImageGrab with absolute path support"""
        try:
            from PIL import ImageGrab

            x, y, w, h = bbox
            # PIL expects (left, top, right, bottom)
            bbox_pil = (x, y, x + w, y + h)

            self.write(f"     PIL capturing: {bbox_pil}\n", "cyan")

            screenshot = ImageGrab.grab(bbox=bbox_pil)

            # Ensure directory exists for absolute path
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            screenshot.save(output_path)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                self.write(f"     PIL saved to: {output_path}\n", "green")
                return True
            else:
                self.write(f"     PIL save failed: file not created or empty\n", "red")
                return False

        except Exception as e:
            self.write(f"  PIL capture error: {e}\n", "red")
            import traceback
            traceback.print_exc()
            return False

    def capture_animation(self, bbox, frame_count, frame_delay, output_path, callback=None):
        """Capture animation frames on Wayland"""
        frames = []
        temp_dir = tempfile.mkdtemp()

        try:
            for i in range(frame_count):
                if callback and not callback(i, frame_count):
                    return False

                frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
                if self.capture_region(bbox, frame_path):
                    frames.append(frame_path)

                if i < frame_count - 1:
                    time.sleep(frame_delay)

            if frames:
                return self._create_gif(frames, output_path, frame_delay)
            return False

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _create_gif(self, frames, output_path, delay):
        """Create GIF from frames"""
        if shutil.which('ffmpeg'):
            try:
                delay_ms = int(delay * 100)
                cmd = [
                    'ffmpeg', '-y',
                    '-framerate', str(1.0/delay),
                    '-i', os.path.join(os.path.dirname(frames[0]), 'frame_%04d.png'),
                    '-vf', 'fps=10,scale=800:-1',
                    '-loop', '0',
                    output_path
                ]
                subprocess.run(cmd, capture_output=True, check=True, timeout=30)
                return True
            except:
                pass

        try:
            from PIL import Image
            images = [Image.open(f) for f in frames]
            if images:
                delay_ms = int(delay * 1000)
                images[0].save(output_path, save_all=True, append_images=images[1:],
                              duration=delay_ms, loop=0)
                return True
        except:
            pass

        return False


class X11ScreenCapture:
    """Screen capture for X11 using import or ffmpeg"""

    def __init__(self, parent=None, verbose=True):
        self.parent = parent
        self.verbose = verbose

    def write(self, text, color="white"):
        if self.parent and hasattr(self.parent, 'write'):
            self.parent.write(text, color)
        elif self.verbose:
            print(text)

    def capture_region(self, bbox, output_path):
        """Capture region using best X11 method"""
        x, y, w, h = bbox

        # Method 1: import (ImageMagick)
        if shutil.which('import'):
            try:
                cmd = ['import', '-window', 'root', '-crop', f'{w}x{h}+{x}+{y}', output_path]
                result = subprocess.run(cmd, capture_output=True, timeout=10)
                if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    self.write("  ✓ import capture successful\n", "green")
                    return True
            except Exception as e:
                self.write(f"  import capture error: {e}\n", "yellow")

        # Method 2: ffmpeg x11grab
        if shutil.which('ffmpeg'):
            try:
                display = os.environ.get('DISPLAY', ':0')
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'x11grab',
                    '-framerate', '30',
                    '-video_size', f'{w}x{h}',
                    '-i', f'{display}+{x},{y}',
                    '-vframes', '1',
                    '-update', '1',
                    output_path
                ]
                result = subprocess.run(cmd, capture_output=True, timeout=15)
                if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    self.write("  ✓ ffmpeg x11grab capture successful\n", "green")
                    return True
            except Exception as e:
                self.write(f"  ffmpeg capture error: {e}\n", "yellow")

        return False

    def capture_animation(self, bbox, frame_count, frame_delay, output_path, callback=None):
        """Capture animation frames on X11"""
        frames = []
        temp_dir = tempfile.mkdtemp()

        try:
            for i in range(frame_count):
                if callback and not callback(i, frame_count):
                    return False

                frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
                if self.capture_region(bbox, frame_path):
                    frames.append(frame_path)

                if i < frame_count - 1:
                    time.sleep(frame_delay)

            if frames:
                return self._create_gif(frames, output_path, frame_delay)
            return False

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _create_gif(self, frames, output_path, delay):
        """Create GIF from frames"""
        if shutil.which('ffmpeg'):
            try:
                cmd = [
                    'ffmpeg', '-y',
                    '-framerate', str(1.0/delay),
                    '-i', os.path.join(os.path.dirname(frames[0]), 'frame_%04d.png'),
                    '-vf', 'fps=10,scale=800:-1',
                    '-loop', '0',
                    output_path
                ]
                subprocess.run(cmd, capture_output=True, check=True, timeout=30)
                return True
            except:
                pass

        try:
            from PIL import Image
            images = [Image.open(f) for f in frames]
            if images:
                delay_ms = int(delay * 1000)
                images[0].save(output_path, save_all=True, append_images=images[1:],
                              duration=delay_ms, loop=0)
                return True
        except:
            pass

        return False


class PILFallbackCapture:
    """Fallback screen capture using PIL (works everywhere)"""

    def __init__(self, parent=None, verbose=True):
        self.parent = parent
        self.verbose = verbose

    def write(self, text, color="white"):
        if self.parent and hasattr(self.parent, 'write'):
            self.parent.write(text, color)
        elif self.verbose:
            print(text)

    def capture_region(self, bbox, output_path):
        """Capture region using PIL ImageGrab"""
        try:
            from PIL import ImageGrab

            x, y, w, h = bbox
            bbox_pil = (x, y, x + w, y + h)

            screenshot = ImageGrab.grab(bbox=bbox_pil)
            screenshot.save(output_path)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                self.write("  ✓ PIL fallback capture successful\n", "green")
                return True
            return False

        except Exception as e:
            self.write(f"  PIL capture error: {e}\n", "red")
            return False

    def capture_animation(self, bbox, frame_count, frame_delay, output_path, callback=None):
        """Capture animation using PIL"""
        try:
            from PIL import Image, ImageGrab

            frames = []
            for i in range(frame_count):
                if callback and not callback(i, frame_count):
                    return False

                x, y, w, h = bbox
                bbox_pil = (x, y, x + w, y + h)
                screenshot = ImageGrab.grab(bbox=bbox_pil)
                frames.append(screenshot)

                if i < frame_count - 1:
                    time.sleep(frame_delay)

            if frames:
                delay_ms = int(frame_delay * 1000)
                frames[0].save(output_path, save_all=True, append_images=frames[1:],
                              duration=delay_ms, loop=0)
                self.write(f"  ✓ PIL animation captured ({len(frames)} frames)\n", "green")
                return True
            return False

        except Exception as e:
            self.write(f"  PIL animation error: {e}\n", "red")
            return False


class UnifiedScreenCapture:
    """Unified screen capture that automatically selects the best method"""

    def __init__(self, parent=None, verbose=True):
        self.parent = parent
        self.verbose = verbose
        self.session_type = None
        self.available_methods = []
        self.wayland_capture = None
        self.x11_capture = None
        self.pil_capture = PILFallbackCapture(parent, verbose)

        self._detect_environment()
        self._initialize_captures()

    def _detect_environment(self):
        """Detect the current display environment"""
        self.session_type, self.available_methods = ScreenCaptureMethod.detect()
        if self.parent and hasattr(self.parent, 'write'):
            self.parent.write(f"\n📺 Display: {self.session_type}\n", "cyan")
            self.parent.write(f"   Methods: {', '.join(self.available_methods)}\n", "cyan")

    def _initialize_captures(self):
        """Initialize appropriate capture handlers"""
        if self.session_type == ScreenCaptureMethod.WAYLAND:
            self.wayland_capture = WaylandScreenCapture(self.parent, self.verbose)
        elif self.session_type == ScreenCaptureMethod.X11:
            self.x11_capture = X11ScreenCapture(self.parent, self.verbose)

    def write(self, text, color="white"):
        if self.parent and hasattr(self.parent, 'write'):
            self.parent.write(text, color)
        elif self.verbose:
            print(text)

    def get_screen_geometry(self):
        """
        Get the bounding box of ALL monitors combined.
        Returns (min_x, min_y, total_width, total_height)
        """
        try:
            from screeninfo import get_monitors

            monitors = get_monitors()
            if monitors and len(monitors) > 0:
                # Calculate the bounding box of all monitors
                min_x = min(m.x for m in monitors)
                min_y = min(m.y for m in monitors)
                max_x = max(m.x + m.width for m in monitors)
                max_y = max(m.y + m.height for m in monitors)

                total_width = max_x - min_x
                total_height = max_y - min_y

                if self.parent and hasattr(self.parent, 'write'):
                    self.parent.write(f"   Detected {len(monitors)} monitor(s):\n", "cyan")
                    for i, m in enumerate(monitors):
                        self.parent.write(f"     Monitor {i+1}: {m.width}x{m.height} at ({m.x}, {m.y})\n", "cyan")
                    self.parent.write(f"   Total area: {total_width}x{total_height}\n", "cyan")

                return (min_x, min_y, total_width, total_height)
        except Exception as e:
            if self.parent and hasattr(self.parent, 'write'):
                self.parent.write(f"   screeninfo error: {e}, falling back to tkinter\n", "yellow")

        # Fallback: try to get combined geometry using tkinter
        try:
            import tkinter as tk

            # Create a temporary root window
            root = tk.Tk()
            root.withdraw()

            # Get the geometry of the entire virtual desktop
            # This works on Windows and some X11 configurations
            try:
                # Try to get virtual screen dimensions
                width = root.winfo_screenwidth()
                height = root.winfo_screenheight()

                # On multi-monitor systems, winfo_screenwidth/height may return combined size
                # But we need to find the offset as well
                x = root.winfo_x()
                y = root.winfo_y()

                root.destroy()

                if self.parent and hasattr(self.parent, 'write'):
                    self.parent.write(f"   Fallback geometry: {width}x{height} at ({x}, {y})\n", "yellow")

                return (x, y, width, height)
            except:
                root.destroy()
                raise
        except Exception as e:
            if self.parent and hasattr(self.parent, 'write'):
                self.parent.write(f"   tkinter fallback error: {e}\n", "yellow")

        # Ultimate fallback: assume single monitor at 0,0
        return (0, 0, 1920, 1080)

    def capture_region(self, bbox, output_path):
        """Capture screen region using best available method"""
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else 'media_files',
                   exist_ok=True)

        if self.session_type == ScreenCaptureMethod.WAYLAND and self.wayland_capture:
            if self.wayland_capture.capture_region(bbox, output_path):
                return True

        if self.session_type == ScreenCaptureMethod.X11 and self.x11_capture:
            if self.x11_capture.capture_region(bbox, output_path):
                return True

        return self.pil_capture.capture_region(bbox, output_path)

    def capture_animation(self, bbox, frame_count, frame_delay, output_path, callback=None):
        """Capture animation frames"""
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else 'media_files',
                   exist_ok=True)

        if self.session_type == ScreenCaptureMethod.WAYLAND and self.wayland_capture:
            if self.wayland_capture.capture_animation(bbox, frame_count, frame_delay,
                                                       output_path, callback):
                return True

        if self.session_type == ScreenCaptureMethod.X11 and self.x11_capture:
            if self.x11_capture.capture_animation(bbox, frame_count, frame_delay,
                                                   output_path, callback):
                return True

        return self.pil_capture.capture_animation(bbox, frame_count, frame_delay,
                                                   output_path, callback)

#-----------------------------------------------Help Functions --------------------------------------------
def modify_preamble_for_notes_mode(tex_content: str, mode: str) -> str:
    """
    Modify preamble based on notes mode while preserving original content.

    Args:
        tex_content: Original TEX content
        mode: 'slides', 'notes', or 'both'
    Returns:
        Modified TEX content
    """
    # First find document begin position
    doc_pos = tex_content.find("\\begin{document}")
    if doc_pos == -1:
        return tex_content

    # Split content into preamble and document
    preamble = tex_content[:doc_pos]
    document = tex_content[doc_pos:]

    # Define notes configurations
    notes_configs = {
        "slides": "\\setbeameroption{hide notes}",
        "notes": "\\setbeameroption{show only notes}",
        "both": "\\setbeameroption{show notes on second screen=right}"
    }

    # Remove any existing notes configurations
    preamble = re.sub(r'\\setbeameroption{[^}]*}', '', preamble)

    # Ensure pgfpages package
    if "\\usepackage{pgfpages}" not in preamble:
        preamble = preamble.rstrip() + "\n\\usepackage{pgfpages}\n"

    # Add appropriate notes configuration
    notes_config = notes_configs.get(mode, notes_configs['both'])
    preamble = preamble.rstrip() + f"\n\n% Notes configuration\n{notes_config}\n"

    # Add template style
    preamble += "\\setbeamertemplate{note page}{\\pagecolor{yellow!5}\\insertnote}\n"

    return preamble + document

def compile_with_notes_mode(input_file: str, mode: str, keep_temp: bool = False) -> str:
    """
    Compile TEX file with specified notes mode.

    Args:
        input_file: Path to input TEX file
        mode: 'slides', 'notes', or 'both'
        keep_temp: Whether to keep temporary files
    Returns:
        Path to generated PDF
    """
    try:
        # Create temp directory for compilation
        temp_dir = tempfile.mkdtemp()
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        temp_tex = os.path.join(temp_dir, f"{base_name}_{mode}.tex")
        output_pdf = os.path.join(temp_dir, f"{base_name}_{mode}.pdf")

        # Read original content
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Modify content for notes mode
        modified_content = modify_preamble_for_notes_mode(content, mode)

        # Write modified content to temp file
        with open(temp_tex, 'w', encoding='utf-8') as f:
            f.write(modified_content)

        # Copy required media files to temp directory
        media_dir = os.path.join(os.path.dirname(input_file), 'media_files')
        if os.path.exists(media_dir):
            temp_media = os.path.join(temp_dir, 'media_files')
            shutil.copytree(media_dir, temp_media)

        # Compile document
        os.chdir(temp_dir)
        for _ in range(2):  # Two passes for references
            subprocess.run(['pdflatex', '-interaction=nonstopmode', temp_tex],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Move final PDF to original directory
        final_pdf = os.path.join(os.path.dirname(input_file), f"{base_name}_{mode}.pdf")
        shutil.copy2(output_pdf, final_pdf)

        return final_pdf

    finally:
        if not keep_temp:
            shutil.rmtree(temp_dir, ignore_errors=True)







#---------------------------------------------------------------------------------


def verify_pymupdf_installation():
    """
    Verify PyMuPDF is installed correctly and usable.
    """
    try:
        import fitz
        # Try to access version info
        version = fitz.version[0]
        print(f"PyMuPDF version: {version}")

        # Try to create a simple test document
        test_doc = fitz.open()  # Creates an empty PDF
        test_doc.new_page()     # Adds a page
        test_doc.close()        # Closes the document

        print("✓ PyMuPDF verification successful")
        return True
    except Exception as e:
        print(f"PyMuPDF verification failed: {str(e)}")
        return False

def get_pymupdf_info():
    """
    Get detailed information about PyMuPDF installation.
    """
    try:
        import fitz
        return {
            'version': fitz.version[0],
            'binding_version': fitz.version[1],
            'build_date': fitz.version[2],
            'lib_path': fitz.__file__
        }
    except Exception as e:
        return f"Error getting PyMuPDF info: {str(e)}"

def import_required_packages():
    """
    Import all required packages with proper error handling and verification.
    """
    try:
        # First verify PyMuPDF
        if not verify_pymupdf_installation():
            raise ImportError("PyMuPDF installation verification failed")

        # Now import everything else
        import tkinter as tk
        from PIL import Image, ImageDraw, ImageTk
        import customtkinter as ctk
        from tkinter import ttk, filedialog, messagebox, simpledialog
        import screeninfo
        import requests
        import cv2
        import yt_dlp
        import fitz

        modules = {
            'tk': tk,
            'Image': Image,
            'ImageDraw': ImageDraw,
            'ImageTk': ImageTk,
            'ctk': ctk,
            'ttk': ttk,
            'fitz': fitz,
            'screeninfo': screeninfo,
            'requests': requests,
            'cv2': cv2,
            'yt_dlp': yt_dlp
        }

        # Print success message with version info
        print(f"\nSuccessfully imported all packages:")
        print(f"PyMuPDF version: {fitz.version[0]}")
        print(f"PIL version: {Image.__version__}")
        print(f"OpenCV version: {cv2.__version__}")

        return modules

    except Exception as e:
        print(f"Error importing required packages: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

def convert_beamer_tex_to_simple_text(tex_file_path):
    """
    Convert Beamer .tex file to simple text format with error tracking.
    Returns tuple (output_path, errors_list) where errors_list contains
    (line_number, error_message, context) for each error found.
    """
    import re
    from pathlib import Path

    errors = []

    def add_error(line_num, error_msg, context_line):
        """Record an error with line number for later editing"""
        errors.append({
            'line': line_num,
            'message': error_msg,
            'context': context_line
        })
        print(f"  ⚠ Line {line_num}: {error_msg}")

    try:
        with open(tex_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            tex_content = ''.join(lines)

        # Create output path
        tex_path = Path(tex_file_path)
        output_path = tex_path.parent / f"{tex_path.stem}_converted.txt"

        # Validate the TeX content line by line
        brace_stack = []
        in_math = False
        dollar_count = 0

        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('%'):
                continue

            # Check for unbalanced braces
            for char in line:
                if char == '{':
                    brace_stack.append(('{', i))
                elif char == '}':
                    if brace_stack:
                        brace_stack.pop()
                    else:
                        add_error(i, "Unmatched closing brace '}'", line_stripped[:80])

            # Check for unbalanced math mode
            dollar_count += line.count('$') - line.count('\\$')
            if dollar_count % 2 != 0:
                add_error(i, "Unbalanced math mode (odd number of $)", line_stripped[:80])

        if brace_stack:
            add_error(brace_stack[0][1], f"Unclosed brace(s): {len(brace_stack)} remaining", "")

        # Extract the document body
        doc_match = re.search(r'\\begin{document}(.*?)\\end{document}', tex_content, re.DOTALL)
        if not doc_match:
            add_error(1, "No \\begin{document} found in TeX file", "")
            raise ValueError("No document body found in TeX file")

        document_body = doc_match.group(1)

        # Find all frames with line number tracking
        frame_pattern = r'\\begin\{frame\}(?:\[[^\]]*\])?(?:\{([^}]*)\})?(?:\{([^}]*)\})?(.*?)\\end\{frame\}'
        frames = list(re.finditer(frame_pattern, document_body, re.DOTALL))

        if not frames:
            add_error(1, "No frames found in document", "")
            return None

        slides = []
        slide_count = 0

        for frame_match in frames:
            slide_count += 1
            title = frame_match.group(1) or f"Slide {slide_count}"
            subtitle = frame_match.group(2) or ""
            frame_content = frame_match.group(3).strip()

            # Skip title page
            if '\\titlepage' in frame_content:
                continue

            # Build the slide content exactly as it appears
            content_lines = []

            if subtitle:
                content_lines.append(f"\\textbf{{{title}}} — {subtitle}")
            else:
                content_lines.append(f"\\textbf{{{title}}}")

            # Add frame content preserving all LaTeX
            for line in frame_content.split('\n'):
                line = line.strip()
                if line:
                    content_lines.append(line)

            slides.append({
                'title': title,
                'content': content_lines,
                'notes': []
            })

        # Write to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            for slide in slides:
                f.write(f"\\title {slide['title']}\n")
                f.write("\\begin{Content}\n")
                f.write("\\None\n")
                for content_line in slide['content']:
                    # Escape any problematic characters for the IDE format
                    escaped_line = content_line.replace('\\&', '&')  # Keep as is
                    f.write(f"{escaped_line}\n")
                f.write("\\end{Content}\n")
                f.write("\\begin{Notes}\n")
                f.write("% No notes for this slide\n")
                f.write("\\end{Notes}\n")
                f.write("\n")

        print(f"✓ Converted {len(slides)} slides from {tex_file_path}")

        if errors:
            print(f"\n⚠ Found {len(errors)} issue(s) during conversion:")
            for err in errors:
                print(f"   Line {err['line']}: {err['message']}")

        return output_path, errors

    except Exception as e:
        print(f"Error converting TeX file: {e}")
        import traceback
        traceback.print_exc()
        return None, []


def update_installation():
    """Silently update installed files if running from a newer version"""
    try:
        system, paths = get_installation_paths()
        current_path = Path(__file__).resolve()

        # Determine installation directory
        install_dir = paths['share'] / 'bsg-ide' if system != "Windows" else paths['bin']

        # If running from an installation directory, no need to update
        if str(current_path).startswith(str(install_dir)):
            return True

        # Get installed version info
        installed_version = "0.0.0"
        version_file = install_dir / "version.txt"
        if version_file.exists():
            installed_version = version_file.read_text().strip()

        # Compare with current version
        current_version = getattr(BeamerSlideEditor, '__version__', "2.4")

        # Always update files if versions don't match
        if installed_version != current_version:
            print(f"Updating BSG-IDE from version {installed_version} to {current_version}")

            # Create directories if they don't exist
            os.makedirs(install_dir, exist_ok=True)
            os.makedirs(paths['bin'], exist_ok=True)

            # Copy current files to installation directory
            current_dir = current_path.parent
            required_files = [
                'BSG_IDE.py',
                'BeamerSlideGenerator.py',
                'requirements.txt'
            ]

            for file in required_files:
                src = current_dir / file
                if src.exists():
                    shutil.copy2(src, install_dir)
                    print(f"Updated {file}")

            # Update version file
            version_file.write_text(current_version)

            # Update launcher script
            launcher_script = create_bsg_launcher(install_dir, paths)

            if system == "Linux":
                launcher_path = paths['bin'] / 'bsg-ide'
                launcher_path.write_text(launcher_script)
                launcher_path.chmod(0o755)

            elif system == "Windows":
                batch_content = f"""@echo off
set PYTHONPATH={install_dir};%PYTHONPATH%
pythonw "{install_dir}\\BSG_IDE.py" %*
"""
                batch_path = paths['bin'] / 'bsg-ide.bat'
                batch_path.write_text(batch_content)

            # Update desktop entry if needed
            if system == "Linux":
                desktop_entry = f"""[Desktop Entry]
Version={current_version}
Type=Application
Name=BSG-IDE
Comment=Beamer Slide Generator IDE
Exec={paths['bin']}/bsg-ide
Icon=bsg-ide
Terminal=false
Categories=Office;Development;Education;
Keywords=presentation;latex;beamer;slides;
StartupWMClass=bsg-ide
"""
                desktop_path = paths['apps'] / 'bsg-ide.desktop'
                desktop_path.write_text(desktop_entry)
                desktop_path.chmod(0o755)

            # Ensure Python paths are correct
            setup_python_paths()

            print("Update completed successfully")

        return True

    except Exception as e:
        print(f"Warning: Update check failed: {str(e)}")
        traceback.print_exc()
        return False


# Function to replace console prompts with GUI dialogs
def handle_long_institution(parent, institution_name):
    """Handle long institution name with GUI dialog"""
    dialog = InstitutionNameDialog(parent, institution_name)
    parent.wait_window(dialog)
    return dialog.short_name

def handle_media_selection(parent, title, content):
    """Handle media selection with GUI dialog"""
    dialog = MediaSelectionDialog(parent, title, content)
    parent.wait_window(dialog)
    return dialog.result
#----------------------------------------------------------Install in local bin -----------------------------------

def setup_python_paths():
    """Setup Python paths for imports"""
    import sys
    import site
    from pathlib import Path

    # Get user's home directory
    home = Path.home()

    # Add common installation paths
    paths = [
        home / '.local' / 'lib' / 'bsg-ide',  # Linux/macOS user installation
        home / '.local' / 'bin',              # Linux/macOS binaries
        home / 'Library' / 'Application Support' / 'BSG-IDE',  # macOS
        Path(site.getusersitepackages()) / 'bsg-ide',  # Windows user site-packages
    ]

    # Add installation directory to PYTHONPATH
    for path in paths:
        str_path = str(path)
        if path.exists() and str_path not in sys.path:
            sys.path.insert(0, str_path)

def create_bsg_launcher(install_dir: Path, paths: dict) -> str:
    """Create launcher script with updated terminal handling"""
    launcher_script = f"""#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import tkinter as tk
import customtkinter as ctk

# Add all possible installation paths
INSTALL_PATHS = [
    '{install_dir}',
    '{paths["bin"]}',
    str(Path.home() / '.local' / 'lib' / 'bsg-ide'),
    str(Path.home() / '.local' / 'bin'),
    str(Path.home() / 'Library' / 'Application Support' / 'BSG-IDE'),
]

# Add paths to Python path
for path in INSTALL_PATHS:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

# Import the terminal module
from BSG_terminal import InteractiveTerminal, SimpleRedirector

# Import and run main program
try:
    #from BSG_IDE import BeamerSlideEditor

    # Create application instance
    app = BeamerSlideEditor()

    # Redirect stdout and stderr to app's terminal after it's created
    if hasattr(app, 'terminal'):
        sys.stdout = SimpleRedirector(app.terminal)
        sys.stderr = SimpleRedirector(app.terminal, "red")

    # Start the application
    app.mainloop()

except Exception as e:
    import traceback
    print(f"Error starting BSG-IDE: {str(e)}")
    traceback.print_exc()
    if sys.platform != "win32":
        input("Press Enter to exit...")
"""
    return launcher_script


def setup_desktop_entry():
    """Create desktop entry and set up icons"""
    try:
        # Get user's home directory
        home_dir = Path.home()

        # Create necessary directories
        apps_dir = home_dir / '.local' / 'share' / 'applications'
        apps_dir.mkdir(parents=True, exist_ok=True)

        icon_base = home_dir / '.local' / 'share' / 'icons' / 'hicolor'

        # Copy icon to appropriate locations for different resolutions
        icon_sizes = ['16x16', '32x32', '48x48', '64x64', '128x128', '256x256']

        # First, ensure we have the source icon
        source_icon = (Path(__file__).parent / 'icons' / 'bsg-ide.png')
        if not source_icon.exists():
            source_icon = Path(__file__).parent / 'bsg-ide.png'

        if not source_icon.exists():
            print("Warning: Could not find source icon file")
            return False

        for size in icon_sizes:
            icon_dir = icon_base / size / 'apps'
            icon_dir.mkdir(parents=True, exist_ok=True)
            icon_path = icon_dir / 'bsg-ide.png'

            try:
                shutil.copy2(source_icon, icon_path)
                print(f"✓ Copied icon for size {size}")
            except Exception as e:
                print(f"Warning: Could not copy icon for size {size}: {e}")

        # Create desktop entry
        desktop_entry = """[Desktop Entry]
Version=1.0
Type=Application
Name=BSG-IDE
Comment=Beamer Slide Generator IDE
Exec=bsg-ide
Icon=bsg-ide
Terminal=false
Categories=Office;Development;Education;
Keywords=presentation;latex;beamer;slides;
StartupWMClass=bsg-ide
"""

        # Write desktop entry file
        desktop_path = apps_dir / 'bsg-ide.desktop'
        desktop_path.write_text(desktop_entry)
        desktop_path.chmod(0o755)

        # Update icon cache
        try:
            subprocess.run(['gtk-update-icon-cache', '--force', '--quiet', str(icon_base)])
            print("✓ Icon cache updated")
        except Exception as e:
            print(f"Warning: Could not update icon cache: {e}")

        print("✓ Desktop entry created successfully")
        return True

    except Exception as e:
        print(f"Error creating desktop entry: {str(e)}")
        return False

def verify_desktop_entry():
    """Verify desktop entry and icon installation"""
    try:
        home_dir = Path.home()
        desktop_entry = home_dir / '.local' / 'share' / 'applications' / 'bsg-ide.desktop'
        icon_path = home_dir / '.local' / 'share' / 'icons' / 'hicolor' / '128x128' / 'apps' / 'bsg-ide.png'

        if not desktop_entry.exists() or not icon_path.exists():
            print("Desktop entry or icon missing. Setting up...")
            return setup_desktop_entry()

        return True

    except Exception as e:
        print(f"Error verifying desktop entry: {str(e)}")
        return False



#-------------------------------------------------pympress installation -----------------------------
def setup_pympress():
    """Verify pympress installation using system packages"""
    try:
        # Check if pympress works by importing required modules
        def check_pympress_deps():
            try:
                import gi
                import cairo
                gi.require_version('Gtk', '3.0')
                from gi.repository import Gtk
                import pympress
                return True
            except ImportError:
                return False

        if check_pympress_deps():
            print("✓ Pympress and dependencies already installed")
            return True

        print("Installing pympress and dependencies using pip...")

        # Install using pip (system level)
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--user", "pympress"
            ])
            print("✓ pympress installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install pympress: {e}")
            return False

    except Exception as e:
        print(f"✗ Error setting up pympress: {str(e)}")
        traceback.print_exc()
        return False

def launch_pympress(pdf_path):
    """Launch pympress with proper environment setup"""
    try:
        # Ensure absolute path
        abs_pdf_path = os.path.abspath(pdf_path)

        # Set up environment variables
        env = os.environ.copy()

        # Add GI typelib path if needed
        typelib_paths = [
            '/usr/lib/girepository-1.0',
            '/usr/local/lib/girepository-1.0',
            '/usr/lib/x86_64-linux-gnu/girepository-1.0'
        ]

        existing_typelib = env.get('GI_TYPELIB_PATH', '').split(':')
        new_typelib = ':'.join(filter(os.path.exists, typelib_paths + existing_typelib))
        env['GI_TYPELIB_PATH'] = new_typelib

        # Try to launch pympress
        if sys.platform.startswith('win'):
            subprocess.Popen(['pympress', abs_pdf_path], shell=True, env=env)
        else:
            # Try different possible pympress locations
            pympress_paths = [
                shutil.which('pympress'),
                '/usr/local/bin/pympress',
                '/usr/bin/pympress',
                os.path.expanduser('~/.local/bin/pympress')
            ]

            for path in filter(None, pympress_paths):
                if os.path.exists(path):
                    subprocess.Popen([path, abs_pdf_path], env=env)
                    return True

            raise FileNotFoundError("pympress executable not found")

    except Exception as e:
        print(f"Error launching pympress: {str(e)}")
        traceback.print_exc()
        return False
#-------------------------------------------------------------------------
def create_icon(install_dir: Path) -> bool:
    """Create icon with airis4D logo and BSG-IDE text below"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import os

        # Create icons directory
        icons_dir = install_dir / 'icons'
        os.makedirs(icons_dir, exist_ok=True)

        # Icon sizes needed for different platforms
        sizes = [16, 32, 48, 64, 128, 256]

        # Create base icon image (make it square)
        size = 256  # Base size
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw airis4D logo - maintaining exact proportions from ASCII art
        logo_height = size * 0.6  # Logo takes up 60% of height
        margin = size * 0.2  # 20% margin from top

        # Calculate logo dimensions
        logo_width = logo_height * 0.8  # Maintain aspect ratio

        # Logo starting position
        start_x = (size - logo_width) / 2
        start_y = margin

        # Draw the triangle (airis4D logo)
        triangle_points = [
            (start_x, start_y + logo_height),  # Bottom left
            (start_x + logo_width/2, start_y), # Top
            (start_x + logo_width, start_y + logo_height)  # Bottom right
        ]

        # Draw outer triangle
        draw.polygon(triangle_points, fill=(255, 0, 0, 255))  # Red for outer triangle

        # Calculate inner triangle points (80% size of outer)
        inner_scale = 0.8
        inner_offset_x = (logo_width * (1 - inner_scale)) / 2
        inner_offset_y = (logo_height * (1 - inner_scale))
        inner_points = [
            (start_x + inner_offset_x, start_y + logo_height - inner_offset_y),
            (start_x + logo_width/2, start_y + inner_offset_y),
            (start_x + logo_width - inner_offset_x, start_y + logo_height - inner_offset_y)
        ]
        draw.polygon(inner_points, fill=(0, 0, 0, 255))  # Black for inner triangle

        # Add "BSG-IDE" text below logo
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(size * 0.15))
        except:
            font = ImageFont.load_default()

        text = "BSG-IDE"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (size - text_width) // 2
        text_y = start_y + logo_height + (size * 0.05)  # Small gap between logo and text
        draw.text((text_x, text_y), text, font=font, fill=(0, 0, 0, 255))

        # Save in different sizes
        for icon_size in sizes:
            resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            icon_path = icons_dir / f'bsg-ide_{icon_size}x{icon_size}.png'
            resized.save(icon_path, 'PNG')

            # For Linux, also save in appropriate hicolor directory
            if sys.platform.startswith('linux'):
                hicolor_path = Path.home() / '.local' / 'share' / 'icons' / 'hicolor' / f'{icon_size}x{icon_size}' / 'apps'
                os.makedirs(hicolor_path, exist_ok=True)
                resized.save(hicolor_path / 'bsg-ide.png', 'PNG')

        # Create .ico file for Windows
        if sys.platform.startswith('win'):
            icon_sizes = [(16,16), (32,32), (48,48), (256,256)]
            images = []
            for size in icon_sizes:
                resized = img.resize(size, Image.Resampling.LANCZOS)
                images.append(resized)
            ico_path = icons_dir / 'bsg-ide.ico'
            img.save(ico_path, format='ICO', sizes=icon_sizes)

        return True

    except Exception as e:
        print(f"Error creating icon: {str(e)}")
        traceback.print_exc()
        return False
#--------------------------------------------------------------------------
def setup_static_directory():
    """
    Create required static directory structure for PyMuPDF
    """
    print("Setting up static directory structure...")

    # Create required directories
    directories = [
        'static',
        'static/css',
        'static/js',
        'static/images'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

    # Create minimal required files
    minimal_files = {
        'static/css/style.css': '/* Minimal CSS */',
        'static/js/script.js': '// Minimal JS',
        'static/.keep': ''  # Empty file to ensure directory is tracked
    }

    for filepath, content in minimal_files.items():
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✓ Created file: {filepath}")



def check_windows_dependencies() -> None:
    """
    Check and setup dependencies for Windows.
    """
    # Check for MiKTeX or TeX Live
    if not (shutil.which('pdflatex') or os.path.exists(r'C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe')):
        print("\nLaTeX is not installed. Please install MiKTeX:")
        print("1. Visit: https://miktex.org/download")
        print("2. Download and install MiKTeX")
        print("3. Run this script again")
        sys.exit(1)

def check_linux_dependencies(system_commands: List[Tuple[str, str]]) -> None:
    """
    Check and setup dependencies for Linux.
    """
    missing_packages = []

    for cmd, packages in system_commands:
        if not shutil.which(cmd):
            missing_packages.append(packages)

    if missing_packages:
        print("\nSome system packages are missing. Installing...")
        try:
            # Try to detect package manager
            if shutil.which('apt'):
                install_cmd = ['sudo', 'apt', 'install', '-y']
            elif shutil.which('dnf'):
                install_cmd = ['sudo', 'dnf', 'install', '-y']
            elif shutil.which('pacman'):
                install_cmd = ['sudo', 'pacman', '-S', '--noconfirm']
            else:
                print("Could not detect package manager. Please install manually:")
                print(" ".join(missing_packages))
                sys.exit(1)

            for packages in missing_packages:
                subprocess.check_call(install_cmd + packages.split())
                print(f"✓ Installed {packages}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error installing system packages: {str(e)}")
            sys.exit(1)

def check_bsg_file() -> None:
    """
    Check for BeamerSlideGenerator.py and download if missing.
    """
    if not os.path.exists('BeamerSlideGenerator.py'):
        print("\nBeamerSlideGenerator.py not found. Downloading...")
        try:
            import requests
            # Replace with actual URL to your BeamerSlideGenerator.py
            url = "https://raw.githubusercontent.com/sajeethphilip/BeamerSlideGenerator/main/BeamerSlideGenerator.py"
            response = requests.get(url)
            response.raise_for_status()

            with open('BeamerSlideGenerator.py', 'w') as f:
                f.write(response.text)
            print("✓ BeamerSlideGenerator.py downloaded successfully")
        except Exception as e:
            print(f"✗ Error downloading BeamerSlideGenerator.py: {str(e)}")
            print("\nPlease manually download BeamerSlideGenerator.py and place it in the same directory.")
            sys.exit(1)

def create_footer(self) -> None:
    """Create footer with institution info and links"""
    # Footer frame with dark theme
    self.footer = ctk.CTkFrame(self)
    self.footer.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

    # Left side - Institution name
    inst_label = ctk.CTkLabel(
        self.footer,
        text="Artificial Intelligence Research and Intelligent Systems (airis4D)",
        font=("Arial", 12, "bold"),
        text_color="#4ECDC4"  # Using the same color scheme as the editor
    )
    inst_label.pack(side="left", padx=10)

    # Right side - Contact and GitHub links
    links_frame = ctk.CTkFrame(self.footer, fg_color="transparent")
    links_frame.pack(side="right", padx=10)

    # Contact link
    contact_button = ctk.CTkButton(
        links_frame,
        text="nsp@airis4d.com",
        command=lambda: webbrowser.open("mailto:nsp@airis4d.com"),
        fg_color="transparent",
        text_color="#FFB86C",  # Using the bracket color from syntax highlighting
        hover_color="#2F3542",
        height=20
    )
    contact_button.pack(side="left", padx=5)

    # Separator
    separator = ctk.CTkLabel(
        links_frame,
        text="|",
        text_color="#6272A4"  # Using comment color from syntax highlighting
    )
    separator.pack(side="left", padx=5)

    # GitHub link with small icon
    github_button = ctk.CTkButton(
        links_frame,
        text="GitHub",
        command=lambda: webbrowser.open("https://github.com/sajeethphilip/Beamer-Slide-Generator.git"),
        fg_color="transparent",
        text_color="#FFB86C",
        hover_color="#2F3542",
        height=20
    )
    github_button.pack(side="left", padx=5)

    # License info
    license_label = ctk.CTkLabel(
        links_frame,
        text="(Creative Commons License)",
        font=("Arial", 10),
        text_color="#6272A4"
    )
    license_label.pack(side="left", padx=5)

# Import BeamerSlideGenerator functions
try:
    from BeamerSlideGenerator import (
        get_beamer_preamble,
        process_media,
        generate_latex_code,
        download_youtube_video,
        construct_search_query,
        open_google_image_search
    )
except ImportError:
    print("Error: BeamerSlideGenerator.py must be in the same directory.")
    sys.exit(1)



def get_installation_paths():
    """Get platform-specific installation paths"""
    import platform
    import os
    from pathlib import Path
    import site
    import sys

    system = platform.system()
    paths = {}

    if os.geteuid() == 0:  # Running as root/sudo
        if system == "Linux":
            paths.update({
                'bin': Path('/usr/local/bin'),
                'share': Path('/usr/local/share'),
                'icons': Path('/usr/share/icons/hicolor'),
                'apps': Path('/usr/share/applications')
            })
        else:
            # For other systems when running as root/admin
            paths.update({
                'bin': Path(sys.prefix) / 'bin',
                'share': Path(sys.prefix) / 'share'
            })
    else:  # Running as normal user
        if system == "Linux":
            # Get user's local bin from PATH or create in ~/.local/bin
            user_bin = None
            for path in os.environ.get('PATH', '').split(os.pathsep):
                if '/.local/bin' in path and os.access(path, os.W_OK):
                    user_bin = Path(path)
                    break
            if not user_bin:
                user_bin = Path.home() / '.local' / 'bin'

            paths.update({
                'bin': user_bin,
                'share': Path.home() / '.local' / 'share',
                'icons': Path.home() / '.local' / 'share' / 'icons' / 'hicolor',
                'apps': Path.home() / '.local' / 'share' / 'applications'
            })

        elif system == "Windows":
            appdata = Path(os.getenv('APPDATA'))
            paths.update({
                'bin': appdata / 'BSG-IDE',
                'shortcut': appdata / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'BSG-IDE'
            })

        elif system == "Darwin":  # macOS
            paths.update({
                'app': Path.home() / 'Applications' / 'BSG-IDE.app',
                'contents': Path.home() / 'Applications' / 'BSG-IDE.app' / 'Contents',
                'bin': Path.home() / 'Applications' / 'BSG-IDE.app' / 'Contents' / 'MacOS',
                'resources': Path.home() / 'Applications' / 'BSG-IDE.app' / 'Contents' / 'Resources'
            })

    return system, paths

def check_installation():
    """Check if BSG-IDE is installed in the system"""
    system, paths = get_installation_paths()

    if system == "Linux":
        return (paths['bin'] / 'bsg-ide').exists()
    elif system == "Windows":
        return (paths['bin'] / 'bsg-ide.pyw').exists()
    elif system == "Darwin":
        return paths['app'].exists()
    return False
def make_executable(file_path):
    """Make file executable on Unix systems or create launcher on Windows"""
    import stat
    import platform

    system = platform.system()
    if system != "Windows":
        # Add executable permission for owner
        current = stat.S_IMODE(os.lstat(file_path).st_mode)
        os.chmod(file_path, current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    else:
        # For Windows, create a .bat launcher
        bat_path = file_path.parent / 'bsg-ide.bat'
        with open(bat_path, 'w') as f:
            f.write(f'@echo off\n"{sys.executable}" "{file_path}" %*')

def check_bsg_file():
    """
    Check for BeamerSlideGenerator.py and install if missing.
    """
    # Get the correct installation path based on platform
    import platform
    system = platform.system()

    if system == "Linux":
        install_lib = Path.home() / '.local' / 'lib' / 'bsg-ide'
    elif system == "Windows":
        install_lib = Path(os.getenv('APPDATA')) / 'BSG-IDE'
    else:  # macOS
        install_lib = Path.home() / 'Library' / 'Application Support' / 'BSG-IDE'

    install_lib.mkdir(parents=True, exist_ok=True)
    bsg_file = install_lib / 'BeamerSlideGenerator.py'

    if not bsg_file.exists():
        print("\nBeamerSlideGenerator.py not found in installation directory. Installing...")
        try:
            # First check if it exists in current directory
            current_bsg = Path('BeamerSlideGenerator.py')
            if current_bsg.exists():
                # Copy the file to installation directory
                shutil.copy2(current_bsg, bsg_file)
                print(f"✓ BeamerSlideGenerator.py installed to {bsg_file}")
            else:
                # Look in script's directory
                script_dir = Path(__file__).parent.resolve()
                script_bsg = script_dir / 'BeamerSlideGenerator.py'
                if script_dir.exists():
                    shutil.copy2(script_bsg, bsg_file)
                    print(f"✓ BeamerSlideGenerator.py installed to {bsg_file}")
                else:
                    print("✗ Error: BeamerSlideGenerator.py not found in current or script directory.")
                    print("Please ensure BeamerSlideGenerator.py is in the same directory as BSG_IDE.py")
                    sys.exit(1)
        except Exception as e:
            print(f"✗ Error installing BeamerSlideGenerator.py: {str(e)}")
            print("\nPlease manually copy BeamerSlideGenerator.py to:", bsg_file)
            sys.exit(1)
    else:
        print("✓ BeamerSlideGenerator.py is installed")

    # Also ensure the file is in the current working directory for direct script mode
    if not Path('BeamerSlideGenerator.py').exists():
        try:
            shutil.copy2(bsg_file, 'BeamerSlideGenerator.py')
        except Exception as e:
            print(f"Warning: Could not copy BeamerSlideGenerator.py to current directory: {e}")


#-------------------------------------INSTALLATION----------------------------
import os
import sys
import platform
import shutil
import subprocess
import json
from pathlib import Path
import site
import socket
import ctypes
from importlib import util

def main():
    """Main entry point for both source and installed runs"""
    try:
        # Setup paths first
        package_root, resources_dir = setup_paths()

        # Parse arguments
        import argparse
        parser = argparse.ArgumentParser(description='BSG-IDE - Beamer Slide Generator IDE')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--fix', action='store_true',
                          help='Fix installation issues')
        group.add_argument('--install', action='store_true',
                          help='Install BSG-IDE')
        group.add_argument('--verify', action='store_true',
                          help='Verify installation')

        args = parser.parse_args()

        if args.fix or args.install:
            #from installation import install_bsg_ide
            success = install_bsg_ide(fix_mode=args.fix)
            verify_installation()
            sys.exit(0 if success else 1)

        # Launch IDE

        app = BeamerSlideEditor()
        app.mainloop()

    except Exception as e:
        print(f"Error starting BSG-IDE: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


    except Exception as e:
        print(f"Error in main: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
#---------------------------------------------------------------------------------------
