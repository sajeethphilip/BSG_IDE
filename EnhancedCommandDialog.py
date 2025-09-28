import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from LatexHelp import LatexHelpLibrary, LatexSymbolsDatabase, LatexCommandHelper

class EnhancedCommandIndexDialog(ctk.CTkToplevel):
    """Enhanced LaTeX command index with comprehensive BSG/Beamer command listing and interactive help"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("BSG-IDE Enhanced Command Reference")
        self.geometry("1400x1000")

        # Initialize LaTeX help system
        self.latex_lib = LatexHelpLibrary()
        self.symbols_db = LatexSymbolsDatabase()
        self.command_helper = LatexCommandHelper()

        # Make it a floating window
        self.transient(parent)
        self.resizable(True, True)
        self.focus_set()
        self.attributes('-topmost', True)

        # Enhanced command database
        self.commands = self.build_enhanced_command_database()
        self.filtered_commands = self.commands.copy()
        self.selected_command = None

        # Add symbols to the database
        self.integrate_symbols_into_database()

        # Display options
        self.display_options = {
            'show_syntax': True,
            'show_examples': True,
            'show_symbols': True,
            'category_filter': "All",
            'view_mode': "categorized",
            'content_type': "all"
        }

        # Performance optimization
        self.resize_timeout_id = None
        self.last_resize_time = 0
        self.min_resize_interval = 500

        self.create_enhanced_widgets()
        self.center_dialog()

        # Bind events
        self.bind('<Escape>', lambda e: self.destroy())
        self.bind('<FocusIn>', lambda e: self.attributes('-topmost', True))
        self.bind('<Configure>', self.on_window_resize_throttled)

        # Initial display
        self.refresh_display()

    def integrate_symbols_into_database(self):
        """Integrate LaTeX symbols into the command database"""
        symbols_category = "Mathematical Symbols"
        self.commands[symbols_category] = []

        # Add symbols by category
        symbol_categories = {
            'Greek Letters': 'greek',
            'Mathematical Operators': 'operators',
            'Relations': 'relations',
            'Arrows': 'arrows',
            'Functions': 'functions',
            'Delimiters': 'delimiters',
            'Miscellaneous': 'misc',
            'Accents': 'accents'
        }

        for category_name, category_key in symbol_categories.items():
            symbols = self.symbols_db.get_symbols_by_category(category_key)
            for symbol_cmd in symbols:
                symbol_info = self.symbols_db.symbols[symbol_cmd]
                symbol_entry = {
                    'command': symbol_cmd,
                    'syntax': symbol_info.get('syntax', symbol_cmd),
                    'description': symbol_info.get('description', 'LaTeX symbol'),
                    'example': self._generate_symbol_example(symbol_cmd, symbol_info),
                    'category': 'symbols',
                    'display_options': ['static'],
                    'auto_complete': symbol_info.get('syntax', symbol_cmd),
                    'usage': f'Mathematical symbol - {category_name}',
                    'symbol': symbol_info.get('symbol', ''),
                    'is_symbol': True
                }
                self.commands[symbols_category].append(symbol_entry)

    def _generate_symbol_example(self, command, info):
        """Generate example for symbols"""
        if 'syntax' in info:
            return info['syntax']
        elif 'symbol' in info:
            return f"{command} → {info['symbol']}"
        else:
            return f"Use: {command}"

    def build_enhanced_command_database(self):
        """Build comprehensive command database with BSG and Beamer specific syntax"""
        return {
            'BSG Document Structure': [
                {
                    'command': '\\title',
                    'syntax': '\\title{Presentation Title}',
                    'description': 'Sets the main presentation title - BSG Enhanced',
                    'example': '\\title{Artificial Intelligence Research}',
                    'category': 'document',
                    'display_options': ['static'],
                    'auto_complete': '\\title{$1}',
                    'usage': 'Required for all BSG presentations',
                    'is_symbol': False
                },
                {
                    'command': '\\author',
                    'syntax': '\\author{Author Name}',
                    'description': 'Sets the author name with BSG affiliation',
                    'example': '\\author{Dr. John Smith\\\\BSG Research Team}',
                    'category': 'document',
                    'display_options': ['static'],
                    'auto_complete': '\\author{$1}',
                    'usage': 'Required for all BSG presentations',
                    'is_symbol': False
                },
                {
                    'command': '\\institute',
                    'syntax': '\\institute{Institution Name}',
                    'description': 'Sets the institution name - BSG Enhanced',
                    'example': '\\institute{BSG Research Institute\\\\University of Technology}',
                    'category': 'document',
                    'display_options': ['static'],
                    'auto_complete': '\\institute{$1}',
                    'usage': 'Recommended for academic presentations',
                    'is_symbol': False
                },
                {
                    'command': '\\date',
                    'syntax': '\\date{date}',
                    'description': 'Sets the presentation date',
                    'example': '\\date{\\today}',
                    'category': 'document',
                    'display_options': ['static'],
                    'auto_complete': '\\date{$1}',
                    'usage': 'Optional, defaults to \\today',
                    'is_symbol': False
                },
                {
                    'command': '\\bsglogo',
                    'syntax': '\\bsglogo[scale]{filename}',
                    'description': 'Inserts BSG logo with scaling option',
                    'example': '\\bsglogo[0.8]{media_files/bsg_logo.png}',
                    'category': 'document',
                    'display_options': ['static'],
                    'auto_complete': '\\bsglogo[$1]{$2}',
                    'usage': 'BSG specific command for branding',
                    'is_symbol': False
                }
            ],

            'BSG Slide Content & Media': [
                {
                    'command': '\\frametitle',
                    'syntax': '\\frametitle{Slide Title}',
                    'description': 'Sets the frame/slide title - BSG Styled',
                    'example': '\\frametitle{BSG Research Methodology}',
                    'category': 'content',
                    'display_options': ['static'],
                    'auto_complete': '\\frametitle{$1}',
                    'usage': 'Per slide, after \\begin{frame}',
                    'is_symbol': False
                },
                {
                    'command': '\\file',
                    'syntax': '\\file{media_files/filename.ext}',
                    'description': 'Includes an image or media file - BSG Enhanced',
                    'example': '\\file{media_files/research_diagram.png}',
                    'category': 'media',
                    'display_options': ['static'],
                    'auto_complete': '\\file{media_files/$1}',
                    'usage': 'BSG media inclusion with automatic path',
                    'is_symbol': False
                },
                {
                    'command': '\\play',
                    'syntax': '\\play{media_files/video.ext}',
                    'description': 'Embeds a playable video - BSG Enhanced',
                    'example': '\\play{media_files/demo.mp4}',
                    'category': 'media',
                    'display_options': ['static'],
                    'auto_complete': '\\play{media_files/$1}',
                    'usage': 'BSG video embedding with auto-controls',
                    'is_symbol': False
                },
                {
                    'command': '\\movie',
                    'syntax': '\\movie[options]{poster}{video}',
                    'description': 'Embeds multimedia with poster - BSG Enhanced',
                    'example': '\\movie[autostart]{\\includegraphics{poster}}{video.mp4}',
                    'category': 'media',
                    'display_options': ['static'],
                    'auto_complete': '\\movie[$1]{$2}{$3}',
                    'usage': 'Advanced media embedding',
                    'is_symbol': False
                },
                {
                    'command': '\\bsgcode',
                    'syntax': '\\bsgcode[language]{code}',
                    'description': 'BSG enhanced code display with syntax highlighting',
                    'example': '\\bsgcode[python]{def hello():\\\\n    print("Hello BSG")}',
                    'category': 'content',
                    'display_options': ['static'],
                    'auto_complete': '\\bsgcode[$1]{$2}',
                    'usage': 'BSG specific code presentation',
                    'is_symbol': False
                },
                {
                    'command': '\\includegraphics',
                    'syntax': '\\includegraphics[options]{filename}',
                    'description': 'Includes an image file - BSG Enhanced',
                    'example': '\\includegraphics[width=0.8\\textwidth]{images/diagram.png}',
                    'category': 'media',
                    'display_options': ['static'],
                    'auto_complete': '\\includegraphics[$1]{$2}',
                    'usage': 'Standard image inclusion with BSG paths',
                    'is_symbol': False
                }
            ],

            'Beamer Text Formatting': [
                {
                    'command': '\\textcolor',
                    'syntax': '\\textcolor{bsg-blue}{text} or \\textcolor[RGB]{0,51,102}{text}',
                    'description': 'Changes text color with BSG color scheme',
                    'example': '\\textcolor{bsg-blue}{BSG Important Text}',
                    'category': 'formatting',
                    'display_options': ['static'],
                    'auto_complete': '\\textcolor{$1}{$2}',
                    'usage': 'Use BSG colors: bsg-blue, bsg-green, bsg-orange',
                    'is_symbol': False
                },
                {
                    'command': '\\textbf',
                    'syntax': '\\textbf{Bold Text}',
                    'description': 'Makes text bold - Beamer enhanced',
                    'example': 'This is \\textbf{important} BSG research',
                    'category': 'formatting',
                    'display_options': ['static'],
                    'auto_complete': '\\textbf{$1}',
                    'usage': 'Inline emphasis in Beamer',
                    'is_symbol': False
                },
                {
                    'command': '\\textit',
                    'syntax': '\\textit{Italic Text}',
                    'description': 'Makes text italic - Beamer enhanced',
                    'example': 'This is \\textit{emphasized} BSG finding',
                    'category': 'formatting',
                    'display_options': ['static'],
                    'auto_complete': '\\textit{$1}',
                    'usage': 'Inline emphasis in Beamer',
                    'is_symbol': False
                },
                {
                    'command': '\\alert',
                    'syntax': '\\alert{Text}',
                    'description': 'Highlights text with BSG alert color',
                    'example': 'Remember: \\alert{BSG key finding}',
                    'category': 'formatting',
                    'display_options': ['dynamic'],
                    'auto_complete': '\\alert{$1}',
                    'usage': 'Highlight important BSG content',
                    'is_symbol': False
                },
                {
                    'command': '\\bsghighlight',
                    'syntax': '\\bsghighlight{text}',
                    'description': 'BSG specific highlight with custom color',
                    'example': '\\bsghighlight{Innovative BSG Approach}',
                    'category': 'formatting',
                    'display_options': ['static'],
                    'auto_complete': '\\bsghighlight{$1}',
                    'usage': 'BSG branded highlighting',
                    'is_symbol': False
                },
                {
                    'command': '\\emph',
                    'syntax': '\\emph{emphasized text}',
                    'description': 'Emphasizes text - Beamer enhanced',
                    'example': 'This is \\emph{very important} for BSG',
                    'category': 'formatting',
                    'display_options': ['static'],
                    'auto_complete': '\\emph{$1}',
                    'usage': 'Text emphasis',
                    'is_symbol': False
                }
            ],

            'Beamer Lists & Environments': [
                {
                    'command': '\\begin{itemize}',
                    'syntax': '\\begin{itemize}\\item First\\item Second\\end{itemize}',
                    'description': 'Creates a bulleted list - Beamer enhanced',
                    'example': '\\begin{itemize}\\item BSG Point one\\item BSG Point two\\end{itemize}',
                    'category': 'lists',
                    'display_options': ['static', 'dynamic'],
                    'auto_complete': '\\begin{itemize}\\item $1\\item $2\\end{itemize}',
                    'usage': 'Unordered lists in Beamer',
                    'is_symbol': False
                },
                {
                    'command': '\\begin{enumerate}',
                    'syntax': '\\begin{enumerate}\\item First\\item Second\\end{enumerate}',
                    'description': 'Creates a numbered list - Beamer enhanced',
                    'example': '\\begin{enumerate}\\item BSG Step one\\item BSG Step two\\end{enumerate}',
                    'category': 'lists',
                    'display_options': ['static', 'dynamic'],
                    'auto_complete': '\\begin{enumerate}\\item $1\\item $2\\end{enumerate}',
                    'usage': 'Ordered lists in Beamer',
                    'is_symbol': False
                },
                {
                    'command': '\\item',
                    'syntax': '\\item Item text',
                    'description': 'Creates a list item - Beamer enhanced',
                    'example': '\\item This is a BSG list item',
                    'category': 'lists',
                    'display_options': ['static', 'dynamic'],
                    'auto_complete': '\\item $1',
                    'usage': 'Within itemize or enumerate',
                    'is_symbol': False
                },
                {
                    'command': '\\begin{columns}',
                    'syntax': '\\begin{columns}\\column{0.5\\textwidth}Left\\column{0.5\\textwidth}Right\\end{columns}',
                    'description': 'Creates multi-column layout - Beamer enhanced',
                    'example': '\\begin{columns}\\column{0.4\\textwidth}BSG Left\\column{0.6\\textwidth}BSG Right\\end{columns}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\begin{columns}\\column{$1\\\\textwidth}$2\\end{columns}',
                    'usage': 'Multi-column slides in Beamer',
                    'is_symbol': False
                },
                {
                    'command': '\\begin{bsgblock}',
                    'syntax': '\\begin{bsgblock}{Title}Content\\end{bsgblock}',
                    'description': 'BSG specific block environment',
                    'example': '\\begin{bsgblock}{Research Objective}Study AI applications\\end{bsgblock}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\begin{bsgblock}{$1}$2\\end{bsgblock}',
                    'usage': 'BSG branded content blocks',
                    'is_symbol': False
                },
                {
                    'command': '\\begin{frame}',
                    'syntax': '\\begin{frame}{Title}Content\\end{frame}',
                    'description': 'Starts a new slide frame - Beamer',
                    'example': '\\begin{frame}{Introduction}Welcome to BSG Research\\end{frame}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\begin{frame}{$1}$2\\end{frame}',
                    'usage': 'Creates new presentation slide',
                    'is_symbol': False
                }
            ],

            'Beamer Display Effects & Animations': [
                {
                    'command': '\\pause',
                    'syntax': '\\pause',
                    'description': 'Pauses between overlay items - Beamer',
                    'example': 'First BSG point\\pause\nSecond BSG point',
                    'category': 'animation',
                    'display_options': ['dynamic', 'overlay'],
                    'auto_complete': '\\pause',
                    'usage': 'Between content items in Beamer',
                    'is_symbol': False
                },
                {
                    'command': '\\only',
                    'syntax': '\\only<overlay>{content}',
                    'description': 'Shows content only on specified overlays - Beamer',
                    'example': '\\only<2>{This appears only on BSG slide 2}',
                    'category': 'animation',
                    'display_options': ['dynamic', 'overlay'],
                    'auto_complete': '\\only<$1>{$2}',
                    'usage': 'Conditional display in Beamer',
                    'is_symbol': False
                },
                {
                    'command': '\\uncover',
                    'syntax': '\\uncover<overlay>{content}',
                    'description': 'Uncovers content gradually - Beamer',
                    'example': '\\uncover<2->{Gradually revealed BSG content}',
                    'category': 'animation',
                    'display_options': ['dynamic', 'overlay'],
                    'auto_complete': '\\uncover<$1>{$2}',
                    'usage': 'Progressive disclosure in Beamer',
                    'is_symbol': False
                },
                {
                    'command': '\\alt',
                    'syntax': '\\alt<overlay>{alternative1}{alternative2}',
                    'description': 'Shows alternative content on different slides - Beamer',
                    'example': '\\alt<2>{BSG Version A}{BSG Version B}',
                    'category': 'animation',
                    'display_options': ['dynamic', 'overlay'],
                    'auto_complete': '\\alt<$1>{$2}{$3}',
                    'usage': 'Alternative content versions in Beamer',
                    'is_symbol': False
                },
                {
                    'command': '\\transdissolve',
                    'syntax': '\\transdissolve[duration=2]',
                    'description': 'Creates smooth dissolve transition between slides',
                    'example': '\\transdissolve[duration=1.5]',
                    'category': 'animation',
                    'display_options': ['dynamic', 'transition'],
                    'auto_complete': '\\transdissolve[duration=$1]',
                    'usage': 'Between frames',
                    'is_symbol': False
                },
                {
                    'command': '\\transwipe',
                    'syntax': '\\transwipe[direction=90]',
                    'description': 'Creates wipe transition in specified direction',
                    'example': '\\transwipe[direction=45]',
                    'category': 'animation',
                    'display_options': ['dynamic', 'transition'],
                    'auto_complete': '\\transwipe[direction=$1]',
                    'usage': 'Between frames',
                    'is_symbol': False
                }
            ],

            'Beamer Item-by-Item Display': [
                {
                    'command': '\\begin{itemize}[<+->]',
                    'syntax': '\\begin{itemize}[<+->]\\item First\\item Second\\end{itemize}',
                    'description': 'Creates bulleted list with automatic item-by-item display - Beamer',
                    'example': '\\begin{itemize}[<+->]\n\\item BSG First point\n\\item BSG Second point\n\\end{itemize}',
                    'category': 'sequential',
                    'display_options': ['dynamic', 'sequential'],
                    'auto_complete': '\\begin{itemize}[<+->]\n\\item $1\n\\item $2\n\\end{itemize}',
                    'usage': 'Automatic sequential display in Beamer',
                    'is_symbol': False
                },
                {
                    'command': '\\begin{enumerate}[<+->]',
                    'syntax': '\\begin{enumerate}[<+->]\\item First\\item Second\\end{enumerate}',
                    'description': 'Creates numbered list with automatic sequential display - Beamer',
                    'example': '\\begin{enumerate}[<+->]\n\\item BSG Step one\n\\item BSG Step two\n\\end{enumerate}',
                    'category': 'sequential',
                    'display_options': ['dynamic', 'sequential'],
                    'auto_complete': '\\begin{enumerate}[<+->]\n\\item $1\n\\item $2\n\\end{enumerate}',
                    'usage': 'Automatic sequential numbering in Beamer',
                    'is_symbol': False
                },
                {
                    'command': '\\begin{overprint}',
                    'syntax': '\\begin{overprint}\\onslide<1>Content A\\onslide<2>Content B\\end{overprint}',
                    'description': 'Creates overlapping content for different slides',
                    'example': '\\begin{overprint}\n\\onslide<1>First version\n\\onslide<2>Second version\n\\end{overprint}',
                    'category': 'animation',
                    'display_options': ['dynamic', 'overlay'],
                    'auto_complete': '\\begin{overprint}\n\\onslide<$1>$2\n\\onslide<$3>$4\n\\end{overprint}',
                    'usage': 'Overlapping content areas',
                    'is_symbol': False
                }
            ],

            'Presentation Features': [
                {
                    'command': '\\note',
                    'syntax': '\\note{Speaker notes}',
                    'description': 'Adds speaker notes (visible in presenter mode) - BSG Enhanced',
                    'example': '\\note{Remember to explain this BSG concept slowly}',
                    'category': 'presentation',
                    'display_options': ['static'],
                    'auto_complete': '\\note{$1}',
                    'usage': 'Speaker notes',
                    'is_symbol': False
                },
                {
                    'command': '\\href',
                    'syntax': '\\href{url}{link text}',
                    'description': 'Creates clickable hyperlink - BSG Enhanced',
                    'example': 'Visit \\href{https://bsg-research.com}{BSG Research Website}',
                    'category': 'interactive',
                    'display_options': ['static'],
                    'auto_complete': '\\href{$1}{$2}',
                    'usage': 'Hyperlinks',
                    'is_symbol': False
                }
            ],

            'Mathematical Symbols': [
                # This will be populated by integrate_symbols_into_database
            ]
        }

    def create_enhanced_widgets(self):
        """Create enhanced interface with comprehensive listing and interactive features"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header with improved styling
        header_frame = ctk.CTkFrame(main_frame, fg_color="#2B3A42")
        header_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(header_frame, text="BSG-IDE Complete Command & Symbol Reference",
                    font=("Arial", 20, "bold"), text_color="#4ECDC4").pack(pady=8)

        ctk.CTkLabel(header_frame,
                    text="Complete listing of all BSG and Beamer commands with interactive help and testing",
                    font=("Arial", 12), text_color="#BDC3C7").pack(pady=4)

        # Enhanced Control Panel
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", padx=5, pady=10)

        # Left side: Search and quick filters
        left_controls = ctk.CTkFrame(control_frame, fg_color="transparent")
        left_controls.pack(side="left", fill="x", expand=True)

        # Enhanced Search with symbols
        search_frame = ctk.CTkFrame(left_controls, fg_color="transparent")
        search_frame.pack(side="top", fill="x", pady=2)

        ctk.CTkLabel(search_frame, text="Search:", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=300,
                                  placeholder_text="Search BSG commands, symbols, or descriptions...")
        search_entry.pack(side="left", padx=5)
        search_entry.bind('<KeyRelease>', self.filter_commands)

        # Content type filter
        content_frame = ctk.CTkFrame(left_controls, fg_color="transparent")
        content_frame.pack(side="top", fill="x", pady=5)

        ctk.CTkLabel(content_frame, text="Content Type:", font=("Arial", 11, "bold")).pack(side="left", padx=5)

        self.content_var = tk.StringVar(value="all")
        ctk.CTkRadioButton(content_frame, text="All", variable=self.content_var,
                          value="all", command=self.refresh_display).pack(side="left", padx=2)
        ctk.CTkRadioButton(content_frame, text="Commands Only", variable=self.content_var,
                          value="commands_only", command=self.refresh_display).pack(side="left", padx=2)
        ctk.CTkRadioButton(content_frame, text="Symbols Only", variable=self.content_var,
                          value="symbols_only", command=self.refresh_display).pack(side="left", padx=2)

        # Quick category filters - organized in three rows
        category_frame = ctk.CTkFrame(left_controls, fg_color="transparent")
        category_frame.pack(side="top", fill="x", pady=5)

        ctk.CTkLabel(category_frame, text="Quick Filters:", font=("Arial", 11, "bold")).pack(side="left", padx=5)

        # Create category buttons organized in three rows
        categories = ["All", "BSG Document Structure", "BSG Slide Content & Media", "Beamer Text Formatting",
                     "Beamer Lists & Environments", "Beamer Display Effects & Animations",
                     "Beamer Item-by-Item Display", "Presentation Features", "Mathematical Symbols"]
        self.category_buttons = {}

        # Create three rows for category buttons
        cat_row1 = ctk.CTkFrame(category_frame, fg_color="transparent")
        cat_row1.pack(side="top", fill="x", pady=1)

        cat_row2 = ctk.CTkFrame(category_frame, fg_color="transparent")
        cat_row2.pack(side="top", fill="x", pady=1)

        cat_row3 = ctk.CTkFrame(category_frame, fg_color="transparent")
        cat_row3.pack(side="top", fill="x", pady=1)

        # Distribute categories across three rows
        for i, category in enumerate(categories):
            if i < 3:
                row_frame = cat_row1
            elif i < 6:
                row_frame = cat_row2
            else:
                row_frame = cat_row3

            btn = ctk.CTkButton(
                row_frame,
                text=category,
                command=lambda c=category: self.filter_by_category(c),
                width=180,
                height=28,
                font=("Arial", 9),
                fg_color="#34495E",
                hover_color="#2C3E50"
            )
            btn.pack(side="left", padx=2, pady=1)
            self.category_buttons[category] = btn

        # Right side: Enhanced Display options
        right_controls = ctk.CTkFrame(control_frame, fg_color="transparent")
        right_controls.pack(side="right", padx=10)

        # View mode
        view_frame = ctk.CTkFrame(right_controls, fg_color="transparent")
        view_frame.pack(side="top", pady=2)

        ctk.CTkLabel(view_frame, text="View Mode:", font=("Arial", 11, "bold")).pack(side="left", padx=5)

        self.view_var = tk.StringVar(value="categorized")
        ctk.CTkRadioButton(view_frame, text="Categorized", variable=self.view_var,
                          value="categorized", command=self.refresh_display).pack(side="left", padx=2)
        ctk.CTkRadioButton(view_frame, text="Flat List", variable=self.view_var,
                          value="all", command=self.refresh_display).pack(side="left", padx=2)

        # Enhanced Display toggles
        toggle_frame = ctk.CTkFrame(right_controls, fg_color="transparent")
        toggle_frame.pack(side="top", pady=5)

        self.syntax_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(toggle_frame, text="Show Syntax", variable=self.syntax_var,
                       command=self.refresh_display).pack(side="top", padx=5, pady=2)

        self.examples_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(toggle_frame, text="Show Examples", variable=self.examples_var,
                       command=self.refresh_display).pack(side="top", padx=5, pady=2)

        self.symbols_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(toggle_frame, text="Show Symbols", variable=self.symbols_var,
                       command=self.refresh_display).pack(side="top", padx=5, pady=2)

        # Content Area with tabs for better organization
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create tab view for different content types
        self.tab_view = ctk.CTkTabview(content_frame)
        self.tab_view.pack(fill="both", expand=True)

        # Add tabs
        self.commands_tab = self.tab_view.add("Commands & Symbols")
        self.quick_ref_tab = self.tab_view.add("Quick Reference")
        self.interactive_tab = self.tab_view.add("Interactive Help")

        # Commands tab content
        self.setup_commands_tab()

        # Quick Reference tab
        self.setup_quick_reference_tab()

        # Interactive Help tab
        self.setup_interactive_help_tab()

        # Statistics and info panel
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", padx=5, pady=5)

        self.stats_label = ctk.CTkLabel(info_frame, text="", font=("Arial", 11))
        self.stats_label.pack(side="left", padx=10, pady=5)

        # Add quick tips
        tips_label = ctk.CTkLabel(info_frame,
                                 text="💡 Tip: Click on any command for detailed help | Double-click to insert",
                                 font=("Arial", 10), text_color="#95A5A6")
        tips_label.pack(side="right", padx=10, pady=5)

        # Enhanced Action buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=5, pady=10)

        ctk.CTkButton(button_frame, text="Insert Selected Command",
                     command=self.insert_selected, width=160,
                     fg_color="#27AE60", hover_color="#219A52").pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="Copy Example",
                     command=self.copy_example, width=120).pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="Show Detailed Help",
                     command=self.show_detailed_help, width=140).pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="Close",
                     command=self.destroy, fg_color="#E74C3C", hover_color="#C0392B").pack(side="right", padx=5)

    def setup_commands_tab(self):
        """Setup the main commands and symbols tab"""
        # Create scrollable content area for commands
        self.scrollable_frame = ctk.CTkScrollableFrame(self.commands_tab)
        self.scrollable_frame.pack(fill="both", expand=True)

    def setup_quick_reference_tab(self):
        """Setup the quick reference tab with common BSG patterns"""
        quick_ref_frame = ctk.CTkScrollableFrame(self.quick_ref_tab)
        quick_ref_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # BSG Common patterns section
        patterns = [
            ("BSG Basic Document Structure", "\\documentclass{beamer}\n\\usepackage{bsg}\n\\title{BSG Research}\n\\author{BSG Team}\n\\institute{BSG Institute}\n\\begin{document}\n\\begin{frame}\n\\frametitle{BSG Slide}\n\\bsglogo[0.8]{logo.png}\nContent\n\\end{frame}\n\\end{document}"),
            ("BSG Lists with Animation", "\\begin{itemize}[<+->]\n\\item \\bsghighlight{BSG First point}\n\\item \\bsghighlight{BSG Second point}\n\\item \\alert{BSG Key finding}\n\\end{itemize}"),
            ("BSG Mathematical Formula", "\\[\n\\sum_{i=1}^{n} \\alpha_i = \\frac{\\beta(\\gamma+1)}{2}\n\\]"),
            ("BSG Columns Layout", "\\begin{columns}\n\\column{0.4\\textwidth}\n\\begin{bsgblock}{Objective}\nResearch goals\n\\end{bsgblock}\n\\column{0.6\\textwidth}\n\\begin{itemize}\n\\item Point 1\n\\item Point 2\n\\end{itemize}\n\\end{columns}"),
            ("BSG Media Inclusion", "\\file{media_files/diagram.png}\n\\play{media_files/demo.mp4}"),
            ("BSG Hyperlink", "\\href{https://bsg-research.com}{BSG Website}"),
        ]

        for i, (title, code) in enumerate(patterns):
            pattern_frame = ctk.CTkFrame(quick_ref_frame)
            pattern_frame.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(pattern_frame, text=title, font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

            # Code display with copy functionality
            code_text = tk.Text(pattern_frame, height=4, font=("Courier", 10), wrap=tk.WORD,
                               bg='#2B2B2B', fg='#FFFFFF', insertbackground='white')
            code_text.pack(fill="x", padx=10, pady=5)
            code_text.insert("1.0", code)
            code_text.config(state="disabled")

            # Add copy button
            copy_btn = ctk.CTkButton(pattern_frame, text="Copy Pattern", width=100,
                                   command=lambda c=code: self.copy_to_clipboard(c))
            copy_btn.pack(anchor="e", padx=10, pady=5)

    def setup_interactive_help_tab(self):
        """Setup the interactive help tab with static button groups"""
        help_frame = ctk.CTkFrame(self.interactive_tab)
        help_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Live command tester
        tester_frame = ctk.CTkFrame(help_frame)
        tester_frame.pack(fill="x", padx=5, pady=10)

        ctk.CTkLabel(tester_frame, text="BSG Live Command Tester",
                    font=("Arial", 14, "bold")).pack(anchor="w", pady=5)

        ctk.CTkLabel(tester_frame, text="Type a BSG or LaTeX command to see its help information:",
                    font=("Arial", 11)).pack(anchor="w", pady=2)

        self.test_var = tk.StringVar()
        test_entry = ctk.CTkEntry(tester_frame, textvariable=self.test_var,
                                 placeholder_text="Enter command (e.g., \\bsglogo, \\frac, \\alpha)")
        test_entry.pack(fill="x", pady=5)
        test_entry.bind('<KeyRelease>', self.update_live_help)

        # Help display area
        self.help_display = ctk.CTkTextbox(help_frame, height=200, font=("Arial", 11))
        self.help_display.pack(fill="both", expand=True, pady=10)
        self.help_display.insert("1.0", "Enter a BSG or LaTeX command above to see detailed help information...")
        self.help_display.configure(state="disabled")

        # Quick Access Button Groups - STATIC layout to avoid performance issues
        self.setup_quick_access_buttons(help_frame)

    def setup_quick_access_buttons(self, parent):
        """Setup colored button groups organized in three rows"""
        # Container for button groups
        button_groups_frame = ctk.CTkFrame(parent)
        button_groups_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(button_groups_frame, text="Quick Access BSG Commands",
                    font=("Arial", 12, "bold")).pack(anchor="w", pady=5)

        # Button group definitions - BSG focused
        button_groups = [
            {
                "name": "BSG Document",
                "color": "#3498DB",
                "commands": ["\\title", "\\author", "\\institute", "\\bsglogo", "\\bsgcode"]
            },
            {
                "name": "BSG Media",
                "color": "#2ECC71",
                "commands": ["\\file", "\\play", "\\movie", "\\includegraphics"]
            },
            {
                "name": "BSG Formatting",
                "color": "#9B59B6",
                "commands": ["\\textcolor", "\\bsghighlight", "\\alert", "\\textbf", "\\textit"]
            },
            {
                "name": "BSG Layout",
                "color": "#E67E22",
                "commands": ["\\begin{bsgblock}", "\\begin{columns}", "\\frametitle", "\\begin{frame}"]
            },
            {
                "name": "Beamer Animations",
                "color": "#E74C3C",
                "commands": ["\\pause", "\\only", "\\uncover", "\\alt", "\\begin{itemize}[<+->]"]
            },
            {
                "name": "Math Symbols",
                "color": "#1ABC9C",
                "commands": ["\\alpha", "\\beta", "\\sum", "\\int", "\\frac", "\\sqrt"]
            },
            {
                "name": "Lists & Items",
                "color": "#8E44AD",
                "commands": ["\\begin{itemize}", "\\begin{enumerate}", "\\item", "\\begin{overprint}"]
            },
            {
                "name": "Transitions",
                "color": "#16A085",
                "commands": ["\\transdissolve", "\\transwipe", "\\note", "\\href"]
            },
            {
                "name": "Greek Letters",
                "color": "#D35400",
                "commands": ["\\alpha", "\\beta", "\\gamma", "\\delta", "\\epsilon", "\\pi"]
            }
        ]

        # Create three rows of button groups
        row1_frame = ctk.CTkFrame(button_groups_frame, fg_color="transparent")
        row1_frame.pack(fill="x", pady=2)

        row2_frame = ctk.CTkFrame(button_groups_frame, fg_color="transparent")
        row2_frame.pack(fill="x", pady=2)

        row3_frame = ctk.CTkFrame(button_groups_frame, fg_color="transparent")
        row3_frame.pack(fill="x", pady=2)

        # Distribute groups between three rows (3 groups per row)
        for i, group in enumerate(button_groups):
            if i < 3:
                parent_frame = row1_frame
            elif i < 6:
                parent_frame = row2_frame
            else:
                parent_frame = row3_frame

            group_frame = self.create_button_group(group, parent_frame)
            group_frame.pack(side="left", fill="x", expand=True, padx=3)


    def create_button_group(self, group_info, parent):
        """Create a single button group with colored buttons"""
        group_frame = ctk.CTkFrame(parent, fg_color="#2B2B2B", corner_radius=8)

        # Group header
        header_frame = ctk.CTkFrame(group_frame, fg_color=group_info["color"], corner_radius=6)
        header_frame.pack(fill="x", padx=2, pady=2)

        ctk.CTkLabel(header_frame, text=group_info["name"], font=("Arial", 11, "bold"),
                    text_color="white").pack(pady=4)

        # Buttons container
        buttons_frame = ctk.CTkFrame(group_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=5, pady=5)

        # Create buttons for each command
        for command in group_info["commands"]:
            btn = ctk.CTkButton(
                buttons_frame,
                text=command,
                command=lambda cmd=command: self.on_quick_button_click(cmd),
                font=("Arial", 10),
                fg_color=group_info["color"],
                hover_color=self.adjust_color_brightness(group_info["color"], -20),
                text_color="white",
                height=28,
                corner_radius=6
            )
            btn.pack(fill="x", pady=2)

        return group_frame

    def adjust_color_brightness(self, color, factor):
        """Adjust color brightness for hover effects"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(max(0, min(255, c + factor)) for c in rgb)
        return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"

    def on_quick_button_click(self, command):
        """Handle quick access button clicks"""
        self.test_var.set(command)
        self.update_live_help()
        self.help_display.see("1.0")

    def on_window_resize_throttled(self, event):
        """Handle window resize with throttling to prevent performance issues"""
        if event.widget == self:
            current_time = self.tk.call('clock', 'milliseconds')

            if self.resize_timeout_id:
                self.after_cancel(self.resize_timeout_id)

            if current_time - self.last_resize_time > self.min_resize_interval:
                self.last_resize_time = current_time
                # Static layout - no dynamic updates needed
            else:
                self.resize_timeout_id = self.after(
                    self.min_resize_interval,
                    lambda: setattr(self, 'last_resize_time', self.tk.call('clock', 'milliseconds'))
                )

    def update_live_help(self, event=None):
        """Update live help display based on entered command"""
        command = self.test_var.get().strip()
        if not command or not command.startswith('\\'):
            self.help_display.configure(state="normal")
            self.help_display.delete("1.0", "end")
            self.help_display.insert("1.0", "Enter a BSG or LaTeX command above to see detailed help information...")
            self.help_display.configure(state="disabled")
            return

        help_info = self.command_helper.get_command_help(command)

        self.help_display.configure(state="normal")
        self.help_display.delete("1.0", "end")

        if help_info:
            help_text = f"Command: {command}\n\n"
            help_text += f"Description: {help_info.get('description', 'No description available')}\n\n"
            help_text += f"Syntax: {help_info.get('syntax', 'No syntax information')}\n\n"
            help_text += f"Category: {help_info.get('category', 'General')}\n"
            help_text += f"Package: {help_info.get('package', 'LaTeX')}\n\n"

            if 'example' in help_info:
                help_text += f"Example:\n{help_info['example']}\n\n"

            if 'symbol' in help_info:
                help_text += f"Symbol: {help_info['symbol']}\n\n"

            if 'url' in help_info:
                help_text += f"Documentation: {help_info['url']}"
        else:
            help_text = f"No detailed help found for: {command}\n\n"
            help_text += "Try searching for similar commands or check the spelling."

        self.help_display.insert("1.0", help_text)
        self.help_display.configure(state="disabled")

    def filter_by_category(self, category):
        """Filter commands by category"""
        if category == "All":
            self.filtered_commands = self.commands.copy()
        else:
            self.filtered_commands = {category: self.commands.get(category, [])}

        # Update button states
        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.configure(fg_color="#4ECDC4", hover_color="#45B7A8")
            else:
                btn.configure(fg_color="#34495E", hover_color="#2C3E50")

        self.refresh_display()

    def filter_commands(self, event=None):
        """Filter commands based on search text and content type"""
        search_text = self.search_var.get().lower()
        content_type = self.content_var.get()

        if not search_text:
            self.filtered_commands = self.commands.copy()
        else:
            self.filtered_commands = {}
            for category, commands in self.commands.items():
                filtered = []
                for cmd in commands:
                    # Filter by content type
                    if content_type == "commands_only" and cmd.get('is_symbol', False):
                        continue
                    if content_type == "symbols_only" and not cmd.get('is_symbol', False):
                        continue

                    # Filter by search text
                    if (search_text in cmd['command'].lower() or
                        search_text in cmd['description'].lower() or
                        search_text in cmd.get('usage', '').lower() or
                        search_text in cmd['syntax'].lower() or
                        search_text in cmd.get('category', '').lower()):
                        filtered.append(cmd)
                if filtered:
                    self.filtered_commands[category] = filtered

        self.refresh_display()

    def refresh_display(self):
        """Refresh the command display"""
        self.display_commands()

    def display_commands(self):
        """Display commands based on current view mode"""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.filtered_commands:
            no_results_frame = ctk.CTkFrame(self.scrollable_frame)
            no_results_frame.pack(fill="both", expand=True, pady=50)

            ctk.CTkLabel(no_results_frame,
                        text="No commands found matching your criteria",
                        font=("Arial", 14)).pack(pady=10)
            ctk.CTkLabel(no_results_frame,
                        text="Try adjusting your search terms or filters",
                        font=("Arial", 12), text_color="#95A5A6").pack(pady=5)
            return

        total_commands = sum(len(commands) for commands in self.filtered_commands.values())
        self.stats_label.configure(text=f"Showing {total_commands} commands and symbols")

        if self.view_var.get() == "categorized":
            self.display_categorized()
        else:
            self.display_flat_list()

    def display_categorized(self):
        """Display commands organized by categories"""
        row = 0
        for category, commands in self.filtered_commands.items():
            if not commands:
                continue

            # Category header
            cat_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#2B3A42", corner_radius=8)
            cat_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=8)
            cat_frame.grid_columnconfigure(0, weight=1)

            # Category title with count
            count = len(commands)
            title_text = f"{category} ({count} item{'s' if count != 1 else ''})"
            ctk.CTkLabel(cat_frame, text=title_text, font=("Arial", 16, "bold"),
                        text_color="#4ECDC4").grid(row=0, column=0, sticky="w", padx=15, pady=8)

            row += 1

            # Commands in this category
            cat_content_frame = ctk.CTkFrame(self.scrollable_frame)
            cat_content_frame.grid(row=row, column=0, sticky="ew", padx=20, pady=5)
            cat_content_frame.grid_columnconfigure(0, weight=1)

            cmd_row = 0
            for i, cmd in enumerate(commands):
                cmd_frame = self.create_command_frame(cmd, i)
                cmd_frame.grid(row=cmd_row, column=0, sticky="ew", padx=5, pady=3)
                cmd_row += 1

            row += 1

            # Add spacer between categories
            spacer = ctk.CTkFrame(self.scrollable_frame, height=15, fg_color="transparent")
            spacer.grid(row=row, column=0, sticky="ew", pady=5)
            row += 1

    def display_flat_list(self):
        """Display all commands in a flat list"""
        row = 0
        all_commands = []
        for commands in self.filtered_commands.values():
            all_commands.extend(commands)

        # Sort alphabetically by command name
        all_commands.sort(key=lambda x: x['command'])

        for i, cmd in enumerate(all_commands):
            cmd_frame = self.create_command_frame(cmd, i)
            cmd_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
            row += 1

    def create_command_frame(self, command_data, index):
        """Create a detailed frame for a single command"""
        frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=6)
        frame.grid_columnconfigure(1, weight=1)

        # Main content frame
        main_content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        main_content_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=8)
        main_content_frame.grid_columnconfigure(1, weight=1)

        # Command header row
        header_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=2)

        # Command name with symbol if available
        cmd_text = command_data['command']
        if command_data.get('is_symbol', False) and self.symbols_var.get():
            symbol = command_data.get('symbol', '')
            if symbol:
                cmd_text = f"{command_data['command']} → {symbol}"

        cmd_label = ctk.CTkLabel(header_frame, text=cmd_text,
                               font=("Arial", 13, "bold"), text_color="#FF6B6B")
        cmd_label.pack(side="left", padx=5)

        # Category badge
        category = command_data.get('category', 'general')
        category_color = self.get_category_color(category)
        category_badge = ctk.CTkLabel(header_frame, text=category,
                                    font=("Arial", 9), text_color="white",
                                    fg_color=category_color, corner_radius=10)
        category_badge.pack(side="left", padx=5)

        # Symbol indicator
        if command_data.get('is_symbol', False):
            symbol_badge = ctk.CTkLabel(header_frame, text="SYMBOL",
                                      font=("Arial", 8, "bold"), text_color="white",
                                      fg_color="#9B59B6", corner_radius=8)
            symbol_badge.pack(side="left", padx=2)

        # Usage hint on the right
        usage_label = ctk.CTkLabel(header_frame, text=command_data.get('usage', ''),
                                 font=("Arial", 9), text_color="#95A5A6")
        usage_label.pack(side="right", padx=5)

        # Description
        desc_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        desc_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)

        desc_label = ctk.CTkLabel(desc_frame, text=command_data['description'],
                                font=("Arial", 11), wraplength=1000, justify="left")
        desc_label.pack(side="left", anchor="w")

        # Syntax (if enabled)
        if self.syntax_var.get():
            syntax_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
            syntax_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=2)

            ctk.CTkLabel(syntax_frame, text="Syntax:",
                        font=("Arial", 10, "bold")).pack(side="left", padx=5)
            syntax_label = ctk.CTkLabel(syntax_frame, text=command_data['syntax'],
                                      font=("Courier", 10), text_color="#4ECDC4")
            syntax_label.pack(side="left", padx=5)

        # Example (if enabled)
        if self.examples_var.get() and command_data.get('example'):
            example_frame = ctk.CTkFrame(main_content_frame)
            example_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)
            example_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(example_frame, text="Example:",
                        font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=2)

            example_text = tk.Text(example_frame, height=2, font=("Courier", 9),
                                 wrap=tk.WORD, bg='#343638', fg='white',
                                 selectbackground='#4ECDC4', borderwidth=1, relief='solid')
            example_text.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
            example_text.insert("1.0", command_data['example'])
            example_text.config(state="normal")

            self.add_text_context_menu(example_text)

        # Action buttons
        action_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        action_frame.grid(row=4, column=0, columnspan=2, sticky="e", pady=5)

        select_btn = ctk.CTkButton(action_frame, text="Select", width=80,
                                 command=lambda cmd=command_data: self.select_command(cmd))
        select_btn.pack(side="left", padx=2)

        copy_btn = ctk.CTkButton(action_frame, text="Copy Example", width=100,
                               command=lambda: self.copy_to_clipboard(command_data['example']))
        copy_btn.pack(side="left", padx=2)

        # Quick insert button for common commands
        if not command_data.get('is_symbol', False):
            insert_btn = ctk.CTkButton(action_frame, text="Quick Insert", width=90,
                                     command=lambda: self.quick_insert(command_data),
                                     fg_color="#27AE60", hover_color="#219A52")
            insert_btn.pack(side="left", padx=2)

        # Bind double-click to select command
        frame.bind("<Double-Button-1>", lambda e, cmd=command_data: self.select_and_insert(cmd))

        return frame

    def get_category_color(self, category):
        """Get consistent color for each category"""
        color_map = {
            'document': '#3498DB',
            'content': '#2ECC71',
            'media': '#9B59B6',
            'formatting': '#E67E22',
            'lists': '#1ABC9C',
            'layout': '#34495E',
            'animation': '#E74C3C',
            'sequential': '#F39C12',
            'transition': '#16A085',
            'presentation': '#8E44AD',
            'interactive': '#D35400',
            'symbols': '#27AE60',
            'math': '#2980B9',
            'general': '#7F8C8D'
        }
        return color_map.get(category, '#7F8C8D')

    def add_text_context_menu(self, text_widget):
        """Add right-click context menu to text widgets for copy/paste"""
        context_menu = tk.Menu(text_widget, tearoff=0)
        context_menu.add_command(label="Copy",
                               command=lambda: self.copy_text_from_widget(text_widget))
        context_menu.add_command(label="Select All",
                               command=lambda: text_widget.tag_add(tk.SEL, "1.0", tk.END))

        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

        text_widget.bind("<Button-3>", show_context_menu)

    def copy_text_from_widget(self, text_widget):
        """Copy selected text from a text widget to clipboard"""
        try:
            selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except tk.TclError:
            pass

    def select_command(self, command):
        """Select a command for insertion"""
        self.selected_command = command

    def select_and_insert(self, command):
        """Select and immediately insert command"""
        self.selected_command = command
        self.insert_selected()

    def quick_insert(self, command_data):
        """Quick insert with auto-completion patterns"""
        self.selected_command = command_data
        if command_data.get('is_symbol', False):
            self.insert_selected()
        else:
            self.show_quick_insert_dialog(command_data)

    def show_quick_insert_dialog(self, command_data):
        """Show dialog for quick insertion with parameters"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Quick Insert: {command_data['command']}")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()

        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(main_frame, text=f"Insert: {command_data['command']}",
                    font=("Arial", 14, "bold")).pack(pady=10)

        ctk.CTkLabel(main_frame, text=command_data['description'],
                    font=("Arial", 11), wraplength=380).pack(pady=5)

        # Parameter fields based on auto_complete pattern
        auto_complete = command_data.get('auto_complete', '')
        if '$' in auto_complete:
            ctk.CTkLabel(main_frame, text="This command requires parameters.",
                        font=("Arial", 10), text_color="#E74C3C").pack(pady=5)

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Insert Basic", width=100,
                     command=lambda: self.insert_basic_command(command_data, dialog)).pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="Cancel", width=80,
                     command=dialog.destroy).pack(side="left", padx=5)

    def insert_basic_command(self, command_data, dialog):
        """Insert basic command without parameters"""
        self.selected_command = command_data
        dialog.destroy()
        self.insert_selected()

    def insert_selected(self):
        """Insert selected command into editor"""
        if self.selected_command:
            self.destroy()
            return self.selected_command
        else:
            messagebox.showinfo("No Selection", "Please select a command first.")
            return None

    def copy_example(self):
        """Copy selected command example to clipboard"""
        if self.selected_command:
            self.copy_to_clipboard(self.selected_command['example'])
        else:
            messagebox.showinfo("No Selection", "Please select a command first.")

    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Content copied to clipboard!")

    def show_detailed_help(self):
        """Show detailed help for selected command"""
        if not self.selected_command:
            messagebox.showinfo("No Selection", "Please select a command first.")
            return

        # Switch to interactive help tab and populate
        self.tab_view.set("Interactive Help")
        self.test_var.set(self.selected_command['command'])
        self.update_live_help()

    def center_dialog(self):
        """Center the dialog on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
