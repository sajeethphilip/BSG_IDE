#!/usr/bin/env python3
"""
BeamerSlideGenerator.py
A tool for generating Beamer presentation slides with multimedia content.
Supports local files, URL downloads, and content-only slides.
"""
import math
import os,re
import time
import requests
import webbrowser
from PIL import Image
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from urllib.parse import urlparse, unquote
from pathlib import Path
import mimetypes
output_dir = ""
#--------------------------------------------------------------------------------------------------------
def set_terminal_io(term_io):
    """Set the terminal I/O object and verify it's working"""
    global terminal_io
    terminal_io = term_io
    # Verify terminal_io is working
    if terminal_io:
        terminal_io.write("Terminal I/O initialized\n", "green")
#--------------------------------------------------------------------------------------------------------

def verify_required_packages(preamble_content: str) -> list:
    """
    Verify required packages are present in preamble.
    Returns list of missing packages.
    """
    required_packages = {
        'tikz': '\\usepackage{tikz}',
        'graphicx': '\\usepackage{graphicx}',
        'multimedia': '\\usepackage{multimedia}',
        'adjustbox': '\\usepackage[export]{adjustbox}',
        'pgfplots': '\\usepackage{pgfplots}',
        'calc': '\\usetikzlibrary{calc}',
        'overlay-beamer-styles': '\\usetikzlibrary{overlay-beamer-styles}'
    }

    missing = []
    for package, command in required_packages.items():
        if command not in preamble_content:
            missing.append(package)

    return missing

def generate_preview_frame(filepath, output_path=None):
    """
    Generates a preview frame for different media types.
    Returns the path to the preview image.
    """
    try:
        import cv2
        from PIL import Image
        import os

        # Default output path if none provided
        if output_path is None:
                global output_dir
                base_name = os.path.splitext(os.path.basename(filepath))[0]
                output_path = os.path.join(output_dir, f"{base_name}_preview.png")
        # Get file extension
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        # Handle different media types
        if ext in ['.mp4', '.avi', '.mov', '.mkv']:
            # Video file
            cap = cv2.VideoCapture(filepath)
            ret, frame = cap.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img.save(output_path)
                cap.release()
                return output_path
        elif ext in ['.gif']:
            # Animated GIF - extract first frame
            with Image.open(filepath) as img:
                img.seek(0)
                img.save(output_path, 'PNG')
                return output_path
        elif ext in ['.mp3', '.wav', '.ogg']:
            # Audio file - create a simple icon
            img = Image.new('RGB', (400, 300), color='black')
            # You could draw a music note or audio symbol here
            img.save(output_path)
            return output_path
        elif ext in ['.png', '.jpg', '.jpeg']:
            # Static image - use as is
            return filepath

        return None
    except Exception as e:
        print(f"Error generating preview frame: {str(e)}")
        return None

def get_beamer_preamble(title, subtitle, author, institution, short_institute, date):
    """Returns complete Beamer preamble including notes support"""

    core_preamble = r"""
\documentclass[aspectratio=169]{beamer}

% Essential packages (core)
\usepackage{hyperref}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{tikz}
\usepackage{pgfplots}
\usepackage{xstring}
\usepackage{animate}
\usepackage{multimedia}
\usepackage{xifthen}
\usepackage{xcolor}
% Define the style for covered text
\setbeamercovered{dynamic} % This should enable progressive transparency
\setbeamerfont{item projected}{size=\small}
%------------------Chenge these options as required for fg text colour in \pause directives--------------------
%\setbeamercolor{alerted text}{fg=blue}        % Standard blue
%\setbeamercolor{alerted text}{fg=darkblue}    % Darker blue
%\setbeamercolor{alerted text}{fg=violet}      % Violet
%\setbeamercolor{alerted text}{fg=purple}      % Purple
%\setbeamercolor{alerted text}{fg=olive}       % Olive green
%\setbeamercolor{alerted text}{fg=teal}        % Teal
\setbeamercolor{alerted text}{fg=white}        % white
#----------------------------------
% Extended packages with fallbacks
\IfFileExists{tcolorbox.sty}{\usepackage{tcolorbox}}{}
\IfFileExists{fontawesome5.sty}{\usepackage{fontawesome5}}{}
\IfFileExists{pifont.sty}{\usepackage{pifont}}{}
\IfFileExists{soul.sty}{\usepackage{soul}}{}

% Package configurations
\pgfplotsset{compat=1.18}
\usetikzlibrary{shadows.blur, shapes.geometric, positioning, arrows.meta, backgrounds, fit}

% Original text effects
\newcommand{\shadowtext}[2][2pt]{%
   \begin{tikzpicture}[baseline]
       \node[blur shadow={shadow blur steps=5,shadow xshift=0pt,shadow yshift=-#1,
             shadow opacity=0.75}, text=white] {#2};
   \end{tikzpicture}%
}

\newcommand{\glowtext}[2][myblue]{%
   \begin{tikzpicture}[baseline]
       \node[circle, inner sep=1pt,
             blur shadow={shadow blur steps=10,shadow xshift=0pt,
             shadow yshift=0pt,shadow blur radius=5pt,
             shadow opacity=0.5,shadow color=#1},
             text=white] {#2};
   \end{tikzpicture}%
}

% Conditional definitions based on package availability
\IfFileExists{tcolorbox.sty}{%
    \newtcolorbox{alertbox}[1][red]{%
        colback=#1!5!white,
        colframe=#1!75!black,
        fonttitle=\bfseries,
        boxrule=0.5pt,
        rounded corners,
        shadow={2mm}{-1mm}{0mm}{black!50}
    }

    \newtcolorbox{infobox}[1][blue]{%
        enhanced,
        colback=#1!5!white,
        colframe=#1!75!black,
        arc=4mm,
        boxrule=0.5pt,
        fonttitle=\bfseries,
        attach boxed title to top center={yshift=-3mm,yshifttext=-1mm},
        boxed title style={size=small,colback=#1!75!black},
        shadow={2mm}{-1mm}{0mm}{black!50}
    }
}{}


% Define colors

\definecolor{myred}{RGB}{255,50,50}
\definecolor{myblue}{RGB}{0,130,255}
\definecolor{mygreen}{RGB}{0,200,100}
\definecolor{myyellow}{RGB}{255,210,0}
\definecolor{myorange}{RGB}{255,130,0}
\definecolor{mypurple}{RGB}{147,112,219}
\definecolor{mypink}{RGB}{255,105,180}
\definecolor{myteal}{RGB}{0,128,128}

% Glow colors
\definecolor{glowblue}{RGB}{0,150,255}
\definecolor{glowyellow}{RGB}{255,223,0}
\definecolor{glowgreen}{RGB}{0,255,128}
\definecolor{glowpink}{RGB}{255,182,193}

% Special effect support
\usetikzlibrary{shadows.blur}
\usetikzlibrary{decorations.text}
\usetikzlibrary{fadings}

% Basic highlighting commands
\newcommand{\hlbias}[1]{\textcolor{myblue}{\textbf{#1}}}
\newcommand{\hlvariance}[1]{\textcolor{mypink}{\textbf{#1}}}
\newcommand{\hltotal}[1]{\textcolor{myyellow}{\textbf{#1}}}
\newcommand{\hlkey}[1]{\colorbox{myblue!20}{\textcolor{white}{\textbf{#1}}}}
\newcommand{\hlnote}[1]{\colorbox{mygreen!20}{\textcolor{white}{\textbf{#1}}}}

% Basic theme setup
\usetheme{Madrid}
\usecolortheme{owl}

% Color settings
\setbeamercolor{normal text}{fg=white}
\setbeamercolor{structure}{fg=myyellow}
\setbeamercolor{alerted text}{fg=myorange}
\setbeamercolor{example text}{fg=mygreen}
\setbeamercolor{background canvas}{bg=black}
\setbeamercolor{frametitle}{fg=white,bg=black}

% Notes support
\usepackage{pgfpages}
\setbeameroption{show notes on second screen=right}
\setbeamertemplate{note page}{\pagecolor{yellow!5}\insertnote}


% Animated background support
\newcommand{\anbg}[2][0.2]{%
    \ifx\@empty#2\@empty
        % Clear background if empty argument
        \setbeamertemplate{background}{}
    \else
        % Set animated background
        \setbeamertemplate{background}{%
            \begin{tikzpicture}[remember picture,overlay]
                \node[opacity=#1] at (current page.center) {%
                    \animategraphics[autoplay,loop,width=\paperwidth]{12}{#2}{}{}
                };
            \end{tikzpicture}%
        }
    \fi
}
"""
   # Progress bar template
    frame_setup = r"""
% Progress bar setup
\makeatletter
\def\progressbar@progressbar{}
\newcount\progressbar@tmpcounta
\newcount\progressbar@tmpcountb
\newdimen\progressbar@pbht
\newdimen\progressbar@pbwd
\newdimen\progressbar@tmpdim

\progressbar@pbwd=\paperwidth
\progressbar@pbht=1pt

\def\progressbar@progressbar{%
   \begin{tikzpicture}[very thin]
       \shade[top color=myblue!50,bottom color=myblue]
           (0pt, 0pt) rectangle (\insertframenumber\progressbar@pbwd/\inserttotalframenumber, \progressbar@pbht);
   \end{tikzpicture}%
}

% Modified frame title template
\setbeamertemplate{frametitle}{
   \nointerlineskip
   \vskip1ex
   \begin{beamercolorbox}[wd=\paperwidth,ht=4ex,dp=2ex]{frametitle}
       \begin{minipage}[t]{\dimexpr\paperwidth-4em}
           \centering
           \vspace{2pt}
           \insertframetitle
           \vspace{2pt}
       \end{minipage}
   \end{beamercolorbox}
   \vskip.5ex
   \progressbar@progressbar
}
\makeatother"""

   # Institution setup
    inst_setup = rf"\makeatletter{chr(10)}\def\insertshortinstitute{{{short_institute if short_institute else institution}}}{chr(10)}\makeatother"

   # Footline template
    footline_template = r"""
% Footline template
\setbeamertemplate{footline}{%
 \leavevmode%
 \hbox{%
   \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,center]{author in head/foot}%
     \usebeamerfont{author in head/foot}\insertshortauthor~(\insertshortinstitute)%
   \end{beamercolorbox}%
   \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,center]{title in head/foot}%
     \usebeamerfont{title in head/foot}\insertshorttitle%
   \end{beamercolorbox}%
   \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,right]{date in head/foot}%
     \usebeamerfont{date in head/foot}\insertshortdate{}\hspace*{2em}%
     \insertframenumber{} / \inserttotalframenumber\hspace*{2ex}%
   \end{beamercolorbox}}%
 \vskip0pt%
}"""

   # Additional settings
    additional_settings = r"""
% Additional settings
\setbeamersize{text margin left=5pt,text margin right=5pt}
\setbeamertemplate{navigation symbols}{}
\setbeamertemplate{blocks}[rounded][shadow=true]"""

    title_setup = (
       "% Title setup\n"
       "\\title{" + title + "}\n"
       + ("\\subtitle{" + subtitle + "}\n" if subtitle else "") +
       "\\author{" + author + "}\n"
       "\\institute{\\textcolor{mygreen}{" + institution + "}}\n"
       "\\date{" + date + "}\n"
       "\\begin{document}\n"
       "\\maketitle\n"
    )

    # Title page template
    title_page = (
       "% Title page\n"
       "\\begin{frame}[plain]\n"
       "   \\begin{tikzpicture}[overlay,remember picture]\n"
       "       % Background gradient\n"
       "       \\fill[top color=black!90,bottom color=black!70,middle color=myblue!30]\n"
       "       (current page.south west) rectangle (current page.north east);\n"
       "       % Title with glow effect\n"
       "       \\node[align=center] at (current page.center) {\n"
       "           \\glowtext[glowblue]{\\Huge\\textbf{" + title + "}}\n"
       + ("           \\\\[1em]\\glowtext[glowyellow]{\\large " + subtitle + "}\n" if subtitle else "") +
       "           \\\\[2em]\n"
       "           \\glowtext[glowgreen]{\\large " + author + "}\n"
       "           \\\\[0.5em]\n"
       "           \\textcolor{white}{\\small " + institution + "}\n"
       "           \\\\[1em]\n"
       "           \\textcolor{white}{\\small " + date + "}\n"
       "       };\n"
       "   \\end{tikzpicture}\n"
       "\\end{frame}"
    )

   # Combine all parts
    return "\n".join([
       core_preamble,
       frame_setup,
       inst_setup,
       footline_template,
       additional_settings,
       title_setup,
       title_page
   ])

def get_footline_template():
    """
    Returns the correct footline template for Beamer.
    """
    return """% Setup footline template with proper short institute handling
\\makeatletter
\\defbeamertemplate*{footline}{custom}
{
  \\leavevmode%
  \\hbox{%
    \\begin{beamercolorbox}[wd=.333333\\paperwidth,ht=2.25ex,dp=1ex,center]{author in head/foot}%
      \\usebeamerfont{author in head/foot}\\insertshortauthor~(\\usebeamercolor[fg]{author in head/foot}\\insertshortinstitute)
    \\end{beamercolorbox}%
    \\begin{beamercolorbox}[wd=.333333\\paperwidth,ht=2.25ex,dp=1ex,center]{title in head/foot}%
      \\usebeamerfont{title in head/foot}\\insertshorttitle
    \\end{beamercolorbox}%
    \\begin{beamercolorbox}[wd=.333333\\paperwidth,ht=2.25ex,dp=1ex,right]{date in head/foot}%
      \\usebeamerfont{date in head/foot}\\insertshortdate{\\,}\\hspace*{2em}
      \\insertframenumber{} / \\inserttotalframenumber\\hspace*{2ex}
    \\end{beamercolorbox}}%
  \\vskip0pt%
}
\\setbeamertemplate{footline}[custom]
\\makeatother
"""

def format_url_footnote(url):
    """
    Format URL footnotes with proper hyperlinks.
    Now used for footnotes instead of tikzpicture sources.
    """
    try:
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            return f"\\footnote{{YouTube video: \\href{{{url}}}{{\\textcolor{{blue}}{{[Watch Video]}}}} }}"
        elif 'github.com' in parsed.netloc:
            return f"\\footnote{{GitHub: \\href{{{url}}}{{\\textcolor{{blue}}{{[View Repository]}}}} }}"
        else:
            return f"\\footnote{{Source: \\href{{{url}}}{{\\textcolor{{blue}}{{[View link]}}}} }}"
    except:
        return f"\\footnote{{Source: {url}}}"

def create_new_input_file(file_path):
    """
    Interactively creates a new input file with slide content and proper preamble.
    """
    global output_dir
    output_dir = os.path.dirname(os.path.abspath(file_path))
    os.chdir(output_dir)
    print("\nPresentation Setup:")
    print("-----------------")
    title = input("Title: ").strip()
    subtitle = input("Subtitle (press Enter to skip): ").strip()
    author = input("Author Name: ").strip()
    institution = input("Institution: ").strip()

    # Ask for short institution name if the institution name is long
    if len(institution) > 50:  # threshold for suggesting short name
        print("\nYour institution name is quite long and might get trimmed in slides.")
        print("It's recommended to provide a shorter version for the slide footers.")
        short_institute = input("Short Institution Name (press Enter to skip): ").strip()
    else:
        short_institute = input("Short Institution Name (optional, press Enter to skip): ").strip()

    date = input("Date (press Enter for today): ").strip()
    if not date:
        date = "\\today"

    # Get the preamble using the helper function
    preamble = get_beamer_preamble(title, subtitle, author, institution, short_institute, date)

    print(f"\nCreating new input file: {file_path}")
    print("Enter empty line at Title prompt to finish.")

    slides = []
    slide_num = 1

    while True:
        print(f"\n[Slide{slide_num}] Title: ", end='')
        title = input().strip()
        if not title:
            break

        # Handle URL/Media
        print(f"[Slide{slide_num}] Media selection:")
        search_query = construct_search_query(title, [])
        print(f"Opening Google Image search for: {search_query}")
        open_google_image_search(search_query)

        print("\nPlease choose one of the following options:")
        print("1. Enter a URL")
        print("2. Use an existing file from media_files folder")
        print("3. Create slide without media")
        choice = input("Your choice (1/2/3): ").strip()

        url = None
        if choice == '1':
            url = input("Enter URL: ").strip()
        elif choice == '2':
            print("\nAvailable files in media folder:")
            media_dir = os.path.join(os.path.dirname(os.path.abspath(file_path)), 'media')
            try:
                files = os.listdir(media_dir)
                for i, file in enumerate(files, 1):
                    print(f"{i}. {file}")
                file_choice = input("Enter file number or name: ").strip()
                if file_choice.isdigit() and 1 <= int(file_choice) <= len(files):
                    chosen_file = files[int(file_choice) - 1]
                else:
                    chosen_file = file_choice
                url = f"\\file {{./media/{chosen_file}}}"
            except Exception as e:
                print(f"Error accessing media_files: {str(e)}")
                url = "\\None"
        else:
            url = "\\None"

        # Collect content items
        print(f"\n[Slide{slide_num}] Content (enter empty line to finish):")
        content = []
        while True:
            item = input("- ").strip()
            if not item:
                break

            # Check if the item contains a footnote
            if "\\footnote{" in item:
                content.append(item)  # Add as is, footnote is already properly formatted
            else:
                content.append(f"- {item}")

        # Optional footnote for the entire slide
        print(f"\n[Slide{slide_num}] Footnote (press Enter to skip): ", end='')
        footnote = input().strip()

        # Build slide content
        slide_content = [f"\\title {title}"]
        slide_content.append("\\begin{Content}" + (f" {url}" if url else ""))
        slide_content.extend(content)

        # Add footnote if provided and content exists
        if footnote:
            if footnote.startswith(('http://', 'https://')):
                footnote = f"{{\\miniscule{ format_url_footnote(footnote)}}}"
            else:
                footnote = f"{{\\miniscule {footnote}}}"

            if content:  # Only add footnote if there's content
                last_content_line = slide_content[-1]
                if not "\\footnote{" in last_content_line:
                    slide_content[-1] = f"{last_content_line}\\footnote{footnote}"

        slide_content.append("\\end{Content}")
        slide_content.append("")  # Empty line between slides

        slides.append("\n".join(slide_content))
        slide_num += 1

    if slides:
        try:
            with open(file_path, 'w') as f:
                f.write(preamble)  # Write preamble first
                f.write("\n".join(slides))  # Write slides
                f.write("\n\\end{document}")  # End the document
            print(f"\nSuccessfully created {file_path} with {slide_num-1} slides.")
            return True
        except Exception as e:
            print(f"Error creating file: {str(e)}")
            return False
    else:
        print("\nNo slides created.")
        return False

def detect_preamble(lines):
    """
    Detects if the input file has a complete preamble by checking for key commands.
    Now also checks for short institution name.
    """
    has_author = False
    has_institute = False
    has_title = False
    has_begin_document = False
    has_titlepage = False
    has_maketitle = False
    has_short_institute = False
    preamble_end_idx = -1

    for i, line in enumerate(lines):
        line = line.strip()
        if '\\author{' in line:
            has_author = True
        if '\\institute{' in line:
            has_institute = True
        if '\\instituteShort{' in line or '\\def\\insertshortinstitute{' in line:
            has_short_institute = True
        if '\\title{' in line and not line.startswith('\\title '):
            has_title = True
        if '\\begin{document}' in line:
            has_begin_document = True
            preamble_end_idx = i
            break

    # If we have a long institution name but no short version, suggest adding one
    if has_institute and not has_short_institute:
        # Find the institution line to check its length
        for line in lines[:preamble_end_idx] if preamble_end_idx >= 0 else lines:
            if '\\institute{' in line:
                inst_text = line[line.find('{')+1:line.rfind('}')]
                if len(inst_text) > 50:  # threshold for suggesting short name
                    print("\nWarning: Long institution name detected.")
                    print("Consider adding a short version using \\instituteShort{} or modifying the footline template.")
                break

    # Check for titlepage and maketitle after \begin{document}
    if preamble_end_idx >= 0:
        for i in range(preamble_end_idx + 1, min(preamble_end_idx + 10, len(lines))):
            if '\\titlepage' in lines[i]:
                has_titlepage = True
            if '\\maketitle' in lines[i]:
                has_maketitle = True

    has_preamble = has_author and has_institute and has_title and has_begin_document

    if has_preamble:
        preamble_lines = lines[:preamble_end_idx + 1]
        content_lines = lines[preamble_end_idx + 1:]
    else:
        preamble_lines = []
        content_lines = lines

    return has_preamble, preamble_lines, content_lines, has_titlepage, has_maketitle
#---------------------------------------------------------------------------------------------------------

def sanitize_filename(filename, max_length=50):
    """
    Sanitizes a filename for safe use in file systems.
    """
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    filename = ''.join(c if c not in unsafe_chars else '_' for c in filename)

    # Keep only alphanumeric characters, spaces, dots, and underscores
    safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ._-')
    filename = ''.join(c if c in safe_chars else '_' for c in filename)

    # Replace multiple spaces/underscores with single ones
    while '__' in filename:
        filename = filename.replace('__', '_')

    # Replace spaces with underscores
    filename = filename.replace(' ', '_')

    # Remove dots from the beginning
    filename = filename.lstrip('.')

    # Limit length while preserving extension
    name, ext = os.path.splitext(filename)
    if len(name) > max_length:
        name = name[:max_length]
    filename = name + ext

    # If filename is empty after sanitization, use a default name
    if not filename or filename == '.':
        filename = 'video.mp4'

    return filename

def validate_url(url):
    """
    Validates a URL and provides specific error messages.
    Now handles file and None directives.
    """
    if url.startswith(('\\file', '\\None', '\\play')):
        return True, "Local file or directive reference"

    try:
        # Remove any leading/trailing whitespace and directives
        cleaned_url = url.split()[-1] if url.split() else url

        # Check if URL is accessible
        response = requests.head(cleaned_url, timeout=5)
        if response.status_code == 403:
            return False, "Access Forbidden - This URL requires authentication or is not publicly accessible"
        elif response.status_code == 404:
            return False, "Resource Not Found - The URL may be incorrect or the content may have been moved"
        elif response.status_code != 200:
            return False, f"URL returned status code {response.status_code}"
        return True, "URL is valid"
    except requests.exceptions.Timeout:
        return False, "URL request timed out"
    except requests.exceptions.RequestException as e:
        return False, f"Error accessing URL: {str(e)}"

def construct_search_query(title, content):
    """
    Constructs a Google search query from title and content.
    """
    search_terms = [title] if title else []
    if isinstance(content, list) and content:
        # Add first non-empty content item to search terms
        search_terms.extend([item.strip('- ') for item in content[:1] if item.strip('- ')])

    # Add relevant keywords based on context
    search_terms.append("scientific diagram")
    if "hopfield" in ' '.join(search_terms).lower():
        search_terms.append("neural network")
    elif "quantum" in ' '.join(search_terms).lower():
        search_terms.append("computing")

    return ' '.join(search_terms)

def open_google_image_search(query):
    """
    Opens Google Image search in default browser.
    """
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    webbrowser.open(search_url)


import os
import subprocess
import tempfile
from pathlib import Path
import mimetypes
from PIL import Image
import io
import requests
import shutil

class MediaConverter:
    """Media conversion utility for BSG-IDE"""

    def __init__(self):
        # Define supported formats
        self.supported_formats = {
            'image': ['.png', '.jpg', '.jpeg', '.gif'],
            'video': ['.mp4', '.webm', '.mkv', '.avi'],
            'animation': ['.gif'],
            'document': ['.pdf']
        }

        # Define preferred formats for each type
        self.preferred_formats = {
            'image': '.png',
            'video': '.mp4',
            'animation': '.gif',
            'document': '.pdf'
        }

        # Max dimensions for images
        self.max_dimensions = (1920, 1080)

    def convert_from_url(self, url: str, output_folder: str = 'media_files') -> tuple:
        """
        Download and convert media from URL to appropriate format.
        Returns (success, file_path, media_type)
        """
        try:
            # Create media_files directory if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)

            # Download content to temporary file
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Get content type and extension
            content_type = response.headers.get('content-type', '').split(';')[0]
            ext = mimetypes.guess_extension(content_type) or '.tmp'

            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_path = temp_file.name

            # Convert the downloaded file
            return self.convert_file(temp_path, output_folder)

        except Exception as e:
            print(f"Error converting from URL: {str(e)}")
            return False, None, None

        finally:
            # Clean up temporary file
            if 'temp_path' in locals():
                try:
                    os.unlink(temp_path)
                except:
                    pass

    def convert_file(self, input_path: str, output_folder: str = 'media_files') -> tuple:
        """
        Convert file to appropriate format based on content type.
        Returns (success, file_path, media_type)
        """
        try:
            # Determine media type
            media_type = self._detect_media_type(input_path)
            if not media_type:
                return False, None, None

            # Generate output filename
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_ext = self.preferred_formats[media_type]
            output_path = os.path.join(output_folder, f"{base_name}{output_ext}")

            # Convert based on media type
            if media_type == 'image':
                success = self._convert_image(input_path, output_path)
            elif media_type == 'video':
                success = self._convert_video(input_path, output_path)
            elif media_type == 'animation':
                success = self._convert_animation(input_path, output_path)
            elif media_type == 'document':
                success = self._convert_document(input_path, output_path)
            else:
                success = False

            if success:
                return True, output_path, media_type
            return False, None, None

        except Exception as e:
            print(f"Error converting file: {str(e)}")
            return False, None, None

    def _detect_media_type(self, file_path: str) -> str:
        """Detect media type based on file content and extension"""
        try:
            # Try to open as image first
            try:
                with Image.open(file_path) as img:
                    if getattr(img, 'is_animated', False):
                        return 'animation'
                    return 'image'
            except:
                pass

            # Check file extension
            ext = os.path.splitext(file_path)[1].lower()

            for media_type, extensions in self.supported_formats.items():
                if ext in extensions:
                    return media_type

            # Try mime type
            mime_type = mimetypes.guess_type(file_path)[0]
            if mime_type:
                if mime_type.startswith('image/'):
                    return 'image'
                elif mime_type.startswith('video/'):
                    return 'video'
                elif mime_type.startswith('application/pdf'):
                    return 'document'

            return None

        except Exception as e:
            print(f"Error detecting media type: {str(e)}")
            return None

    def _convert_image(self, input_path: str, output_path: str) -> bool:
        """Convert image to preferred format with optimization"""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

                # Resize if too large
                if img.size[0] > self.max_dimensions[0] or img.size[1] > self.max_dimensions[1]:
                    img.thumbnail(self.max_dimensions, Image.Resampling.LANCZOS)

                # Optimize and save
                if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
                    img.save(output_path, 'JPEG', quality=85, optimize=True)
                elif output_path.lower().endswith('.png'):
                    img.save(output_path, 'PNG', optimize=True)
                else:
                    img.save(output_path)

                return True

        except Exception as e:
            print(f"Error converting image: {str(e)}")
            return False

    def _convert_animation(self, input_path: str, output_path: str) -> bool:
        """Convert animation to optimized GIF"""
        try:
            with Image.open(input_path) as img:
                if not getattr(img, 'is_animated', False):
                    # Single frame - convert as regular image
                    return self._convert_image(input_path, output_path)

                # Get all frames
                frames = []
                durations = []
                for frame in range(img.n_frames):
                    img.seek(frame)
                    # Convert and append frame
                    new_frame = img.convert('RGBA')
                    frames.append(new_frame)
                    durations.append(img.info.get('duration', 100))

                # Save optimized GIF
                frames[0].save(
                    output_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=0,
                    optimize=True
                )
                return True

        except Exception as e:
            print(f"Error converting animation: {str(e)}")
            return False

    def _convert_video(self, input_path: str, output_path: str) -> bool:
        """Convert video to MP4 using ffmpeg"""
        try:
            # Check if ffmpeg is available
            if not shutil.which('ffmpeg'):
                print("ffmpeg not found. Please install ffmpeg.")
                return False

            command = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                '-y',  # Overwrite output file if exists
                output_path
            ]

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            return process.returncode == 0

        except Exception as e:
            print(f"Error converting video: {str(e)}")
            return False

    def _convert_document(self, input_path: str, output_path: str) -> bool:
        """Convert document to PDF if needed"""
        try:
            # For now, just copy PDF files
            if input_path.lower().endswith('.pdf'):
                shutil.copy2(input_path, output_path)
                return True

            # Add other document conversion methods as needed
            return False

        except Exception as e:
            print(f"Error converting document: {str(e)}")
            return False
def convert_media(url_or_path: str, output_folder: str = 'media_files') -> tuple:
    """
    High-level function to convert media from URL or local file.
    Returns (success, file_path, media_type)
    """
    converter = MediaConverter()

    if url_or_path.startswith(('http://', 'https://')):
        return converter.convert_from_url(url_or_path, output_folder)
    else:
        return converter.convert_file(url_or_path, output_folder)

def download_media(url, output_folder='media_files'):
    """
    Enhanced version with source tracking and automatic format conversion.
    Returns (base_name, filename, first_frame_path)
    """
    try:
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Handle local files
        if url.startswith('local:'):
            local_file = url.split('local:')[1].strip()
            local_path = os.path.join(output_folder, local_file)
            if os.path.exists(local_path):
                # Convert local file if needed
                success, converted_path, media_type = convert_media(local_path, output_folder)
                if success:
                    base_name = os.path.splitext(os.path.basename(converted_path))[0]
                    filename = os.path.basename(converted_path)
                    return base_name, filename, filename
                return None, None, None
            return None, None, None

        # Handle Giphy URLs
        if 'giphy.com' in url:
            return download_giphy_gif(url, output_folder)

        # Handle regular URLs
        try:
            # First download the content
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Convert the downloaded content
            success, converted_path, media_type = convert_media(url, output_folder)

            if success:
                base_name = os.path.splitext(os.path.basename(converted_path))[0]
                filename = os.path.basename(converted_path)

                # Generate preview frame if needed
                first_frame_path = None
                if media_type in ['video', 'animation']:
                    first_frame_path = generate_preview_frame(converted_path)
                elif media_type == 'image':
                    first_frame_path = converted_path

                # Store metadata
                metadata_path = os.path.join(output_folder, f"{base_name}_metadata.txt")
                with open(metadata_path, 'w') as f:
                    f.write(f"Source: {url}\n")
                    f.write(f"Original Type: {media_type}\n")
                    f.write(f"Converted Format: {os.path.splitext(filename)[1]}\n")
                    f.write(f"Downloaded: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

                    # Add media-specific metadata
                    if media_type == 'image':
                        try:
                            with Image.open(converted_path) as img:
                                f.write(f"Dimensions: {img.size}\n")
                                f.write(f"Mode: {img.mode}\n")
                        except Exception as e:
                            f.write(f"Image info error: {str(e)}\n")
                    elif media_type == 'video':
                        try:
                            import cv2
                            video = cv2.VideoCapture(converted_path)
                            fps = video.get(cv2.CAP_PROP_FPS)
                            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                            duration = frame_count/fps if fps > 0 else 0
                            f.write(f"Duration: {duration:.2f} seconds\n")
                            f.write(f"FPS: {fps}\n")
                            video.release()
                        except Exception as e:
                            f.write(f"Video info error: {str(e)}\n")

                return base_name, filename, first_frame_path

        except requests.exceptions.RequestException as e:
            print(f"Error downloading from URL {url}: {str(e)}")
            return None, None, None

    except Exception as e:
        print(f"Error processing media from {url}: {str(e)}")
        return None, None, None


def download_giphy_gif(url, output_folder='media_files'):
    """
    Enhanced Giphy GIF downloader with format conversion.
    """
    try:
        # Extract the GIF ID from the URL
        gif_id = url.split('/')[-1].split('-')[-1]

        # Construct direct gif URL
        direct_url = f"https://media.giphy.com/media/{gif_id}/giphy.gif"

        # Download and convert
        success, converted_path, media_type = convert_media(direct_url, output_folder)

        if success:
            base_name = os.path.splitext(os.path.basename(converted_path))[0]
            filename = os.path.basename(converted_path)

            # Generate preview if it's an animated GIF
            first_frame_path = None
            if media_type == 'animation':
                first_frame_path = generate_preview_frame(converted_path)
            else:
                first_frame_path = converted_path

            # Store Giphy-specific metadata
            metadata_path = os.path.join(output_folder, f"{base_name}_metadata.txt")
            with open(metadata_path, 'w') as f:
                f.write(f"Source: {url}\n")
                f.write(f"Giphy ID: {gif_id}\n")
                f.write(f"Direct URL: {direct_url}\n")
                f.write(f"Downloaded: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

                # Add animation metadata
                try:
                    with Image.open(converted_path) as img:
                        f.write(f"Dimensions: {img.size}\n")
                        f.write(f"Frames: {getattr(img, 'n_frames', 1)}\n")
                        f.write(f"Duration: {img.info.get('duration', 0)}ms\n")
                except Exception as e:
                    f.write(f"Animation info error: {str(e)}\n")

            return base_name, filename, first_frame_path

        return None, None, None

    except Exception as e:
        print(f"Error processing Giphy URL: {str(e)}")
        return None, None, None


def parse_color_args(color_spec):
    """Parse color specifications from text effect arguments"""
    if not color_spec:
        return None, None

    # Remove brackets and split colors
    colors = color_spec.strip('[]').split(',')
    if len(colors) == 1:
        return colors[0].strip(), None
    elif len(colors) >= 2:
        return colors[0].strip(), colors[1].strip()
    return None, None

def process_special_effects(content_line):
    """Process all special text effects with color support"""
    if not content_line:
        return content_line

    # Process shadowtext
    while '\\shadowtext[' in content_line or '\\shadowtext{' in content_line:
        match = re.search(r'\\shadowtext(?:\[(.*?)\])?\{(.*?)\}', content_line)
        if not match:
            break
        color_args, text = match.group(1), match.group(2)
        shadow_color, text_color = parse_color_args(color_args) if color_args else ('black', 'white')
        replacement = f"""\\begin{{tikzpicture}}[baseline]
            \\node[blur shadow={{shadow blur steps=5,shadow xshift=0pt,shadow yshift=-2pt,
                  shadow opacity=0.75,shadow color={shadow_color}}},
                  text={text_color if text_color else 'white'}] {{{text}}};
        \\end{{tikzpicture}}"""
        content_line = content_line.replace(match.group(0), replacement)

    # Process glowtext
    while '\\glowtext[' in content_line or '\\glowtext{' in content_line:
        match = re.search(r'\\glowtext(?:\[(.*?)\])?\{(.*?)\}', content_line)
        if not match:
            break
        color_args, text = match.group(1), match.group(2)
        glow_color, text_color = parse_color_args(color_args) if color_args else ('myblue', 'white')
        replacement = f"""\\begin{{tikzpicture}}[baseline]
            \\node[circle, inner sep=1pt,
                  blur shadow={{shadow blur steps=10,shadow xshift=0pt,
                  shadow yshift=0pt,shadow blur radius=5pt,
                  shadow opacity=0.5,shadow color={glow_color}}},
                  text={text_color if text_color else 'white'}] {{{text}}};
        \\end{{tikzpicture}}"""
        content_line = content_line.replace(match.group(0), replacement)

    # Process gradienttext
    while '\\gradienttext[' in content_line:
        match = re.search(r'\\gradienttext\[(.*?)\]\[(.*?)\]\{(.*?)\}', content_line)
        if not match:
            break
        start_color, end_color, text = match.group(1), match.group(2), match.group(3)
        replacement = f"""\\begin{{tikzpicture}}[baseline]
            \\node[fill={start_color},fill opacity=0.15,
                  path picture={{\\node at (path picture bounding box.center) {{
                  \\color{{{end_color}}}{text}
                  }};}},inner sep=2pt] {{}};
        \\end{{tikzpicture}}"""
        content_line = content_line.replace(match.group(0), replacement)

    # Process highlighting
    while '\\hlkey[' in content_line or '\\hlkey{' in content_line:
        match = re.search(r'\\hlkey(?:\[(.*?)\])?\{(.*?)\}', content_line)
        if not match:
            break
        color_args, text = match.group(1), match.group(2)
        bg_color, text_color = parse_color_args(color_args) if color_args else ('myblue!20', 'white')
        replacement = f"\\colorbox{{{bg_color}}}{{\\textcolor{{{text_color if text_color else 'black'}}}" + \
                     "{\\textbf{" + text + "}}}"
        content_line = content_line.replace(match.group(0), replacement)

    # Process note highlighting
    while '\\hlnote[' in content_line or '\\hlnote{' in content_line:
        match = re.search(r'\\hlnote(?:\[(.*?)\])?\{(.*?)\}', content_line)
        if not match:
            break
        color_args, text = match.group(1), match.group(2)
        bg_color, text_color = parse_color_args(color_args) if color_args else ('mygreen!20', 'white')
        replacement = f"\\colorbox{{{bg_color}}}{{\\textcolor{{{text_color if text_color else 'black'}}}" + \
                     "{\\textbf{" + text + "}}}"
        content_line = content_line.replace(match.group(0), replacement)

    return content_line

def process_latex_content(content_line: str) -> str:
    """Enhanced content processing with special effects support"""
    if not content_line:
        return content_line

    # First process special effects
    content_line = process_special_effects(content_line)

    # Then process standard LaTeX content
    result = []
    in_math = False
    brace_level = 0
    i = 0

    while i < len(content_line):
        char = content_line[i]

        # Handle math mode transitions
        if char == '$':
            in_math = not in_math
            result.append(char)
            i += 1
            continue

        # Handle braces
        if char == '{':
            brace_level += 1
            result.append(char)
            i += 1
            continue
        elif char == '}':
            brace_level -= 1
            result.append(char)
            i += 1
            continue

        # Process characters based on context
        if in_math or brace_level > 0:
            result.append(char)
        else:
            if char in '_&%#~^':
                result.append('\\' + char)
            else:
                result.append(char)
        i += 1

    return ''.join(result)
#----------------------------------------------------------------------
def generate_latex_code(base_name, filename, first_frame_path, content=None, title=None, playable=False, source_url=None, layout=None):
    """Generate LaTeX code with support for all media layouts."""

    # Process title
    if title:
        frame_title = process_latex_content(title)
    else:
        base_name_escaped = process_latex_content(base_name if base_name else 'Untitled')
        frame_title = "Media: " + base_name_escaped

    # Handle no media case first
    if not filename or filename == "\\None":
        latex_code = "\\begin{frame}{\\Large\\textbf{" + frame_title + "}}\n"
        latex_code += "    \\vspace{0.5em}\n"
        latex_code += "    \\begin{itemize}\n"
        latex_code += "        " + generate_content_items(content) + "\n"
        latex_code += "    \\end{itemize}\n"
        latex_code += "\\end{frame}\n"
        return latex_code

    # Generate layout based on directive
    latex_code = ""

    if layout == 'watermark':
        latex_code = "\\begin{frame}{" + (frame_title if title else '') + "}\n"
        latex_code += "    \\begin{tikzpicture}[remember picture,overlay]\n"
        latex_code += "        \\node[opacity=0.15] at (current page.center) {%\n"
        latex_code += "            \\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{" + filename + "}%\n"
        latex_code += "        };\n"
        latex_code += "    \\end{tikzpicture}\n"
        latex_code += "    \\begin{itemize}\n"
        latex_code += "        " + generate_content_items(content) + "\n"
        latex_code += "    \\end{itemize}"

    elif layout == 'fullframe':
        latex_code = "\\begin{frame}[plain]\n"
        latex_code += "    \\begin{tikzpicture}[remember picture,overlay]\n"
        latex_code += "        \\node at (current page.center) {%\n"
        latex_code += "            \\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{" + filename + "}%\n"
        latex_code += "        };\n"
        latex_code += "        \\node[text width=0.8\\paperwidth,align=center,text=white] at (current page.center) {\n"
        latex_code += "            \\Large\\textbf{" + frame_title + "}\\\\[1em]\n"
        latex_code += "            \\begin{itemize}\n"
        latex_code += "                " + generate_content_items(content, color='white') + "\n"
        latex_code += "            \\end{itemize}\n"
        latex_code += "        };\n"
        latex_code += "    \\end{tikzpicture}"

    elif layout == 'pip':
        latex_code = "\\begin{frame}{\\Large\\textbf{" + frame_title + "}}\n"
        latex_code += "    \\begin{columns}[T]\n"
        latex_code += "        \\begin{column}{0.7\\textwidth}\n"
        latex_code += "            \\begin{itemize}\n"
        latex_code += "                " + generate_content_items(content) + "\n"
        latex_code += "            \\end{itemize}\n"
        latex_code += "        \\end{column}\n"
        latex_code += "        \\begin{column}{0.28\\textwidth}\n"
        latex_code += "            \\vspace{1em}\n"
        latex_code += "            \\includegraphics[width=\\textwidth,keepaspectratio]{" + filename + "}\n"
        latex_code += "        \\end{column}\n"
        latex_code += "    \\end{columns}"

    elif layout == 'split':
        latex_code = "\\begin{frame}{\\Large\\textbf{" + frame_title + "}}\n"
        latex_code += "    \\begin{columns}[T]\n"
        latex_code += "        \\begin{column}{0.48\\textwidth}\n"
        latex_code += "            \\includegraphics[width=\\textwidth,keepaspectratio]{" + filename + "}\n"
        latex_code += "        \\end{column}\n"
        latex_code += "        \\begin{column}{0.48\\textwidth}\n"
        latex_code += "            \\begin{itemize}\n"
        latex_code += "                " + generate_content_items(content) + "\n"
        latex_code += "            \\end{itemize}\n"
        latex_code += "        \\end{column}\n"
        latex_code += "    \\end{columns}"

    elif layout == 'highlight':
        latex_code = "\\begin{frame}{\\Large\\textbf{" + frame_title + "}}\n"
        latex_code += "    \\begin{center}\n"
        latex_code += "        \\includegraphics[width=0.8\\textwidth,height=0.6\\textheight,keepaspectratio]{" + filename + "}\n"
        latex_code += "    \\end{center}\n"
        latex_code += "    \\vspace{0.5em}\n"
        latex_code += "    \\begin{itemize}\n"
        latex_code += "        " + generate_content_items(content) + "\n"
        latex_code += "    \\end{itemize}"

    elif layout == 'mosaic':
        images = [img.strip() for img in filename.split(',')]
        grid_size = int(math.ceil(math.sqrt(len(images))))

        latex_code = "\\begin{frame}{\\Large\\textbf{" + frame_title + "}}\n"
        latex_code += "    \\begin{center}\n"  # Center the entire grid
        latex_code += "    \\vbox{\\vspace{1em}}\n"  # Add some vertical space at top

        # Start a tabular environment for grid layout
        latex_code += "    \\begin{tabular}{" + "c" * grid_size + "}\n"

        # Calculate image size - use smaller of width/height constraint
        img_width = "0.25\\textwidth"  # Adjust these values to control image size
        img_height = "0.2\\textheight"

        # Generate grid row by row
        for i in range(grid_size):
            row_images = []
            for j in range(grid_size):
                idx = i * grid_size + j
                if idx < len(images):
                    # Each image in its own box for consistent spacing
                    cell = "\\includegraphics[width=" + img_width + ",height=" + img_height + ",keepaspectratio]{" + images[idx] + "}"
                    row_images.append(cell)
                else:
                    row_images.append("")  # Empty cell

            # Join cells with & and end row with \\
            latex_code += "        " + " & ".join(row_images)
            if i < grid_size - 1:  # Don't add \\ after last row
                latex_code += " \\\\\n        \\vspace{0.5em}\\\\\n"  # Add vertical space between rows

        latex_code += "\n    \\end{tabular}\n"
        latex_code += "    \\end{center}\n"

        if content:
            latex_code += "    \\vspace{1em}\n"  # Space between grid and content
            latex_code += "    \\begin{itemize}\n"
            latex_code += "        " + generate_content_items(content) + "\n"
            latex_code += "    \\end{itemize}\n"

        latex_code += "    \\end{columns}"

    elif layout == 'background':
        latex_code = "\\begin{frame}{\\Large\\textbf{" + frame_title + "}}\n"
        latex_code += "    \\begin{tikzpicture}[remember picture,overlay]\n"
        latex_code += "        \\node[opacity=0.1] at (current page.center) {%\n"
        latex_code += "            \\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{" + filename + "}%\n"
        latex_code += "        };\n"
        latex_code += "    \\end{tikzpicture}\n"
        latex_code += "    \\begin{itemize}\n"
        latex_code += "        " + generate_content_items(content) + "\n"
        latex_code += "    \\end{itemize}"

    elif layout == 'topbottom':
        latex_code = "\\begin{frame}{\\Large\\textbf{" + frame_title + "}}\n"
        latex_code += "    \\vspace{-0.5em}\n"
        latex_code += "    \\begin{center}\n"
        latex_code += "        \\includegraphics[width=0.8\\textwidth,height=0.45\\textheight,keepaspectratio]{" + filename + "}\n"
        latex_code += "    \\end{center}\n"
        latex_code += "    \\vspace{0.5em}\n"
        latex_code += "    \\begin{itemize}\n"
        latex_code += "        " + generate_content_items(content) + "\n"
        latex_code += "    \\end{itemize}"

    elif layout == 'overlay':
        latex_code = "\\begin{frame}{\\Large\\textbf{" + frame_title + "}}\n"
        latex_code += "    \\begin{tikzpicture}[remember picture,overlay]\n"
        latex_code += "        \\node[opacity=0.3] at (current page.center) {%\n"
        latex_code += "            \\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{" + filename + "}%\n"
        latex_code += "        };\n"
        latex_code += "        \\node[text width=0.8\\paperwidth,align=center,text=white] at (current page.center) {\n"
        latex_code += "            \\begin{itemize}\n"
        latex_code += "                " + generate_content_items(content, color='white') + "\n"
        latex_code += "            \\end{itemize}\n"
        latex_code += "        };\n"
        latex_code += "    \\end{tikzpicture}"

    elif layout == 'corner':
        latex_code = "\\begin{frame}{\\Large\\textbf{" + frame_title + "}}\n"
        latex_code += "    \\begin{itemize}\n"
        latex_code += "        " + generate_content_items(content) + "\n"
        latex_code += "    \\end{itemize}\n"
        latex_code += "    \\begin{tikzpicture}[remember picture,overlay]\n"
        latex_code += "        \\node[anchor=south east] at (current page.south east) {%\n"
        latex_code += "            \\includegraphics[width=0.2\\textwidth,keepaspectratio]{" + filename + "}%\n"
        latex_code += "        };\n"
        latex_code += "    \\end{tikzpicture}"

    else:
        # Default side-by-side layout
        if playable and first_frame_path:
            latex_code = "\\begin{frame}{\\Large\\textbf{" + frame_title + "}}\n"
            latex_code += "    \\begin{columns}[T]\n"
            latex_code += "        \\begin{column}{0.48\\textwidth}\n"
            latex_code += "            \\includegraphics[width=\\textwidth,height=0.6\\textheight,keepaspectratio]{" + first_frame_path + "}\n"
            latex_code += "            \\begin{center}\n"
            latex_code += "                \\vspace{0.3em}\n"
            latex_code += "                \\footnotesize{Click to play}\\\\\n"
            latex_code += "                \\movie[externalviewer]{\\textcolor{blue}{\\underline{Play}}}{" + filename + "}\n"
            latex_code += "            \\end{center}\n"
            latex_code += "        \\end{column}\n"
            latex_code += "        \\begin{column}{0.48\\textwidth}\n"
            latex_code += "            \\begin{itemize}\n"
            latex_code += "                " + generate_content_items(content) + "\n"
            latex_code += "            \\end{itemize}"

            if source_url:
                latex_code = latex_code.rstrip() + format_url_footnote(source_url)

            latex_code += "\n        \\end{column}\n"
            latex_code += "    \\end{columns}"
        else:
            latex_code = "\\begin{frame}{\\Large\\textbf{" + frame_title + "}}\n"
            latex_code += "    \\begin{columns}[T]\n"
            latex_code += "        \\begin{column}{0.48\\textwidth}\n"
            latex_code += "            \\includegraphics[width=\\textwidth,height=0.6\\textheight,keepaspectratio]{" + filename + "}\n"
            latex_code += "        \\end{column}\n"
            latex_code += "        \\begin{column}{0.48\\textwidth}\n"
            latex_code += "            \\begin{itemize}\n"
            latex_code += "                " + generate_content_items(content) + "\n"
            latex_code += "            \\end{itemize}"

            if source_url:
                latex_code = latex_code.rstrip() + format_url_footnote(source_url)

            latex_code += "\n        \\end{column}\n"
            latex_code += "    \\end{columns}"

    latex_code += "\n\\end{frame}\n"
    return latex_code
#----------------------------------------------------------------------

def generate_source_citation(source_url):
    """Generate LaTeX code for source citation"""
    return f"""
    \\vspace{{0.3em}}
    \\begin{{tikzpicture}}[remember picture,overlay]
        \\node[anchor=south,font=\\tiny] at (current page.south) {{
            Source: \\url{{{source_url}}}
        }};
    \\end{{tikzpicture}}"""

def generate_content_items(content, color=None):
    """Generate formatted content items with optional color"""
    if not content:
        return ""
    cnt=1
    items = []
    pause_set=False
    for itemx in content:
        if itemx.startswith(('\\pause')):
            pause_set=True
    for item in content:

        if item.strip():
            item = str(item).strip()
            if pause_set and not item.startswith(('\\pause','\\begin','\\end','\\item')):
                item=f'\item<{cnt}| alert@1>'+item
            elif pause_set and item.startswith(('\\item')):
                item = re.sub('item',f'item<{cnt}| alert@1>',item)
            elif pause_set and item.startswith(('\\pause')):
                cnt=cnt+1
            if item.startswith(('\\pause','\\item')):
                items.append(item)
                continue
            # Preserve original item format if it starts with special characters
            if item.startswith(('\\pause', '•')):
                processed_item = process_latex_content(item)
            else:
                # Remove any leading hyphen before processing
                clean_item = item.lstrip('- ')
                processed_item = process_latex_content(clean_item)
            # Handle environment directives
            if item == '\\begin{enumerate}':
                in_enumerate = True
                items.append(item)
                continue
            elif item == '\\end{enumerate}':
                in_enumerate = False
                items.append(item)
                continue
            elif item in ['\\begin{itemize}', '\\end{itemize}']:
                continue
            if item.startswith('-'):
                item = item[1:].strip()
            processed_item = process_latex_content(item)
            if color:
                processed_item = f"{{\\color{{{color}}}{processed_item}}}"
            items.append(f"\\item {processed_item}")

    return '\n        '.join(items)

def format_source_citation(url):
    """
    Format source URLs for citation with proper LaTeX formatting and hyperlinks.
    Abbreviates long URLs and ensures proper clickable links.
    """
    try:
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        path = parsed.path

        # Handle different types of URLs
        if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            # For YouTube, show friendly format
            return f"{{\\tiny YouTube video: \\href{{{url}}}{{\\textcolor{{blue}}{{[Watch Video]}}}}}}"
        elif 'github.com' in parsed.netloc:
            # For GitHub, show repository info
            return f"{{\\tiny GitHub: \\href{{{url}}}{{\\textcolor{{blue}}{{[View Repository]}}}}}}"
        else:
            # For general URLs, abbreviate if too long
            if len(url) > 15:  # Threshold for abbreviation
                display_url = base_url + '/...' + str(split(path,"/")[-1]) if len(path) > 10 else base_url
                return f"{{\\tiny Source: {display_url} \\href{{{url}}}{{\\textcolor{{blue}}{{[link]}}}}}}"
            else:
                return f"{{\\tiny Source: \\href{{{url}}}{{\\textcolor{{blue}}{{{url}}}}}}}"
    except:
        return f"{{\\tiny Source: {url}}}"



def verify_media_file(filepath):
    """
    Verifies that a media file exists and returns its proper path.
    """
    if os.path.exists(filepath):
        return filepath

    base_filepath = os.path.join('media_files', os.path.basename(filepath))
    if os.path.exists(base_filepath):
        return base_filepath

    # Try to find the file with any extension
    global output_dir
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    output_dir = os.path.dirname(os.path.abspath(file_path))  # Get the directory of the input file
    base_path = os.path.join(output_dir,'media_files', base_name)
    import glob
    possible_files = glob.glob(base_path + '.*')
    if possible_files:
        return possible_files[0]

    print(f"Warning: Media file not found: {filepath}")
    return None


def process_media(url, content=None, title=None, playable=False, slide_index=None, callback=None):
    """Process media with graceful handling of missing files and URLs"""


    try:

        directive_type, media_source, is_playable, original_directive = parse_media_directive(url)
        playable = playable or is_playable

        # Initialize content list if None
        if content is None:
            content = []

        # Create a list to store footnotes
        footnotes = []


        # First collect any existing footnotes from content
        processed_content = []
        for item in content:
            if '\\anbg' in item:
                    # Extract image name from \anbg command
                    match = re.search(r'\\anbg\{(.*?)\}', item)
                    if match:
                        image_name = match.group(1)
                        if image_name:
                            # Add background command before frame
                           processed_content.append(f"\\anbg{{{image_name}}}")
                        else:
                            # Clear background if empty
                            processed_content.append("\\anbg{}")
                    # Remove \anbg line from content
                    content.pop(i)
            elif '\\footnote{' in item:
                # Extract footnote text
                footnote_start = item.index('\\footnote{') + len('\\footnote{')
                footnote_end = item.rindex('}')
                footnote_text = item[footnote_start:footnote_end]
                footnotes.append(footnote_text)

                # Remove footnote from content item
                cleaned_item = item[:item.index('\\footnote{')] + item[item.rindex('}')+1:]
                processed_content.append(cleaned_item)
            else:
                processed_content.append(item)


        # Now add all footnotes to the last content item or create a phantom item
        if processed_content:
            last_item = processed_content[-1]
            for i, footnote in enumerate(footnotes):
                if i == 0:
                    last_item = f"{last_item}\\footnote{{{footnote}}}"
                else:
                    # Add subsequent footnotes with proper spacing
                    last_item = f"{last_item}\\footnote{{{footnote}}}"
            processed_content[-1] = last_item
        elif footnotes:
            # If no content but we have footnotes, create a phantom item
            combined_footnotes = ''.join([f"\\footnote{{{f}}}" for f in footnotes])
            processed_content.append(f"\\phantom{{.}}{combined_footnotes}")


        # Handle explicit \None directive
        if url.strip() == "\\None":
            return generate_latex_code(None, "\\None", None, content, title, False), "\\None"

        # Handle URLs in \play directive
        if directive_type == 'url' and playable:
            if media_source.startswith(('http://', 'https://')):
                if 'youtube.com' in media_source or 'youtu.be' in media_source:
                    # Download YouTube video
                    result = download_youtube_video(media_source)
                    if result:
                        base_name, filename, filepath = result
                        first_frame_path = generate_preview_frame(filepath)
                        return generate_latex_code(
                            base_name,
                            f"media_files/{filename}",
                            first_frame_path,
                            content,
                            title,
                            True,
                            media_source
                        ), f"\\play \\file media_files/{filename}"
                else:
                    # Download other media URLs
                    base_name, filename, first_frame_path = download_media(media_source)
                    if base_name and filename:
                        return generate_latex_code(
                            base_name,
                            f"media_files/{filename}",
                            first_frame_path,
                            content,
                            title,
                            True,
                            media_source
                        ), f"\\play \\file media_files/{filename}"

        # Handle regular URLs
        elif directive_type == 'url' :
            if media_source.startswith(('http://', 'https://')):
                base_name, filename, first_frame_path = download_media(media_source)
                if base_name and filename:
                    return generate_latex_code(
                        base_name,
                        f"media_files/{filename}",
                        first_frame_path,
                        content,
                        title,
                        False,
                        media_source
                    ), f"\\file media_files/{filename}"

        # Handle local files
        elif directive_type == 'file':
            media_path = media_source
            if not os.path.exists(media_path):
                media_path = os.path.join('media_files', os.path.basename(media_path))

            if os.path.exists(media_path):
                first_frame_path = None
                if playable:
                    first_frame_path = generate_preview_frame(media_path)
                return generate_latex_code(
                    os.path.splitext(os.path.basename(media_path))[0],
                    media_path,
                    first_frame_path,
                    content,
                    title,
                    playable
                ), original_directive

        # Handle layout directives (watermark, fullframe, etc.)
        elif directive_type in ['watermark', 'fullframe', 'pip', 'split', 'highlight',
                              'background', 'topbottom', 'overlay', 'corner', 'mosaic']:
            return generate_latex_code(
                base_name=None,
                filename=media_source,
                first_frame_path=None,
                content=content,
                title=title,
                playable=playable,
                layout=directive_type
            ), original_directive

        # If we get here, the media wasn't handled
        if callback and slide_index is not None:
            callback(slide_index)
        return handle_missing_media(url, content, title, playable)

    except Exception as e:
        print(f"Error processing media: {str(e)}")
        return handle_missing_media(url, content, title, playable)


import urllib.parse

def update_text_file(file_path, line_number, new_directive):
    """Update the text file with new directive"""
    if not file_path or not line_number:
        return

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Find the correct position to insert the directive
        if line_number - 1 < len(lines):
            current_line = lines[line_number - 1].strip()

            # Check if the line starts with \begin{Content}
            if current_line.startswith("\\begin{Content}"):
                # Extract the original directive
                original_directive = current_line.replace("\\begin{Content}", "").strip()
                print(f"The original directive is: {original_directive}")
                # Check if the original directive is a URL
                try:
                    result = urllib.parse.urlparse(original_directive)
                    if all([result.scheme, result.netloc]):
                        # The original directive is a URL, do not replace it
                        if terminal_io:
                            terminal_io.write(f"Skipping update at line {line_number} as it contains a URL\n", "yellow")
                        return
                except ValueError:
                    pass

                # Replace everything after \begin{Content} with the new directive
                lines[line_number - 1] = f"\\begin{{Content}} {new_directive}\n"
            else:
                # Extract the original directive
                original_directive = current_line

                # Check if the original directive is a URL
                try:
                    result = urllib.parse.urlparse(original_directive)
                    if all([result.scheme, result.netloc]):
                        # The original directive is a URL, do not replace it
                        if terminal_io:
                            terminal_io.write(f"Skipping update at line {line_number} as it contains a URL\n", "yellow")
                        return
                except ValueError:
                    pass

                # Replace the entire line with the new directive
                lines[line_number - 1] = f"{new_directive}\n"

            # Write the updated content back to file
            with open(file_path, 'w') as f:
                f.writelines(lines)

            if terminal_io:
                terminal_io.write(f"✓ File updated successfully at line {line_number}\n", "green")

    except Exception as e:
        if terminal_io:
            terminal_io.write(f"Error updating file: {str(e)}\n", "red")


def handle_missing_media(original_url, content, title, playable):
    """Handle missing media gracefully in GUI mode by defaulting to \\None"""
    try:
        # Check if we're in GUI mode (IDE)
        in_gui_mode = terminal_io and hasattr(terminal_io, 'editor')

        if in_gui_mode:
            # In GUI mode, silently default to \None
            latex_code = generate_latex_code(None, "\\None", None, content, title, False)
            return latex_code, ("\\None", "\\None")
        else:
            # In terminal mode, use the original interactive behavior
            return handle_missing_media_fallback(original_url, content, title, playable)

    except Exception as e:
        print(f"Error handling missing media: {str(e)}")
        # Default to \None in case of any error
        latex_code = generate_latex_code(None, "\\None", None, content, title, False)
        return latex_code, ("\\None", "\\None")




def handle_missing_media_fallback(original_url, content, title, playable):
    """
    Original implementation using standard I/O for fallback.
    Returns tuple of (latex_code, directives) where directives can be a single string or tuple of (tex_directive, text_directive)
    """
    search_query = construct_search_query(title, content)
    print(f"\nOpening Google Image search for: {search_query}")
    open_google_image_search(search_query)

    print("\nPlease choose one of the following options:")
    print("1. Enter a new URL")
    print("2. Use an existing file from media_files folder")
    print("3. Create slide without media")
    choice = input("Your choice (1/2/3): ").strip()

    if choice == '1':
        new_url = input("Enter URL: ").strip()
        if new_url:
            if 'youtube.com' in new_url or 'youtu.be' in new_url:
                result = download_youtube_video(new_url)
                if result:
                    base_name, filename, filepath = result
                    # For tex file - use local path
                    tex_directive = f"\\play \\file media_files/{filename}"
                    # For text file - use new URL with play directive if original had it
                    text_directive = f"\\play {new_url}" if playable else new_url
                    latex_code = generate_latex_code(
                        base_name,
                        filename,
                        filepath,
                        content,
                        title,
                        True,
                        new_url  # Pass URL for citation
                    )
                    return latex_code, (tex_directive, text_directive)

            # Process other URLs
            valid, message = validate_url(new_url)
            if valid:
                base_name, filename, first_frame_path = download_media(new_url)
                if base_name and filename:
                    # For tex file - use local path
                    tex_directive = f"\\file media_files/{filename}"
                    # For text file - use new URL
                    text_directive = new_url
                    if playable:
                        tex_directive = f"\\play {tex_directive}"
                        text_directive = f"\\play {text_directive}"
                    return generate_latex_code(
                        base_name,
                        filename,
                        first_frame_path,
                        content,
                        title,
                        playable,
                        new_url  # Pass URL for citation
                    ), (tex_directive, text_directive)

    elif choice == '2':
        print("\nAvailable files in media_files folder:")
        try:
            files = os.listdir('media_files')
            for i, file in enumerate(files, 1):
                print(f"{i}. {file}")
            file_choice = input("Enter file number or name: ").strip()
            if file_choice.isdigit() and 1 <= int(file_choice) <= len(files):
                chosen_file = files[int(file_choice) - 1]
            else:
                chosen_file = file_choice

            # Verify file exists
            if not os.path.exists(os.path.join('media_files', chosen_file)):
                print(f"Error: File {chosen_file} not found in media_files directory")
                return generate_latex_code(None, None, None, content, title, False), ("\\None", "\\None")

            # Use same file directive for both tex and text files
            file_directive = f"\\file media_files/{chosen_file}"
            if playable:
                file_directive = f"\\play {file_directive}"

            # Generate preview for video files if needed
            first_frame_path = None
            if playable:
                first_frame_path = generate_preview_frame(os.path.join('media_files', chosen_file))

            return generate_latex_code(
                os.path.splitext(chosen_file)[0],
                chosen_file,
                first_frame_path or chosen_file,
                content,
                title,
                playable
            ), (file_directive, file_directive)  # Same directive for both files
        except Exception as e:
            print(f"Error accessing media_files: {str(e)}")
            return generate_latex_code(None, None, None, content, title, False), ("\\None", "\\None")

    # Default to no media (choice 3 or any invalid input)
    latex_code = generate_latex_code(None, None, None, content, title, False)
    return latex_code, ("\\None", "\\None")




# Initialize terminal_io as None - will be set by IDE
terminal_io = None


def download_youtube_video(url, file_path=None):
    """
    Downloads YouTube video and returns file information.
    Returns (base_name, filename, filepath) or None if download fails.
    """
    try:
        import yt_dlp
    except ImportError:
        print("\nInstalling yt-dlp for YouTube video download...")
        os.system('pip install yt-dlp')
        import yt_dlp

    print("\nDownloading YouTube video...")
    os.makedirs('media_files', exist_ok=True)
    clean_url = url.replace('\\play', '').strip()

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'writethumbnail': False,
        'merge_output_format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info
            info = ydl.extract_info(clean_url, download=False)
            if info is None:
                print("Error: Could not extract video information")
                return None

            # Create safe filename
            video_title = info.get('title', 'video')
            safe_filename = sanitize_filename(video_title + '.mp4')
            output_path = os.path.join('media_files', safe_filename)

            # Update options with output path
            ydl_opts['outtmpl'] = output_path

            # Download with updated options
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([clean_url])

            if os.path.exists(output_path):
                base_name = os.path.splitext(safe_filename)[0]
                print(f"Video downloaded successfully to: {output_path}")
                return base_name, safe_filename, output_path

            print(f"Error: Downloaded file not found at {output_path}")
            return None

    except Exception as e:
        print(f"Error downloading YouTube video: {str(e)}")
        # Fallback to simpler format if initial attempt fails
        try:
            fallback_opts = ydl_opts.copy()
            fallback_opts['format'] = 'best'
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                ydl.download([clean_url])
                if os.path.exists(output_path):
                    base_name = os.path.splitext(safe_filename)[0]
                    print(f"Video downloaded successfully to: {output_path}")
                    return base_name, safe_filename, output_path
        except Exception as fallback_error:
            print(f"Fallback download failed: {str(fallback_error)}")
        return None



def update_input_file(file_path, url_updates, is_tex_file=False):
    """Update input file only when explicitly needed"""
    if not url_updates:  # If no updates are needed
        return True

    backup_path = file_path + '.backup'
    try:
        # Create backup
        with open(file_path, 'r') as f:
            original_content = f.readlines()
        with open(backup_path, 'w') as f:
            f.writelines(original_content)

        # Only process updates that are explicitly marked for change
        updated_lines = []
        in_content_block = False

        for line in original_content:
            line = line.rstrip('\n')

            if line.startswith("\\begin{Content}"):
                in_content_block = True
                content_parts = line.split("\\begin{Content}", 1)
                if len(content_parts) > 1 and content_parts[1].strip():
                    url_part = content_parts[1].strip()
                    if url_part in url_updates and url_updates[url_part] is not None:
                        # Only update if we have an explicit new directive
                        new_directive = url_updates[url_part][0] if is_tex_file else url_updates[url_part][1]
                        line = f"\\begin{{Content}} {new_directive}"
                updated_lines.append(line)
                continue

            elif in_content_block and (line.startswith(("http", "\\play", "\\file")) or not line.strip()):
                if line in url_updates and url_updates[line] is not None:
                    new_directive = url_updates[line][0] if is_tex_file else url_updates[line][1]
                    updated_lines.append(new_directive)
                else:
                    updated_lines.append(line)
                continue

            elif line.startswith("\\end{Content}"):
                in_content_block = False
                updated_lines.append(line)
                continue

            else:
                updated_lines.append(line)

        # Only write if there were actual changes
        if updated_lines != original_content:
            with open(file_path, 'w') as f:
                for line in updated_lines:
                    f.write(line + '\n')
            print(f"\nInput file has been updated with necessary changes.")
            print(f"Original file backed up as: {backup_path}")
        else:
            # Remove backup if no changes were made
            os.remove(backup_path)

        return True

    except Exception as e:
        print(f"Error updating file: {str(e)}")
        return False

def parse_media_directive(directive_string):
    """Parse media directive string into components.
    Returns: (directive_type, media_source, playable, original_directive)"""
    try:
        directive_string = directive_string.strip()
        playable = False
        original_directive = directive_string

        # Handle empty or None cases
        if not directive_string or directive_string == '\\None':
            return 'none', None, False, original_directive

        # Define directive mappings
        directives = {
            '\\wm': 'watermark',
            '\\ff': 'fullframe',
            '\\pip': 'pip',
            '\\split': 'split',
            '\\hl': 'highlight',
            '\\bg': 'background',
            '\\tb': 'topbottom',
            '\\ol': 'overlay',
            '\\corner': 'corner',
            '\\mosaic': 'mosaic'
        }

        # Split the string to handle multiple parts
        parts = directive_string.split()

        # Check for layout directives first
        if parts and parts[0] in directives:
            return directives[parts[0]], ' '.join(parts[1:]), False, original_directive

        # Initialize variables for other directives
        directive_type = 'url'  # default type
        media_source = directive_string  # default to full string

        # Process standard directives
        for i, part in enumerate(parts):
            if part.startswith('\\'):
                if part == '\\play':
                    playable = True
                    if i < len(parts) - 1:
                        remaining_parts = parts[i + 1:]
                        if remaining_parts[0] == '\\file':
                            directive_type = 'file'
                            media_source = ' '.join(remaining_parts[1:])
                        elif remaining_parts[0] == '\\url':
                            directive_type = 'url'
                            media_source = ' '.join(remaining_parts[1:])
                        else:
                            media_source = ' '.join(remaining_parts)
                    break
                elif part == '\\file':
                    directive_type = 'file'
                    if i < len(parts) - 1:
                        media_source = ' '.join(parts[i + 1:])
                    break
                elif part == '\\None':
                    return 'none', None, False, original_directive
                elif part == '\\url':
                    directive_type = 'url'
                    if i < len(parts) - 1:
                        media_source = ' '.join(parts[i + 1:])
                    break

        # Clean up media source
        if media_source and media_source.startswith('\\'):
            # Remove any leading \ and command name
            parts = media_source.split(maxsplit=1)
            if len(parts) > 1:
                media_source = parts[1]

        # Handle special URLs
        if directive_type == 'url' and media_source.startswith(('http://', 'https://')):
            # Special handling for known video platforms
            if any(domain in media_source.lower() for domain in ['youtube.com', 'youtu.be', 'vimeo.com']):
                playable = True

        # Handle local file paths
        if directive_type == 'file':
            # Check if it's a video file
            if media_source.lower().endswith(('.mp4', '.avi', '.mov', '.webm', '.mkv')):
                playable = True
            # Ensure proper path format
            media_source = media_source.replace('\\', '/')
            if not media_source.startswith('media_files/') and not media_source.startswith('./'):
                media_source = f"media_files/{media_source}"

        # Special handling for mosaic directive
        if directive_type == 'mosaic':
            # Ensure all image paths are properly formatted
            images = [img.strip() for img in media_source.split(',')]
            media_source = ','.join(
                f"media_files/{img}" if not img.startswith(('media_files/', './')) else img
                for img in images
            )

        return directive_type, media_source, playable, original_directive

    except Exception as e:
        print(f"Error parsing media directive: {str(e)}")
        return 'none', None, False, directive_string

def generate_special_commands():
    """Generate special effect commands for LaTeX"""
    return r"""
% Special effect commands
\newcommand{\spotlight}[1]{%
    \begin{tikzpicture}[baseline]
        \node[circle, inner sep=1pt,
              blur shadow={shadow blur steps=15, shadow xshift=0pt,
              shadow yshift=0pt, shadow blur radius=7pt,
              shadow opacity=0.3, shadow color=yellow},
              text=white] {#1};
    \end{tikzpicture}%
}

"""

def process_box_environment(content):
    """Process box environments correctly"""
    if not content:
        return ""

    result = []
    in_box = False
    current_box = []

    for line in content:
        line = line.strip()
        if line.startswith('\\begin{alertbox}') or line.startswith('\\begin{infobox}'):
            in_box = True
            current_box = [line]
        elif line.startswith('\\end{alertbox}') or line.startswith('\\end{infobox}'):
            in_box = False
            if current_box:
                current_box.append(line)
                result.append('\n'.join(current_box))
            current_box = []
        elif in_box:
            if line.startswith('-'):
                current_box.append(line[1:].strip())
            else:
                current_box.append(line)
        else:
            result.append(line)

    return result

#-----------------------------------------------------
def format_url_note(url):
    """Format URL as a clickable note with proper LaTeX hyperref formatting"""
    if 'youtube.com' in url or 'youtu.be' in url:
        return "\\textcolor{blue}{[Watch Video]: %s}" %(url)
    elif 'github.com' in url:
        return "\\textcolor{blue}{[View Repository]: %s}}" %(url)
    else:
        return "\\textcolor{blue}{[%s]}" %(url)


#------------------------------------------------------
def process_input_file(file_path, output_filename='movie.tex', ide_callback=None):
    """Process input file to convert to TeX format with proper slide navigation"""
    processed = 0
    failed = 0
    errors = []

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Get preamble information first
        has_preamble, preamble_lines, content_lines, has_titlepage, has_maketitle = detect_preamble(lines)

        with open(output_filename, 'w') as outfile:
            # Write preamble
            if has_preamble:
                outfile.writelines(preamble_lines)
                if '\\newcommand{\\spotlight}' not in ''.join(preamble_lines):
                    outfile.write(generate_special_commands())
                if not has_maketitle:
                    outfile.write("\\maketitle\n")
                if not has_titlepage:
                    outfile.write("\\begin{frame}\n\\titlepage\n\\end{frame}\n\n")
            else:
                outfile.write("\\documentclass[12pt]{beamer}\n")
                outfile.write("\\usepackage{graphicx}\n\\usepackage{multimedia}\n")
                outfile.write("\\usepackage{tcolorbox}\n")
                outfile.write(generate_special_commands())
                outfile.write("\\begin{document}\n\n")

            i = 0
            current_frame_notes = []
            current_frame_content = []
            current_frame_title = None
            current_media = None
            in_content_block = False
            in_notes_block = False

            while i < len(content_lines):
                line = content_lines[i].strip()

                # Handle document end
                if line.startswith('\\end{document}'):
                    if should_process_frame(current_frame_title, current_frame_content, current_media, current_frame_notes):
                        # Process last frame
                        process_frame(outfile, current_frame_title, current_frame_content,
                                   current_frame_notes, current_media)
                        processed += 1
                    outfile.write("\\end{document}\n")
                    break

                # Handle new frame
                if line.startswith('\\title'):
                    # Process previous frame if exists
                    if should_process_frame(current_frame_title, current_frame_content, current_media, current_frame_notes):
                        process_frame(outfile, current_frame_title, current_frame_content,
                                   current_frame_notes, current_media)
                        processed += 1

                    # Start new frame
                    current_frame_title = line[6:].strip()  # Remove '\title' prefix
                    current_frame_content = []
                    current_frame_notes = []
                    current_media = None

                # Handle Content blocks
                elif line.startswith('\\begin{Content}'):
                    in_content_block = True
                    if len(line) > len('\\begin{Content}'):
                        current_media = line[len('\\begin{Content}'):].strip()

                elif line.startswith('\\end{Content}'):
                    in_content_block = False

                # Handle Notes blocks
                elif line.startswith('\\begin{Notes}'):
                    in_notes_block = True
                elif line.startswith('\\end{Notes}'):
                    in_notes_block = False

                # Process content
                elif in_content_block:
                    if line.strip():  # Only add non-empty lines
                        current_frame_content.append(line)
                # Process notes
                elif in_notes_block:
                    if line.strip() and not line.startswith('%'):
                        if line.startswith(('http://', 'https://','www')):
                            current_frame_notes.append('\\begin{itemize}')
                            current_frame_notes.append(format_url_note(line.strip()))
                            current_frame_notes.append('\\end{itemize}')
                        else:
                            current_frame_notes.append(line.strip())

                i += 1

        return processed, failed, errors

    except Exception as e:
        error_msg = f"Error processing file: {str(e)}"
        errors.append(error_msg)
        if ide_callback:
            ide_callback("error", {'message': error_msg})
        return processed, failed, errors

def should_process_frame(title, content, media, notes):
    """
    Determine if a frame should be processed based on its components.
    A frame should be processed if it has any of: title, content, media, or notes.
    """
    return (title is not None or
            media is not None or
            (content is not None and len(content) > 0) or
            (notes is not None and len(notes) > 0))

def process_frame(outfile, title, content, notes, media):
    """Process a single frame and write it to the output file"""
    # Generate frame content
    latex_code, directive = process_media(
        media if media else "\\None",
        content if content else [],  # Pass empty list instead of None
        title,
        False  # playable flag
    )

    # Insert notes before \end{frame}
    if latex_code and notes:
        frame_end = latex_code.rfind('\\end{frame}')
        if frame_end != -1:
            notes_text = '\n'.join(f'    \\note{{{note}}}' for note in notes)
            latex_code = latex_code[:frame_end] + '\n' + notes_text + '\n' + latex_code[frame_end:]

    outfile.write(latex_code + '\n')

#------------------------------------------------------

def main():
    """
    Main execution function with enhanced file creation capability.
    """
    print("BeamerSlideGenerator: Creating slides for presentations")
    print("Choose an option:")
    print("1. Process a single media URL (appends to movie.tex)")
    print("2. Process multiple media files from an input file (creates new .tex file)")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        url = input("Enter the media URL or local file (local:filename): ").strip()
        title = input("Enter slide title (optional, press Enter to skip): ").strip()
        content = input("Enter content for the right column (optional, press Enter to skip): ").strip()
        playable = input("Is this media playable? (y/n): ").lower().startswith('y')

        latex_code = process_media(url, content if content else None, title if title else None, playable)
        if latex_code:
            with open('movie.tex', 'a') as f:
                if not os.path.exists('movie.tex'):
                    f.write("""\\documentclass{beamer}
\\usepackage{graphicx}
\\usepackage{multimedia}
\\usepackage{xcolor}

\\begin{document}

""")
                f.write(latex_code)
                f.write("\\end{document}")
            print("Slide has been added to 'movie.tex'.")
    elif choice == '2':
        file_path = input("Enter the path to the input file: ")

        # Check if file exists
        if not os.path.exists(file_path):
            print(f"\nFile {file_path} does not exist.")
            create_new = input("Would you like to create a new presentation? (y/n): ").lower().strip()

            if create_new.startswith('y'):
                if create_new_input_file(file_path):
                    print("\nNew presentation file created. Processing the file...")
                else:
                    print("\nFailed to create new presentation file.")
                    return
            else:
                print("\nOperation cancelled.")
                return

        output_file = os.path.splitext(os.path.basename(file_path))[0] + '.tex'
        process_input_file(file_path, output_file)
        print(f"All slides have been written to '{output_file}'.")
    else:
        print("Invalid choice. Please run the script again and choose 1 or 2.")


if __name__ == "__main__":
    main()
