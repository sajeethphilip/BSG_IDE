import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

class EnhancedCommandIndexDialog(ctk.CTkToplevel):
    """Enhanced LaTeX command index with comprehensive listing and filtering - FLOATING VERSION"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("BSG-IDE Enhanced Command Reference")
        self.geometry("1200x900")

        # Make it a floating window - NO grab_set() that blocks main window
        self.transient(parent)
        self.resizable(True, True)

        # Set focus to this window but don't block main window
        self.focus_set()

        # Make window stay on top of parent but allow interaction with both
        self.attributes('-topmost', True)

        # Enhanced command database
        self.commands = self.build_enhanced_command_database()
        self.filtered_commands = self.commands.copy()
        self.selected_command = None

        # Display options
        self.display_options = {
            'show_syntax': True,
            'show_examples': True,
            'category_filter': "All",
            'view_mode': "categorized"
        }

        self.create_enhanced_widgets()
        self.center_dialog()

        # Bind escape key to close
        self.bind('<Escape>', lambda e: self.destroy())

        # Bind focus events to maintain topmost behavior
        self.bind('<FocusIn>', lambda e: self.attributes('-topmost', True))

    def build_enhanced_command_database(self):
        """Build comprehensive command database with display options"""
        return {
            'Document Structure': [
                {
                    'command': '\\title',
                    'syntax': '\\title{Presentation Title}',
                    'description': 'Sets the main presentation title',
                    'example': '\\title{Artificial Intelligence Research}',
                    'category': 'document',
                    'display_options': ['static'],
                    'auto_complete': '\\title{$1}',
                    'usage': 'Required for all presentations'
                },
                {
                    'command': '\\author',
                    'syntax': '\\author{Author Name}',
                    'description': 'Sets the author name',
                    'example': '\\author{Dr. John Smith}',
                    'category': 'document',
                    'display_options': ['static'],
                    'auto_complete': '\\author{$1}',
                    'usage': 'Required for all presentations'
                },
                {
                    'command': '\\institute',
                    'syntax': '\\institute{Institution Name}',
                    'description': 'Sets the institution name',
                    'example': '\\institute{University of Technology}',
                    'category': 'document',
                    'display_options': ['static'],
                    'auto_complete': '\\institute{$1}',
                    'usage': 'Recommended for academic presentations'
                },
                {
                    'command': '\\date',
                    'syntax': '\\date{date}',
                    'description': 'Sets the presentation date',
                    'example': '\\date{\\today}',
                    'category': 'document',
                    'display_options': ['static'],
                    'auto_complete': '\\date{$1}',
                    'usage': 'Optional, defaults to \\today'
                }
            ],

            'Slide Content & Media': [
                {
                    'command': '\\frametitle',
                    'syntax': '\\frametitle{Slide Title}',
                    'description': 'Sets the frame/slide title',
                    'example': '\\frametitle{Introduction}',
                    'category': 'content',
                    'display_options': ['static'],
                    'auto_complete': '\\frametitle{$1}',
                    'usage': 'Per slide, after \\begin{frame}'
                },
                {
                    'command': '\\file',
                    'syntax': '\\file{media_files/filename.ext}',
                    'description': 'Includes an image or media file',
                    'example': '\\file{media_files/diagram.png}',
                    'category': 'media',
                    'display_options': ['static'],
                    'auto_complete': '\\file{media_files/$1}',
                    'usage': 'Inline within slide content'
                },
                {
                    'command': '\\play',
                    'syntax': '\\play{media_files/video.ext}',
                    'description': 'Embeds a playable video',
                    'example': '\\play{media_files/demo.mp4}',
                    'category': 'media',
                    'display_options': ['static'],
                    'auto_complete': '\\play{media_files/$1}',
                    'usage': 'Inline within slide content'
                },
                {
                    'command': '\\movie',
                    'syntax': '\\movie[options]{poster}{video}',
                    'description': 'Embeds multimedia with poster',
                    'example': '\\movie[autostart]{\\includegraphics{poster}}{video.mp4}',
                    'category': 'media',
                    'display_options': ['static'],
                    'auto_complete': '\\movie[$1]{$2}{$3}',
                    'usage': 'Advanced media embedding'
                }
            ],

            'Text Formatting': [
                {
                    'command': '\\textcolor',
                    'syntax': '\\textcolor{color}{text} or \\textcolor[RGB]{r,g,b}{text}',
                    'description': 'Changes text color with named or RGB colors',
                    'example': '\\textcolor{blue}{Highlighted text}',
                    'category': 'formatting',
                    'display_options': ['static'],
                    'auto_complete': '\\textcolor{$1}{$2}',
                    'usage': 'Inline text formatting'
                },
                {
                    'command': '\\textbf',
                    'syntax': '\\textbf{Bold Text}',
                    'description': 'Makes text bold',
                    'example': 'This is \\textbf{important} text',
                    'category': 'formatting',
                    'display_options': ['static'],
                    'auto_complete': '\\textbf{$1}',
                    'usage': 'Inline emphasis'
                },
                {
                    'command': '\\textit',
                    'syntax': '\\textit{Italic Text}',
                    'description': 'Makes text italic',
                    'example': 'This is \\textit{emphasized} text',
                    'category': 'formatting',
                    'display_options': ['static'],
                    'auto_complete': '\\textit{$1}',
                    'usage': 'Inline emphasis'
                },
                {
                    'command': '\\alert',
                    'syntax': '\\alert{Text}',
                    'description': 'Highlights text with alert color',
                    'example': 'Remember: \\alert{key point}',
                    'category': 'formatting',
                    'display_options': ['dynamic'],
                    'auto_complete': '\\alert{$1}',
                    'usage': 'Highlight important content'
                }
            ],

            'Lists & Environments': [
                {
                    'command': '\\begin{itemize}',
                    'syntax': '\\begin{itemize}\\item First\\item Second\\end{itemize}',
                    'description': 'Creates a bulleted list',
                    'example': '\\begin{itemize}\\item Point one\\item Point two\\end{itemize}',
                    'category': 'lists',
                    'display_options': ['static', 'dynamic'],
                    'auto_complete': '\\begin{itemize}\\item $1\\item $2\\end{itemize}',
                    'usage': 'Unordered lists'
                },
                {
                    'command': '\\begin{enumerate}',
                    'syntax': '\\begin{enumerate}\\item First\\item Second\\end{enumerate}',
                    'description': 'Creates a numbered list',
                    'example': '\\begin{enumerate}\\item Step one\\item Step two\\end{enumerate}',
                    'category': 'lists',
                    'display_options': ['static', 'dynamic'],
                    'auto_complete': '\\begin{enumerate}\\item $1\\item $2\\end{itemize}',
                    'usage': 'Ordered lists'
                },
                {
                    'command': '\\item',
                    'syntax': '\\item Item text',
                    'description': 'Creates a list item',
                    'example': '\\item This is a list item',
                    'category': 'lists',
                    'display_options': ['static', 'dynamic'],
                    'auto_complete': '\\item $1',
                    'usage': 'Within itemize or enumerate'
                },
                {
                    'command': '\\begin{columns}',
                    'syntax': '\\begin{columns}\\column{0.5\\textwidth}Left\\column{0.5\\textwidth}Right\\end{columns}',
                    'description': 'Creates multi-column layout',
                    'example': '\\begin{columns}\\column{0.4\\textwidth}Left\\column{0.6\\textwidth}Right\\end{columns}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\begin{columns}\\column{$1\\\\textwidth}$2\\end{columns}',
                    'usage': 'Multi-column slides'
                }
            ],

            'Display Effects & Animations': [
                {
                    'command': '\\pause',
                    'syntax': '\\pause',
                    'description': 'Pauses between overlay items',
                    'example': 'First point\\pause\nSecond point',
                    'category': 'animation',
                    'display_options': ['dynamic', 'overlay'],
                    'auto_complete': '\\pause',
                    'usage': 'Between content items'
                },
                {
                    'command': '\\only',
                    'syntax': '\\only<overlay>{content}',
                    'description': 'Shows content only on specified overlays',
                    'example': '\\only<2>{This appears only on slide 2}',
                    'category': 'animation',
                    'display_options': ['dynamic', 'overlay'],
                    'auto_complete': '\\only<$1>{$2}',
                    'usage': 'Conditional display'
                },
                {
                    'command': '\\uncover',
                    'syntax': '\\uncover<overlay>{content}',
                    'description': 'Uncovers content gradually',
                    'example': '\\uncover<2->{Gradually revealed content}',
                    'category': 'animation',
                    'display_options': ['dynamic', 'overlay'],
                    'auto_complete': '\\uncover<$1>{$2}',
                    'usage': 'Progressive disclosure'
                },
                {
                    'command': '\\alt',
                    'syntax': '\\alt<overlay>{alternative1}{alternative2}',
                    'description': 'Shows alternative content on different slides',
                    'example': '\\alt<2>{Version A}{Version B}',
                    'category': 'animation',
                    'display_options': ['dynamic', 'overlay'],
                    'auto_complete': '\\alt<$1>{$2}{$3}',
                    'usage': 'Alternative content versions'
                }
            ],

            'Item-by-Item Display': [
                {
                    'command': '\\begin{itemize}[<+->]',
                    'syntax': '\\begin{itemize}[<+->]\\item First\\item Second\\end{itemize}',
                    'description': 'Creates bulleted list with automatic item-by-item display',
                    'example': '\\begin{itemize}[<+->]\n\\item First point\n\\item Second point\n\\end{itemize}',
                    'category': 'sequential',
                    'display_options': ['dynamic', 'sequential'],
                    'auto_complete': '\\begin{itemize}[<+->]\n\\item $1\n\\item $2\n\\end{itemize}',
                    'usage': 'Automatic sequential display'
                },
                {
                    'command': '\\begin{enumerate}[<+->]',
                    'syntax': '\\begin{enumerate}[<+->]\\item First\\item Second\\end{enumerate}',
                    'description': 'Creates numbered list with automatic sequential display',
                    'example': '\\begin{enumerate}[<+->]\n\\item Step one\n\\item Step two\n\\end{enumerate}',
                    'category': 'sequential',
                    'display_options': ['dynamic', 'sequential'],
                    'auto_complete': '\\begin{enumerate}[<+->]\n\\item $1\n\\item $2\n\\end{itemize}',
                    'usage': 'Automatic sequential numbering'
                },
                {
                    'command': '\\begin{overprint}',
                    'syntax': '\\begin{overprint}\\onslide<1>Content A\\onslide<2>Content B\\end{overprint}',
                    'description': 'Creates overlapping content for different slides',
                    'example': '\\begin{overprint}\n\\onslide<1>First version\n\\onslide<2>Second version\n\\end{overprint}',
                    'category': 'animation',
                    'display_options': ['dynamic', 'overlay'],
                    'auto_complete': '\\begin{overprint}\n\\onslide<$1>$2\n\\onslide<$3>$4\n\\end{overprint}',
                    'usage': 'Overlapping content areas'
                }
            ],

            'Transitions & Advanced Effects': [
                {
                    'command': '\\transdissolve',
                    'syntax': '\\transdissolve[duration=2]',
                    'description': 'Creates smooth dissolve transition between slides',
                    'example': '\\transdissolve[duration=1.5]',
                    'category': 'transition',
                    'display_options': ['dynamic', 'transition'],
                    'auto_complete': '\\transdissolve[duration=$1]',
                    'usage': 'Between frames'
                },
                {
                    'command': '\\transwipe',
                    'syntax': '\\transwipe[direction=90]',
                    'description': 'Creates wipe transition in specified direction',
                    'example': '\\transwipe[direction=45]',
                    'category': 'transition',
                    'display_options': ['dynamic', 'transition'],
                    'auto_complete': '\\transwipe[direction=$1]',
                    'usage': 'Between frames'
                },
                {
                    'command': '\\animatevalue',
                    'syntax': '\\animatevalue<start-end>{variable}{initial}{final}',
                    'description': 'Animates numerical values over specified slides',
                    'example': '\\animatevalue<1-10>{x}{0}{100}',
                    'category': 'animation',
                    'display_options': ['dynamic', 'numeric'],
                    'auto_complete': '\\animatevalue<$1-$2>{$3}{$4}{$5}',
                    'usage': 'Numerical animations'
                }
            ],

            'Presentation Features': [
                {
                    'command': '\\note',
                    'syntax': '\\note{Speaker notes}',
                    'description': 'Adds speaker notes (visible in presenter mode)',
                    'example': '\\note{Remember to explain this concept slowly}',
                    'category': 'presentation',
                    'display_options': ['static'],
                    'auto_complete': '\\note{$1}',
                    'usage': 'Speaker notes'
                },
                {
                    'command': '\\href',
                    'syntax': '\\href{url}{link text}',
                    'description': 'Creates clickable hyperlink',
                    'example': 'Visit \\href{https://airis4d.com}{our website}',
                    'category': 'interactive',
                    'display_options': ['static'],
                    'auto_complete': '\\href{$1}{$2}',
                    'usage': 'Hyperlinks'
                }
            ]
        }

    def create_enhanced_widgets(self):
        """Create enhanced interface with comprehensive listing"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(header_frame, text="BSG-IDE Complete Command Reference",
                    font=("Arial", 18, "bold")).pack(pady=5)

        ctk.CTkLabel(header_frame,
                    text="Complete listing of all available LaTeX/Beamer commands with examples and usage tips",
                    font=("Arial", 12)).pack(pady=2)

        # Control Panel
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", padx=5, pady=5)

        # Left side: Search and quick filters
        left_controls = ctk.CTkFrame(control_frame, fg_color="transparent")
        left_controls.pack(side="left", fill="x", expand=True)

        # Search
        search_frame = ctk.CTkFrame(left_controls, fg_color="transparent")
        search_frame.pack(side="top", fill="x", pady=2)

        ctk.CTkLabel(search_frame, text="Search:", font=("Arial", 12)).pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=250,
                                  placeholder_text="Type to search commands...")
        search_entry.pack(side="left", padx=5)
        search_entry.bind('<KeyRelease>', self.filter_commands)

        # Quick category filters
        category_frame = ctk.CTkFrame(left_controls, fg_color="transparent")
        category_frame.pack(side="top", fill="x", pady=2)

        ctk.CTkLabel(category_frame, text="Quick Filters:", font=("Arial", 12)).pack(side="left", padx=5)

        # Create category buttons
        categories = ["All"] + list(self.commands.keys())
        self.category_buttons = {}

        for category in categories:
            btn = ctk.CTkButton(
                category_frame,
                text=category,
                command=lambda c=category: self.filter_by_category(c),
                width=120,
                height=25,
                font=("Arial", 10)
            )
            btn.pack(side="left", padx=2)
            self.category_buttons[category] = btn

        # Right side: Display options
        right_controls = ctk.CTkFrame(control_frame, fg_color="transparent")
        right_controls.pack(side="right", padx=5)

        # View mode
        view_frame = ctk.CTkFrame(right_controls, fg_color="transparent")
        view_frame.pack(side="top", pady=2)

        ctk.CTkLabel(view_frame, text="View:", font=("Arial", 12)).pack(side="left", padx=5)

        self.view_var = tk.StringVar(value="categorized")
        ctk.CTkRadioButton(view_frame, text="Categorized", variable=self.view_var,
                          value="categorized", command=self.refresh_display).pack(side="left", padx=2)
        ctk.CTkRadioButton(view_frame, text="All Commands", variable=self.view_var,
                          value="all", command=self.refresh_display).pack(side="left", padx=2)

        # Display toggles
        toggle_frame = ctk.CTkFrame(right_controls, fg_color="transparent")
        toggle_frame.pack(side="top", pady=2)

        self.syntax_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(toggle_frame, text="Show Syntax", variable=self.syntax_var,
                       command=self.refresh_display).pack(side="left", padx=5)

        self.examples_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(toggle_frame, text="Show Examples", variable=self.examples_var,
                       command=self.refresh_display).pack(side="left", padx=5)

        # Content Area
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create scrollable content area
        self.scrollable_frame = ctk.CTkScrollableFrame(content_frame)
        self.scrollable_frame.pack(fill="both", expand=True)

        # Statistics label
        self.stats_label = ctk.CTkLabel(main_frame, text="", font=("Arial", 10))
        self.stats_label.pack(side="left", padx=10, pady=5)

        # Action buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=5, pady=10)

        ctk.CTkButton(button_frame, text="Insert Selected Command",
                     command=self.insert_selected, width=150).pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="Copy Example",
                     command=self.copy_example, width=120).pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="Close",
                     command=self.destroy).pack(side="right", padx=5)

        # Initial display
        self.display_commands()

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
                btn.configure(fg_color="#3B8ED0", hover_color="#3672A4")

        self.refresh_display()

    def display_commands(self):
        """Display commands based on current view mode"""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.filtered_commands:
            ctk.CTkLabel(self.scrollable_frame,
                        text="No commands found matching your criteria",
                        font=("Arial", 12)).pack(pady=20)
            return

        total_commands = sum(len(commands) for commands in self.filtered_commands.values())
        self.stats_label.configure(text=f"Showing {total_commands} commands")

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
            cat_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#2B3A42")
            cat_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=10)
            cat_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(cat_frame, text=category, font=("Arial", 14, "bold"),
                        text_color="#4ECDC4").grid(row=0, column=0, sticky="w", padx=10, pady=5)

            row += 1

            # Commands in this category
            for i, cmd in enumerate(commands):
                cmd_frame = self.create_command_frame(cmd, i)
                cmd_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
                row += 1

            # Add some space between categories
            spacer = ctk.CTkFrame(self.scrollable_frame, height=10, fg_color="transparent")
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
            cmd_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=2)
            row += 1

    def create_command_frame(self, command_data, index):
        """Create a detailed frame for a single command"""
        frame = ctk.CTkFrame(self.scrollable_frame)
        frame.grid_columnconfigure(1, weight=1)

        # Command header row
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=2)

        # Command name (bold and prominent)
        cmd_label = ctk.CTkLabel(header_frame, text=command_data['command'],
                               font=("Arial", 13, "bold"), text_color="#FF6B6B")
        cmd_label.pack(side="left", padx=5)

        # Category badge
        category_badge = ctk.CTkLabel(header_frame, text=command_data['category'],
                                    font=("Arial", 9), text_color="#95A5A6",
                                    fg_color="#34495E", corner_radius=10)
        category_badge.pack(side="left", padx=5)

        # Usage hint
        usage_label = ctk.CTkLabel(header_frame, text=command_data.get('usage', ''),
                                 font=("Arial", 9), text_color="#BDC3C7")
        usage_label.pack(side="left", padx=5, fill="x", expand=True)

        # Description
        desc_frame = ctk.CTkFrame(frame, fg_color="transparent")
        desc_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=2)

        desc_label = ctk.CTkLabel(desc_frame, text=command_data['description'],
                                font=("Arial", 11), wraplength=800, justify="left")
        desc_label.pack(side="left", anchor="w")

        # Syntax (if enabled)
        if self.syntax_var.get():
            syntax_frame = ctk.CTkFrame(frame, fg_color="transparent")
            syntax_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=2)

            ctk.CTkLabel(syntax_frame, text="Syntax:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
            syntax_label = ctk.CTkLabel(syntax_frame, text=command_data['syntax'],
                                      font=("Courier", 10), text_color="#4ECDC4")
            syntax_label.pack(side="left", padx=5)

        # Example (if enabled) - FIXED with proper text widget and copy functionality
        if self.examples_var.get() and command_data.get('example'):
            example_frame = ctk.CTkFrame(frame)
            example_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
            example_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(example_frame, text="Example:", font=("Arial", 10, "bold")).grid(
                row=0, column=0, sticky="w", padx=5, pady=2)

            # Use a regular tkinter Text widget for better copy/paste support
            example_text = tk.Text(example_frame, height=3, font=("Courier", 9),
                                 wrap=tk.WORD, bg='#343638', fg='white',
                                 selectbackground='#4ECDC4', borderwidth=1, relief='solid')
            example_text.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
            example_text.insert("1.0", command_data['example'])
            example_text.config(state="normal")  # Allow copying but not editing

            # Add right-click context menu for copy
            self.add_text_context_menu(example_text)

        # Action buttons
        action_frame = ctk.CTkFrame(frame, fg_color="transparent")
        action_frame.grid(row=4, column=0, columnspan=3, sticky="e", padx=5, pady=5)

        select_btn = ctk.CTkButton(action_frame, text="Select", width=80,
                                 command=lambda cmd=command_data: self.select_command(cmd))
        select_btn.pack(side="left", padx=2)

        copy_btn = ctk.CTkButton(action_frame, text="Copy Example", width=100,
                               command=lambda: self.copy_to_clipboard(command_data['example']))
        copy_btn.pack(side="left", padx=2)

        return frame

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

        text_widget.bind("<Button-3>", show_context_menu)  # Right-click

    def copy_text_from_widget(self, text_widget):
        """Copy selected text from a text widget to clipboard"""
        try:
            selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except tk.TclError:
            # No text selected
            pass

    def filter_commands(self, event=None):
        """Filter commands based on search text"""
        search_text = self.search_var.get().lower()

        if not search_text:
            self.filtered_commands = self.commands.copy()
        else:
            self.filtered_commands = {}
            for category, commands in self.commands.items():
                filtered = []
                for cmd in commands:
                    if (search_text in cmd['command'].lower() or
                        search_text in cmd['description'].lower() or
                        search_text in cmd.get('usage', '').lower() or
                        search_text in cmd['syntax'].lower()):
                        filtered.append(cmd)
                if filtered:
                    self.filtered_commands[category] = filtered

        self.refresh_display()

    def refresh_display(self):
        """Refresh the command display"""
        self.display_commands()

    def select_command(self, command):
        """Select a command for insertion"""
        self.selected_command = command
        # Highlight or show selection feedback
        print(f"Selected command: {command['command']}")

    def insert_selected(self):
        """Insert selected command into editor"""
        if self.selected_command:
            # This will be handled by the parent window
            self.destroy()
            return self.selected_command
        else:
            from tkinter import messagebox
            messagebox.showinfo("No Selection", "Please select a command first.")
            return None

    def copy_example(self):
        """Copy selected command example to clipboard"""
        if self.selected_command:
            self.copy_to_clipboard(self.selected_command['example'])
        else:
            from tkinter import messagebox
            messagebox.showinfo("No Selection", "Please select a command first.")

    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(text)
        # Show confirmation
        from tkinter import messagebox
        messagebox.showinfo("Copied", "Example copied to clipboard!")

    def center_dialog(self):
        """Center the dialog on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
