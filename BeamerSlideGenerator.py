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
    """Returns complete Beamer preamble with intelligent auto-scaling and frame mode support"""

    def clean_text(text):
        if not text:
            return text
        text = text.replace('{{', '').replace('}}', '')
        text = text.replace('{{{', '').replace('}}}', '')
        text = text.replace('&', '\\&')
        text = text.replace('%', '\\%')
        text = text.replace('$', '\\$')
        text = text.replace('#', '\\#')
        text = text.replace('_', '\\_')
        text = text.replace('{', '\\{')
        text = text.replace('}', '\\}')
        text = text.replace('~', '\\textasciitilde')
        text = text.replace('^', '\\textasciicircum')
        return text

    title = clean_text(title)
    subtitle = clean_text(subtitle) if subtitle else ""
    author = clean_text(author)
    institution = clean_text(institution)
    short_institute = clean_text(short_institute) if short_institute else clean_text(institution)
    date = clean_text(date) if date else r'\today'

    core_preamble = r"""
\documentclass[aspectratio=169]{beamer}

% Essential packages
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
\usepackage{booktabs}
\usepackage{grffile}
\usepackage{adjustbox}
\usepackage{environ}

% NO geometry - let aspectratio handle sizing

% Load TikZ libraries
\usetikzlibrary{positioning}
\usetikzlibrary{shapes.symbols}
\usetikzlibrary{shapes.callouts}
\usetikzlibrary{shapes.multipart}
\usetikzlibrary{calc}
\usetikzlibrary{overlay-beamer-styles}
\usetikzlibrary{shapes.geometric}
\usetikzlibrary{arrows.meta}
\usetikzlibrary{backgrounds}
\usetikzlibrary{fit}

\setbeamercovered{dynamic}
\setbeamerfont{item projected}{size=\small}
\setbeamercolor{alerted text}{fg=white}

% Extended packages with fallbacks
\IfFileExists{tcolorbox.sty}{\usepackage{tcolorbox}}{}
\IfFileExists{fontawesome5.sty}{\usepackage{fontawesome5}}{}
\IfFileExists{pifont.sty}{\usepackage{pifont}}{}
\IfFileExists{soul.sty}{\usepackage{soul}}{}

\pgfplotsset{compat=1.18}

\newcommand{\shadowtext}[2][2pt]{%
    \textcolor{white}{\textbf{#2}}%
}

\newcommand{\glowtext}[2][myblue]{%
    \textcolor{#1}{\textbf{#2}}%
}

\IfFileExists{tcolorbox.sty}{%
    \newtcolorbox{alertbox}[1][red]{%
        colback=##1!5!white,
        colframe=##1!75!black,
        fonttitle=\bfseries,
        boxrule=0.5pt,
        rounded corners
    }
    \newtcolorbox{infobox}[1][blue]{%
        enhanced,
        colback=##1!5!white,
        colframe=##1!75!black,
        arc=4mm,
        boxrule=0.5pt,
        fonttitle=\bfseries,
        attach boxed title to top center={yshift=-3mm,yshifttext=-1mm},
        boxed title style={size=small,colback=##1!75!black}
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
\definecolor{mygray}{RGB}{128,128,128}
\definecolor{mybrown}{RGB}{139,69,19}
\definecolor{mycyan}{RGB}{0,255,255}

\newcommand{\hlbias}[1]{\textcolor{myblue}{\textbf{#1}}}
\newcommand{\hlvariance}[1]{\textcolor{mypink}{\textbf{#1}}}
\newcommand{\hltotal}[1]{\textcolor{myyellow}{\textbf{#1}}}
\newcommand{\hlkey}[1]{\colorbox{myblue!20}{\textbf{#1}}}
\newcommand{\hlnote}[1]{\colorbox{mygreen!20}{\textbf{#1}}}
"""

    layout_commands = r"""
% ========== LAYOUT COMMANDS ==========
\ifcsname split\endcsname\else
\newcommand{\split}[2]{%
    \begin{columns}[T]
        \begin{column}{0.45\textwidth}
            \begin{center}
                \includegraphics[width=\textwidth,keepaspectratio]{#1}
            \end{center}
        \end{column}
        \begin{column}{0.5\textwidth}
            #2
        \end{column}
    \end{columns}
}
\fi

\ifcsname pip\endcsname\else
\newcommand{\pip}[2]{%
    \begin{columns}[T]
        \begin{column}{0.68\textwidth}
            #2
        \end{column}
        \begin{column}{0.28\textwidth}
            \vspace{1em}
            \includegraphics[width=\textwidth,keepaspectratio]{#1}
        \end{column}
    \end{columns}
}
\fi

\ifcsname ff\endcsname\else
\newcommand{\ff}[1]{%
    \setbeamertemplate{background}{%
        \begin{tikzpicture}[remember picture,overlay]
            \node at (current page.center) {%
                \includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio]{#1}
            };
        \end{tikzpicture}%
    }
    \begin{center}
        \vfill
        \textcolor{white}{\textbf{Full Frame Image}}
        \vfill
    \end{center}
}
\fi

\ifcsname wm\endcsname\else
\newcommand{\wm}[1]{%
    \setbeamertemplate{background}{%
        \begin{tikzpicture}[remember picture,overlay]
            \node[opacity=0.15] at (current page.center) {%
                \includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio]{#1}
            };
        \end{tikzpicture}%
    }
}
\fi

\ifcsname hl\endcsname\else
\newcommand{\hl}[2]{%
    \begin{columns}[T]
        \begin{column}{0.6\textwidth}
            \includegraphics[width=\textwidth,keepaspectratio]{#1}
        \end{column}
        \begin{column}{0.36\textwidth}
            \colorbox{yellow!20}{%
                \begin{minipage}{\textwidth}
                    #2
                \end{minipage}%
            }
        \end{column}
    \end{columns}
}
\fi

\ifcsname bg\endcsname\else
\newcommand{\bg}[1]{%
    \setbeamertemplate{background}{%
        \begin{tikzpicture}[remember picture,overlay]
            \node[opacity=0.3] at (current page.center) {%
                \includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio]{#1}
            };
        \end{tikzpicture}%
    }
}
\fi

\ifcsname tb\endcsname\else
\newcommand{\tb}[2]{%
    \begin{center}
        \includegraphics[width=0.8\textwidth,keepaspectratio]{#1}
    \end{center}
    \vspace{0.5em}
    #2
}
\fi

\ifcsname ol\endcsname\else
\newcommand{\ol}[1]{%
    \begin{tikzpicture}[remember picture,overlay]
        \node at (current page.center) {%
            \includegraphics[width=\paperwidth,keepaspectratio]{#1}
        };
    \end{tikzpicture}%
}
\fi

\ifcsname corner\endcsname\else
\newcommand{\corner}[2]{%
    \begin{tikzpicture}[remember picture,overlay]
        \node[anchor=south east] at (current page.south east) {%
            \includegraphics[width=0.25\textwidth,keepaspectratio]{#1}
        };
    \end{tikzpicture}%
    #2
}
\fi

\ifcsname mosaic\endcsname\else
\newcommand{\mosaic}[2]{%
    \begingroup
    \def\mosaic@params{#1}%
    \def\mosaic@images{#2}%
    \pgfmathsetmacro{\mosaic@rows}{{\mosaic@params}[0]}%
    \pgfmathsetmacro{\mosaic@cols}{{\mosaic@params}[2]}%
    \begin{center}
    \begin{tabular}{*{\mosaic@cols}{c}}
    \hline
    \mosaic@process
    \hline
    \end{tabular}
    \end{center}
    \endgroup
}
\def\mosaic@process{%
    \mosaic@process@helper\mosaic@images,\@empty
}
\def\mosaic@process@helper#1,#2\@empty{%
    \ifx\@empty#2\@empty
        \includegraphics[width=0.3\textwidth,keepaspectratio]{#1}%
    \else
        \includegraphics[width=0.3\textwidth,keepaspectratio]{#1} &
        \def\mosaic@remaining{#2}%
        \mosaic@process@next
    \fi
}
\def\mosaic@process@next{%
    \mosaic@process@helper\mosaic@remaining,\@empty
}
\fi
"""

    theme_setup = r"""
% Theme setup
\usetheme{Madrid}
\usecolortheme{owl}

\setbeamercolor{normal text}{fg=white}
\setbeamercolor{structure}{fg=myyellow}
\setbeamercolor{alerted text}{fg=myorange}
\setbeamercolor{example text}{fg=mygreen}
\setbeamercolor{background canvas}{bg=black}
\setbeamercolor{frametitle}{fg=white,bg=black}

\usepackage{pgfpages}
\setbeameroption{show notes on second screen=right}
\setbeamertemplate{note page}{\pagecolor{yellow!5}\insertnote}

\newcommand{\anbg}[2][0.2]{%
    \ifx\@empty#2\@empty
        \setbeamertemplate{background}{}
    \else
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

    progress_bar = r"""
% Progress bar
\makeatletter
\def\progressbar@progressbar{}
\newcount\progressbar@tmpcounta
\newcount\progressbar@tmpcountb
\newdimen\progressbar@pbht
\newdimen\progressbar@pbwd
\newdimen\progressbar@tmpdim

\progressbar@pbwd=\paperwidth
\progressbar@pbht=2pt

\def\progressbar@progressbar{%
   \begin{tikzpicture}[very thin]
       \ifnum\insertframenumber>0
           \pgfmathparse{\insertframenumber/\inserttotalframenumber}
           \edef\progress@ratio{\pgfmathresult}
           \shade[top color=myblue!50,bottom color=myblue]
               (0pt, 0pt) rectangle (\progress@ratio\progressbar@pbwd, \progressbar@pbht);
       \fi
   \end{tikzpicture}%
}

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
\makeatother
"""

    # ========== TIGHTER SPACING - NO FRAME REDEFINITION ==========
    auto_scaling = r"""
% ========== TIGHTER SPACING FOR DENSE CONTENT ==========
% This reduces whitespace to fit more content
% No frame redefinition - safe and reliable

\setlength{\parskip}{0.12em}
\setlength{\itemsep}{0.04em}
\setlength{\topsep}{0.04em}
\setlength{\partopsep}{0pt}
\setlength{\abovedisplayskip}{0pt}
\setlength{\belowdisplayskip}{0pt}
\setlength{\abovedisplayshortskip}{0pt}
\setlength{\belowdisplayshortskip}{0pt}

% Make itemize more compact
\def\beamer@itemize@itemshape{%
    \setlength{\itemsep}{0.04em}%
    \setlength{\topsep}{0.04em}%
    \setlength{\partopsep}{0pt}%
}

% Reduce block spacing
\setbeamertemplate{blocks}[rounded][shadow=true]
\addtobeamertemplate{block begin}{%
    \setlength{\abovedisplayskip}{0pt}%
    \setlength{\belowdisplayskip}{0pt}%
}{}

% Reduce table spacing
\setlength{\arrayrulewidth}{0.4pt}
\renewcommand{\arraystretch}{0.9}
\setlength{\tabcolsep}{2pt}
"""

    inst_setup = rf"\makeatletter\def\insertshortinstitute{{{short_institute}}}\makeatother"

    footline_template = r"""
% Footline
\setbeamertemplate{footline}{%
 \leavevmode%
 \hbox{%
   \begin{beamercolorbox}[wd=.333333\paperwidth,ht=1.8ex,dp=0.6ex,center]{author in head/foot}%
     \usebeamerfont{author in head/foot}\insertshortauthor~(\insertshortinstitute)%
   \end{beamercolorbox}%
   \begin{beamercolorbox}[wd=.333333\paperwidth,ht=1.8ex,dp=0.6ex,center]{title in head/foot}%
     \usebeamerfont{title in head/foot}\insertshorttitle%
   \end{beamercolorbox}%
   \begin{beamercolorbox}[wd=.333333\paperwidth,ht=1.8ex,dp=0.6ex,right]{date in head/foot}%
     \usebeamerfont{date in head/foot}\insertshortdate{}\hspace*{1em}%
     \insertframenumber{} / \inserttotalframenumber\hspace*{1ex}%
   \end{beamercolorbox}}%
 \vskip0pt%
}

\setbeamersize{text margin left=4pt,text margin right=4pt}
\setbeamertemplate{navigation symbols}{}
"""

    # ========== FRAME MODE HELPER MACROS ==========
    # NOTE: plainframe is already defined in BeamerSlideGenerator, so we skip it
    helper_macros = r"""
% ========== FRAME MODE HELPER MACROS ==========
% These macros support the GUI frame mode selector
% - Normal: Standard Beamer frame
% - Shrink: Auto-shrinks content to fit
% - Break: Auto-breaks content across frames
% - Smart: Both shrink and break

% Shrink frame - content auto-shrinks if too large
\ifcsname shrinkframe\endcsname\else
\newenvironment{shrinkframe}[1][]{%
    \begin{frame}[#1, shrink, shrink=3, shrink=5, shrink=8, shrink=10]%
}{%
    \end{frame}%
}
\fi

% Break frame - content auto-breaks across frames
\ifcsname breakframe\endcsname\else
\newenvironment{breakframe}[1][]{%
    \begin{frame}[#1, allowframebreaks]%
}{%
    \end{frame}%
}
\fi

% Smart frame - both shrink and break
\ifcsname smartframe\endcsname\else
\newenvironment{smartframe}[1][]{%
    \begin{frame}[#1, allowframebreaks, shrink, shrink=3, shrink=5, shrink=8, shrink=10]%
}{%
    \end{frame}%
}
\fi

% plainframe is already defined in BeamerSlideGenerator, so we don't redefine it
"""

    title_setup = (
       "% Title setup\n"
       f"\\title{{{title}}}\n"
       + (f"\\subtitle{{{subtitle}}}\n" if subtitle else "") +
       f"\\author{{{author}}}\n"
       f"\\institute{{\\textcolor{{mygreen}}{{{institution}}}}}\n"
       f"\\date{{{date}}}\n"
       "\\begin{document}\n"
    )

    title_page = (
       "% Title page\n"
       "\\begin{frame}[plain]\n"
       "   \\begin{tikzpicture}[overlay,remember picture]\n"
       "       \\fill[top color=black!90,bottom color=black!70,middle color=myblue!30]\n"
       "       (current page.south west) rectangle (current page.north east);\n"
       "       \\node[align=center] at (current page.center) {\n"
       f"           {{\\Huge\\textcolor{{myblue}}{{\\textbf{{{title}}}}}}}\n"
       + (f"           \\\\[1em]{{\\large\\textcolor{{myyellow}}{{{subtitle}}}}}\n" if subtitle else "") +
       f"           \\\\[2em]\n"
       f"           {{\\large\\textcolor{{mygreen}}{{{author}}}}}\n"
       f"           \\\\[0.5em]\n"
       f"           \\textcolor{{white}}{{\\small {institution}}}\n"
       f"           \\\\[1em]\n"
       f"           \\textcolor{{white}}{{\\small {date}}}\n"
       "       };\n"
       "   \\end{tikzpicture}\n"
       "\\end{frame}"
    )

    return "\n".join([
        core_preamble,
        layout_commands,
        theme_setup,
        progress_bar,
        inst_setup,
        footline_template,
        auto_scaling,
        helper_macros,
        title_setup,
        title_page
    ])

def get_footline_template():
    """
    Returns the correct footline template for Beamer.
    FIXED: Removed problematic parameter references
    """
    return r"""% Setup footline template with proper short institute handling
\makeatletter
\defbeamertemplate*{footline}{custom}
{
  \leavevmode%
  \hbox{%
    \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,center]{author in head/foot}%
      \usebeamerfont{author in head/foot}\insertshortauthor~(\usebeamercolor[fg]{author in head/foot}\insertshortinstitute)
    \end{beamercolorbox}%
    \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,center]{title in head/foot}%
      \usebeamerfont{title in head/foot}\insertshorttitle
    \end{beamercolorbox}%
    \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,right]{date in head/foot}%
      \usebeamerfont{date in head/foot}\insertshortdate{\,}\hspace*{2em}
      \insertframenumber{} / \inserttotalframenumber\hspace*{2ex}
    \end{beamercolorbox}}%
  \vskip0pt%
}
\setbeamertemplate{footline}[custom]
\makeatother
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
    Detects if the input file has a complete preamble.
    Handles both standard LaTeX and native format.
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
        # Check for \title{...} (not \title Slide 1)
        if '\\title{' in line and not line.startswith('\\title '):
            has_title = True
        if '\\begin{document}' in line:
            has_begin_document = True
            preamble_end_idx = i
            break

    # If we have \begin{document}, we have a preamble
    if has_begin_document:
        # Check if we also have native format slides (\title without braces)
        has_native_titles = any(line.strip().startswith('\\title ') and '\\title{' not in line for line in lines)

        if has_native_titles:
            # This is a hybrid format: preamble + native slides
            # The preamble ends at \begin{document}
            preamble_lines = lines[:preamble_end_idx + 1]
            content_lines = lines[preamble_end_idx + 1:]
            return True, preamble_lines, content_lines, has_titlepage, has_maketitle

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
    """Process all special text effects - SIMPLIFIED VERSION"""
    if not content_line:
        return content_line

    # Replace all custom text effects with simple LaTeX equivalents
    # This prevents compilation errors from problematic TikZ code

    # Process glowtext - replace with colored text
    while '\\glowtext[' in content_line or '\\glowtext{' in content_line:
        match = re.search(r'\\glowtext(?:\[(.*?)\])?\{(.*?)\}', content_line)
        if not match:
            break
        color_args, text = match.group(1), match.group(2)
        color = color_args.strip() if color_args else 'myblue'
        # Simple colored bold text instead of glow effect
        replacement = f"\\textcolor{{{color}}}{{\\textbf{{{text}}}}}"
        content_line = content_line.replace(match.group(0), replacement)

    # Process shadowtext - replace with bold text
    while '\\shadowtext[' in content_line or '\\shadowtext{' in content_line:
        match = re.search(r'\\shadowtext(?:\[(.*?)\])?\{(.*?)\}', content_line)
        if not match:
            break
        color_args, text = match.group(1), match.group(2)
        # Simple bold text instead of shadow effect
        replacement = f"\\textbf{{{text}}}"
        content_line = content_line.replace(match.group(0), replacement)

    # Process gradienttext - replace with colored text
    while '\\gradienttext[' in content_line:
        match = re.search(r'\\gradienttext\[(.*?)\]\[(.*?)\]\{(.*?)\}', content_line)
        if not match:
            break
        start_color, end_color, text = match.group(1), match.group(2), match.group(3)
        # Use the second color (end color) for simple coloring
        replacement = f"\\textcolor{{{end_color}}}{{{text}}}"
        content_line = content_line.replace(match.group(0), replacement)

    # Keep highlighting commands but ensure they're properly formatted
    # Process highlighting
    while '\\hlkey[' in content_line or '\\hlkey{' in content_line:
        match = re.search(r'\\hlkey(?:\[(.*?)\])?\{(.*?)\}', content_line)
        if not match:
            break
        color_args, text = match.group(1), match.group(2)
        bg_color = color_args.strip() if color_args else 'myblue!20'
        replacement = f"\\colorbox{{{bg_color}}}{{\\textbf{{{text}}}}}"
        content_line = content_line.replace(match.group(0), replacement)

    # Process note highlighting
    while '\\hlnote[' in content_line or '\\hlnote{' in content_line:
        match = re.search(r'\\hlnote(?:\[(.*?)\])?\{(.*?)\}', content_line)
        if not match:
            break
        color_args, text = match.group(1), match.group(2)
        bg_color = color_args.strip() if color_args else 'mygreen!20'
        replacement = f"\\colorbox{{{bg_color}}}{{\\textbf{{{text}}}}}"
        content_line = content_line.replace(match.group(0), replacement)

    return content_line

def process_latex_content(content_line: str) -> str:
    """Enhanced content processing that preserves TikZ content."""
    if not content_line:
        return content_line

    # If it's TikZ content, return as-is (but sanitized)
    if '\\begin{tikzpicture}' in content_line or '\\end{tikzpicture}' in content_line:
        return sanitize_latex_content(content_line)

    # If it's other LaTeX environment, return as-is (but sanitized)
    if content_line.startswith(('\\begin{', '\\end{', '\\scalebox{')):
        return sanitize_latex_content(content_line)

    # Original processing for regular text
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

    processed = ''.join(result)
    # Final sanitization
    return sanitize_latex_content(processed)

#----------------------------------------------------------------------
def generate_latex_code(base_name, filename, first_frame_path, content=None, title=None, playable=False, source_url=None, layout=None):
    """
    Generate LaTeX code with support for all media layouts.
    PRESERVES all user specifications including column widths, math, TikZ, and LaTeX environments.
    NO HARDCODED COLUMN WIDTHS - respects user input completely.
    """

    def clean_frame_title(title_text):
        """Clean frame title to prevent compilation errors"""
        if not title_text:
            return "Untitled"

        title_text = str(title_text)
        title_text = title_text.replace('\\{', '').replace('\\}', '')
        title_text = title_text.replace('{', '').replace('}', '')
        title_text = title_text.replace('&', '\\&')
        title_text = title_text.replace('%', '\\%')
        title_text = title_text.replace('#', '\\#')
        title_text = title_text.strip()

        if not title_text:
            return "Untitled"
        return title_text

    # Process title
    if title:
        frame_title = clean_frame_title(title)
    else:
        base_name_escaped = clean_frame_title(base_name if base_name else 'Untitled')
        frame_title = "Media: " + base_name_escaped

    frame_title_code = frame_title

    # ========== CHECK FOR EXISTING COLUMNS IN CONTENT ==========
    has_existing_columns = False
    existing_columns_content = None

    if content:
        content_str = '\n'.join(str(c) for c in content)
        if '\\begin{columns}' in content_str and '\\end{columns}' in content_str:
            has_existing_columns = True
            import re
            col_match = re.search(r'(\\begin\{columns\}.*?\\end\{columns\})', content_str, re.DOTALL)
            if col_match:
                existing_columns_content = col_match.group(1)

    # ========== IF CONTENT HAS EXISTING COLUMNS, USE THEM DIRECTLY ==========
    if has_existing_columns and existing_columns_content:
        latex_code = f"\\begin{{frame}}{{{frame_title_code}}}\n"
        latex_code += f"\\frametitle{{{frame_title_code}}}\n"

        content_str = '\n'.join(str(c) for c in content)
        before_columns = content_str.split('\\begin{columns}')[0].strip()
        if before_columns:
            latex_code += before_columns + "\n"

        latex_code += existing_columns_content + "\n"

        after_columns = content_str.split('\\end{columns}')[-1].strip() if '\\end{columns}' in content_str else ""
        if after_columns:
            latex_code += after_columns + "\n"

        latex_code += "\\end{frame}\n"
        return latex_code

    # ========== EXTRACT CUSTOM COLUMN WIDTHS FROM CONTENT ==========
    custom_left_width = None
    custom_right_width = None

    if content:
        content_str = '\n'.join(str(c) for c in content)
        import re
        col_match = re.findall(r'\\column\{([^}]+)\}', content_str)
        if len(col_match) >= 1:
            custom_left_width = col_match[0]
        if len(col_match) >= 2:
            custom_right_width = col_match[1]

    # ========== CHECK IF CONTENT HAS CUSTOM IMAGE WIDTH ==========
    custom_image_width = None
    if content:
        content_str = '\n'.join(str(c) for c in content)
        import re
        # Look for \includegraphics[width=...] or similar
        width_match = re.search(r'\\includegraphics\[width=([^\]]+)\]', content_str)
        if width_match:
            custom_image_width = width_match.group(1)
        else:
            # Look for width parameter in the filename or params
            width_match = re.search(r'width[=\s]*([0-9.]+\\?\\?textwidth)', content_str, re.IGNORECASE)
            if width_match:
                custom_image_width = width_match.group(1)

    # Check if content contains TikZ
    has_tikz = False
    if content:
        for item in content:
            if isinstance(item, str) and '\\begin{tikzpicture}' in item:
                has_tikz = True
                break

    # ========== HANDLE NO MEDIA CASE WITH TIKZ ==========
    if has_tikz and (not filename or filename == "\\None"):
        latex_code = f"\\begin{{frame}}{{{frame_title_code}}}\n"
        latex_code += f"\\frametitle{{{frame_title_code}}}\n"

        in_itemize = False
        for item in content:
            if isinstance(item, str):
                item_str = item.strip()
                if not item_str:
                    continue

                if '\\begin{tikzpicture}' in item_str:
                    if in_itemize:
                        latex_code += "    \\end{itemize}\n"
                        in_itemize = False
                    latex_code += f"    {item_str}\n"
                elif item_str.startswith('-'):
                    if not in_itemize:
                        latex_code += "    \\begin{itemize}\n"
                        in_itemize = True
                    clean_item = item_str[1:].strip()
                    processed_item = process_latex_content(clean_item)
                    latex_code += f"        \\item {processed_item}\n"
                elif in_itemize:
                    latex_code += "    \\end{itemize}\n"
                    in_itemize = False
                    processed_item = process_latex_content(item_str)
                    latex_code += f"    {processed_item}\n"
                else:
                    processed_item = process_latex_content(item_str)
                    latex_code += f"    {processed_item}\n"

        if in_itemize:
            latex_code += "    \\end{itemize}\n"
        latex_code += "\\end{frame}\n"
        return latex_code

    # ========== HANDLE NO MEDIA CASE ==========
    if not filename or filename == "\\None":
        latex_code = f"\\begin{{frame}}{{{frame_title_code}}}\n"
        latex_code += f"\\frametitle{{{frame_title_code}}}\n"
        content_items = generate_content_items(content)
        if content_items:
            latex_code += "    " + content_items + "\n"
        latex_code += "\\end{frame}\n"
        return latex_code

    # ========== GENERATE LAYOUT BASED ON DIRECTIVE ==========
    latex_code = ""

    # SPLIT LAYOUT - Preserve user column widths
    if layout == 'split':
        left_width = custom_left_width if custom_left_width else "0.48\\textwidth"
        right_width = custom_right_width if custom_right_width else "0.48\\textwidth"

        latex_code = f"\\begin{{frame}}{{{frame_title_code}}}\n"
        latex_code += f"\\frametitle{{{frame_title_code}}}\n"
        latex_code += "    \\begin{columns}[T]\n"
        latex_code += f"        \\begin{{column}}{{{left_width}}}\n"

        # Use custom image width if specified
        if custom_image_width:
            latex_code += f"            \\includegraphics[width={custom_image_width},keepaspectratio]{{{filename}}}\n"
        else:
            latex_code += f"            \\includegraphics[width=\\textwidth,keepaspectratio]{{{filename}}}\n"

        latex_code += "        \\end{column}\n"
        latex_code += f"        \\begin{{column}}{{{right_width}}}\n"
        content_items = generate_content_items(content)
        if content_items:
            latex_code += "        " + content_items + "\n"
        latex_code += "        \\end{column}\n"
        latex_code += "    \\end{columns}\n"
        latex_code += "\\end{frame}\n"
        return latex_code

    # PIP LAYOUT - Preserve user column widths
    elif layout == 'pip':
        left_width = custom_left_width if custom_left_width else "0.68\\textwidth"
        right_width = custom_right_width if custom_right_width else "0.28\\textwidth"

        latex_code = f"\\begin{{frame}}{{{frame_title_code}}}\n"
        latex_code += f"\\frametitle{{{frame_title_code}}}\n"
        latex_code += "    \\begin{columns}[T]\n"
        latex_code += f"        \\begin{{column}}{{{left_width}}}\n"
        content_items = generate_content_items(content)
        if content_items:
            latex_code += "        " + content_items + "\n"
        latex_code += "        \\end{column}\n"
        latex_code += f"        \\begin{{column}}{{{right_width}}}\n"
        latex_code += "            \\vspace{1em}\n"

        if custom_image_width:
            latex_code += f"            \\includegraphics[width={custom_image_width},keepaspectratio]{{{filename}}}\n"
        else:
            latex_code += f"            \\includegraphics[width=\\textwidth,keepaspectratio]{{{filename}}}\n"

        latex_code += "        \\end{column}\n"
        latex_code += "    \\end{columns}\n"
        latex_code += "\\end{frame}\n"
        return latex_code

    # ========== DEFAULT SIDE-BY-SIDE LAYOUT ==========
    # Determine if we should use two columns or single column
    use_two_columns = False

    # Check if content has multiple items or bullet points that would benefit from two columns
    if content:
        non_empty_items = [c for c in content if c and str(c).strip()]
        if len(non_empty_items) > 1 or has_tikz:
            use_two_columns = True

    # Check if user specified a custom image width
    image_width = custom_image_width if custom_image_width else "0.7\\textwidth"
    if not use_two_columns and not custom_image_width:
        # Single column - use larger image
        image_width = "0.7\\textwidth"

    if playable and first_frame_path:
        latex_code = f"\\begin{{frame}}{{{frame_title_code}}}\n"
        latex_code += f"\\frametitle{{{frame_title_code}}}\n"

        if use_two_columns:
            # Two columns - respect user column widths if specified
            left_width = custom_left_width if custom_left_width else "0.48\\textwidth"
            right_width = custom_right_width if custom_right_width else "0.48\\textwidth"

            latex_code += "    \\begin{columns}[T]\n"
            latex_code += f"        \\begin{{column}}{{{left_width}}}\n"
            latex_code += f"            \\includegraphics[width=\\textwidth,height=0.6\\textheight,keepaspectratio]{{{first_frame_path}}}\n"
            latex_code += "            \\begin{center}\n"
            latex_code += "                \\vspace{0.3em}\n"
            latex_code += "                \\footnotesize Click to play\\\\\n"
            latex_code += f"                \\movie[externalviewer]{{\\textcolor{{blue}}{{\\underline{{Play}}}}}}{{{filename}}}\n"
            latex_code += "            \\end{center}\n"
            latex_code += "        \\end{column}\n"
            latex_code += f"        \\begin{{column}}{{{right_width}}}\n"
            content_items = generate_content_items(content)
            if content_items:
                latex_code += "        " + content_items + "\n"
            if source_url:
                latex_code += "        " + format_url_footnote(source_url) + "\n"
            latex_code += "        \\end{column}\n"
            latex_code += "    \\end{columns}\n"
        else:
            # Single column layout - content below image
            latex_code += "    \\begin{center}\n"
            latex_code += f"        \\includegraphics[width={image_width},keepaspectratio]{{{first_frame_path}}}\n"
            latex_code += "        \\begin{center}\n"
            latex_code += "            \\vspace{0.3em}\n"
            latex_code += "            \\footnotesize Click to play\\\\\n"
            latex_code += f"            \\movie[externalviewer]{{\\textcolor{{blue}}{{\\underline{{Play}}}}}}{{{filename}}}\n"
            latex_code += "        \\end{center}\n"
            latex_code += "    \\end{center}\n"
            content_items = generate_content_items(content)
            if content_items:
                latex_code += "    " + content_items + "\n"
            if source_url:
                latex_code += "    " + format_url_footnote(source_url) + "\n"

        latex_code += "\\end{frame}\n"
    else:
        latex_code = f"\\begin{{frame}}{{{frame_title_code}}}\n"
        latex_code += f"\\frametitle{{{frame_title_code}}}\n"

        if use_two_columns:
            # Two columns - respect user column widths if specified
            left_width = custom_left_width if custom_left_width else "0.48\\textwidth"
            right_width = custom_right_width if custom_right_width else "0.48\\textwidth"

            latex_code += "    \\begin{columns}[T]\n"
            latex_code += f"        \\begin{{column}}{{{left_width}}}\n"
            latex_code += f"            \\includegraphics[width=\\textwidth,keepaspectratio]{{{filename}}}\n"
            latex_code += "        \\end{column}\n"
            latex_code += f"        \\begin{{column}}{{{right_width}}}\n"
            content_items = generate_content_items(content)
            if content_items:
                latex_code += "        " + content_items + "\n"
            if source_url:
                latex_code += "        " + format_url_footnote(source_url) + "\n"
            latex_code += "        \\end{column}\n"
            latex_code += "    \\end{columns}\n"
        else:
            # Single column layout - content below image
            latex_code += "    \\begin{center}\n"
            latex_code += f"        \\includegraphics[width={image_width},keepaspectratio]{{{filename}}}\n"
            latex_code += "    \\end{center}\n"
            content_items = generate_content_items(content)
            if content_items:
                latex_code += "    " + content_items + "\n"
            if source_url:
                latex_code += "    " + format_url_footnote(source_url) + "\n"

    latex_code += "\\end{frame}\n"
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

# Add this function to detect and process TikZ content
def detect_tikz_content(content_lines):
    """Detect if content contains TikZ diagram and extract it properly."""
    tikz_blocks = []
    remaining_content = []
    in_tikz = False
    current_tikz = []

    for line in content_lines:
        stripped = line.strip()

        # Detect start of TikZ environment
        if '\\begin{tikzpicture}' in stripped:
            in_tikz = True
            current_tikz = [stripped]
        # Detect end of TikZ environment
        elif in_tikz and '\\end{tikzpicture}' in stripped:
            current_tikz.append(stripped)
            tikz_blocks.append('\n'.join(current_tikz))
            in_tikz = False
        # Inside TikZ environment
        elif in_tikz:
            current_tikz.append(stripped)
        # Outside TikZ environment - treat as regular content
        else:
            if stripped and not stripped.startswith('%'):
                remaining_content.append(line)

    return tikz_blocks, remaining_content

# Update the process_frame function to handle TikZ content
def process_frame(outfile, title, content, notes, media):
    """Process a single frame and write it to the output file"""

    # Separate TikZ content from regular content
    tikz_blocks, regular_content = detect_tikz_content(content if content else [])

    # If we have TikZ content, handle it specially
    if tikz_blocks:
        # Create a combined content list with TikZ blocks properly formatted
        combined_content = []

        for tikz_block in tikz_blocks:
            # Wrap TikZ block in appropriate LaTeX environment
            wrapped_tikz = f"\\begin{{center}}\n\\scalebox{{0.8}}{{\n{tikz_block}\n}}\n\\end{{center}}"
            combined_content.append(wrapped_tikz)

        # Add regular content items (bulleted lists, etc.)
        for item in regular_content:
            if item.strip() and item.strip().startswith('-'):
                combined_content.append(item.strip())

        # Generate LaTeX code with the combined content
        latex_code, directive = process_media(
            media if media else "\\None",
            combined_content,
            title,
            False  # playable flag
        )
    else:
        # Original processing for non-TikZ content
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

def generate_content_items(content, color=None):
    """Generate formatted content items with optional color, handling TikZ and math separately."""
    if not content:
        return ""

    cnt = 1
    items = []
    pause_set = False
    in_itemize = False
    in_math = False  # NEW: Track math mode
    opened_environments = []

    # Check if any item has \pause
    for itemx in content:
        if isinstance(itemx, str) and itemx.startswith('\\pause'):
            pause_set = True

    for item in content:
        if not item:
            continue

        item_str = str(item).strip()
        if not item_str:
            continue

        # ====== NEW: Check for math expressions FIRST ======
        # Detect standalone math expressions ($...$, $$...$$, \[...\], '[...]')
        is_math_expression = False
        if item_str.startswith('$') and item_str.endswith('$'):
            is_math_expression = True
        elif item_str.startswith('$$') and item_str.endswith('$$'):
            is_math_expression = True
        elif item_str.startswith('\\[') and item_str.endswith('\\]'):
            is_math_expression = True
        elif re.match(r'[\'"]\[.*?[\'"]\]', item_str, re.DOTALL):
            is_math_expression = True

        if is_math_expression:
            # Close any open itemize before adding math
            if in_itemize:
                items.append('\\end{itemize}')
                in_itemize = False
            items.append(item_str)
            continue

        # ====== SECTION 1: Pass-through LaTeX commands and environments ======

        # Handle environment begin/end markers
        if item_str.startswith('\\begin{'):
            # Track opened environments
            opened_environments.append(item_str)
            items.append(item_str)

            # If starting itemize, mark as in itemize
            if 'itemize' in item_str or 'enumerate' in item_str or 'description' in item_str:
                in_itemize = True
            continue

        elif item_str.startswith('\\end{'):
            # Close environment
            if opened_environments:
                opened_environments.pop()
            items.append(item_str)

            # If ending itemize, mark as not in itemize
            if 'itemize' in item_str or 'enumerate' in item_str or 'description' in item_str:
                in_itemize = False
            continue

        # ====== NEW: Handle TikZ content specially ======
        if '\\begin{tikzpicture}' in item_str or '\\end{tikzpicture}' in item_str:
            # Close any open itemize
            if in_itemize:
                items.append('\\end{itemize}')
                in_itemize = False
            items.append(item_str)
            continue

        # ====== NEW: Handle column commands ======
        if item_str.startswith('\\column'):
            if in_itemize:
                items.append('\\end{itemize}')
                in_itemize = False
            items.append(item_str)
            continue

        # ====== NEW: Handle begin/end columns ======
        if '\\begin{columns}' in item_str or '\\end{columns}' in item_str:
            if in_itemize:
                items.append('\\end{itemize}')
                in_itemize = False
            items.append(item_str)
            continue

        # A) Graphics and media commands
        graphics_commands = [
            '\\includegraphics', '\\movie', '\\animategraphics',
            '\\sound', '\\hyperlinksound'
        ]
        if any(cmd in item_str for cmd in graphics_commands):
            if in_itemize:
                items.append('\\end{itemize}')
                in_itemize = False
            items.append(item_str)
            continue

        # B) Text formatting and styling commands
        styling_commands = [
            '\\textbf{', '\\textit{', '\\texttt{', '\\textsf{', '\\textrm{',
            '\\underline{', '\\emph{', '\\textsc{', '\\textsuperscript{',
            '\\textsubscript{', '\\sout{', '\\uline{', '\\uuline{',
            '\\uwave{', '\\textcolor{', '\\color{', '\\colorbox{',
            '\\fcolorbox{', '\\hl{', '\\hlkey{', '\\hlnote{',
            '\\shadowtext{', '\\glowtext{', '\\gradienttext{',
            '\\scalebox{', '\\resizebox{', '\\rotatebox{'
        ]
        if any(item_str.startswith(cmd) for cmd in styling_commands):
            items.append(item_str)
            continue

        # C) Math and symbol commands (preserve these)
        math_commands = [
            '\\(', '\\)', '\\[', '\\]', '\\begin{equation', '\\end{equation',
            '\\begin{align', '\\end{align', '\\begin{gather', '\\end{gather',
            '\\begin{multline', '\\end{multline}', '\\mathbb{', '\\mathcal{',
            '\\mathfrak{', '\\mathscr{', '\\mathbf{', '\\mathit{', '\\mathrm{',
            '\\mathsf{', '\\mathtt{', '\\boldsymbol{', '\\vec{', '\\hat{',
            '\\tilde{', '\\dot{', '\\ddot{', '\\bar{'
        ]
        if any(cmd in item_str for cmd in math_commands):
            items.append(item_str)
            continue

        # D) Cross-referencing commands
        ref_commands = [
            '\\label{', '\\ref{', '\\pageref{', '\\cite{', '\\citep{',
            '\\citet{', '\\citeauthor{', '\\citeyear{', '\\footnote{',
            '\\footnotemark', '\\footnotetext{', '\\marginpar{'
        ]
        if any(item_str.startswith(cmd) for cmd in ref_commands):
            items.append(item_str)
            continue

        # E) Spacing and layout commands
        spacing_commands = [
            '\\vspace{', '\\hspace{', '\\vfill', '\\hfill', '\\vskip',
            '\\hskip', '\\smallskip', '\\medskip', '\\bigskip',
            '\\quad', '\\qquad', '\\,', '\\:', '\\;', '\\!', '\\enspace',
            '\\phantom{', '\\hphantom{', '\\vphantom{'
        ]
        if any(item_str.startswith(cmd) for cmd in spacing_commands):
            items.append(item_str)
            continue

        # F) Box and frame commands
        box_commands = [
            '\\framebox{', '\\fbox{', '\\makebox{', '\\parbox{',
            '\\minipage', '\\raisebox{', '\\savebox{', '\\usebox{',
            '\\sbox{', '\\newsavebox'
        ]
        if any(item_str.startswith(cmd) for cmd in box_commands):
            items.append(item_str)
            continue

        # G) Float environments
        float_envs = [
            '\\begin{figure', '\\end{figure}', '\\begin{table', '\\end{table}',
            '\\begin{wrapfigure', '\\end{wrapfigure}', '\\begin{wraptable',
            '\\end{wraptable}', '\\centering', '\\caption{', '\\captionof{',
            '\\listoffigures', '\\listoftables'
        ]
        if any(item_str.startswith(cmd) for cmd in float_envs):
            items.append(item_str)
            continue

        # H) List and description environments - already handled by begin/end logic
        # Special handling for \item commands
        if item_str.startswith('\\item'):
            # Ensure we're in an itemize environment
            if not in_itemize:
                items.append('\\begin{itemize}')
                opened_environments.append('\\begin{itemize}')
                in_itemize = True

            # Handle pause overlay if needed
            if pause_set and not any(tag in item_str for tag in ['<', '>']):
                items.append(f'\\item<{cnt}> {item_str[5:].strip()}')
                cnt += 1
            else:
                items.append(item_str)
            continue

        # I) Special Beamer/BSG commands
        beamer_commands = [
            '\\begin{alertbox}', '\\end{alertbox}', '\\begin{infobox}',
            '\\end{infobox}', '\\begin{block}', '\\end{block}',
            '\\begin{exampleblock}', '\\end{exampleblock}',
            '\\begin{alertblock}', '\\end{alertblock}', '\\anbg{',
            '\\only<', '\\visible<', '\\invisible<', '\\alt<',
            '\\temporal<', '\\uncover<'
        ]
        if any(item_str.startswith(cmd) for cmd in beamer_commands):
            items.append(item_str)
            continue

        # J) Table/tabular environments
        table_envs = [
            '\\begin{tabular}', '\\end{tabular}', '\\begin{tabularx}',
            '\\end{tabularx}', '\\begin{longtable}', '\\end{longtable}',
            '\\hline', '\\cline{', '\\multicolumn{', '\\multirow{',
            '\\toprule', '\\midrule', '\\bottomrule', '\\addlinespace'
        ]
        if any(item_str.startswith(cmd) for cmd in table_envs):
            if in_itemize:
                items.append('\\end{itemize}')
                in_itemize = False
            items.append(item_str)
            continue

        # K) Miscellaneous LaTeX commands
        misc_commands = [
            '\\url{', '\\href{', '\\usepackage', '\\documentclass',
            '\\newcommand{', '\\renewcommand{', '\\providecommand{',
            '\\def', '\\let', '\\usepackage', '\\RequirePackage',
            '\\input{', '\\include{', '\\includeonly{', '\\bibliography{',
            '\\bibliographystyle{', '\\printbibliography', '\\nocite{',
            '\\index{', '\\glossary{', '\\addcontentsline',
            '\\addtocontents', '\\tableofcontents', '\\listoffigures',
            '\\listoftables', '\\appendix', '\\part{', '\\chapter{',
            '\\section{', '\\subsection{', '\\subsubsection{',
            '\\paragraph{', '\\subparagraph{', '\\pagebreak',
            '\\newpage', '\\clearpage', '\\cleardoublepage'
        ]
        if any(item_str.startswith(cmd) for cmd in misc_commands):
            items.append(item_str)
            continue

        # ====== SECTION 2: Handle regular text content ======
        # Handle pause directives
        if item_str.startswith('\\pause'):
            cnt += 1
            items.append(item_str)
            continue

        # Process regular text content (bullet points)
        if item_str.startswith('-') or item_str.startswith('•'):
            bullet_content = re.sub(r'^[-•]\s*', '', item_str)
            processed_item = process_latex_content(bullet_content)
            processed_item = sanitize_latex_content(processed_item)

            if color:
                processed_item = f"{{\\color{{{color}}}{processed_item}}}"

            # Ensure we're in an itemize environment
            if not in_itemize:
                items.append('\\begin{itemize}')
                opened_environments.append('\\begin{itemize}')
                in_itemize = True

            # Add pause overlay if needed
            if pause_set:
                items.append(f'\\item<{cnt}> {processed_item}')
                cnt += 1
            else:
                items.append(f'\\item {processed_item}')
            continue

        # Regular non-bullet text
        if item_str and item_str.strip():
            # Close any open itemize first
            if in_itemize:
                items.append('\\end{itemize}')
                in_itemize = False

            processed_item = process_latex_content(item_str)
            processed_item = sanitize_latex_content(processed_item)

            if color:
                processed_item = f"{{\\color{{{color}}}{processed_item}}}"

            items.append(processed_item)

    # CRITICAL FIX: Close any opened itemize environments
    while in_itemize:
        items.append('\\end{itemize}')
        in_itemize = False
        # Remove from opened environments if present
        for i in range(len(opened_environments)-1, -1, -1):
            if 'itemize' in opened_environments[i]:
                opened_environments.pop(i)
                break

    return '\n        '.join(items)

def clean_frame_title(title):
    """Clean frame titles to prevent brace issues"""
    if not title:
        return ""
    # Remove excessive braces and escape special characters
    title = title.replace('{{{', '{').replace('}}}', '}')
    title = title.replace('{{', '{').replace('}}', '}')
    return title

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

        # Process footnotes and anbg commands
        processed_content = []
        footnotes = []
        i = 0
        while i < len(content):
            item = content[i]
            if isinstance(item, str) and '\\anbg' in item:
                match = re.search(r'\\anbg\{(.*?)\}', item)
                if match:
                    image_name = match.group(1)
                    if image_name:
                        processed_content.append(f"\\anbg{{{image_name}}}")
                    else:
                        processed_content.append("\\anbg{}")
                i += 1
                continue
            elif isinstance(item, str) and '\\footnote{' in item:
                footnote_start = item.index('\\footnote{') + len('\\footnote{')
                footnote_end = item.rindex('}')
                footnote_text = item[footnote_start:footnote_end]
                footnotes.append(footnote_text)
                cleaned_item = item[:item.index('\\footnote{')] + item[item.rindex('}')+1:]
                processed_content.append(cleaned_item)
                i += 1
            else:
                processed_content.append(item)
                i += 1

        # Add footnotes to last item
        if processed_content and footnotes:
            last_item = processed_content[-1]
            for j, footnote in enumerate(footnotes):
                last_item = f"{last_item}\\footnote{{{footnote}}}"
            processed_content[-1] = last_item
        elif footnotes:
            combined_footnotes = ''.join([f"\\footnote{{{f}}}" for f in footnotes])
            processed_content.append(f"\\phantom{{.}}{combined_footnotes}")

        # Handle explicit \None directive
        if url.strip() == "\\None":
            return generate_latex_code(None, "\\None", None, processed_content, title, False), "\\None"

        # Helper function to download video from URL
        def download_video_from_url(video_url, output_folder='media_files'):
            """Download video from URL to local file"""
            try:
                import requests
                import time

                os.makedirs(output_folder, exist_ok=True)

                # Generate safe filename
                timestamp = int(time.time())
                # Try to get filename from URL
                url_filename = os.path.basename(video_url.split('?')[0])
                if url_filename and '.' in url_filename and len(url_filename) < 50:
                    # Remove any query parameters
                    url_filename = url_filename.split('?')[0]
                    if url_filename.lower().endswith(('.mp4', '.webm', '.mov', '.avi', '.mkv')):
                        filename = url_filename
                    else:
                        filename = f"video_{timestamp}.mp4"
                else:
                    filename = f"video_{timestamp}.mp4"

                output_path = os.path.join(output_folder, filename)

                # Download with progress
                response = requests.get(video_url, stream=True, timeout=30)
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            if terminal_io:
                                terminal_io.write(f"  Downloading: {percent:.1f}%\r", "cyan")
                            else:
                                print(f"  Downloading: {percent:.1f}%\r", end='')

                if terminal_io:
                    terminal_io.write(f"\n  ✓ Downloaded: {filename}\n", "green")
                else:
                    print(f"\n  ✓ Downloaded: {filename}")
                return output_path

            except Exception as e:
                if terminal_io:
                    terminal_io.write(f"  ✗ Download error: {str(e)}\n", "red")
                else:
                    print(f"  ✗ Download error: {e}")
                return None

        # Helper function to add source attribution
        def add_source_attribution(media_source, local_path):
            """Add source attribution message and metadata"""
            if terminal_io:
                terminal_io.write(f"\n📝 Source Attribution:\n", "yellow")
                terminal_io.write(f"   Original URL: {media_source}\n", "white")
                terminal_io.write(f"   Saved to: {local_path}\n", "white")
                terminal_io.write(f"   This video is saved locally for offline presentation\n", "white")
                terminal_io.write(f"   Please credit the original source when presenting\n\n", "yellow")

            # Save metadata file
            metadata_path = local_path.rsplit('.', 1)[0] + '_source.txt'
            with open(metadata_path, 'w', encoding='utf-8') as f:
                f.write(f"Source URL: {media_source}\n")
                f.write(f"Downloaded: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Local Path: {local_path}\n")
                f.write("Please credit the original content creator when using this media.\n")

        # ========== HANDLE PLAYABLE MEDIA ==========
        if playable:
            # Case 1: Playable local file
            if directive_type == 'file' and media_source:
                media_path = media_source
                if not os.path.exists(media_path):
                    test_paths = [
                        media_path,
                        os.path.join('media_files', os.path.basename(media_path)),
                        os.path.join('media_files', media_path),
                    ]
                    for test_path in test_paths:
                        if os.path.exists(test_path):
                            media_path = test_path
                            break

                if os.path.exists(media_path):
                    first_frame_path = generate_preview_frame(media_path)
                    return generate_latex_code(
                        os.path.splitext(os.path.basename(media_path))[0],
                        media_path,
                        first_frame_path,
                        processed_content,
                        title,
                        True
                    ), original_directive

            # Case 2: Playable URL (YouTube or other)
            elif directive_type == 'url' and media_source:
                if media_source.startswith(('http://', 'https://')):
                    downloaded_file = None

                    # Handle YouTube videos with yt-dlp - DOWNLOAD LOCALLY
                    if 'youtube.com' in media_source or 'youtu.be' in media_source:
                        try:
                            import yt_dlp
                            os.makedirs('media_files', exist_ok=True)

                            # Generate safe filename from video title
                            timestamp = int(time.time())
                            video_title = "youtube_video"

                            # First get video info to get title
                            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                                try:
                                    info = ydl.extract_info(media_source, download=False)
                                    video_title = info.get('title', 'youtube_video')
                                    safe_title = sanitize_filename(video_title)
                                    output_template = f"media_files/{safe_title}.mp4"
                                except Exception as e:
                                    if terminal_io:
                                        terminal_io.write(f"  ⚠ Could not get video title: {str(e)}\n", "yellow")
                                    output_template = f"media_files/youtube_video_{timestamp}.mp4"

                            ydl_opts = {
                                'format': 'best[ext=mp4]/best',
                                'outtmpl': output_template,
                                'quiet': False,
                                'no_warnings': False,
                            }

                            if terminal_io:
                                terminal_io.write(f"\n  📥 Downloading YouTube video locally...\n", "cyan")
                                terminal_io.write(f"  📹 Title: {video_title}\n", "white")
                                terminal_io.write(f"  ⏳ This may take a few moments...\n", "yellow")
                            else:
                                print(f"\n  📥 Downloading YouTube video locally...")

                            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                ydl.download([media_source])

                            # Check for downloaded file
                            if os.path.exists(output_template):
                                downloaded_file = output_template
                                if terminal_io:
                                    terminal_io.write(f"\n  ✓ Video downloaded successfully!\n", "green")
                                    terminal_io.write(f"  📁 Saved to: {downloaded_file}\n", "green")
                                    terminal_io.write(f"  💡 This video is now available offline\n", "cyan")
                                else:
                                    print(f"\n  ✓ Video downloaded successfully!")
                                    print(f"  📁 Saved to: {downloaded_file}")
                            else:
                                # Try to find any mp4 file with similar name
                                import glob
                                search_pattern = f"media_files/*{safe_title}*.mp4" if 'safe_title' in dir() else f"media_files/*youtube_video_{timestamp}*.mp4"
                                possible_files = glob.glob(search_pattern)
                                if possible_files:
                                    downloaded_file = possible_files[0]
                                    if terminal_io:
                                        terminal_io.write(f"\n  ✓ Video downloaded: {os.path.basename(downloaded_file)}\n", "green")
                                else:
                                    raise Exception("Downloaded file not found")

                            if downloaded_file and os.path.exists(downloaded_file):
                                # Add source attribution
                                add_source_attribution(media_source, downloaded_file)

                                first_frame_path = generate_preview_frame(downloaded_file)
                                base_name = os.path.splitext(os.path.basename(downloaded_file))[0]

                                return generate_latex_code(
                                    base_name,
                                    downloaded_file,
                                    first_frame_path,
                                    processed_content,
                                    title,
                                    True,
                                    media_source
                                ), f"\\play \\file {downloaded_file}"
                            else:
                                raise Exception("Could not locate downloaded file")

                        except ImportError:
                            error_msg = ("  ✗ yt-dlp not installed. Please run: pip install yt-dlp\n"
                                        "  ℹ Without yt-dlp, YouTube videos will use online links only.\n"
                                        "  💡 For offline playback, install yt-dlp: pip install yt-dlp")
                            if terminal_io:
                                terminal_io.write(error_msg + "\n", "red")
                            else:
                                print(error_msg)
                            # Fall back to URL link
                            return handle_missing_media(url, processed_content, title, playable)

                        except Exception as e:
                            error_msg = f"  ✗ YouTube download failed: {str(e)}"
                            if terminal_io:
                                terminal_io.write(error_msg + "\n", "red")
                                terminal_io.write("  ℹ Check your internet connection and try again\n", "yellow")
                            else:
                                print(error_msg)
                            return handle_missing_media(url, processed_content, title, playable)

                    # Handle other URLs with direct download
                    else:
                        if terminal_io:
                            terminal_io.write(f"\n  📥 Downloading video from URL...\n", "cyan")
                        downloaded_file = download_video_from_url(media_source)

                    if downloaded_file and os.path.exists(downloaded_file):
                        # Add source attribution for non-YouTube URLs too
                        add_source_attribution(media_source, downloaded_file)

                        first_frame_path = generate_preview_frame(downloaded_file)
                        base_name = os.path.splitext(os.path.basename(downloaded_file))[0]

                        if terminal_io:
                            terminal_io.write(f"  ✓ Media downloaded successfully!\n", "green")
                            terminal_io.write(f"  📁 Saved to: {downloaded_file}\n", "green")

                        return generate_latex_code(
                            base_name,
                            downloaded_file,
                            first_frame_path,
                            processed_content,
                            title,
                            True,
                            media_source
                        ), f"\\play \\file {downloaded_file}"
                    else:
                        if terminal_io:
                            terminal_io.write(f"  ✗ Failed to download video from URL\n", "red")
                            terminal_io.write(f"  ℹ Falling back to URL link\n", "yellow")
                        return handle_missing_media(url, processed_content, title, playable)

        # ========== HANDLE NON-PLAYABLE (STATIC) MEDIA ==========
        # Case 3: Regular URL (non-playable, e.g., image URL)
        if directive_type == 'url' and media_source:
            if media_source.startswith(('http://', 'https://')):
                if terminal_io:
                    terminal_io.write(f"\n  📥 Downloading image from URL...\n", "cyan")
                base_name, filename, first_frame_path = download_media(media_source)
                if base_name and filename:
                    if terminal_io:
                        terminal_io.write(f"  ✓ Image downloaded: {filename}\n", "green")
                        terminal_io.write(f"  📁 Saved to: media_files/{filename}\n", "green")
                    return generate_latex_code(
                        base_name,
                        f"media_files/{filename}",
                        first_frame_path,
                        processed_content,
                        title,
                        False,
                        media_source
                    ), f"\\file media_files/{filename}"
                else:
                    if terminal_io:
                        terminal_io.write(f"  ✗ Failed to download image\n", "red")
                    return handle_missing_media(url, processed_content, title, playable)

        # Case 4: Local file (non-playable)
        if directive_type == 'file' and media_source:
            media_path = media_source
            found = False

            # Try multiple paths
            test_paths = [
                media_path,
                os.path.join('media_files', os.path.basename(media_path)),
                os.path.join('media_files', media_path),
                media_path.replace('\\', '/'),
                os.path.join('media_files', media_path.replace('media_files/', ''))
            ]

            # Also try with common extensions if no extension
            if '.' not in media_path:
                extensions = ['.png', '.jpg', '.jpeg', '.pdf', '.mp4', '.gif']
                for ext in extensions:
                    for test_path in test_paths[:]:
                        test_paths.append(test_path + ext)

            for test_path in test_paths:
                if os.path.exists(test_path):
                    media_path = test_path
                    found = True
                    break

            if found:
                if terminal_io:
                    terminal_io.write(f"  ✓ Found local file: {os.path.basename(media_path)}\n", "green")
                return generate_latex_code(
                    os.path.splitext(os.path.basename(media_path))[0],
                    media_path,
                    media_path,  # For images, the file itself is the preview
                    processed_content,
                    title,
                    False
                ), original_directive
            else:
                if terminal_io:
                    terminal_io.write(f"  ⚠ Local file not found: {media_source}\n", "yellow")
                    terminal_io.write(f"  ℹ Creating slide without media\n", "cyan")
                return handle_missing_media(url, processed_content, title, playable)

        # ========== HANDLE LAYOUT DIRECTIVES ==========
        layout_directives = ['watermark', 'fullframe', 'pip', 'split', 'highlight',
                            'background', 'topbottom', 'overlay', 'corner', 'mosaic']

        if directive_type in layout_directives:
            return generate_latex_code(
                base_name=None,
                filename=media_source if media_source else "\\None",
                first_frame_path=None,
                content=processed_content,
                title=title,
                playable=False,
                source_url=None,
                layout=directive_type
            ), original_directive

        # ========== FALLBACK ==========
        if callback and slide_index is not None:
            callback(slide_index)
        return handle_missing_media(url, processed_content, title, playable)

    except Exception as e:
        error_msg = f"Error processing media: {str(e)}"
        if terminal_io:
            terminal_io.write(f"{error_msg}\n", "red")
        else:
            print(error_msg)
        import traceback
        traceback.print_exc()
        return handle_missing_media(url, content, title, playable)

def download_video_from_url(url, output_folder='media_files'):
    """Download video from any URL to local file"""
    try:
        import requests

        os.makedirs(output_folder, exist_ok=True)

        # Generate safe filename
        timestamp = int(time.time())
        filename = f"video_{timestamp}.mp4"

        # Try to get filename from URL if possible
        url_filename = os.path.basename(url.split('?')[0])
        if url_filename and '.' in url_filename and len(url_filename) < 50:
            filename = url_filename

        output_path = os.path.join(output_folder, filename)

        # Download with progress
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    if hasattr(self, 'write'):
                        self.write(f"  Downloading: {percent:.1f}%\r", "cyan")

        if hasattr(self, 'write'):
            self.write(f"\n", "cyan")

        return output_path

    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

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

        # Initialize variables
        directive_type = 'url'
        media_source = ''

        # Process sequentially through parts
        i = 0
        while i < len(parts):
            part = parts[i]

            if part == '\\play':
                playable = True
                i += 1
                # Look at the next part after \play
                if i < len(parts):
                    next_part = parts[i]
                    if next_part == '\\file':
                        directive_type = 'file'
                        i += 1
                        # Collect all remaining parts as the file path
                        if i < len(parts):
                            media_source = ' '.join(parts[i:])
                        break
                    elif next_part == '\\url':
                        directive_type = 'url'
                        i += 1
                        if i < len(parts):
                            media_source = ' '.join(parts[i:])
                        break
                    else:
                        # Just a URL or path after \play (no \file or \url)
                        directive_type = 'url'
                        media_source = ' '.join(parts[i:])
                        break
                break

            elif part == '\\file':
                directive_type = 'file'
                i += 1
                if i < len(parts):
                    media_source = ' '.join(parts[i:])
                break

            elif part == '\\url':
                directive_type = 'url'
                i += 1
                if i < len(parts):
                    media_source = ' '.join(parts[i:])
                break

            elif part == '\\None':
                return 'none', None, False, original_directive

            elif part.startswith('\\') and part in directives:
                # Layout directive without \play prefix
                return directives[part], ' '.join(parts[i+1:]), False, original_directive

            else:
                # No directive found - treat as plain URL or path
                if not media_source:
                    media_source = part
                else:
                    media_source += ' ' + part
                i += 1

        # Clean up media source
        if media_source:
            # Remove quotes if present
            media_source = media_source.strip().strip('"').strip("'")

            # Remove any leading backslashes or commands
            if media_source.startswith('\\'):
                parts = media_source.split(maxsplit=1)
                if len(parts) > 1:
                    media_source = parts[1]

        # CRITICAL FIX: Detect YouTube URLs and mark as playable AND url
        if directive_type == 'url' and media_source:
            media_source_lower = media_source.lower()
            # Always treat YouTube URLs as playable
            if any(domain in media_source_lower for domain in ['youtube.com', 'youtu.be']):
                playable = True
                print(f"  ℹ Detected YouTube URL: {media_source}")
                print(f"  📥 Will download video locally for offline use")

        # Handle local file paths
        if directive_type == 'file' and media_source:
            # Check if it's a video file by extension
            video_extensions = ('.mp4', '.avi', '.mov', '.webm', '.mkv', '.flv', '.wmv')
            if media_source.lower().endswith(video_extensions):
                playable = True

            # Ensure proper path format
            media_source = media_source.replace('\\', '/')

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
def sanitize_latex_content(content_line):
    """Sanitize LaTeX content to prevent compilation errors while preserving math."""
    if not content_line:
        return ""

    # If this is a math expression, preserve it completely without modification
    # Check for various math patterns
    is_math = False

    # Inline math
    if content_line.startswith('$') and content_line.endswith('$'):
        is_math = True
    # Display math
    elif content_line.startswith('$$') and content_line.endswith('$$'):
        is_math = True
    elif content_line.startswith('\\[') and content_line.endswith('\\]'):
        is_math = True
    # Quote-bracket math
    elif re.match(r'[\'"]\[.*?[\'"]\]', content_line, re.DOTALL):
        is_math = True
    # Math environments
    elif '\\begin{align' in content_line or '\\begin{equation}' in content_line:
        is_math = True

    # If it's math, return as-is (preserve everything)
    if is_math:
        return content_line

    # For non-math content, only fix brace issues
    content_line = content_line.strip()

    # Fix unbalanced braces (but preserve math mode)
    # Don't modify braces inside math mode
    in_math = False
    open_braces = 0
    close_braces = 0

    i = 0
    while i < len(content_line):
        char = content_line[i]

        # Track math mode
        if char == '$' and (i == 0 or content_line[i-1] != '\\'):
            in_math = not in_math
            i += 1
            continue
        elif char == '\\' and i + 1 < len(content_line) and content_line[i+1] == '[':
            in_math = True
            i += 2
            continue
        elif char == '\\' and i + 1 < len(content_line) and content_line[i+1] == ']':
            in_math = False
            i += 2
            continue

        if not in_math:
            if char == '{':
                open_braces += 1
            elif char == '}':
                close_braces += 1
        i += 1

    if open_braces != close_braces:
        if open_braces > close_braces:
            content_line += '}' * (open_braces - close_braces)
        elif close_braces > open_braces:
            content_line = '{' * (close_braces - open_braces) + content_line

    # Fix excessive brace nesting (but not in math)
    if '$' not in content_line:
        content_line = content_line.replace('{{{', '{').replace('}}}', '}')
        content_line = content_line.replace('{{', '{').replace('}}', '}')

    # Only escape special characters outside math mode
    if '$' not in content_line and '\\[' not in content_line:
        special_chars = ['#', '%', '&', '_']
        for char in special_chars:
            if char in content_line and f'\\{char}' not in content_line:
                content_line = content_line.replace(char, f'\\{char}')

    return content_line

import re  # Add this at the top of BeamerSlideGenerator.py if not already there

def process_input_file(file_path, output_filename='movie.tex', presentation_info=None, ide_callback=None):
    r"""
    Comprehensive input file processor for BeamerSlideGenerator.
    Handles ALL features: mosaic, YouTube, layouts, media, TikZ, effects, etc.
    """
    import re
    from collections import deque

    processed = 0
    failed = 0
    errors = []
    warnings = []

    try:
        # ========== READ INPUT FILE ==========
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        if not lines:
            errors.append("Input file is empty")
            return 0, 1, errors

        file_content = ''.join(lines)

        # ========== DETECT FILE FORMAT ==========
        has_document_begin = '\\begin{document}' in file_content
        has_document_end = '\\end{document}' in file_content
        has_native_titles = bool(re.search(r'^\\title\s+[^{]', file_content, re.MULTILINE))
        has_latex_frames = '\\begin{frame}' in file_content
        has_content_blocks = '\\begin{Content}' in file_content
        has_notes_blocks = '\\begin{Notes}' in file_content

        file_type = 'native'
        if has_latex_frames and has_document_begin:
            file_type = 'latex'
        elif has_native_titles and has_content_blocks:
            file_type = 'native'
        elif has_document_begin and (has_native_titles or has_content_blocks):
            file_type = 'hybrid'
        elif has_latex_frames and not has_document_begin:
            file_type = 'latex_standalone'

        print(f"File type detected: {file_type}")
        print(f"has_document_begin: {has_document_begin}")
        print(f"has_native_titles: {has_native_titles}")
        print(f"has_latex_frames: {has_latex_frames}")
        print(f"has_content_blocks: {has_content_blocks}")

        # ========== EXTRACT PREAMBLE AND CONTENT ==========
        preamble_lines = []
        content_lines = []
        preamble_found = False

        # Find ALL \begin{document} positions
        doc_positions = [i for i, line in enumerate(lines) if '\\begin{document}' in line]
        if doc_positions:
            doc_pos = doc_positions[-1]
            preamble_lines = lines[:doc_pos + 1]
            content_lines = lines[doc_pos + 1:]
            preamble_found = True

            # ============================================================
            # CRITICAL FIX: Remove \end{document} from content
            # ============================================================
            # Find \end{document} position and strip it from content
            end_doc_positions = [i for i, line in enumerate(content_lines) if '\\end{document}' in line]
            if end_doc_positions:
                # Remove everything from \end{document} onwards
                end_doc_pos = end_doc_positions[0]
                content_lines = content_lines[:end_doc_pos]
                has_document_end = True
            else:
                has_document_end = False


                # Remove any leading empty lines from content
                while content_lines and not content_lines[0].strip():
                    content_lines.pop(0)
        else:
            content_lines = lines
            preamble_lines = []
            preamble_found = False

        # If no preamble found, generate one
        if not preamble_found and presentation_info:
            from BeamerSlideGenerator import get_beamer_preamble
            preamble_text = get_beamer_preamble(
                title=presentation_info.get('title', 'Presentation'),
                subtitle=presentation_info.get('subtitle', ''),
                author=presentation_info.get('author', 'Author'),
                institution=presentation_info.get('institution', ''),
                short_institute=presentation_info.get('short_institute', ''),
                date=presentation_info.get('date', r'\today')
            )
            preamble_lines = preamble_text.split('\n')
            warnings.append("Generated default preamble (no preamble found in file)")

        # ========== DEBUG: Print first 20 content lines ==========
        print("\nFirst 20 content lines:")
        for i, line in enumerate(content_lines[:20]):
            print(f"  {i}: {line.rstrip()}")

        # ========== PARSE SLIDES ==========
        slides = []

        # Try different parsers
        print("\nTrying native parser...")
        native_slides = parse_native_slides_full(content_lines, warnings)
        if native_slides:
            slides = native_slides
            print(f"✓ Native parser found {len(slides)} slides")
        else:
            print("✗ Native parser found no slides")

            print("\nTrying hybrid parser...")
            hybrid_slides = parse_hybrid_slides(content_lines, warnings)
            if hybrid_slides:
                slides = hybrid_slides
                print(f"✓ Hybrid parser found {len(slides)} slides")
            else:
                print("✗ Hybrid parser found no slides")

                print("\nTrying LaTeX parser...")
                latex_slides = parse_latex_slides_full(content_lines, warnings)
                if latex_slides:
                    slides = latex_slides
                    print(f"✓ LaTeX parser found {len(slides)} slides")
                else:
                    print("✗ LaTeX parser found no slides")

        if not slides:
            errors.append("No slides were found in the input file")
            return 0, 1, errors

        # ========== WRITE OUTPUT ==========
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            # Write preamble
            if preamble_lines:
                for line in preamble_lines:
                    if line.strip() or line == '\n':
                        outfile.write(line if line.endswith('\n') else line + '\n')
                outfile.write('\n')

                outfile.write("% ====== CRITICAL FIXES ======\n")
                outfile.write("\\overfullrule=0pt\n")
                outfile.write("\\sloppy\n")
                outfile.write("\\tolerance=9999\n")
                outfile.write("\\emergencystretch=3em\n")
                outfile.write("\\hfuzz=2pt\n")
                outfile.write("\\raggedright\n")
                outfile.write("% ===========================\n\n")

            # Write document begin if not already in preamble
            if not has_document_begin:
                outfile.write("\\begin{document}\n")

            # Write maketitle if needed
            if '\\maketitle' not in file_content and '\\titlepage' not in file_content:
                outfile.write("\\maketitle\n\n")

            # Process each slide
            # In process_input_file, before processing content:
            for slide in slides:
                # Protect TikZ content before any processing
                if slide.get('content'):
                    protected_content = []
                    for line in slide['content']:
                        protected_content.append(protect_tikz_content(line))
                    slide['content'] = protected_content

                processed_slide = process_slide_with_features(slide, outfile, warnings)
                if processed_slide:
                    outfile.write(processed_slide)
                    outfile.write('\n')
                    processed += 1
                else:
                    failed += 1

            # After processing all slides, add \end{document} if not present
            if not has_document_end:
                outfile.write("\n\\end{document}\n")
            else:
                # If it was present in the original, make sure it's at the end
                outfile.write("\n\\end{document}\n")

        print(f"\nProcessed {processed} slides, {failed} failed")

        if processed == 0:
            errors.append("No slides were processed")
            return 0, 1, errors

        return processed, failed, errors

    except Exception as e:
        error_msg = f"Error processing file: {str(e)}"
        errors.append(error_msg)
        import traceback
        traceback.print_exc()
        return processed, failed, errors

def _fix_table_formatting(self, table_lines: list) -> list:
    """
    Fix table formatting issues including:
    - Missing @{} syntax
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

            # ============================================================
            # FIX: Correct malformed @{} syntax
            # ============================================================
            # Pattern: @ followed by space and then l/r/c without {}
            import re
            # Fix: @ l -> @{}l, @ r -> @{}r, @ c -> @{}c
            line_stripped = re.sub(r'@\s+([lrc])', r'@{\1}', line_stripped)
            # Fix: l @ -> l@{} (this is less common but possible)
            line_stripped = re.sub(r'([lrc])\s+@', r'\1@{}', line_stripped)
            # Fix: @{ l -> @{}l (if there's a space after @{)
            line_stripped = re.sub(r'@\{\s+([lrc])', r'@{\1}', line_stripped)
            # Fix: l @} -> l@{} (if there's a space before @})
            line_stripped = re.sub(r'([lrc])\s+@\}', r'\1@{}', line_stripped)

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
                if line_stripped.count('&') > 0:
                    pass
                else:
                    line_stripped = line_stripped.rstrip('\\')

            # Add missing initial \hline if needed
            if not hline_added and (line_stripped.startswith('\\textbf') or
                                     (line_stripped and line_stripped[0].isalpha())):
                fixed_lines.append('\\hline')
                hline_added = True

            fixed_lines.append(line_stripped)
        else:
            fixed_lines.append(line_stripped)

    return fixed_lines


def parse_hybrid_slides(lines, warnings):
    """
    Parse hybrid format slides - \title without \begin{Content}
    This handles cases where the content is directly after \title
    """
    import re

    print(f"  Hybrid parser: processing {len(lines)} lines")

    slides = []
    current_slide = None
    content_buffer = []
    notes_buffer = []
    media = ""
    found_media = False
    in_notes = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Detect title
        title_match = re.match(r'^%?\s*\\title\s+(.+)$', line)
        if title_match:
            print(f"  Hybrid parser: Found title: {title_match.group(1).strip()[:50]}...")

            # Save previous slide
            if current_slide:
                current_slide['content'] = content_buffer.copy()
                current_slide['notes'] = notes_buffer.copy()
                slides.append(current_slide)

            # Start new slide
            title = title_match.group(1).strip()
            title = clean_title(title)

            current_slide = {
                'title': title,
                'content': [],
                'notes': [],
                'media': '',
                'layout': None,
                'layout_params': None,
                'playable': False,
                'source_url': None
            }
            content_buffer = []
            notes_buffer = []
            media = ""
            found_media = False
            in_notes = False
            i += 1
            continue

        # If we're not in a slide, skip
        if current_slide is None:
            i += 1
            continue

        # Check for Content block - if found, switch to native parser
        if '\\begin{Content}' in stripped:
            print(f"  Hybrid parser: Found \\begin{{Content}}, switching to native parser")
            return parse_native_slides_full(lines, warnings)

        # Check for Notes block
        if '\\begin{Notes}' in stripped:
            in_notes = True
            i += 1
            continue
        if '\\end{Notes}' in stripped:
            in_notes = False
            i += 1
            continue

        # Check for end of slide (next title or end of file)
        # If we see another \title, this slide ends
        if re.match(r'^%?\s*\\title\s+', line):
            # The next iteration will handle this as a new slide
            # But we need to save the current slide first
            if current_slide:
                current_slide['content'] = content_buffer.copy()
                current_slide['notes'] = notes_buffer.copy()
                slides.append(current_slide)
            current_slide = None
            content_buffer = []
            notes_buffer = []
            i += 1
            continue

        # Process content
        if not in_notes:
            # Check for media directive
            if not found_media and stripped and stripped.startswith(('\\file', '\\play')):
                media = stripped
                found_media = True
                current_slide['media'] = media
                i += 1
                continue

            if stripped and not stripped.startswith('%') and not stripped.startswith('\\end{Content}'):
                # Fix braces and add to content
                clean_line = fix_braces(stripped)
                if clean_line and clean_line not in ['\\None', 'None']:
                    content_buffer.append(clean_line)

        # Process notes
        if in_notes:
            if stripped and not stripped.startswith('%'):
                clean_note = fix_braces(stripped)
                if clean_note:
                    notes_buffer.append(clean_note)
            elif stripped.startswith('%'):
                notes_buffer.append(stripped)

        i += 1

    # Save last slide
    if current_slide:
        current_slide['content'] = content_buffer.copy()
        current_slide['notes'] = notes_buffer.copy()
        current_slide['media'] = media
        slides.append(current_slide)

    print(f"  Hybrid parser: found {len(slides)} slides")
    return slides


def parse_hybrid_slides(lines, warnings):
    """
    Parse hybrid format slides - \title without \begin{Content}
    This handles cases where the content is directly after \title
    """
    import re

    slides = []
    current_slide = None
    content_buffer = []
    notes_buffer = []
    media = ""
    found_media = False
    in_notes = False

    # First, find all \title lines and their content
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Detect title
        title_match = re.match(r'^%?\s*\\title\s+(.+)$', line)
        if title_match:
            # Save previous slide
            if current_slide:
                current_slide['content'] = content_buffer.copy()
                current_slide['notes'] = notes_buffer.copy()
                slides.append(current_slide)

            # Start new slide
            title = title_match.group(1).strip()
            title = clean_title(title)

            current_slide = {
                'title': title,
                'content': [],
                'notes': [],
                'media': '',
                'layout': None,
                'layout_params': None,
                'playable': False,
                'source_url': None
            }
            content_buffer = []
            notes_buffer = []
            media = ""
            found_media = False
            in_notes = False
            i += 1
            continue

        # Check for Content block
        if '\\begin{Content}' in stripped:
            # This will be handled by the native parser
            return parse_native_slides_full(lines, warnings)

        # Check for Notes block
        if '\\begin{Notes}' in stripped:
            in_notes = True
            i += 1
            continue
        if '\\end{Notes}' in stripped:
            in_notes = False
            i += 1
            continue

        # If we're in a slide and this is content
        if current_slide is not None and not in_notes:
            # Check for media directive
            if not found_media and stripped and stripped.startswith(('\\file', '\\play')):
                media = stripped
                found_media = True
                current_slide['media'] = media
                i += 1
                continue

            if stripped and not stripped.startswith('%') and not stripped.startswith('\\end{Content}'):
                # Fix braces and add to content
                clean_line = fix_braces(stripped)
                if clean_line:
                    content_buffer.append(clean_line)

        # Process notes
        if in_notes and current_slide is not None:
            if stripped and not stripped.startswith('%'):
                clean_note = fix_braces(stripped)
                if clean_note:
                    notes_buffer.append(clean_note)
            elif stripped.startswith('%'):
                notes_buffer.append(stripped)

        i += 1

    # Save last slide
    if current_slide:
        current_slide['content'] = content_buffer.copy()
        current_slide['notes'] = notes_buffer.copy()
        current_slide['media'] = media
        slides.append(current_slide)

    return slides


def parse_native_slides_full(lines, warnings):
    """Parse native format slides with ALL features supported"""
    import re

    slides = []
    current_slide = None
    in_content = False
    in_notes = False
    content_buffer = []
    notes_buffer = []
    media = ""
    found_media = False
    pending_font_cmd = None
    itemize_stack = []
    in_tabular = False  # Track tabular environment

    for line in lines:
        stripped = line.strip()

        # Detect title
        title_match = re.match(r'^%?\s*\\title\s+(.+)$', line)
        if title_match:
            if current_slide:
                current_slide['content'] = content_buffer.copy()
                current_slide['notes'] = notes_buffer.copy()
                slides.append(current_slide)

            title = title_match.group(1).strip()
            title = clean_title(title)

            current_slide = {
                'title': title,
                'content': [],
                'notes': [],
                'media': '',
                'layout': None,
                'layout_params': None,
                'playable': False,
                'source_url': None
            }
            content_buffer = []
            notes_buffer = []
            media = ""
            found_media = False
            in_content = False
            in_notes = False
            pending_font_cmd = None
            itemize_stack = []
            in_tabular = False
            continue

        if current_slide is None:
            continue

        # Detect Content block
        if re.match(r'^%?\s*\\begin{Content}\s*$', stripped):
            in_content = True
            in_notes = False
            found_media = False
            in_tabular = False
            continue
        elif re.match(r'^%?\s*\\end{Content}\s*$', stripped):
            in_content = False
            # Close any open itemize environments
            while itemize_stack:
                content_buffer.append("\\end{itemize}")
                itemize_stack.pop()
            continue

        # Detect Notes block
        if re.match(r'^%?\s*\\begin{Notes}\s*$', stripped):
            in_notes = True
            in_content = False
            continue
        elif re.match(r'^%?\s*\\end{Notes}\s*$', stripped):
            in_notes = False
            continue

        # Process content
        if in_content:
            if not stripped or stripped.startswith('%'):
                if stripped:
                    content_buffer.append(stripped)
                continue

            # ============================================================
            # CRITICAL: Track tabular environment to prevent bullet conversion inside tables
            # ============================================================
            if '\\begin{tabular}' in stripped or '\\begin{array}' in stripped:
                in_tabular = True
                # Close any open itemize before tabular
                while itemize_stack:
                    content_buffer.append("\\end{itemize}")
                    itemize_stack.pop()
                content_buffer.append(stripped)
                continue

            if '\\end{tabular}' in stripped or '\\end{array}' in stripped:
                in_tabular = False
                # Close any open itemize before ending tabular
                while itemize_stack:
                    content_buffer.append("\\end{itemize}")
                    itemize_stack.pop()
                content_buffer.append(stripped)
                continue

            # ========== CHECK FOR LAYOUT DIRECTIVES ==========
            layout_match = re.match(r'\\(ff|wm|pip|split|hl|bg|tb|ol|corner|mosaic)\s*\{([^}]*)\}', stripped)
            if layout_match:
                layout_type = layout_match.group(1)
                layout_params = layout_match.group(2)
                current_slide['layout'] = layout_type
                current_slide['layout_params'] = layout_params
                # Don't add to content - it's handled separately
                continue

            # ========== CHECK FOR MEDIA DIRECTIVES ==========
            if not found_media:
                # Check for play directive with URL or file
                play_match = re.match(r'\\play\s+(.+)$', stripped)
                if play_match:
                    media_source = play_match.group(1).strip()
                    current_slide['playable'] = True
                    if 'youtube.com' in media_source or 'youtu.be' in media_source:
                        current_slide['source_url'] = media_source
                        result = download_youtube_video(media_source)
                        if result:
                            base_name, filename, filepath = result
                            media = f"\\play \\file media_files/{filename}"
                            found_media = True
                            current_slide['media'] = media
                            continue
                    elif media_source.startswith('\\file'):
                        media = stripped
                        found_media = True
                        current_slide['media'] = media
                        continue
                    else:
                        media = stripped
                        found_media = True
                        current_slide['media'] = media
                        continue

                if stripped.startswith('\\file'):
                    media = stripped
                    found_media = True
                    current_slide['media'] = media
                    continue

                if stripped == '\\None':
                    found_media = True
                    current_slide['media'] = ''
                    continue

            # ============================================================
            # CRITICAL FIX: Bullet points - skip if inside tabular
            # ============================================================
            # Bullet points
            if not in_tabular and (stripped.startswith('-') or stripped.startswith('•')):
                bullet_content = re.sub(r'^[-•]\s*', '', stripped)
                if itemize_stack:
                    content_buffer.append(f"\\item {bullet_content}")
                else:
                    content_buffer.append("\\begin{itemize}")
                    itemize_stack.append('itemize')
                    content_buffer.append(f"\\item {bullet_content}")
                continue
            elif stripped.startswith('-') or stripped.startswith('•'):
                # Inside tabular - keep as-is (don't convert to item)
                content_buffer.append(stripped)
                continue

            # ========== PROCESS CONTENT WITH FULL FEATURE SUPPORT ==========

            # Font size commands
            font_commands = ['\\tiny', '\\scriptsize', '\\footnotesize', '\\small',
                           '\\normalsize', '\\large', '\\Large', '\\LARGE', '\\huge', '\\Huge']
            is_font_cmd = False
            for font_cmd in font_commands:
                if stripped.startswith(font_cmd):
                    pending_font_cmd = stripped
                    is_font_cmd = True
                    break
            if is_font_cmd:
                continue

            # Special effects
            if '\\shadowtext' in stripped or '\\glowtext' in stripped or '\\gradienttext' in stripped:
                stripped = process_special_effects(stripped)
                content_buffer.append(stripped)
                continue

            # TikZ content - preserve exactly
            if '\\begin{tikzpicture}' in stripped:
                while itemize_stack:
                    content_buffer.append("\\end{itemize}")
                    itemize_stack.pop()
                content_buffer.append(stripped)
                continue

            # Block environments
            if '\\begin{block}' in stripped or '\\begin{alertblock}' in stripped or '\\begin{exampleblock}' in stripped:
                while itemize_stack:
                    content_buffer.append("\\end{itemize}")
                    itemize_stack.pop()
                content_buffer.append(stripped)
                continue
            if '\\end{block}' in stripped or '\\end{alertblock}' in stripped or '\\end{exampleblock}' in stripped:
                content_buffer.append(stripped)
                continue

            # Columns
            if '\\begin{columns}' in stripped or '\\end{columns}' in stripped:
                while itemize_stack:
                    content_buffer.append("\\end{itemize}")
                    itemize_stack.pop()
                content_buffer.append(stripped)
                continue
            if stripped.startswith('\\column'):
                while itemize_stack:
                    content_buffer.append("\\end{itemize}")
                    itemize_stack.pop()
                content_buffer.append(stripped)
                continue

            # Itemize/Enumerate
            if '\\begin{itemize}' in stripped:
                itemize_stack.append('itemize')
                content_buffer.append(stripped)
                if pending_font_cmd:
                    content_buffer.append(pending_font_cmd)
                    pending_font_cmd = None
                continue
            if '\\begin{enumerate}' in stripped:
                itemize_stack.append('enumerate')
                content_buffer.append(stripped)
                if pending_font_cmd:
                    content_buffer.append(pending_font_cmd)
                    pending_font_cmd = None
                continue
            if '\\end{itemize}' in stripped:
                if itemize_stack and itemize_stack[-1] == 'itemize':
                    itemize_stack.pop()
                content_buffer.append(stripped)
                continue
            if '\\end{enumerate}' in stripped:
                if itemize_stack and itemize_stack[-1] == 'enumerate':
                    itemize_stack.pop()
                content_buffer.append(stripped)
                continue

            # Standalone \item
            if stripped.startswith('\\item'):
                if pending_font_cmd:
                    content_buffer.append(pending_font_cmd)
                    pending_font_cmd = None
                content_buffer.append(stripped)
                continue

            # Table commands
            if stripped in ['\\hline', '\\toprule', '\\midrule', '\\bottomrule']:
                content_buffer.append(stripped)
                continue

            # Center environment
            if stripped == '\\begin{center}' or stripped == '\\end{center}':
                content_buffer.append(stripped)
                continue

            # Beamercolorbox
            if stripped.startswith('\\begin{beamercolorbox}') or stripped == '\\end{beamercolorbox}':
                content_buffer.append(stripped)
                continue

            # Text formatting
            if stripped.startswith(('\\textcolor', '\\textbf', '\\textit', '\\emph', '\\alert')):
                stripped = process_special_effects(stripped)
                content_buffer.append(stripped)
                continue

            # Math mode
            if stripped.startswith('$') or stripped.startswith('\\[') or stripped.startswith('\\('):
                content_buffer.append(stripped)
                continue

            # URL or hyperlink
            if stripped.startswith(('http://', 'https://', '\\url{', '\\href{')):
                content_buffer.append(stripped)
                continue

            # Vspace and spacing
            if stripped.startswith('\\vspace') or stripped.startswith('\\hspace'):
                content_buffer.append(stripped)
                continue

            # Regular text - fix braces and add
            if stripped:
                stripped = fix_braces(stripped)
                if stripped:
                    content_buffer.append(stripped)

        # Process notes
        elif in_notes:
            if stripped and not stripped.startswith('%'):
                stripped = fix_braces(stripped)
                if stripped:
                    notes_buffer.append(stripped)
            elif stripped.startswith('%'):
                notes_buffer.append(stripped)

    # Save last slide
    if current_slide:
        while itemize_stack:
            content_buffer.append("\\end{itemize}")
            itemize_stack.pop()
        current_slide['content'] = content_buffer.copy()
        current_slide['notes'] = notes_buffer.copy()
        slides.append(current_slide)

    return slides


def parse_latex_slides_full(lines, warnings):
    r"""Parse LaTeX format slides with \begin{frame} and \end{frame}"""
    import re

    slides = []
    content = '\n'.join(lines)

    # Find all frames
    frame_pattern = r'\\begin{frame}(?:\[[^\]]*\])?(?:\{([^}]*)\})?(.*?)\\end{frame}'
    frames = re.finditer(frame_pattern, content, re.DOTALL)

    # Extract notes separately
    note_pattern = r'\\begin{Notes}(.*?)\\end{Notes}'
    notes_blocks = list(re.finditer(note_pattern, content, re.DOTALL))

    frame_index = 0

    for frame_match in frames:
        frame_title = frame_match.group(1) or ""
        frame_content = frame_match.group(2)

        # Extract frametitle
        frametitle_match = re.search(r'\\frametitle\{([^}]*)\}', frame_content)
        if frametitle_match:
            title = frametitle_match.group(1).strip()
            frame_content = re.sub(r'\\frametitle\{[^}]*\}', '', frame_content)
        elif frame_title:
            title = frame_title.strip()
        else:
            title = f"Slide {len(slides) + 1}"

        title = clean_title(title)

        # Extract notes for this frame
        notes = []
        if frame_index < len(notes_blocks):
            note_content = notes_blocks[frame_index].group(1).strip()
            if note_content:
                for note_line in note_content.split('\n'):
                    note_line = note_line.strip()
                    if note_line and not note_line.startswith('%'):
                        notes.append(note_line)

        # Extract media
        media = ""
        media_match = re.search(r'\\includegraphics(?:\[[^\]]*\])?{([^}]*)}', frame_content)
        if media_match:
            media = f"\\file {media_match.group(1)}"
        else:
            movie_match = re.search(r'\\movie(?:\[[^\]]*\])?{[^}]*}{([^}]*)}', frame_content)
            if movie_match:
                media = f"\\play {movie_match.group(1)}"

        # Check for layout directives in frame content
        layout = None
        layout_params = None
        layout_match = re.search(r'\\(ff|wm|pip|split|hl|bg|tb|ol|corner|mosaic)\s*\{([^}]*)\}', frame_content)
        if layout_match:
            layout = layout_match.group(1)
            layout_params = layout_match.group(2)

        # Extract content lines
        content_lines = []
        for line in frame_content.split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith('\\begin{frame}') or line.startswith('\\end{frame}'):
                continue
            if line.startswith('\\frametitle'):
                continue
            content_lines.append(line)

        # Check if content already has frame commands (for pass-through)
        has_inner_frame = any('\\begin{frame}' in line for line in content_lines)
        if has_inner_frame:
            # Pass through as-is
            slides.append(frame_match.group(0))
            frame_index += 1
            continue

        # Create slide dictionary
        slide = {
            'title': title,
            'content': content_lines,
            'notes': notes,
            'media': media,
            'layout': layout,
            'layout_params': layout_params,
            'playable': '\\play' in frame_content or media.startswith('\\play'),
            'source_url': None
        }

        # Check for YouTube URLs
        youtube_match = re.search(r'(?:\\play\s+)?(?:\\url\s+)?(https?://(?:www\.)?(?:youtube\.com|youtu\.be)/[^\s\n]+)', frame_content)
        if youtube_match:
            slide['source_url'] = youtube_match.group(1)
            slide['playable'] = True

        slides.append(slide)
        frame_index += 1

    return slides

def process_slide_with_features(slide, outfile=None, warnings=None):
    """
    Process a slide with FULL feature support.
    Returns the processed LaTeX string or None if failed.
    """
    import re

    title = slide.get('title', 'Untitled')
    content = slide.get('content', [])
    notes = slide.get('notes', [])
    media = slide.get('media', '')
    layout = slide.get('layout')
    layout_params = slide.get('layout_params')
    playable = slide.get('playable', False)
    source_url = slide.get('source_url')

    # ============================================================
    # DEBUG: Log content BEFORE any processing
    # ============================================================
    debug_logger.debug(f"\n{'='*60}")
    debug_logger.debug(f"SLIDE: {title} - RAW CONTENT FROM PARSER")
    debug_logger.debug(f"{'='*60}")
    for i, line in enumerate(content):
        if isinstance(line, str) and ('tabular' in line or 'itemize' in line or '-20' in line or '&' in line):
            debug_logger.debug(f"  LINE {i}: {repr(line)}")
    debug_logger.debug(f"{'='*60}\n")

    # ============================================================
    # FIX: Clean tabular specifications and fix bullet points
    # ============================================================
    def clean_tabular_and_bullets(content_list):
        """Clean tabular specs and fix bullet points in content"""
        if not content_list:
            return content_list

        # First pass: identify table rows
        is_table_row = [False] * len(content_list)
        in_tabular = False

        for i, line in enumerate(content_list):
            if not isinstance(line, str):
                continue
            stripped = line.strip()

            if '\\begin{tabular}' in stripped or '\\begin{array}' in stripped:
                in_tabular = True
                continue
            if '\\end{tabular}' in stripped or '\\end{array}' in stripped:
                in_tabular = False
                continue

            if in_tabular and '&' in stripped:
                is_table_row[i] = True

        # Second pass: fix content
        fixed_content = []
        for i, line in enumerate(content_list):
            if not isinstance(line, str):
                fixed_content.append(line)
                continue

            stripped = line.strip()

            # If this is a table row that starts with -, fix it
            if is_table_row[i] and (stripped.startswith('-') or stripped.startswith('•')):
                # Remove the leading - or • and keep the rest of the line
                fixed_line = re.sub(r'^[-•]\s*', '', line)
                debug_logger.debug(f"  FIXED table row: {repr(line)} -> {repr(fixed_line)}")
                fixed_content.append(fixed_line)
            else:
                fixed_content.append(line)

        return fixed_content

    # ============================================================
    # Apply fixes to content
    # ============================================================
    content = clean_tabular_and_bullets(content)

    # ============================================================
    # DEBUG: Log content AFTER cleaning
    # ============================================================
    debug_logger.debug(f"\n{'='*60}")
    debug_logger.debug(f"SLIDE: {title} - AFTER CLEANING")
    debug_logger.debug(f"{'='*60}")
    for i, line in enumerate(content):
        if isinstance(line, str) and ('tabular' in line or 'itemize' in line or '-20' in line or '&' in line):
            debug_logger.debug(f"  LINE {i}: {repr(line)}")
    debug_logger.debug(f"{'='*60}\n")

    # Clean title
    clean_title = clean_title_for_latex(title)

    # ========== HANDLE LAYOUT DIRECTIVES ==========
    if layout:
        if layout == 'mosaic':
            return generate_mosaic_layout(clean_title, layout_params, content, media)
        elif layout == 'split':
            return generate_split_layout(clean_title, layout_params, content, media)
        elif layout == 'pip':
            return generate_pip_layout(clean_title, layout_params, content, media)
        elif layout == 'ff':
            return generate_fullframe_layout(clean_title, layout_params, content, media)
        elif layout == 'wm':
            return generate_watermark_layout(clean_title, layout_params, content, media)
        elif layout == 'hl':
            return generate_highlight_layout(clean_title, layout_params, content, media)
        elif layout == 'bg':
            return generate_background_layout(clean_title, layout_params, content, media)
        elif layout == 'tb':
            return generate_topbottom_layout(clean_title, layout_params, content, media)
        elif layout == 'ol':
            return generate_overlay_layout(clean_title, layout_params, content, media)
        elif layout == 'corner':
            return generate_corner_layout(clean_title, layout_params, content, media)

    # ========== HANDLE MEDIA ==========
    first_frame_path = None
    media_path = None

    if media and media != "\\None":
        # Parse media directive
        directive_type, media_source, is_playable, original_directive = parse_media_directive(media)
        playable = playable or is_playable

        # Handle YouTube videos
        if directive_type == 'url' and media_source and ('youtube.com' in media_source or 'youtu.be' in media_source):
            # Download YouTube video
            result = download_youtube_video(media_source)
            if result:
                base_name, filename, filepath = result
                media_path = f"media_files/{filename}"
                first_frame_path = generate_preview_frame(filepath)
                playable = True
                source_url = media_source
            else:
                # Fallback to URL
                media_path = media_source
                playable = False

        # Handle local files
        elif directive_type == 'file' and media_source:
            media_path = media_source
            if not os.path.exists(media_path):
                # Try in media_files
                test_path = os.path.join('media_files', os.path.basename(media_path))
                if os.path.exists(test_path):
                    media_path = test_path
            if os.path.exists(media_path):
                # Generate preview for videos
                video_extensions = ('.mp4', '.avi', '.mov', '.webm', '.mkv', '.flv', '.wmv')
                if media_path.lower().endswith(video_extensions):
                    first_frame_path = generate_preview_frame(media_path)
                    playable = True
                elif media_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    first_frame_path = media_path

    # ========== GENERATE FRAME ==========
    frame_lines = []
    frame_lines.append(f"\\begin{{frame}}{{{clean_title}}}")
    frame_lines.append(f"\\frametitle{{{clean_title}}}")
    frame_lines.append("")

    # Add media (playable or static)
    if media_path and media_path != "\\None":
        if playable and first_frame_path:
            # Playable media with preview
            frame_lines.append("\\begin{center}")
            frame_lines.append(f"    \\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{first_frame_path}}}")
            frame_lines.append("    \\vspace{0.3em}")
            frame_lines.append("    \\footnotesize Click to play\\\\")
            frame_lines.append(f"    \\movie[externalviewer]{{\\textcolor{{blue}}{{\\underline{{Play}}}}}}{{{media_path}}}")
            frame_lines.append("\\end{center}")
        elif playable:
            # Playable media without preview
            frame_lines.append("\\begin{center}")
            frame_lines.append(f"    \\movie[externalviewer]{{\\textcolor{{blue}}{{\\underline{{Play Video}}}}}}{{{media_path}}}")
            frame_lines.append("\\end{center}")
        else:
            # Static image
            frame_lines.append("\\begin{center}")
            frame_lines.append(f"    \\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{media_path}}}")
            frame_lines.append("\\end{center}")

    # Add source URL citation if present
    if source_url:
        frame_lines.append("\\vspace{0.3em}")
        frame_lines.append(f"\\begin{{center}}{{\\tiny Source: \\href{{{source_url}}}{{\\textcolor{{blue}}{{[Link]}}}}}}\\end{{center}}")

    # Add content
    if content:
        # Process content for itemize/enumerate
        processed_content = process_content_with_features(content)

        # ============================================================
        # DEBUG: Log content AFTER process_content_with_features
        # ============================================================
        debug_logger.debug(f"\n{'='*60}")
        debug_logger.debug(f"SLIDE: {title} - AFTER process_content_with_features")
        debug_logger.debug(f"{'='*60}")
        for line in processed_content.split('\n'):
            if 'tabular' in line or 'itemize' in line or '-20' in line or '&' in line:
                debug_logger.debug(f"  {repr(line)}")
        debug_logger.debug(f"{'='*60}\n")

        if processed_content:
            frame_lines.append(processed_content)

    # Add notes
    if notes:
        frame_lines.append("")
        frame_lines.append("\\note{")
        has_bullets = any(note.strip().startswith(('•', '-', '\\item')) for note in notes if note.strip())
        if has_bullets:
            frame_lines.append("\\begin{itemize}")
            for note in notes:
                if note and note.strip():
                    note_text = re.sub(r'^[•-]\s*', '', note.strip())
                    note_text = re.sub(r'^\\item\s*', '', note_text)
                    if note_text:
                        frame_lines.append(f"    \\item {note_text}")
            frame_lines.append("\\end{itemize}")
        else:
            for note in notes:
                if note and note.strip():
                    frame_lines.append(f"    {note}")
        frame_lines.append("}")

    frame_lines.append("\\end{frame}")
    return '\n'.join(frame_lines)


import logging
import datetime

import logging
import datetime
import sys

# Setup debug logging
def setup_debug_logging():
    """Setup debug logging to a file"""
    log_filename = f"tabular_debug_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # Create logger
    logger = logging.getLogger('tabular_debug')
    logger.setLevel(logging.DEBUG)

    # File handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # Also print to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(file_format)
    logger.addHandler(console_handler)

    logger.info(f"Debug logging started. Log file: {log_filename}")
    return logger

# Initialize logger
debug_logger = setup_debug_logging()

def log_line_by_line(func_name, lines, label=""):
    """Log each line of content"""
    if not lines:
        return

    debug_logger.debug(f"\n{'-'*40}")
    debug_logger.debug(f"FUNCTION: {func_name} {label}")
    debug_logger.debug(f"{'-'*40}")
    for i, line in enumerate(lines):
        if isinstance(line, str) and ('tabular' in line or '@{}' in line or 'PROTECTED' in line):
            debug_logger.debug(f"  LINE {i}: {repr(line)}")
    debug_logger.debug(f"{'-'*40}\n")


logger = setup_debug_logging()

# ============================================================
# DEBUG WRAPPER FUNCTIONS
# ============================================================

def log_tabular_content(func_name, input_text, output_text, label=""):
    """Log tabular content before and after a function"""
    if not isinstance(input_text, str):
        return

    if 'tabular' in input_text or 'tabular' in str(output_text):
        logger.debug(f"\n{'='*60}")
        logger.debug(f"FUNCTION: {func_name} {label}")
        logger.debug(f"{'='*60}")
        logger.debug(f"INPUT ({len(input_text)} chars):\n{repr(input_text)}")
        logger.debug(f"OUTPUT ({len(output_text)} chars):\n{repr(output_text)}")
        if 'tabular' in input_text and 'tabular' in output_text:
            logger.debug(f"CHANGED: {input_text != output_text}")
        logger.debug(f"{'='*60}\n")



def generate_mosaic_layout(title, params, content, media):
    """Generate mosaic layout with grid of images"""
    import re

    # Parse params: \mosaic{rows,cols}{image1, image2, ...}
    match = re.match(r'\{(\d+),(\d+)\}\{(.*?)\}', params)
    if not match:
        return None

    rows = int(match.group(1))
    cols = int(match.group(2))
    images = [img.strip() for img in match.group(3).split(',') if img.strip()]

    # Calculate column width
    col_width = 0.94 / cols

    frame_lines = []
    frame_lines.append(f"\\begin{{frame}}{{{title}}}")
    frame_lines.append(f"\\frametitle{{{title}}}")
    frame_lines.append("")

    # Check if content should be in columns with mosaic
    has_content = any(line.strip() for line in content if line.strip())

    if has_content:
        # Two columns: content + mosaic
        frame_lines.append("\\begin{columns}[T]")
        frame_lines.append("\\begin{column}{0.48\\textwidth}")
        processed_content = process_content_with_features(content)
        if processed_content:
            frame_lines.append(processed_content)
        frame_lines.append("\\end{column}")
        frame_lines.append("\\begin{column}{0.48\\textwidth}")

    # Generate mosaic grid
    frame_lines.append("\\begin{center}")
    frame_lines.append(f"\\begin{{tabular}}{{{'c' * cols}}}")
    frame_lines.append("\\hline")

    for idx, img_path in enumerate(images):
        # Clean image path
        if not img_path.startswith(('media_files/', './', '/')):
            img_path = f"media_files/{img_path}"

        frame_lines.append(f"\\includegraphics[width={col_width}\\textwidth,height=0.25\\textheight,keepaspectratio]{{{img_path}}}")

        if (idx + 1) % cols == 0:
            if idx < len(images) - 1:
                frame_lines.append("\\\\ \\hline")
        else:
            frame_lines[-1] = frame_lines[-1] + " &"

    if not frame_lines[-1].endswith('\\\\ \\hline'):
        frame_lines.append("\\\\ \\hline")

    frame_lines.append("\\end{tabular}")
    frame_lines.append("\\end{center}")

    if has_content:
        frame_lines.append("\\end{column}")
        frame_lines.append("\\end{columns}")

    frame_lines.append("\\end{frame}")
    return '\n'.join(frame_lines)


def generate_split_layout(title, params, content, media):
    """Generate split layout: image on left, content on right"""
    # params is the image path
    image_path = params.strip()
    if not image_path.startswith(('media_files/', './')):
        image_path = f"media_files/{image_path}"

    frame_lines = []
    frame_lines.append(f"\\begin{{frame}}{{{title}}}")
    frame_lines.append(f"\\frametitle{{{title}}}")
    frame_lines.append("")
    frame_lines.append("\\begin{columns}[T]")
    frame_lines.append("\\begin{column}{0.48\\textwidth}")
    frame_lines.append(f"\\includegraphics[width=\\textwidth,keepaspectratio]{{{image_path}}}")
    frame_lines.append("\\end{column}")
    frame_lines.append("\\begin{column}{0.48\\textwidth}")

    processed_content = process_content_with_features(content)
    if processed_content:
        frame_lines.append(processed_content)

    frame_lines.append("\\end{column}")
    frame_lines.append("\\end{columns}")
    frame_lines.append("\\end{frame}")
    return '\n'.join(frame_lines)


def generate_pip_layout(title, params, content, media):
    """Generate picture-in-picture layout: content on left, small image on right"""
    image_path = params.strip()
    if not image_path.startswith(('media_files/', './')):
        image_path = f"media_files/{image_path}"

    frame_lines = []
    frame_lines.append(f"\\begin{{frame}}{{{title}}}")
    frame_lines.append(f"\\frametitle{{{title}}}")
    frame_lines.append("")
    frame_lines.append("\\begin{columns}[T]")
    frame_lines.append("\\begin{column}{0.68\\textwidth}")

    processed_content = process_content_with_features(content)
    if processed_content:
        frame_lines.append(processed_content)

    frame_lines.append("\\end{column}")
    frame_lines.append("\\begin{column}{0.28\\textwidth}")
    frame_lines.append("\\vspace{1em}")
    frame_lines.append(f"\\includegraphics[width=\\textwidth,keepaspectratio]{{{image_path}}}")
    frame_lines.append("\\end{column}")
    frame_lines.append("\\end{columns}")
    frame_lines.append("\\end{frame}")
    return '\n'.join(frame_lines)


def generate_fullframe_layout(title, params, content, media):
    """Generate fullframe layout: image takes entire frame"""
    image_path = params.strip()
    if not image_path.startswith(('media_files/', './')):
        image_path = f"media_files/{image_path}"

    frame_lines = []
    frame_lines.append(f"\\begin{{frame}}{{{title}}}")
    frame_lines.append("\\setbeamertemplate{background}{")
    frame_lines.append("\\begin{tikzpicture}[remember picture,overlay]")
    frame_lines.append(f"\\node at (current page.center) {{\\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{{{image_path}}}}}")
    frame_lines.append("\\end{tikzpicture}")
    frame_lines.append("}")
    frame_lines.append(f"\\frametitle{{{title}}}")

    if content:
        processed_content = process_content_with_features(content)
        if processed_content:
            frame_lines.append("\\vspace{0.5em}")
            frame_lines.append(processed_content)

    frame_lines.append("\\end{frame}")
    return '\n'.join(frame_lines)


def generate_watermark_layout(title, params, content, media):
    """Generate watermark layout: image as background watermark"""
    image_path = params.strip()
    if not image_path.startswith(('media_files/', './')):
        image_path = f"media_files/{image_path}"

    frame_lines = []
    frame_lines.append(f"\\begin{{frame}}{{{title}}}")
    frame_lines.append("\\setbeamertemplate{background}{")
    frame_lines.append("\\begin{tikzpicture}[remember picture,overlay]")
    frame_lines.append(f"\\node[opacity=0.15] at (current page.center) {{\\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{{{image_path}}}}}")
    frame_lines.append("\\end{tikzpicture}")
    frame_lines.append("}")
    frame_lines.append(f"\\frametitle{{{title}}}")

    if content:
        processed_content = process_content_with_features(content)
        if processed_content:
            frame_lines.append(processed_content)

    frame_lines.append("\\end{frame}")
    return '\n'.join(frame_lines)


def generate_highlight_layout(title, params, content, media):
    """Generate highlight layout: image with highlighted content overlay"""
    image_path = params.strip()
    if not image_path.startswith(('media_files/', './')):
        image_path = f"media_files/{image_path}"

    frame_lines = []
    frame_lines.append(f"\\begin{{frame}}{{{title}}}")
    frame_lines.append(f"\\frametitle{{{title}}}")
    frame_lines.append("")
    frame_lines.append("\\begin{columns}[T]")
    frame_lines.append("\\begin{column}{0.6\\textwidth}")
    frame_lines.append(f"\\includegraphics[width=\\textwidth,keepaspectratio]{{{image_path}}}")
    frame_lines.append("\\end{column}")
    frame_lines.append("\\begin{column}{0.36\\textwidth}")
    frame_lines.append("\\colorbox{yellow!20}{")
    frame_lines.append("\\begin{minipage}{\\textwidth}")

    processed_content = process_content_with_features(content)
    if processed_content:
        frame_lines.append(processed_content)

    frame_lines.append("\\end{minipage}")
    frame_lines.append("}")
    frame_lines.append("\\end{column}")
    frame_lines.append("\\end{columns}")
    frame_lines.append("\\end{frame}")
    return '\n'.join(frame_lines)


def generate_background_layout(title, params, content, media):
    """Generate background layout: image as background with content overlay"""
    image_path = params.strip()
    if not image_path.startswith(('media_files/', './')):
        image_path = f"media_files/{image_path}"

    frame_lines = []
    frame_lines.append(f"\\begin{{frame}}{{{title}}}")
    frame_lines.append("\\setbeamertemplate{background}{")
    frame_lines.append("\\begin{tikzpicture}[remember picture,overlay]")
    frame_lines.append(f"\\node[opacity=0.3] at (current page.center) {{\\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{{{image_path}}}}}")
    frame_lines.append("\\end{tikzpicture}")
    frame_lines.append("}")
    frame_lines.append(f"\\frametitle{{{title}}}")

    if content:
        frame_lines.append("\\begin{beamercolorbox}[wd=\\paperwidth,ht=\\paperheight,center]{}")
        processed_content = process_content_with_features(content)
        if processed_content:
            frame_lines.append(processed_content)
        frame_lines.append("\\end{beamercolorbox}")

    frame_lines.append("\\end{frame}")
    return '\n'.join(frame_lines)


def generate_topbottom_layout(title, params, content, media):
    """Generate top-bottom layout: image at top, content at bottom"""
    image_path = params.strip()
    if not image_path.startswith(('media_files/', './')):
        image_path = f"media_files/{image_path}"

    frame_lines = []
    frame_lines.append(f"\\begin{{frame}}{{{title}}}")
    frame_lines.append(f"\\frametitle{{{title}}}")
    frame_lines.append("")
    frame_lines.append("\\begin{center}")
    frame_lines.append(f"\\includegraphics[width=0.8\\textwidth,keepaspectratio]{{{image_path}}}")
    frame_lines.append("\\end{center}")
    frame_lines.append("\\vspace{0.5em}")

    processed_content = process_content_with_features(content)
    if processed_content:
        frame_lines.append(processed_content)

    frame_lines.append("\\end{frame}")
    return '\n'.join(frame_lines)


def generate_overlay_layout(title, params, content, media):
    """Generate overlay layout: image with overlaid text blocks"""
    parts = params.split('|')
    image_path = parts[0].strip()
    if not image_path.startswith(('media_files/', './')):
        image_path = f"media_files/{image_path}"

    frame_lines = []
    frame_lines.append(f"\\begin{{frame}}{{{title}}}")
    frame_lines.append(f"\\frametitle{{{title}}}")
    frame_lines.append("\\begin{tikzpicture}[remember picture,overlay]")
    frame_lines.append(f"\\node at (current page.center) {{\\includegraphics[width=\\paperwidth,keepaspectratio]{{{image_path}}}}}")

    # Add overlay text blocks
    for i in range(1, len(parts)):
        if '|' not in parts[i]:
            continue
        coords, text = parts[i].split('|', 1)
        x, y = coords.split(',')
        frame_lines.append(f"\\node[fill=black!70, text=white, rounded corners, anchor=north west] at ({x},{y}) {{\\textbf{{{text}}}}}")

    frame_lines.append("\\end{tikzpicture}")
    frame_lines.append("\\end{frame}")
    return '\n'.join(frame_lines)


def generate_corner_layout(title, params, content, media):
    """Generate corner layout: image in corner with content"""
    parts = params.split('|')
    image_path = parts[0].strip()
    corner = parts[1].strip() if len(parts) > 1 else 'br'

    if not image_path.startswith(('media_files/', './')):
        image_path = f"media_files/{image_path}"

    positions = {
        'tl': ('0.05\\textwidth', '0.05\\textheight', 'north west'),
        'tr': ('0.95\\textwidth', '0.05\\textheight', 'north east'),
        'bl': ('0.05\\textwidth', '0.95\\textheight', 'south west'),
        'br': ('0.95\\textwidth', '0.95\\textheight', 'south east')
    }
    x, y, anchor = positions.get(corner, positions['br'])

    frame_lines = []
    frame_lines.append(f"\\begin{{frame}}{{{title}}}")
    frame_lines.append(f"\\frametitle{{{title}}}")
    frame_lines.append("\\begin{tikzpicture}[remember picture,overlay]")
    frame_lines.append(f"\\node[anchor={anchor}] at ({x},{y}) {{\\includegraphics[width=0.25\\textwidth,keepaspectratio]{{{image_path}}}}}")
    frame_lines.append("\\end{tikzpicture}")
    frame_lines.append("")

    processed_content = process_content_with_features(content)
    if processed_content:
        frame_lines.append(processed_content)

    frame_lines.append("\\end{frame}")
    return '\n'.join(frame_lines)

def process_content_with_features(content):
    """Process content with full feature support including itemize/enumerate"""
    import re

    if not content:
        return ""

    # Log input
    log_line_by_line("process_content_with_features", content, "INPUT")

    # ============================================================
    # PRE-PROCESSING PASS: Identify table rows before any conversion
    # ============================================================
    # First, identify which lines are table rows (contain &)
    is_table_row = [False] * len(content)
    in_tabular = False

    for i, line in enumerate(content):
        if not isinstance(line, str):
            continue
        stripped = line.strip()

        # Track tabular environment
        if '\\begin{tabular}' in stripped or '\\begin{array}' in stripped:
            in_tabular = True
            continue
        if '\\end{tabular}' in stripped or '\\end{array}' in stripped:
            in_tabular = False
            continue

        # Mark table rows (lines containing &)
        if in_tabular and '&' in stripped:
            is_table_row[i] = True

    # ============================================================
    # MAIN PROCESSING PASS
    # ============================================================
    result = []
    itemize_stack = []
    in_tikz = False
    tikz_buffer = []
    in_math = False
    math_buffer = []
    in_tabular = False

    for idx, line in enumerate(content):
        if not line or not line.strip():
            continue

        stripped = line.strip()

        # ============================================================
        # TRACK TABULAR ENVIRONMENT
        # ============================================================
        if '\\begin{tabular}' in stripped or '\\begin{array}' in stripped:
            in_tabular = True
            # Close any open itemize before tabular
            while itemize_stack:
                result.append("\\end{itemize}")
                itemize_stack.pop()
            result.append(line)
            continue

        if '\\end{tabular}' in stripped or '\\end{array}' in stripped:
            in_tabular = False
            # Close any open itemize before ending tabular
            while itemize_stack:
                result.append("\\end{itemize}")
                itemize_stack.pop()
            result.append(line)
            continue

        # ============================================================
        # FIX: Clean up any remaining placeholder artifacts
        # ============================================================
        if isinstance(line, str):
            line = re.sub(r'@@@[^@]+@@@', '', line)
            line = re.sub(r'PROTECTED_\d+', '', line)
            line = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', line)

        # ============================================================
        # 1. TIKZ ENVIRONMENT HANDLING - PRESERVE COMPLETELY
        # ============================================================
        if '\\begin{tikzpicture}' in stripped:
            in_tikz = True
            tikz_buffer = [line]
            while itemize_stack:
                result.append("\\end{itemize}")
                itemize_stack.pop()
            continue

        if in_tikz:
            tikz_buffer.append(line)
            if '\\end{tikzpicture}' in stripped:
                in_tikz = False
                result.append('\n'.join(tikz_buffer))
                tikz_buffer = []
            continue

        # ============================================================
        # 2. MATH ENVIRONMENT HANDLING - PRESERVE COMPLETELY
        # ============================================================
        if any(stripped.startswith(start) for start in ['\\begin{align', '\\begin{equation', '\\begin{gather', '\\begin{multline']):
            in_math = True
            math_buffer = [line]
            while itemize_stack:
                result.append("\\end{itemize}")
                itemize_stack.pop()
            continue

        if in_math:
            math_buffer.append(line)
            if any(end in stripped for end in ['\\end{align', '\\end{equation}', '\\end{gather}', '\\end{multline']):
                in_math = False
                result.append('\n'.join(math_buffer))
                math_buffer = []
            continue

        # ============================================================
        # 3. LIST ENVIRONMENTS - ITEMIZE/ENUMERATE
        # ============================================================
        if '\\begin{itemize}' in stripped:
            # If we're in tabular, just pass through
            if in_tabular:
                result.append(line)
                continue
            itemize_stack.append('itemize')
            result.append(stripped)
            continue

        if '\\end{itemize}' in stripped:
            if itemize_stack and itemize_stack[-1] == 'itemize':
                itemize_stack.pop()
            result.append(stripped)
            continue

        if '\\begin{enumerate}' in stripped:
            if in_tabular:
                result.append(line)
                continue
            itemize_stack.append('enumerate')
            result.append(stripped)
            continue

        if '\\end{enumerate}' in stripped:
            if itemize_stack and itemize_stack[-1] == 'enumerate':
                itemize_stack.pop()
            result.append(stripped)
            continue

        # ============================================================
        # 4. BULLET POINTS - USE PRE-PROCESSED TABLE ROW INFO
        # ============================================================
        is_bullet = stripped.startswith('-') or stripped.startswith('•')

        # CRITICAL: If this line was marked as a table row, skip bullet conversion
        if is_bullet and is_table_row[idx]:
            result.append(line)
            continue

        # If we're in tabular, skip bullet point conversion entirely
        if in_tabular and is_bullet:
            result.append(line)
            continue

        # Handle bullet points (convert - or • to \item)
        if is_bullet:
            bullet_content = re.sub(r'^[-•]\s*', '', stripped)
            if not itemize_stack:
                result.append("\\begin{itemize}")
                itemize_stack.append('itemize')
                result.append(f"\\item {bullet_content}")
            else:
                result.append(f"\\item {bullet_content}")
            continue

        # ============================================================
        # 5. \item COMMANDS
        # ============================================================
        if stripped.startswith('\\item'):
            if in_tabular:
                result.append(line)
                continue
            result.append(stripped)
            continue

        # ============================================================
        # 6. BLOCK ENVIRONMENTS
        # ============================================================
        if stripped.startswith(('\\begin{block}', '\\begin{alertblock}', '\\begin{exampleblock}')):
            while itemize_stack:
                result.append("\\end{itemize}")
                itemize_stack.pop()
            result.append(stripped)
            continue

        if stripped.startswith(('\\end{block}', '\\end{alertblock}', '\\end{exampleblock}')):
            result.append(stripped)
            continue

        # ============================================================
        # 7. COLUMN ENVIRONMENTS
        # ============================================================
        if stripped.startswith(('\\begin{columns}', '\\end{columns}')):
            while itemize_stack:
                result.append("\\end{itemize}")
                itemize_stack.pop()
            result.append(stripped)
            continue

        if stripped.startswith('\\column'):
            while itemize_stack:
                result.append("\\end{itemize}")
                itemize_stack.pop()
            result.append(stripped)
            continue

        # ============================================================
        # 8. TABLE COMMANDS - PASS THROUGH
        # ============================================================
        if stripped in ['\\hline', '\\toprule', '\\midrule', '\\bottomrule', '\\addlinespace']:
            result.append(stripped)
            continue

        # ============================================================
        # 9. MATH MODE (INLINE)
        # ============================================================
        if stripped.startswith('$') or stripped.startswith('\\[') or stripped.startswith('\\('):
            result.append(stripped)
            continue

        # ============================================================
        # 10. CENTER ENVIRONMENT
        # ============================================================
        if stripped == '\\begin{center}' or stripped == '\\end{center}':
            result.append(stripped)
            continue

        # ============================================================
        # 11. BEAMER COLOR BOX
        # ============================================================
        if stripped.startswith('\\begin{beamercolorbox}') or stripped == '\\end{beamercolorbox}':
            result.append(stripped)
            continue

        # ============================================================
        # 12. TEXT FORMATTING WITH SPECIAL EFFECTS
        # ============================================================
        if stripped.startswith(('\\textcolor', '\\textbf', '\\textit', '\\emph', '\\alert')):
            stripped = process_special_effects(stripped)
            result.append(stripped)
            continue

        # ============================================================
        # 13. URLS AND HYPERLINKS
        # ============================================================
        if stripped.startswith(('http://', 'https://', '\\url{', '\\href{')):
            result.append(stripped)
            continue

        # ============================================================
        # 14. SPACING COMMANDS
        # ============================================================
        if stripped.startswith(('\\vspace', '\\hspace')):
            result.append(stripped)
            continue

        # ============================================================
        # 15. SCAN FOR TIKZ INSIDE OTHER ENVIRONMENTS
        # ============================================================
        if '\\begin{tikzpicture}' in stripped or '\\end{tikzpicture}' in stripped:
            while itemize_stack:
                result.append("\\end{itemize}")
                itemize_stack.pop()
            result.append(stripped)
            continue

        # ============================================================
        # 16. REGULAR TEXT - Fix braces and add
        # ============================================================
        stripped = fix_braces(stripped)
        if stripped:
            result.append(stripped)

    # ============================================================
    # 17. CLEANUP - Close any remaining itemize environments
    # ============================================================
    while itemize_stack:
        if itemize_stack[-1] == 'itemize':
            result.append("\\end{itemize}")
        elif itemize_stack[-1] == 'enumerate':
            result.append("\\end{enumerate}")
        itemize_stack.pop()

    # Log output
    log_line_by_line("process_content_with_features", result, "OUTPUT")

    return '\n'.join(result)

def clean_title(title):
    """Clean title for LaTeX - remove braces and special characters"""
    if not title:
        return "Untitled"

    # Remove braces
    title = title.replace('{', '').replace('}', '')
    title = title.replace('\\{', '').replace('\\}', '')

    # Escape special characters
    title = title.replace('&', '\\&')
    title = title.replace('%', '\\%')
    title = title.replace('$', '\\$')
    title = title.replace('#', '\\#')
    title = title.replace('_', '\\_')

    return title.strip() or "Untitled"


def clean_title_for_latex(title):
    """Clean title for LaTeX frame"""
    return clean_title(title)

def fix_braces(text):
    """Fix malformed braces in LaTeX content - COMPLETELY PRESERVES tabular and TikZ content"""
    if not text:
        return text
    # Log input
    if isinstance(text, str) and ('tabular' in text or '@{}' in text):
        logger.debug(f"fix_braces INPUT: {repr(text)}")

    import re

    # ============================================================
    # CRITICAL: If this contains ANY tabular, array, or @{} patterns,
    # return it unchanged - these are LaTeX syntax, not braces to fix
    # ============================================================
    if '\\begin{tabular}' in text or '\\begin{array}' in text:
        if 'tabular' in text:
            logger.debug(f"fix_braces: EARLY RETURN - found tabular/array")
            logger.debug(f"fix_braces OUTPUT (unchanged): {repr(text)}")
        return text

    if '@{}' in text or re.search(r'@\{[^}]*\}', text):
        if '@{}' in text:
            logger.debug(f"fix_braces: EARLY RETURN - found @{{}} pattern")
            logger.debug(f"fix_braces OUTPUT (unchanged): {repr(text)}")
        return text

    # ============================================================
    # CRITICAL: Detect and preserve TikZ content
    # ============================================================
    if '\\begin{tikzpicture}' in text or '\\end{tikzpicture}' in text:
        logger.debug(f"fix_braces OUTPUT: {repr(text)}")
        return text

    # Also check for common TikZ patterns
    tikz_patterns = [
        r'\\node\[.*?\]\s*\(.*?\)\s*\{.*?\};',
        r'\\draw.*?;',
        r'\\fill.*?;',
        r'\\scope.*?;',
        r'\\begin\{scope\}',
        r'\\end\{scope\}',
    ]

    for pattern in tikz_patterns:
        if re.search(pattern, text, re.DOTALL):
            return text

    # ============================================================
    # Now apply brace fixes (only for non-tabular, non-TikZ content)
    # ============================================================
    # Remove triple or more closing braces
    text = re.sub(r'\}{3,}', '}}', text)

    # Fix: \Huge{...} -> {\Huge ...}
    text = re.sub(r'\\Huge\{', r'\\Huge ', text)
    text = re.sub(r'\\Large\{', r'\\Large ', text)
    text = re.sub(r'\\large\{', r'\\large ', text)

    # Fix: \textbf{...}} -> \textbf{...}
    text = re.sub(r'\\textbf\{([^}]*?)\}(?=\})', r'\\textbf{\1}', text)

    # Fix: \textcolor{blue}{text}} -> \textcolor{blue}{text}
    text = re.sub(r'\\textcolor\{([^}]+)\}\{([^}]*?)\}(?=\})', r'\\textcolor{\1}{\2}', text)

    # Fix: \large text -> \large{text}
    if '\\large ' in text and '{' not in text:
        parts = text.split('\\large ')
        if len(parts) == 2:
            text = parts[0] + '\\large{' + parts[1] + '}'

    # Balance braces
    open_count = text.count('{')
    close_count = text.count('}')
    if open_count > close_count:
        text = text + '}' * (open_count - close_count)
    elif close_count > open_count:
        while text.endswith('}') and text.count('}') > text.count('{'):
            text = text[:-1]

    # Remove empty braces (only for non-tabular content, already returned early)
    text = re.sub(r'\{\}', '', text)

    return text

def process_line_for_media(line, inside_column=False):
    """Process a single line, converting any media or layout directives"""
    stripped = line.strip()

    # Skip empty lines
    if not stripped:
        return line

    # ============================================================
    # CRITICAL: PRESERVE TIKZ CONTENT COMPLETELY
    # ============================================================
    if '\\begin{tikzpicture}' in stripped or '\\end{tikzpicture}' in stripped:
        return line

    if '\\begin{scope}' in stripped or '\\end{scope}' in stripped:
        return line

    if '\\node' in stripped and ('draw' in stripped or 'fill' in stripped or 'fit' in stripped):
        # This is likely a TikZ node - preserve it
        return line

    # FIRST: Check for layout directives
    if stripped.startswith('\\mosaic'):
        return convert_mosaic_to_latex(line)
    elif stripped.startswith('\\split'):
        return line
    elif stripped.startswith('\\pip'):
        return line
    elif stripped.startswith('\\wm') or stripped.startswith('\\ff') or stripped.startswith('\\hl') or \
         stripped.startswith('\\bg') or stripped.startswith('\\tb') or stripped.startswith('\\ol') or \
         stripped.startswith('\\corner'):
        return line

    # THEN: Check for media directives (including YouTube)
    if '\\play' in stripped:
        return convert_play_to_movie(line)
    elif '\\file' in stripped and '\\play' not in stripped:
        file_match = re.search(r'\\file\s+(.+?)(?=\s*$|\s*\\|$)', stripped)
        if file_match:
            file_path = file_match.group(1).strip()
            converted = convert_file_to_includegraphics(file_path)
            if converted:
                if inside_column:
                    return converted
                else:
                    remaining = stripped[file_match.end():].strip()
                    if remaining:
                        return f"\\begin{{center}}{converted}\\end{{center}} {remaining}"
                    return f"\\begin{{center}}{converted}\\end{{center}}"
            else:
                return f"\\textcolor{{gray}}{{[File not found: {os.path.basename(file_path)}]}}"
        return line

    # Handle direct URLs (without \file or \play)
    elif stripped.startswith(('http://', 'https://')):
        if 'youtube.com' in stripped or 'youtu.be' in stripped:
            # ... YouTube handling ...
            pass
        else:
            return f"\\href{{{stripped}}}{{\\textcolor{{blue}}{{\\underline{{Open Link}}}}}}"

    return line

# Add this near the top of the file with other imports
import re

def protect_tikz_content(text):
    """
    Protect TikZ content from being modified by other processing functions.
    Returns the protected text with TikZ content preserved.
    """
    if not text:
        return text

    # If this is a TikZ line, return it unchanged
    tikz_patterns = [
        r'\\begin\{tikzpicture\}',
        r'\\end\{tikzpicture\}',
        r'\\begin\{scope\}',
        r'\\end\{scope\}',
        r'\\node\[.*?\]\s*\(.*?\)\s*\{.*?\};',
        r'\\draw\[.*?\].*?;',
        r'\\fill\[.*?\].*?;',
        r'\\scope\[.*?\].*?;',
        r'\\path\[.*?\].*?;',
        r'\\clip\[.*?\].*?;',
    ]

    for pattern in tikz_patterns:
        if re.search(pattern, text, re.DOTALL):
            return text

    return text

def parse_native_slides(lines, warnings):
    """Parse native format slides with \title and \begin{Content}"""
    import re

    slides = []
    current_slide = None
    in_content = False
    in_notes = False
    content_buffer = []
    notes_buffer = []
    media = ""
    found_media = False

    for line in lines:
        stripped = line.strip()

        # Detect title
        title_match = re.match(r'^%?\s*\\title\s+(.+)$', line)
        if title_match:
            # Save previous slide
            if current_slide:
                current_slide['content'] = content_buffer.copy()
                current_slide['notes'] = notes_buffer.copy()
                slides.append(current_slide)

            # Start new slide
            title = title_match.group(1).strip()
            # Clean title - remove braces
            title = title.replace('{', '').replace('}', '')
            title = title.replace('\\{', '').replace('\\}', '')
            if not title.strip():
                title = f"Slide {len(slides) + 1}"

            current_slide = {
                'title': title,
                'content': [],
                'notes': [],
                'media': ''
            }
            content_buffer = []
            notes_buffer = []
            media = ""
            found_media = False
            in_content = False
            in_notes = False
            continue

        if current_slide is None:
            continue

        # Detect Content block
        if re.match(r'^%?\s*\\begin{Content}\s*$', stripped):
            in_content = True
            in_notes = False
            found_media = False
            continue
        elif re.match(r'^%?\s*\\end{Content}\s*$', stripped):
            in_content = False
            continue

        # Detect Notes block
        if re.match(r'^%?\s*\\begin{Notes}\s*$', stripped):
            in_notes = True
            in_content = False
            continue
        elif re.match(r'^%?\s*\\end{Notes}\s*$', stripped):
            in_notes = False
            continue

        # Process content
        if in_content:
            if stripped and not stripped.startswith('%'):
                # Check for media directive
                if not found_media and stripped in ['\\None', '\\file', '\\play'] or stripped.startswith(('\\file', '\\play')):
                    if stripped != '\\None':
                        media = stripped
                    found_media = True
                    current_slide['media'] = media
                    continue

                # Fix malformed braces
                clean_line = fix_braces(stripped)
                if clean_line:
                    content_buffer.append(clean_line)
            elif stripped.startswith('%'):
                # Keep comments
                content_buffer.append(stripped)

        # Process notes
        elif in_notes:
            if stripped and not stripped.startswith('%'):
                clean_note = fix_braces(stripped)
                if clean_note:
                    notes_buffer.append(clean_note)
            elif stripped.startswith('%'):
                notes_buffer.append(stripped)

    # Save last slide
    if current_slide:
        current_slide['content'] = content_buffer.copy()
        current_slide['notes'] = notes_buffer.copy()
        current_slide['media'] = media
        slides.append(current_slide)

    return slides


def parse_latex_slides(lines, warnings):
    """Parse LaTeX format slides with \begin{frame} and \end{frame}"""
    import re

    slides = []
    content = '\n'.join(lines)

    # Find all frames
    frame_pattern = r'\\begin{frame}(?:\[[^\]]*\])?(?:\{([^}]*)\})?(.*?)\\end{frame}'
    frames = re.finditer(frame_pattern, content, re.DOTALL)

    for frame_match in frames:
        frame_title = frame_match.group(1) or ""
        frame_content = frame_match.group(2)

        # Extract frametitle if present
        frametitle_match = re.search(r'\\frametitle\{([^}]*)\}', frame_content)
        if frametitle_match:
            title = frametitle_match.group(1).strip()
            # Remove frametitle from content
            frame_content = re.sub(r'\\frametitle\{[^}]*\}', '', frame_content)
        elif frame_title:
            title = frame_title.strip()
        else:
            title = f"Slide {len(slides) + 1}"

        # Clean title
        title = title.replace('{', '').replace('}', '')
        title = title.replace('\\{', '').replace('\\}', '')
        if not title.strip():
            title = f"Slide {len(slides) + 1}"

        # Build slide content
        slide_content = []
        slide_content.append(f"\\begin{{frame}}{{{title}}}")
        slide_content.append(f"\\frametitle{{{title}}}")
        slide_content.append("")

        # Add frame content
        for line in frame_content.split('\n'):
            line = line.strip()
            if line:
                # Skip commands we already handled
                if line.startswith('\\frametitle'):
                    continue
                if line.startswith('\\begin{frame}') or line.startswith('\\end{frame}'):
                    continue
                slide_content.append(line)

        # Check for notes (might be outside frame in native format)
        # We'll handle notes separately

        slide_content.append("\\end{frame}")
        slides.append('\n'.join(slide_content))

    return slides


def write_slide(outfile, slide, warnings):
    """Write a slide to the output file"""
    import re

    title = slide.get('title', 'Untitled')
    content = slide.get('content', [])
    notes = slide.get('notes', [])
    media = slide.get('media', '')

    # Clean title
    clean_title = title.replace('{', '').replace('}', '')
    clean_title = clean_title.replace('\\{', '').replace('\\}', '')
    if not clean_title.strip():
        clean_title = "Untitled"

    # Start frame
    outfile.write(f"\\begin{{frame}}{{{clean_title}}}\n")
    outfile.write(f"\\frametitle{{{clean_title}}}\n")
    outfile.write("\n")

    # Add media if present
    if media and media != "\\None":
        if media.startswith('\\file'):
            file_path = media.replace('\\file', '').strip()
            outfile.write("\\begin{center}\n")
            outfile.write(f"    \\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{file_path}}}\n")
            outfile.write("\\end{center}\n")
        elif media.startswith('\\play'):
            play_content = media.replace('\\play', '').strip()
            if play_content.startswith('\\file'):
                file_path = play_content.replace('\\file', '').strip()
                outfile.write("\\begin{center}\n")
                outfile.write(f"    \\movie[externalviewer]{{\\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{file_path}}}}}{{{file_path}}}\n")
                outfile.write("\\end{center}\n")

    # Add content
    if content:
        # Process content for itemize/enumerate
        processed_content = process_content_with_features(content)

        # ============================================================
        # DEBUG: Log content AFTER processing
        # ============================================================
        debug_logger.debug(f"\n{'='*60}")
        debug_logger.debug(f"SLIDE: {title} - AFTER PROCESSING")
        debug_logger.debug(f"{'='*60}")
        for line in processed_content.split('\n'):
            if 'tabular' in line or 'itemize' in line or '-20' in line:
                debug_logger.debug(f"  {repr(line)}")
        debug_logger.debug(f"{'='*60}\n")

        if processed_content:
            frame_lines.append(processed_content)


        for line in content:
            if line and line.strip():
                # Fix braces and write
                clean_line = fix_braces(line)
                if clean_line:
                    outfile.write(f"{clean_line}\n")

    # Add notes
    if notes:
        outfile.write("\n")
        outfile.write("\\note{\n")
        has_bullets = any(note.strip().startswith(('•', '-', '\\item')) for note in notes if note.strip())
        if has_bullets:
            outfile.write("\\begin{itemize}\n")
            for note in notes:
                if note and note.strip():
                    note_text = re.sub(r'^[•-]\s*', '', note.strip())
                    note_text = re.sub(r'^\\item\s*', '', note_text)
                    if note_text:
                        outfile.write(f"    \\item {note_text}\n")
            outfile.write("\\end{itemize}\n")
        else:
            for note in notes:
                if note and note.strip():
                    outfile.write(f"    {note}\n")
        outfile.write("}\n")

    outfile.write("\\end{frame}\n")
    outfile.write("\n")




def _parse_native_format(content: str) -> list:
    """Parse native format (\title + \begin{Content}) into slide dictionaries"""
    import re

    slides = []
    current_slide = None
    in_content = False
    in_notes = False
    content_buffer = []  # Buffer for collecting content lines
    itemize_stack = []   # Track nested itemize/enumerate environments
    pending_font_cmd = None  # Track font commands that should be applied

    lines = content.split('\n')

    for line in lines:
        stripped = line.strip()

        # Detect title
        title_match = re.match(r'^%?\s*\\title\s+(.+)$', line)
        if title_match:
            # Save previous slide
            if current_slide:
                if content_buffer:
                    current_slide['content'].extend(content_buffer)
                    content_buffer = []
                slides.append(current_slide)
            # Start new slide
            title = title_match.group(1).strip()
            current_slide = {
                'title': title,
                'content': [],
                'notes': [],
                'media': ''
            }
            in_content = False
            in_notes = False
            itemize_stack = []
            pending_font_cmd = None
            continue

        if current_slide is None:
            continue

        # Detect Content block
        if re.match(r'^%?\s*\\begin{Content}\s*$', stripped):
            in_content = True
            in_notes = False
            content_buffer = []
            itemize_stack = []
            pending_font_cmd = None
            continue
        elif re.match(r'^%?\s*\\end{Content}\s*$', stripped):
            in_content = False
            # Close any open itemize environments
            while itemize_stack:
                content_buffer.append("\\end{itemize}")
                itemize_stack.pop()
            if content_buffer:
                current_slide['content'].extend(content_buffer)
                content_buffer = []
            continue

        # Detect Notes block
        if re.match(r'^%?\s*\\begin{Notes}\s*$', stripped):
            in_notes = True
            in_content = False
            continue
        elif re.match(r'^%?\s*\\end{Notes}\s*$', stripped):
            in_notes = False
            continue

        # Process content lines
        if in_content:
            # Skip empty \None lines
            if stripped == "\\None" or stripped.startswith("\\None"):
                if not current_slide['media']:
                    current_slide['media'] = ""
                continue

            # Check if this is a media directive
            if stripped.startswith(('\\file', '\\play')):
                current_slide['media'] = stripped
                continue

            # ========== FIX: Handle itemize environments properly ==========
            # Track font size commands
            font_commands = ['\\tiny', '\\scriptsize', '\\footnotesize', '\\small',
                           '\\normalsize', '\\large', '\\Large', '\\LARGE', '\\huge', '\\Huge']

            is_font_cmd = False
            for font_cmd in font_commands:
                if stripped.startswith(font_cmd):
                    # Store font command to apply to next item
                    pending_font_cmd = stripped
                    is_font_cmd = True
                    break
            if is_font_cmd:
                continue

            # Handle itemize environment start
            if '\\begin{itemize}' in stripped:
                itemize_stack.append('itemize')
                content_buffer.append(stripped)
                # If we have a pending font command, add it AFTER \begin{itemize}
                if pending_font_cmd:
                    content_buffer.append(pending_font_cmd)
                    pending_font_cmd = None
                continue

            # Handle itemize environment end
            if '\\end{itemize}' in stripped:
                if itemize_stack and itemize_stack[-1] == 'itemize':
                    itemize_stack.pop()
                content_buffer.append(stripped)
                continue

            # Handle enumerate environment start
            if '\\begin{enumerate}' in stripped:
                itemize_stack.append('enumerate')
                content_buffer.append(stripped)
                if pending_font_cmd:
                    content_buffer.append(pending_font_cmd)
                    pending_font_cmd = None
                continue

            # Handle enumerate environment end
            if '\\end{enumerate}' in stripped:
                if itemize_stack and itemize_stack[-1] == 'enumerate':
                    itemize_stack.pop()
                content_buffer.append(stripped)
                continue

            # Handle bullet points (lines starting with - or •)
            if stripped.startswith('-') or stripped.startswith('•'):
                bullet_content = re.sub(r'^[-•]\s*', '', stripped)
                # If we're not in an itemize environment, we shouldn't be here
                # But if we are, add the \item
                if itemize_stack:
                    # If we have a pending font command, add it before the item
                    if pending_font_cmd:
                        content_buffer.append(pending_font_cmd)
                        pending_font_cmd = None
                    content_buffer.append(f"\\item {bullet_content}")
                else:
                    # Not in itemize - this shouldn't happen with proper formatting
                    # But just in case, wrap it
                    content_buffer.append("\\begin{itemize}")
                    itemize_stack.append('itemize')
                    if pending_font_cmd:
                        content_buffer.append(pending_font_cmd)
                        pending_font_cmd = None
                    content_buffer.append(f"\\item {bullet_content}")
                continue

            # Handle standalone \item commands
            if stripped.startswith('\\item'):
                if pending_font_cmd:
                    content_buffer.append(pending_font_cmd)
                    pending_font_cmd = None
                content_buffer.append(stripped)
                continue

            # Handle block environments
            if '\\begin{block}' in stripped or '\\begin{alertblock}' in stripped or '\\begin{exampleblock}' in stripped:
                # Close any open itemize before starting a block
                while itemize_stack:
                    content_buffer.append("\\end{itemize}")
                    itemize_stack.pop()
                content_buffer.append(stripped)
                continue

            if '\\end{block}' in stripped or '\\end{alertblock}' in stripped or '\\end{exampleblock}' in stripped:
                content_buffer.append(stripped)
                continue

            # Handle columns and column commands
            if '\\begin{columns}' in stripped or '\\end{columns}' in stripped:
                # Close any open itemize before columns
                while itemize_stack:
                    content_buffer.append("\\end{itemize}")
                    itemize_stack.pop()
                content_buffer.append(stripped)
                continue

            if stripped.startswith('\\column'):
                # Close any open itemize before a new column
                while itemize_stack:
                    content_buffer.append("\\end{itemize}")
                    itemize_stack.pop()
                content_buffer.append(stripped)
                continue

            # Handle \hline commands (tables)
            if stripped == '\\hline':
                content_buffer.append(stripped)
                continue

            # Handle \centering
            if stripped == '\\centering':
                content_buffer.append(stripped)
                continue

            # Handle \vspace commands
            if stripped.startswith('\\vspace'):
                content_buffer.append(stripped)
                continue

            # Handle other LaTeX commands that should pass through
            if stripped.startswith('\\'):
                content_buffer.append(stripped)
                continue

            # Regular text - pass through
            if stripped:
                content_buffer.append(stripped)

        # Process notes lines
        if in_notes:
            if stripped and not stripped.startswith('%'):
                # Remove bullet markers if present
                note_text = stripped
                if note_text.startswith('•') or note_text.startswith('-'):
                    note_text = re.sub(r'^[-•]\s*', '', note_text)
                # Remove \item if present
                if note_text.startswith('\\item'):
                    note_text = note_text[5:].strip()
                current_slide['notes'].append(note_text)

    # Save last slide
    if current_slide:
        # Close any open itemize environments
        while itemize_stack:
            content_buffer.append("\\end{itemize}")
            itemize_stack.pop()
        if content_buffer:
            current_slide['content'].extend(content_buffer)
            content_buffer = []
        slides.append(current_slide)

    return slides


def _get_preamble(content: str) -> str:  # Remove self parameter
    """Extract or generate preamble"""
    import re  # Add import inside function

    # Try to find existing preamble
    doc_match = re.search(r'(.*?)\\begin{document}', content, re.DOTALL)
    if doc_match:
        preamble = doc_match.group(1).strip()
        # Remove any \title, \author, \date commands (they'll be in slides)
        preamble = re.sub(r'\\title\{[^}]*\}', '', preamble)
        preamble = re.sub(r'\\author\{[^}]*\}', '', preamble)
        preamble = re.sub(r'\\date\{[^}]*\}', '', preamble)
        return preamble

    # Generate default preamble with all needed colors
    return r"""\documentclass[aspectratio=169]{beamer}
\usepackage{graphicx}
\usepackage{multimedia}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{pgfplots}
\usepackage{booktabs}
\usepackage{array}
\usepackage{hyperref}
\usepackage{textcomp}
\usepackage{amsmath}
\usepackage{amssymb}

\usetheme{Madrid}
\usecolortheme{default}

% Color definitions
\definecolor{myred}{RGB}{255,50,50}
\definecolor{myblue}{RGB}{0,130,255}
\definecolor{mygreen}{RGB}{0,200,100}
\definecolor{myyellow}{RGB}{255,210,0}
\definecolor{myorange}{RGB}{255,130,0}
\definecolor{mypurple}{RGB}{147,112,219}
\definecolor{mypink}{RGB}{255,105,180}
\definecolor{myteal}{RGB}{0,128,128}
\definecolor{mygray}{RGB}{128,128,128}
\definecolor{mybrown}{RGB}{139,69,19}
\definecolor{mycyan}{RGB}{0,255,255}
\definecolor{gold}{RGB}{212,175,55}
\definecolor{primary}{RGB}{0,90,156}
\definecolor{primarylight}{RGB}{230,242,255}
\definecolor{secondary}{RGB}{0,162,184}
\definecolor{secondarylight}{RGB}{220,245,250}
\definecolor{accent}{RGB}{239,127,56}
\definecolor{accentlight}{RGB}{255,240,230}
\definecolor{forest}{RGB}{34,139,34}
\definecolor{forestlight}{RGB}{220,245,220}
\definecolor{teal}{RGB}{0,128,128}
\definecolor{teallight}{RGB}{220,245,245}
\definecolor{greenbiodiv}{RGB}{46,139,87}
\definecolor{blueai}{RGB}{70,130,180}
\definecolor{redwarning}{RGB}{200,50,50}
\definecolor{redlight}{RGB}{255,230,230}

\setbeamertemplate{navigation symbols}{}
\setbeamertemplate{blocks}[rounded][shadow=true]
\setbeamersize{text margin left=5pt,text margin right=5pt}

% Notes support
\usepackage{pgfpages}
\setbeameroption{show notes on second screen=right}
\setbeamertemplate{note page}{\pagecolor{yellow!5}\insertnote}

% TikZ libraries
\usetikzlibrary{positioning, shapes, arrows.meta, calc, backgrounds, fit, shapes.geometric}
\pgfplotsset{compat=1.18}
"""


def _generate_latex_frame(slide: dict) -> str:
    """Generate a proper LaTeX frame from a slide dictionary"""
    import re

    # generate_content_items is already defined in this module
    # No import needed - just use it directly

    title = slide.get('title', 'Untitled')
    media = slide.get('media', '')
    content = slide.get('content', [])
    notes = slide.get('notes', [])

    # Clean title for LaTeX - inline the cleaning function
    def clean_title_for_latex(title_text):
        """Clean title for LaTeX - remove problematic characters"""
        if not title_text:
            return "Untitled"

        # Remove excessive braces
        title_text = title_text.replace('{{{', '{').replace('}}}', '}')
        title_text = title_text.replace('{{', '{').replace('}}', '}')

        # Remove any LaTeX formatting commands that might cause issues
        title_text = re.sub(r'\\[a-zA-Z]+\{', '', title_text)
        title_text = re.sub(r'[{}]', '', title_text)

        # Escape special characters
        title_text = title_text.replace('&', '\\&')
        title_text = title_text.replace('%', '\\%')
        title_text = title_text.replace('$', '\\$')
        title_text = title_text.replace('#', '\\#')
        title_text = title_text.replace('_', '\\_')

        return title_text.strip() or "Untitled"

    clean_title = clean_title_for_latex(title)

    frame_lines = []
    frame_lines.append(f"\\begin{{frame}}{{{clean_title}}}")
    frame_lines.append(f"\\frametitle{{{clean_title}}}")
    frame_lines.append("")

    # Add media if present
    if media:
        if media.startswith('\\file'):
            file_path = media.replace('\\file', '').strip()
            frame_lines.append("\\begin{center}")
            frame_lines.append(f"    \\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{file_path}}}")
            frame_lines.append("\\end{center}")
        elif media.startswith('\\play'):
            play_content = media.replace('\\play', '').strip()
            if play_content.startswith('\\file'):
                file_path = play_content.replace('\\file', '').strip()
                frame_lines.append("\\begin{center}")
                movie_line = f"    \\movie[externalviewer]{{\\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{file_path}}}}}{{{file_path}}}"
                frame_lines.append(movie_line)
                frame_lines.append("\\end{center}")
            else:
                # URL-based play
                frame_lines.append(f"    \\href{{{play_content}}}{{\\textcolor{{blue}}{{\\underline{{Play Video}}}}}}")

    # Add content - use the library's generate_content_items function
    if content:
        # Use the library's function for proper content formatting
        # This handles itemize, enumerate, bullet points, etc.
        content_str = generate_content_items(content)
        if content_str:
            frame_lines.append(content_str)
        else:
            # Fallback: just join content as-is
            frame_lines.append('\n'.join(content))

    # Add notes - properly formatted with itemize
    if notes:
        frame_lines.append("")
        frame_lines.append("\\note{")
        # Check if notes already contain itemize or bullet points
        has_bullets = any(n.strip().startswith(('•', '-')) for n in notes)
        if has_bullets:
            frame_lines.append("\\begin{itemize}")
            for note in notes:
                note_text = note.strip()
                if note_text:
                    # Remove bullet markers if present
                    note_text = re.sub(r'^[-•]\s*', '', note_text)
                    frame_lines.append(f"    \\item {note_text}")
            frame_lines.append("\\end{itemize}")
        else:
            # Simple notes without bullets
            for note in notes:
                note_text = note.strip()
                if note_text:
                    frame_lines.append(f"    \\item {note_text}")
        frame_lines.append("}")

    frame_lines.append("\\end{frame}")

    return '\n'.join(frame_lines)

def extract_preamble_colors(tex_content: str) -> dict:
    """
    Extract ALL color definitions from TeX content including common color packages.
    """
    import re

    colors = {}

    # Standard color definitions
    definecolor_pattern = r'\\definecolor\{([^}]+)\}\{([^}]+)\}\{([^}]+)\}'
    for name, model, value in re.findall(definecolor_pattern, tex_content):
        colors[name] = {'model': model, 'value': value}

    # Colorlet definitions
    colorlet_pattern = r'\\colorlet\{([^}]+)\}\{([^}]+)\}'
    for name, source in re.findall(colorlet_pattern, tex_content):
        colors[name] = {'model': 'colorlet', 'value': source}

    # Xcolor named colors (if xcolor package is used)
    if '\\usepackage{xcolor}' in tex_content or '\\usepackage[usenames]{xcolor}' in tex_content:
        # Common xcolor named colors
        common_colors = {
            'red': 'RGB{255,0,0}',
            'green': 'RGB{0,255,0}',
            'blue': 'RGB{0,0,255}',
            'yellow': 'RGB{255,255,0}',
            'cyan': 'RGB{0,255,255}',
            'magenta': 'RGB{255,0,255}',
            'orange': 'RGB{255,165,0}',
            'purple': 'RGB{128,0,128}',
            'brown': 'RGB{165,42,42}',
            'pink': 'RGB{255,192,203}',
            'gold': 'RGB{212,175,55}',
            'silver': 'RGB{192,192,192}',
        }
        for name, rgb in common_colors.items():
            if name not in colors:
                colors[name] = {'model': 'RGB', 'value': rgb}

    # Check for custom gold definition
    if 'gold' not in colors and ('gold' in tex_content or '\\textcolor{gold}' in tex_content):
        colors['gold'] = {'model': 'RGB', 'value': '212,175,55'}

    return colors

def _clean_title_for_latex(self, title: str) -> str:
    """Clean title for LaTeX - remove problematic characters"""
    if not title:
        return "Untitled"

    # Remove excessive braces
    title = title.replace('{{{', '{').replace('}}}', '}')
    title = title.replace('{{', '{').replace('}}', '}')

    # Escape special characters
    title = title.replace('&', '\\&')
    title = title.replace('%', '\\%')
    title = title.replace('$', '\\$')
    title = title.replace('#', '\\#')
    title = title.replace('_', '\\_')

    return title.strip() or "Untitled"

def _extract_preamble(content: str) -> str:
    """Extract the preamble from the content or generate default"""
    import re

    # Try to find existing preamble
    doc_match = re.search(r'(.*?)\\begin{document}', content, re.DOTALL)
    if doc_match:
        preamble = doc_match.group(1).strip()
        # Remove any \title, \author, \date commands from preamble (they'll be in slides)
        preamble = re.sub(r'\\title\{[^}]*\}', '', preamble)
        preamble = re.sub(r'\\author\{[^}]*\}', '', preamble)
        preamble = re.sub(r'\\date\{[^}]*\}', '', preamble)
        return preamble

    # Generate default preamble
    return r"""\documentclass[aspectratio=169]{beamer}
\usepackage{graphicx}
\usepackage{multimedia}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{pgfplots}
\usepackage{booktabs}
\usepackage{array}
\usepackage{hyperref}
\usepackage{textcomp}
\usepackage{amsmath}
\usepackage{amssymb}

\usetheme{Madrid}
\usecolortheme{default}

\definecolor{myred}{RGB}{255,50,50}
\definecolor{myblue}{RGB}{0,130,255}
\definecolor{mygreen}{RGB}{0,200,100}
\definecolor{myyellow}{RGB}{255,210,0}
\definecolor{myorange}{RGB}{255,130,0}
\definecolor{mypurple}{RGB}{147,112,219}
\definecolor{mypink}{RGB}{255,105,180}
\definecolor{myteal}{RGB}{0,128,128}
\definecolor{mygray}{RGB}{128,128,128}
\definecolor{mybrown}{RGB}{139,69,19}
\definecolor{mycyan}{RGB}{0,255,255}

\setbeamertemplate{navigation symbols}{}
\setbeamertemplate{blocks}[rounded][shadow=true]
\setbeamersize{text margin left=5pt,text margin right=5pt}

% Notes support
\usepackage{pgfpages}
\setbeameroption{show notes on second screen=right}
\setbeamertemplate{note page}{\pagecolor{yellow!5}\insertnote}
"""

def _generate_frame_from_slide(slide: dict) -> str:
    """Generate a proper LaTeX frame from a slide dictionary"""
    title = slide.get('title', 'Untitled')
    media = slide.get('media', '')
    content = slide.get('content', [])
    notes = slide.get('notes', [])

    frame_lines = []
    frame_lines.append(f"\\begin{{frame}}{{{title}}}")
    frame_lines.append(f"\\frametitle{{{title}}}")
    frame_lines.append("")

    # Add media if present
    if media:
        # Convert media directives to proper LaTeX
        if media.startswith('\\file'):
            file_path = media.replace('\\file', '').strip()
            # Use raw string or escape properly
            frame_lines.append("\\begin{center}")
            frame_lines.append(f"    \\includegraphics[width=0.7\\textwidth,keepaspectratio]{{{file_path}}}")
            frame_lines.append("\\end{center}")
        elif media.startswith('\\play'):
            # Handle playable media
            play_content = media.replace('\\play', '').strip()
            if play_content.startswith('\\file'):
                file_path = play_content.replace('\\file', '').strip()
                # Fixed: Use separate lines or properly escape the f-string
                frame_lines.append("\\begin{center}")
                movie_line = "    \\movie[externalviewer]{\\includegraphics[width=0.7\\textwidth,keepaspectratio]{%s}}{%s}" % (file_path, file_path)
                frame_lines.append(movie_line)
                frame_lines.append("\\end{center}")
            else:
                # Handle URL-based play
                frame_lines.append(f"    \\href{{{play_content}}}{{\\textcolor{{blue}}{{\\underline{{Play Video}}}}}}")

    # Add content
    if content:
        # Check if content is already in a columns environment
        content_str = '\n'.join(content)
        if '\\begin{columns}' in content_str:
            # Preserve columns as-is
            frame_lines.append(content_str)
        else:
            # Process content lines
            in_itemize = False
            for line in content:
                stripped = line.strip()
                if not stripped:
                    continue

                # Check for LaTeX environments
                if stripped.startswith('\\begin{'):
                    if in_itemize:
                        frame_lines.append("\\end{itemize}")
                        in_itemize = False
                    frame_lines.append(stripped)
                    continue
                elif stripped.startswith('\\end{'):
                    frame_lines.append(stripped)
                    if 'itemize' in stripped or 'enumerate' in stripped:
                        in_itemize = False
                    continue

                # Handle bullet points
                if stripped.startswith('-') or stripped.startswith('•'):
                    if not in_itemize:
                        frame_lines.append("\\begin{itemize}")
                        in_itemize = True
                    bullet_text = stripped[1:].strip()
                    frame_lines.append(f"    \\item {bullet_text}")
                else:
                    if in_itemize:
                        frame_lines.append("\\end{itemize}")
                        in_itemize = False
                    frame_lines.append(stripped)

            if in_itemize:
                frame_lines.append("\\end{itemize}")

    # Add notes
    if notes:
        frame_lines.append("")
        frame_lines.append("\\note{")
        frame_lines.append("\\begin{itemize}")
        for note in notes:
            note_text = note.strip()
            if note_text.startswith('•'):
                note_text = note_text[1:].strip()
            frame_lines.append(f"    \\item {note_text}")
        frame_lines.append("\\end{itemize}")
        frame_lines.append("}")

    frame_lines.append("\\end{frame}")

    return '\n'.join(frame_lines)

def should_process_frame(title, content, media, notes):
    """
    Determine if a frame should be processed based on its components.
    A frame should be processed if it has any meaningful content.
    """
    # Check if title is not empty
    has_title = title is not None and title.strip() != ''

    # Check if content has meaningful lines
    has_content = False
    if content:
        for line in content:
            if line and line.strip() and not line.strip().startswith('%'):
                has_content = True
                break

    # Check if media is present
    has_media = media is not None and media != '' and media != '\\None'

    # Check if notes have meaningful content
    has_notes = False
    if notes:
        for note in notes:
            if note and note.strip() and not note.strip().startswith('%'):
                has_notes = True
                break

    return has_title or has_content or has_media or has_notes


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
