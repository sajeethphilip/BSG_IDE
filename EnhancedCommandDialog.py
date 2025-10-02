import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import threading
import queue
import time

import customtkinter as ctk
import tkinter as tk
import json
import webbrowser
import tempfile
import subprocess
import re
from pathlib import Path
from datetime import datetime
from tkinter import messagebox
from typing import Dict, List, Optional, Tuple

#---------------Enhanced Latex Help Library --------------------------
class LatexCommandHelper:
    """Enhanced LaTeX command help system with symbols and autocompletion"""

    def __init__(self):
        self.commands_db = {}
        self.symbols_db = LatexSymbolsDatabase()
        self.cache_file = Path.home() / '.bsg-ide' / 'latex_help_cache.json'
        self.cache_expiry_days = 30
        self.load_local_database()

    def load_local_database(self):
        """Load local LaTeX command database with enhanced content"""
        # Basic LaTeX commands database
        self.commands_db = {
            '\\title': {
                'syntax': '\\title{title text}',
                'description': 'Sets the presentation title',
                'category': 'document',
                'package': 'beamer',
                'example': '\\title{My Presentation}'
            },
                '\\inlineimg': {
                'syntax': '\\inlineimg[options]{image} or \\inlineimg{image}{scale}',
                'description': 'Inserts inline images within text flow',
                'category': 'formatting',
                'package': 'graphicx',
                'example': 'Cats are amazing \\inlineimg{cat.png} and make great pets.'
            },
            '\\author': {
                'syntax': '\\author{author name}',
                'description': 'Sets the author name',
                'category': 'document',
                'package': 'beamer',
                'example': '\\author{John Doe}'
            },
            '\\institute': {
                'syntax': '\\institute{institution name}',
                'description': 'Sets the institution name',
                'category': 'document',
                'package': 'beamer',
                'example': '\\institute{University of Example}'
            },
            '\\date': {
                'syntax': '\\date{date}',
                'description': 'Sets the presentation date',
                'category': 'document',
                'package': 'beamer',
                'example': '\\date{\\today}'
            },
            '\\frametitle': {
                'syntax': '\\frametitle{slide title}',
                'description': 'Sets the frame/slide title',
                'category': 'frame',
                'package': 'beamer',
                'example': '\\frametitle{Introduction}'
            },
            '\\file': {
                'syntax': '\\file{media_files/filename.ext}',
                'description': 'Includes an image or media file',
                'category': 'media',
                'package': 'beamer',
                'example': '\\file{images/photo.jpg}'
            },
            '\\play': {
                'syntax': '\\play{media_files/video.ext}',
                'description': 'Embeds a playable video',
                'category': 'media',
                'package': 'beamer',
                'example': '\\play{videos/demo.mp4}'
            },
            '\\textcolor': {
                'syntax': '\\textcolor{color}{text} or \\textcolor[RGB]{r,g,b}{text}',
                'description': 'Changes text color',
                'category': 'formatting',
                'package': 'xcolor',
                'example': '\\textcolor{red}{Important text}'
            },
            '\\textbf': {
                'syntax': '\\textbf{bold text}',
                'description': 'Makes text bold',
                'category': 'formatting',
                'package': 'latex',
                'example': '\\textbf{Bold text}'
            },
            '\\textit': {
                'syntax': '\\textit{italic text}',
                'description': 'Makes text italic',
                'category': 'formatting',
                'package': 'latex',
                'example': '\\textit{Italic text}'
            },
            '\\begin': {
                'syntax': '\\begin{environment} ... \\end{environment}',
                'description': 'Starts an environment block',
                'category': 'structure',
                'package': 'latex',
                'example': '\\begin{document}...\\end{document}'
            },
            '\\end': {
                'syntax': '\\end{environment}',
                'description': 'Ends an environment block',
                'category': 'structure',
                'package': 'latex',
                'example': '\\end{document}'
            },
            '\\item': {
                'syntax': '\\item item text',
                'description': 'Creates a list item',
                'category': 'lists',
                'package': 'latex',
                'example': '\\item First item'
            },
            '\\includegraphics': {
                'syntax': '\\includegraphics[options]{filename}',
                'description': 'Includes an image file',
                'category': 'graphics',
                'package': 'graphicx',
                'example': '\\includegraphics[width=0.5\\textwidth]{image.png}'
            },
            '\\movie': {
                'syntax': '\\movie[options]{poster}{video}',
                'description': 'Embeds a multimedia file',
                'category': 'media',
                'package': 'multimedia',
                'example': '\\movie[width=8cm,height=6cm]{poster.jpg}{video.mp4}'
            },
            '\\href': {
                'syntax': '\\href{url}{link text}',
                'description': 'Creates a hyperlink',
                'category': 'hyperlinks',
                'package': 'hyperref',
                'example': '\\href{https://example.com}{Visit Example}'
            },
            '\\note': {
                'syntax': '\\note{note content}',
                'description': 'Adds speaker notes',
                'category': 'notes',
                'package': 'beamer',
                'example': '\\note{Remember to emphasize this point}'
            },
            '\\pause': {
                'syntax': '\\pause',
                'description': 'Pauses between overlay items',
                'category': 'overlays',
                'package': 'beamer',
                'example': 'First line\\pause\\Second line'
            },
            '\\only': {
                'syntax': '\\only<overlay>{content}',
                'description': 'Shows content only on specified overlays',
                'category': 'overlays',
                'package': 'beamer',
                'example': '\\only<2>{This appears on slide 2}'
            },
            '\\alert': {
                'syntax': '\\alert{highlighted text}',
                'description': 'Highlights text for emphasis',
                'category': 'formatting',
                'package': 'beamer',
                'example': '\\alert{Important!}'
            }
        }

        # Add symbols to commands database
        for symbol, info in self.symbols_db.symbols.items():
            if symbol not in self.commands_db:
                self.commands_db[symbol] = {
                    'syntax': info.get('syntax', symbol),
                    'description': info.get('description', 'LaTeX symbol'),
                    'category': info.get('category', 'symbol'),
                    'package': 'latex',
                    'symbol': info.get('symbol', ''),
                    'example': self._generate_example(symbol, info)
                }

        # Try to load cached online data
        self.load_cached_online_data()

    def _generate_example(self, command: str, info: Dict) -> str:
        """Generate example usage for a command"""
        if 'syntax' in info:
            return info['syntax']

        symbol = info.get('symbol', '')
        if symbol:
            return f'{command} → {symbol}'

        return f'Use: {command}'

    def load_cached_online_data(self):
        """Load cached online command help"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)

                # Check if cache is still valid
                from datetime import datetime, timedelta
                cache_date = datetime.fromisoformat(cache_data.get('cache_date', ''))
                if datetime.now() - cache_date < timedelta(days=self.cache_expiry_days):
                    self.commands_db.update(cache_data.get('commands', {}))
        except:
            pass  # Use basic database if cache fails

    def save_cache(self):
        """Save online data to cache"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_data = {
                'cache_date': datetime.now().isoformat(),
                'commands': {k: v for k, v in self.commands_db.items()
                           if v.get('source') == 'online'}
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except:
            pass

    def get_command_help(self, command: str) -> Optional[Dict]:
        """Get help for a LaTeX command with online fallback"""
        # Clean the command (remove arguments, etc.)
        base_command = command.split('{')[0] if '{' in command else command
        base_command = base_command.split('[')[0] if '[' in command else base_command

        if base_command in self.commands_db:
            return self.commands_db[base_command]

        # Try to fetch from online if not found locally
        return self.fetch_online_help(base_command)

    def fetch_online_help(self, command: str) -> Dict:
        """Fetch command help from online resources"""
        try:
            # Try CTAN first
            ctan_url = f"https://ctan.org/pkg/{command.strip('\\')}"

            # Create a basic entry (in real implementation, you'd parse CTAN)
            help_info = {
                'syntax': f'{command}{{...}}',
                'description': f'LaTeX command: {command}',
                'category': 'unknown',
                'package': 'unknown',
                'source': 'online',
                'url': ctan_url,
                'example': f'Example usage of {command}'
            }

            # Add to database
            self.commands_db[command] = help_info
            self.save_cache()

            return help_info

        except Exception as e:
            # Fallback basic info
            return {
                'syntax': f'{command}{{...}}',
                'description': f'LaTeX command',
                'category': 'general',
                'package': 'latex',
                'example': f'Use {command} in your document'
            }

    def get_autocomplete_suggestions(self, partial_command: str, max_results: int = 10) -> List[Tuple[str, str]]:
        """Get autocomplete suggestions for partial command"""
        suggestions = []
        partial_lower = partial_command.lower()

        for cmd, info in self.commands_db.items():
            if cmd.lower().startswith(partial_lower):
                description = info.get('description', 'LaTeX command')
                suggestions.append((cmd, description))

            if len(suggestions) >= max_results:
                break

        # If not enough prefix matches, search in descriptions
        if len(suggestions) < max_results:
            for cmd, info in self.commands_db.items():
                if (partial_lower in cmd.lower() or
                    partial_lower in info.get('description', '').lower()) and cmd not in [s[0] for s in suggestions]:
                    description = info.get('description', 'LaTeX command')
                    suggestions.append((cmd, description))

                if len(suggestions) >= max_results:
                    break

        return suggestions

    def get_symbols_by_category(self, category: str) -> List[Tuple[str, str]]:
        """Get symbols by category with their visual representation"""
        symbols = []
        for cmd in self.symbols_db.get_symbols_by_category(category):
            info = self.symbols_db.symbols[cmd]
            symbol = info.get('symbol', '')
            description = info.get('description', '')
            symbols.append((cmd, symbol, description))
        return symbols

    def search_commands(self, query: str, max_results: int = 20) -> List[Tuple[str, Dict]]:
        """Search commands and symbols by query"""
        results = []
        query_lower = query.lower()

        # Search in commands database
        for cmd, info in self.commands_db.items():
            if (query_lower in cmd.lower() or
                query_lower in info.get('description', '').lower() or
                query_lower in info.get('category', '').lower()):
                results.append((cmd, info))

            if len(results) >= max_results:
                break

        return results
class LatexAutocomplete:
    """Autocomplete system for LaTeX commands"""

    def __init__(self, helper: LatexCommandHelper):
        self.helper = helper
        self.current_suggestions = []
        self.selected_index = 0

    def get_suggestions(self, text: str, cursor_position: int) -> List[Tuple[str, str]]:
        """Get suggestions based on current text and cursor position"""
        # Extract the current word being typed
        line_start = text.rfind('\n', 0, cursor_position) + 1
        current_line = text[line_start:cursor_position]

        # Find the start of the current command
        backslash_pos = current_line.rfind('\\')
        if backslash_pos == -1:
            return []

        partial_command = current_line[backslash_pos:]
        return self.helper.get_autocomplete_suggestions(partial_command)

    def complete_command(self, text: str, cursor_position: int, suggestion: str) -> Tuple[str, int]:
        """Complete the command with the selected suggestion"""
        line_start = text.rfind('\n', 0, cursor_position) + 1
        current_line = text[line_start:cursor_position]

        backslash_pos = current_line.rfind('\\')
        if backslash_pos == -1:
            return text, cursor_position

        # Replace the partial command with the full command
        new_text = text[:line_start + backslash_pos] + suggestion + text[cursor_position:]
        new_cursor = line_start + backslash_pos + len(suggestion)

        return new_text, new_cursor
class CommandTooltip:
    """Enhanced tooltip for LaTeX command help with symbols"""

    def __init__(self, parent):
        self.parent = parent
        self.tooltip = None
        self.helper = LatexCommandHelper()
        self.autocomplete = LatexAutocomplete(self.helper)

    def show_tooltip(self, widget, command, x, y):
        """Show command help tooltip"""
        self.hide_tooltip()

        help_info = self.helper.get_command_help(command)
        if not help_info:
            return

        # Create tooltip content
        content = self.format_tooltip_content(command, help_info)

        # Create tooltip window
        self.tooltip = tk.Toplevel(widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x+20}+{y+20}")

        # Style the tooltip
        self.tooltip.configure(background='#FFFFE0', relief='solid', borderwidth=1)

        # Create content with better formatting
        frame = tk.Frame(self.tooltip, background='#FFFFE0', padx=10, pady=10)
        frame.pack(fill='both', expand=True)

        # Command title
        title_label = tk.Label(frame, text=f"Command: {command}",
                              font=('Arial', 11, 'bold'),
                              background='#FFFFE0', justify='left')
        title_label.pack(anchor='w')

        # Syntax
        syntax_label = tk.Label(frame, text=f"Syntax: {help_info.get('syntax', 'Unknown')}",
                               font=('Arial', 10),
                               background='#FFFFE0', justify='left')
        syntax_label.pack(anchor='w', pady=(5,0))

        # Description
        desc_label = tk.Label(frame, text=f"Description: {help_info.get('description', 'No description')}",
                             font=('Arial', 10),
                             background='#FFFFE0', justify='left', wraplength=300)
        desc_label.pack(anchor='w', pady=(5,0))

        # Example
        if 'example' in help_info:
            example_label = tk.Label(frame, text=f"Example: {help_info['example']}",
                                   font=('Arial', 9, 'italic'),
                                   background='#FFFFE0', justify='left', wraplength=300)
            example_label.pack(anchor='w', pady=(5,0))

        # Category and package
        meta_text = f"Category: {help_info.get('category', 'General')} | Package: {help_info.get('package', 'LaTeX')}"
        meta_label = tk.Label(frame, text=meta_text,
                             font=('Arial', 9),
                             background='#FFFFE0', justify='left')
        meta_label.pack(anchor='w', pady=(5,0))

        # URL if available
        if 'url' in help_info:
            url_label = tk.Label(frame, text=f"Docs: {help_info['url']}",
                               font=('Arial', 9), fg='blue', cursor='hand2',
                               background='#FFFFE0', justify='left')
            url_label.pack(anchor='w', pady=(5,0))
            url_label.bind('<Button-1>', lambda e: webbrowser.open(help_info['url']))

        # Make tooltip disappear when mouse leaves
        widget.bind('<Leave>', lambda e: self.hide_tooltip())

    def format_tooltip_content(self, command, help_info):
        """Format tooltip content (legacy method)"""
        lines = [
            f"Command: {command}",
            f"Syntax: {help_info.get('syntax', 'Unknown')}",
            f"Description: {help_info.get('description', 'No description available')}",
            f"Category: {help_info.get('category', 'General')}",
            f"Package: {help_info.get('package', 'LaTeX')}"
        ]

        if 'example' in help_info:
            lines.append(f"Example: {help_info['example']}")

        if 'url' in help_info:
            lines.append(f"Docs: {help_info['url']}")

        return '\n'.join(lines)

    def hide_tooltip(self):
        """Hide the tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def show_autocomplete(self, widget, text, cursor_position, x, y):
        """Show autocomplete suggestions"""
        self.hide_tooltip()

        suggestions = self.autocomplete.get_suggestions(text, cursor_position)
        if not suggestions:
            return

        self.current_suggestions = suggestions

        # Create autocomplete window
        self.tooltip = tk.Toplevel(widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y+20}")

        # Style the autocomplete
        self.tooltip.configure(background='white', relief='solid', borderwidth=1)

        # Create listbox for suggestions
        listbox = tk.Listbox(self.tooltip, font=('Arial', 10),
                            selectbackground='#E0E0E0', selectmode='browse',
                            height=min(len(suggestions), 8))
        listbox.pack()

        # Add suggestions
        for i, (cmd, desc) in enumerate(suggestions):
            listbox.insert(i, f"{cmd} - {desc}")

        listbox.select_set(0)

        # Bind events
        def on_select(event):
            selection = listbox.curselection()
            if selection:
                self.selected_index = selection[0]

        def on_double_click(event):
            selection = listbox.curselection()
            if selection:
                self.complete_selection(widget, selection[0])

        listbox.bind('<<ListboxSelect>>', on_select)
        listbox.bind('<Double-Button-1>', on_double_click)

        # Make autocomplete disappear when focus is lost
        widget.bind('<FocusOut>', lambda e: self.hide_tooltip())

    def complete_selection(self, widget, index):
        """Complete with the selected suggestion"""
        if 0 <= index < len(self.current_suggestions):
            # This would need to be integrated with the text widget
            # For now, just hide the tooltip
            self.hide_tooltip()
class LatexHelpLibrary:
    """Main library class for LaTeX help functionality"""

    def __init__(self):
        self.helper = LatexCommandHelper()
        self.autocomplete = LatexAutocomplete(self.helper)
        self.tooltip = None  # Will be set when attached to a widget

    def attach_to_text_widget(self, text_widget):
        """Attach the help system to a text widget"""
        self.tooltip = CommandTooltip(text_widget)

        # Bind events for tooltips
        text_widget.bind('<KeyRelease>', self._on_key_release)
        text_widget.bind('<Motion>', self._on_motion)

    def _on_key_release(self, event):
        """Handle key release for autocomplete"""
        if event.keysym == 'BackSpace' or event.char == '\\':
            # Trigger autocomplete
            widget = event.widget
            cursor_pos = widget.index(tk.INSERT)
            text = widget.get('1.0', tk.END)

            # Get cursor position in characters
            line, col = map(int, cursor_pos.split('.'))
            pos = widget.count('1.0', '1.0', cursor_pos)[0]

            self.tooltip.show_autocomplete(widget, text, pos, event.x, event.y)

    def _on_motion(self, event):
        """Handle mouse motion for tooltips"""
        widget = event.widget
        cursor_pos = widget.index(f"@{event.x},{event.y}")

        # Get the word under cursor
        word_start = widget.index(f"{cursor_pos} wordstart")
        word_end = widget.index(f"{cursor_pos} wordend")
        word = widget.get(word_start, word_end)

        if word.startswith('\\'):
            # Show tooltip for LaTeX command
            self.tooltip.show_tooltip(widget, word, event.x_root, event.y_root)
        else:
            self.tooltip.hide_tooltip()


class LatexSymbolsDatabase:
    """Database of LaTeX symbols and mathematical constructs"""

    def __init__(self):
        self.symbols = self._load_symbols()
        self.categories = self._categorize_symbols()

    def _load_symbols(self) -> Dict[str, Dict]:
        """Load all LaTeX symbols from the PDF content"""
        symbols = {
            # Greek letters
            '\\alpha': {'symbol': 'α', 'category': 'greek', 'description': 'Greek letter alpha'},
            '\\beta': {'symbol': 'β', 'category': 'greek', 'description': 'Greek letter beta'},
            '\\gamma': {'symbol': 'γ', 'category': 'greek', 'description': 'Greek letter gamma'},
            '\\delta': {'symbol': 'δ', 'category': 'greek', 'description': 'Greek letter delta'},
            '\\epsilon': {'symbol': 'ϵ', 'category': 'greek', 'description': 'Greek letter epsilon'},
            '\\zeta': {'symbol': 'ζ', 'category': 'greek', 'description': 'Greek letter zeta'},
            '\\eta': {'symbol': 'η', 'category': 'greek', 'description': 'Greek letter eta'},
            '\\theta': {'symbol': 'θ', 'category': 'greek', 'description': 'Greek letter theta'},
            '\\iota': {'symbol': 'ι', 'category': 'greek', 'description': 'Greek letter iota'},
            '\\kappa': {'symbol': 'κ', 'category': 'greek', 'description': 'Greek letter kappa'},
            '\\lambda': {'symbol': 'λ', 'category': 'greek', 'description': 'Greek letter lambda'},
            '\\mu': {'symbol': 'μ', 'category': 'greek', 'description': 'Greek letter mu'},
            '\\nu': {'symbol': 'ν', 'category': 'greek', 'description': 'Greek letter nu'},
            '\\xi': {'symbol': 'ξ', 'category': 'greek', 'description': 'Greek letter xi'},
            '\\pi': {'symbol': 'π', 'category': 'greek', 'description': 'Greek letter pi'},
            '\\rho': {'symbol': 'ρ', 'category': 'greek', 'description': 'Greek letter rho'},
            '\\sigma': {'symbol': 'σ', 'category': 'greek', 'description': 'Greek letter sigma'},
            '\\tau': {'symbol': 'τ', 'category': 'greek', 'description': 'Greek letter tau'},
            '\\upsilon': {'symbol': 'υ', 'category': 'greek', 'description': 'Greek letter upsilon'},
            '\\phi': {'symbol': 'φ', 'category': 'greek', 'description': 'Greek letter phi'},
            '\\chi': {'symbol': 'χ', 'category': 'greek', 'description': 'Greek letter chi'},
            '\\psi': {'symbol': 'ψ', 'category': 'greek', 'description': 'Greek letter psi'},
            '\\omega': {'symbol': 'ω', 'category': 'greek', 'description': 'Greek letter omega'},

            # Mathematical constructs
            '\\frac': {'syntax': '\\frac{numerator}{denominator}', 'category': 'math', 'description': 'Fraction'},
            '\\sqrt': {'syntax': '\\sqrt{expression}', 'category': 'math', 'description': 'Square root'},
            '\\overline': {'syntax': '\\overline{expression}', 'category': 'math', 'description': 'Overline'},
            '\\underline': {'syntax': '\\underline{expression}', 'category': 'math', 'description': 'Underline'},
            '\\overrightarrow': {'syntax': '\\overrightarrow{expression}', 'category': 'math', 'description': 'Right arrow over'},
            '\\overleftarrow': {'syntax': '\\overleftarrow{expression}', 'category': 'math', 'description': 'Left arrow over'},
            '\\widehat': {'syntax': '\\widehat{expression}', 'category': 'math', 'description': 'Wide hat'},
            '\\widetilde': {'syntax': '\\widetilde{expression}', 'category': 'math', 'description': 'Wide tilde'},

            # Delimiters
            '\\left': {'syntax': '\\left delimiter', 'category': 'delimiters', 'description': 'Left delimiter'},
            '\\right': {'syntax': '\\right delimiter', 'category': 'delimiters', 'description': 'Right delimiter'},
            '\\lfloor': {'symbol': '⌊', 'category': 'delimiters', 'description': 'Left floor'},
            '\\rfloor': {'symbol': '⌋', 'category': 'delimiters', 'description': 'Right floor'},
            '\\lceil': {'symbol': '⌈', 'category': 'delimiters', 'description': 'Left ceiling'},
            '\\rceil': {'symbol': '⌉', 'category': 'delimiters', 'description': 'Right ceiling'},

            # Big operators
            '\\sum': {'symbol': '∑', 'category': 'operators', 'description': 'Summation'},
            '\\prod': {'symbol': '∏', 'category': 'operators', 'description': 'Product'},
            '\\int': {'symbol': '∫', 'category': 'operators', 'description': 'Integral'},
            '\\oint': {'symbol': '∮', 'category': 'operators', 'description': 'Contour integral'},

            # Binary operators
            '\\pm': {'symbol': '±', 'category': 'operators', 'description': 'Plus-minus'},
            '\\mp': {'symbol': '∓', 'category': 'operators', 'description': 'Minus-plus'},
            '\\times': {'symbol': '×', 'category': 'operators', 'description': 'Multiplication'},
            '\\div': {'symbol': '÷', 'category': 'operators', 'description': 'Division'},
            '\\cdot': {'symbol': '·', 'category': 'operators', 'description': 'Dot operator'},
            '\\ast': {'symbol': '∗', 'category': 'operators', 'description': 'Asterisk operator'},
            '\\circ': {'symbol': '∘', 'category': 'operators', 'description': 'Circle operator'},

            # Relations
            '\\leq': {'symbol': '≤', 'category': 'relations', 'description': 'Less than or equal'},
            '\\geq': {'symbol': '≥', 'category': 'relations', 'description': 'Greater than or equal'},
            '\\neq': {'symbol': '≠', 'category': 'relations', 'description': 'Not equal'},
            '\\approx': {'symbol': '≈', 'category': 'relations', 'description': 'Approximately equal'},
            '\\equiv': {'symbol': '≡', 'category': 'relations', 'description': 'Equivalent'},
            '\\in': {'symbol': '∈', 'category': 'relations', 'description': 'Element of'},
            '\\subset': {'symbol': '⊂', 'category': 'relations', 'description': 'Subset'},
            '\\subseteq': {'symbol': '⊆', 'category': 'relations', 'description': 'Subset or equal'},

            # Arrows
            '\\leftarrow': {'symbol': '←', 'category': 'arrows', 'description': 'Left arrow'},
            '\\rightarrow': {'symbol': '→', 'category': 'arrows', 'description': 'Right arrow'},
            '\\uparrow': {'symbol': '↑', 'category': 'arrows', 'description': 'Up arrow'},
            '\\downarrow': {'symbol': '↓', 'category': 'arrows', 'description': 'Down arrow'},
            '\\Leftarrow': {'symbol': '⇐', 'category': 'arrows', 'description': 'Double left arrow'},
            '\\Rightarrow': {'symbol': '⇒', 'category': 'arrows', 'description': 'Double right arrow'},
            '\\leftrightarrow': {'symbol': '↔', 'category': 'arrows', 'description': 'Left-right arrow'},
            '\\mapsto': {'symbol': '↦', 'category': 'arrows', 'description': 'Maps to'},

            # Miscellaneous
            '\\infty': {'symbol': '∞', 'category': 'misc', 'description': 'Infinity'},
            '\\partial': {'symbol': '∂', 'category': 'misc', 'description': 'Partial derivative'},
            '\\nabla': {'symbol': '∇', 'category': 'misc', 'description': 'Nabla'},
            '\\forall': {'symbol': '∀', 'category': 'misc', 'description': 'For all'},
            '\\exists': {'symbol': '∃', 'category': 'misc', 'description': 'There exists'},
            '\\emptyset': {'symbol': '∅', 'category': 'misc', 'description': 'Empty set'},
            '\\angle': {'symbol': '∠', 'category': 'misc', 'description': 'Angle'},

            # Function names
            '\\sin': {'syntax': '\\sin x', 'category': 'functions', 'description': 'Sine function'},
            '\\cos': {'syntax': '\\cos x', 'category': 'functions', 'description': 'Cosine function'},
            '\\tan': {'syntax': '\\tan x', 'category': 'functions', 'description': 'Tangent function'},
            '\\log': {'syntax': '\\log x', 'category': 'functions', 'description': 'Logarithm'},
            '\\ln': {'syntax': '\\ln x', 'category': 'functions', 'description': 'Natural logarithm'},
            '\\lim': {'syntax': '\\lim_{x \\to a} f(x)', 'category': 'functions', 'description': 'Limit'},
            '\\exp': {'syntax': '\\exp x', 'category': 'functions', 'description': 'Exponential'},

            # Array and matrix
            '\\begin': {'syntax': '\\begin{environment}...\\end{environment}', 'category': 'environments', 'description': 'Begin environment'},
            '\\end': {'syntax': '\\end{environment}', 'category': 'environments', 'description': 'End environment'},
            '\\array': {'syntax': '\\begin{array}{cols}...\\end{array}', 'category': 'environments', 'description': 'Array environment'},

            # Text formatting
            '\\textbf': {'syntax': '\\textbf{bold text}', 'category': 'formatting', 'description': 'Bold text'},
            '\\textit': {'syntax': '\\textit{italic text}', 'category': 'formatting', 'description': 'Italic text'},
            '\\textcolor': {'syntax': '\\textcolor{color}{text}', 'category': 'formatting', 'description': 'Colored text'},

            # Accents
            '\\acute': {'syntax': '\\acute{a}', 'category': 'accents', 'description': 'Acute accent'},
            '\\grave': {'syntax': '\\grave{a}', 'category': 'accents', 'description': 'Grave accent'},
            '\\hat': {'syntax': '\\hat{a}', 'category': 'accents', 'description': 'Hat accent'},
            '\\tilde': {'syntax': '\\tilde{a}', 'category': 'accents', 'description': 'Tilde accent'},
            '\\dot': {'syntax': '\\dot{a}', 'category': 'accents', 'description': 'Dot accent'},
            '\\ddot': {'syntax': '\\ddot{a}', 'category': 'accents', 'description': 'Double dot accent'},
        }
        return symbols

    def _categorize_symbols(self) -> Dict[str, List[str]]:
        """Categorize symbols for easy retrieval"""
        categories = {}
        for cmd, info in self.symbols.items():
            category = info.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(cmd)
        return categories

    def get_symbols_by_category(self, category: str) -> List[str]:
        """Get all symbols in a category"""
        return self.categories.get(category, [])

    def search_symbols(self, query: str) -> List[Tuple[str, Dict]]:
        """Search symbols by name or description"""
        results = []
        query = query.lower()
        for cmd, info in self.symbols.items():
            if (query in cmd.lower() or
                query in info.get('description', '').lower() or
                query in info.get('category', '').lower()):
                results.append((cmd, info))
        return results

class LatexCommandHelper:
    """Enhanced LaTeX command help system with symbols and autocompletion"""

    def __init__(self):
        self.commands_db = {}
        self.symbols_db = LatexSymbolsDatabase()
        self.cache_file = Path.home() / '.bsg-ide' / 'latex_help_cache.json'
        self.cache_expiry_days = 30
        self.load_local_database()

    def load_local_database(self):
        """Load local LaTeX command database with enhanced content"""
        # Basic LaTeX commands database
        self.commands_db = {
            '\\title': {
                'syntax': '\\title{title text}',
                'description': 'Sets the presentation title',
                'category': 'document',
                'package': 'beamer',
                'example': '\\title{My Presentation}'
            },
            '\\author': {
                'syntax': '\\author{author name}',
                'description': 'Sets the author name',
                'category': 'document',
                'package': 'beamer',
                'example': '\\author{John Doe}'
            },
            '\\institute': {
                'syntax': '\\institute{institution name}',
                'description': 'Sets the institution name',
                'category': 'document',
                'package': 'beamer',
                'example': '\\institute{University of Example}'
            },
            '\\date': {
                'syntax': '\\date{date}',
                'description': 'Sets the presentation date',
                'category': 'document',
                'package': 'beamer',
                'example': '\\date{\\today}'
            },
            '\\frametitle': {
                'syntax': '\\frametitle{slide title}',
                'description': 'Sets the frame/slide title',
                'category': 'frame',
                'package': 'beamer',
                'example': '\\frametitle{Introduction}'
            },
            '\\file': {
                'syntax': '\\file{media_files/filename.ext}',
                'description': 'Includes an image or media file',
                'category': 'media',
                'package': 'beamer',
                'example': '\\file{images/photo.jpg}'
            },
            '\\play': {
                'syntax': '\\play{media_files/video.ext}',
                'description': 'Embeds a playable video',
                'category': 'media',
                'package': 'beamer',
                'example': '\\play{videos/demo.mp4}'
            },
            '\\textcolor': {
                'syntax': '\\textcolor{color}{text} or \\textcolor[RGB]{r,g,b}{text}',
                'description': 'Changes text color',
                'category': 'formatting',
                'package': 'xcolor',
                'example': '\\textcolor{red}{Important text}'
            },
            '\\textbf': {
                'syntax': '\\textbf{bold text}',
                'description': 'Makes text bold',
                'category': 'formatting',
                'package': 'latex',
                'example': '\\textbf{Bold text}'
            },
            '\\textit': {
                'syntax': '\\textit{italic text}',
                'description': 'Makes text italic',
                'category': 'formatting',
                'package': 'latex',
                'example': '\\textit{Italic text}'
            },
            '\\begin': {
                'syntax': '\\begin{environment} ... \\end{environment}',
                'description': 'Starts an environment block',
                'category': 'structure',
                'package': 'latex',
                'example': '\\begin{document}...\\end{document}'
            },
            '\\end': {
                'syntax': '\\end{environment}',
                'description': 'Ends an environment block',
                'category': 'structure',
                'package': 'latex',
                'example': '\\end{document}'
            },
            '\\item': {
                'syntax': '\\item item text',
                'description': 'Creates a list item',
                'category': 'lists',
                'package': 'latex',
                'example': '\\item First item'
            },
            '\\includegraphics': {
                'syntax': '\\includegraphics[options]{filename}',
                'description': 'Includes an image file',
                'category': 'graphics',
                'package': 'graphicx',
                'example': '\\includegraphics[width=0.5\\textwidth]{image.png}'
            },
            '\\movie': {
                'syntax': '\\movie[options]{poster}{video}',
                'description': 'Embeds a multimedia file',
                'category': 'media',
                'package': 'multimedia',
                'example': '\\movie[width=8cm,height=6cm]{poster.jpg}{video.mp4}'
            },
            '\\href': {
                'syntax': '\\href{url}{link text}',
                'description': 'Creates a hyperlink',
                'category': 'hyperlinks',
                'package': 'hyperref',
                'example': '\\href{https://example.com}{Visit Example}'
            },
            '\\note': {
                'syntax': '\\note{note content}',
                'description': 'Adds speaker notes',
                'category': 'notes',
                'package': 'beamer',
                'example': '\\note{Remember to emphasize this point}'
            },
            '\\pause': {
                'syntax': '\\pause',
                'description': 'Pauses between overlay items',
                'category': 'overlays',
                'package': 'beamer',
                'example': 'First line\\pause\\Second line'
            },
            '\\only': {
                'syntax': '\\only<overlay>{content}',
                'description': 'Shows content only on specified overlays',
                'category': 'overlays',
                'package': 'beamer',
                'example': '\\only<2>{This appears on slide 2}'
            },
            '\\alert': {
                'syntax': '\\alert{highlighted text}',
                'description': 'Highlights text for emphasis',
                'category': 'formatting',
                'package': 'beamer',
                'example': '\\alert{Important!}'
            }
        }

        # Add symbols to commands database
        for symbol, info in self.symbols_db.symbols.items():
            if symbol not in self.commands_db:
                self.commands_db[symbol] = {
                    'syntax': info.get('syntax', symbol),
                    'description': info.get('description', 'LaTeX symbol'),
                    'category': info.get('category', 'symbol'),
                    'package': 'latex',
                    'symbol': info.get('symbol', ''),
                    'example': self._generate_example(symbol, info)
                }

        # Try to load cached online data
        self.load_cached_online_data()

    def _generate_example(self, command: str, info: Dict) -> str:
        """Generate example usage for a command"""
        if 'syntax' in info:
            return info['syntax']

        symbol = info.get('symbol', '')
        if symbol:
            return f'{command} → {symbol}'

        return f'Use: {command}'

    def load_cached_online_data(self):
        """Load cached online command help"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)

                # Check if cache is still valid
                from datetime import datetime, timedelta
                cache_date = datetime.fromisoformat(cache_data.get('cache_date', ''))
                if datetime.now() - cache_date < timedelta(days=self.cache_expiry_days):
                    self.commands_db.update(cache_data.get('commands', {}))
        except:
            pass  # Use basic database if cache fails

    def save_cache(self):
        """Save online data to cache"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_data = {
                'cache_date': datetime.now().isoformat(),
                'commands': {k: v for k, v in self.commands_db.items()
                           if v.get('source') == 'online'}
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except:
            pass

    def get_command_help(self, command: str) -> Optional[Dict]:
        """Get help for a LaTeX command with online fallback"""
        # Clean the command (remove arguments, etc.)
        base_command = command.split('{')[0] if '{' in command else command
        base_command = base_command.split('[')[0] if '[' in command else base_command

        if base_command in self.commands_db:
            return self.commands_db[base_command]

        # Try to fetch from online if not found locally
        return self.fetch_online_help(base_command)

    def fetch_online_help(self, command: str) -> Dict:
        """Fetch command help from online resources"""
        try:
            # Try CTAN first
            ctan_url = f"https://ctan.org/pkg/{command.strip('\\')}"

            # Create a basic entry (in real implementation, you'd parse CTAN)
            help_info = {
                'syntax': f'{command}{{...}}',
                'description': f'LaTeX command: {command}',
                'category': 'unknown',
                'package': 'unknown',
                'source': 'online',
                'url': ctan_url,
                'example': f'Example usage of {command}'
            }

            # Add to database
            self.commands_db[command] = help_info
            self.save_cache()

            return help_info

        except Exception as e:
            # Fallback basic info
            return {
                'syntax': f'{command}{{...}}',
                'description': f'LaTeX command',
                'category': 'general',
                'package': 'latex',
                'example': f'Use {command} in your document'
            }

    def get_autocomplete_suggestions(self, partial_command: str, max_results: int = 10) -> List[Tuple[str, str]]:
        """Get autocomplete suggestions for partial command"""
        suggestions = []
        partial_lower = partial_command.lower()

        for cmd, info in self.commands_db.items():
            if cmd.lower().startswith(partial_lower):
                description = info.get('description', 'LaTeX command')
                suggestions.append((cmd, description))

            if len(suggestions) >= max_results:
                break

        # If not enough prefix matches, search in descriptions
        if len(suggestions) < max_results:
            for cmd, info in self.commands_db.items():
                if (partial_lower in cmd.lower() or
                    partial_lower in info.get('description', '').lower()) and cmd not in [s[0] for s in suggestions]:
                    description = info.get('description', 'LaTeX command')
                    suggestions.append((cmd, description))

                if len(suggestions) >= max_results:
                    break

        return suggestions

    def get_symbols_by_category(self, category: str) -> List[Tuple[str, str]]:
        """Get symbols by category with their visual representation"""
        symbols = []
        for cmd in self.symbols_db.get_symbols_by_category(category):
            info = self.symbols_db.symbols[cmd]
            symbol = info.get('symbol', '')
            description = info.get('description', '')
            symbols.append((cmd, symbol, description))
        return symbols

    def search_commands(self, query: str, max_results: int = 20) -> List[Tuple[str, Dict]]:
        """Search commands and symbols by query"""
        results = []
        query_lower = query.lower()

        # Search in commands database
        for cmd, info in self.commands_db.items():
            if (query_lower in cmd.lower() or
                query_lower in info.get('description', '').lower() or
                query_lower in info.get('category', '').lower()):
                results.append((cmd, info))

            if len(results) >= max_results:
                break

        return results

class IntelligentAutocomplete:
    """Intelligent autocomplete system for LaTeX commands with enhanced module integration"""

    def __init__(self, parent):
        self.parent = parent
        self.autocomplete_window = None
        self.suggestions = []
        self.current_suggestion_index = 0
        self.command_database = {}
        self.selected_widget = None
        self.ignore_next_click = False
        self.last_key_time = 0
        self.update_pending = False
        self.last_command_text = ""  # Track last command to avoid redundant updates

        # Try to use enhanced LatexHelp module, fallback to basic
        self.setup_autocomplete_system()

    def setup_autocomplete_system(self):
        """Setup the appropriate autocomplete system"""
        try:
            from LatexHelp import LatexAutocomplete, LatexCommandHelper
            self.enhanced_system = LatexAutocomplete(LatexCommandHelper())
            self.use_enhanced = True
            print("✓ Enhanced LaTeX autocomplete system loaded")
        except ImportError as e:
            print(f"Using basic autocomplete system: {e}")
            self.enhanced_system = None
            self.use_enhanced = False
            self.command_database = self.build_autocomplete_database()

    def build_autocomplete_database(self):
        """Build database for autocomplete suggestions (fallback)"""
        return {
            '\\begin': {
                'completion': '\\begin{$1}\n$2\n\\end{$1}',
                'description': 'Begin environment block',
                'type': 'environment_starter',
                'pairs': {
                    'itemize': '\\begin{itemize}\n\\item $1\n\\end{itemize}',
                    'enumerate': '\\begin{enumerate}\n\\item $1\n\\end{enumerate}',
                    'frame': '\\begin{frame}{$1}\n$2\n\\end{frame}',
                    'columns': '\\begin{columns}\n\\column{0.5\\textwidth}\n$1\n\\column{0.5\\textwidth}\n$2\n\\end{columns}',
                    'block': '\\begin{block}{$1}\n$2\n\\end{block}',
                    'exampleblock': '\\begin{exampleblock}{$1}\n$2\n\\end{exampleblock}',
                    'alertblock': '\\begin{alertblock}{$1}\n$2\n\\end{alertblock}',
                    'theorem': '\\begin{theorem}{$1}\n$2\n\\end{theorem}',
                    'proof': '\\begin{proof}\n$1\n\\end{proof}',
                    'figure': '\\begin{figure}\n\\centering\n\\includegraphics[width=0.8\\textwidth]{$1}\n\\caption{$2}\n\\label{fig:$3}\n\\end{figure}',
                    'table': '\\begin{table}\n\\centering\n\\begin{tabular}{$1}\n$2\n\\end{tabular}\n\\caption{$3}\n\\label{tab:$4}\n\\end{table}',
                    'equation': '\\begin{equation}\n$1\n\\end{equation}',
                    'align': '\\begin{align}\n$1\n\\end{align}',
                    'matrix': '\\begin{matrix}\n$1\n\\end{matrix}',
                    'cases': '\\begin{cases}\n$1\n\\end{cases}'
                }
            },
            '\\end': {
                'completion': '\\end{$1}',
                'description': 'End environment block',
                'type': 'environment_ender'
            },
            '\\item': {
                'completion': '\\item $1',
                'description': 'List item',
                'context': ['itemize', 'enumerate']
            },
            '\\title': {
                'completion': '\\title{$1}',
                'description': 'Presentation title'
            },
            '\\author': {
                'completion': '\\author{$1}',
                'description': 'Author name'
            },
            '\\institute': {
                'completion': '\\institute{$1}',
                'description': 'Institute name'
            },
            '\\frametitle': {
                'completion': '\\frametitle{$1}',
                'description': 'Frame title'
            },
            '\\file': {
                'completion': '\\file{media_files/$1}',
                'description': 'Insert image file'
            },
            '\\play': {
                'completion': '\\play{media_files/$1}',
                'description': 'Play media file'
            },
            '\\textcolor': {
                'completion': '\\textcolor{$1}{$2}',
                'description': 'Colored text'
            },
            '\\only': {
                'completion': '\\only<$1>{$2}',
                'description': 'Content visible only on specific slides'
            },
            '\\uncover': {
                'completion': '\\uncover<$1>{$2}',
                'description': 'Uncover content on specific slides'
            },
            '\\pause': {
                'completion': '\\pause',
                'description': 'Pause between slide content'
            },
            '\\note': {
                'completion': '\\note{$1}',
                'description': 'Speaker notes'
            },
            '\\alert': {
                'completion': '\\alert{$1}',
                'description': 'Alert highlighted text'
            },
            '\\textbf': {
                'completion': '\\textbf{$1}',
                'description': 'Bold text'
            },
            '\\textit': {
                'completion': '\\textit{$1}',
                'description': 'Italic text'
            },
            '\\href': {
                'completion': '\\href{$1}{$2}',
                'description': 'Hyperlink'
            },
            '\\section': {
                'completion': '\\section{$1}',
                'description': 'Section heading'
            },
            '\\subsection': {
                'completion': '\\subsection{$1}',
                'description': 'Subsection heading'
            },
            '\\caption': {
                'completion': '\\caption{$1}',
                'description': 'Figure or table caption'
            },
            '\\label': {
                'completion': '\\label{$1}',
                'description': 'Label for cross-referencing'
            },
            '\\cite': {
                'completion': '\\cite{$1}',
                'description': 'Citation reference'
            },
            '\\footnote': {
                'completion': '\\footnote{$1}',
                'description': 'Footnote'
            },
            '\\emph': {
                'completion': '\\emph{$1}',
                'description': 'Emphasized text'
            },
            '\\underline': {
                'completion': '\\underline{$1}',
                'description': 'Underlined text'
            },
            '\\texttt': {
                'completion': '\\texttt{$1}',
                'description': 'Typewriter text'
            },
            '\\mathbb': {
                'completion': '\\mathbb{$1}',
                'description': 'Blackboard bold (math mode)'
            },
            '\\mathcal': {
                'completion': '\\mathcal{$1}',
                'description': 'Calligraphic font (math mode)'
            },
            '\\mathbf': {
                'completion': '\\mathbf{$1}',
                'description': 'Bold font (math mode)'
            },
            '\\mathrm': {
                'completion': '\\mathrm{$1}',
                'description': 'Roman font (math mode)'
            },
            '\\frac': {
                'completion': '\\frac{$1}{$2}',
                'description': 'Fraction'
            },
            '\\sqrt': {
                'completion': '\\sqrt{$1}',
                'description': 'Square root'
            },
            '\\sum': {
                'completion': '\\sum_{$1}^{$2}',
                'description': 'Summation'
            },
            '\\int': {
                'completion': '\\int_{$1}^{$2}',
                'description': 'Integral'
            },
            '\\lim': {
                'completion': '\\lim_{$1 \\to $2}',
                'description': 'Limit'
            },
            '\\infty': {
                'completion': '\\infty',
                'description': 'Infinity symbol'
            },
            '\\alpha': {
                'completion': '\\alpha',
                'description': 'Greek letter alpha'
            },
            '\\beta': {
                'completion': '\\beta',
                'description': 'Greek letter beta'
            },
            '\\gamma': {
                'completion': '\\gamma',
                'description': 'Greek letter gamma'
            },
            '\\delta': {
                'completion': '\\delta',
                'description': 'Greek letter delta'
            },
            '\\epsilon': {
                'completion': '\\epsilon',
                'description': 'Greek letter epsilon'
            },
            '\\theta': {
                'completion': '\\theta',
                'description': 'Greek letter theta'
            },
            '\\lambda': {
                'completion': '\\lambda',
                'description': 'Greek letter lambda'
            },
            '\\pi': {
                'completion': '\\pi',
                'description': 'Greek letter pi'
            },
            '\\sigma': {
                'completion': '\\sigma',
                'description': 'Greek letter sigma'
            },
            '\\omega': {
                'completion': '\\omega',
                'description': 'Greek letter omega'
            },
            '\\cdot': {
                'completion': '\\cdot',
                'description': 'Multiplication dot'
            },
            '\\times': {
                'completion': '\\times',
                'description': 'Multiplication cross'
            },
            '\\pm': {
                'completion': '\\pm',
                'description': 'Plus-minus symbol'
            },
            '\\mp': {
                'completion': '\\mp',
                'description': 'Minus-plus symbol'
            },
            '\\leq': {
                'completion': '\\leq',
                'description': 'Less than or equal to'
            },
            '\\geq': {
                'completion': '\\geq',
                'description': 'Greater than or equal to'
            },
            '\\neq': {
                'completion': '\\neq',
                'description': 'Not equal to'
            },
            '\\approx': {
                'completion': '\\approx',
                'description': 'Approximately equal to'
            },
            '\\sim': {
                'completion': '\\sim',
                'description': 'Similar to'
            },
            '\\propto': {
                'completion': '\\propto',
                'description': 'Proportional to'
            },
            '\\partial': {
                'completion': '\\partial',
                'description': 'Partial derivative'
            },
            '\\nabla': {
                'completion': '\\nabla',
                'description': 'Nabla operator'
            },
            '\\ldots': {
                'completion': '\\ldots',
                'description': 'Lower dots'
            },
            '\\cdots': {
                'completion': '\\cdots',
                'description': 'Center dots'
            },
            '\\vdots': {
                'completion': '\\vdots',
                'description': 'Vertical dots'
            },
             '\\inlineimg': {
                'completion': '\\inlineimg[$1]{$2}',
                'description': 'Inline image within text flow',
                'type': 'inline_image'
            },
            '\\ddots': {
                'completion': '\\ddots',
                'description': 'Diagonal dots'
            }
        }

    def setup_autocomplete(self, text_widget):
        """Setup autocomplete for a text widget - TARGETED approach"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'setup_autocomplete'):
            self.enhanced_system.setup_autocomplete(text_widget)
        else:
            # TARGETED binding - only trigger on specific keys
            text_widget.bind('<KeyPress>', self.on_key_pressed_targeted, add='+')
            text_widget.bind('<KeyRelease>', self.on_key_release_targeted, add='+')
            text_widget.bind('<Tab>', self.on_tab)
            text_widget.bind('<Return>', self.on_return)
            text_widget.bind('<Escape>', self.hide_autocomplete)
            text_widget.bind('<Up>', self.on_arrow_key)
            text_widget.bind('<Down>', self.on_arrow_key)
            text_widget.bind('<Button-1>', self.on_editor_click)
            text_widget.bind('<FocusIn>', self.on_focus_in)

    def on_key_pressed_targeted(self, event):
        """Handle key press - ONLY for backslash and specific triggers"""
        # ONLY trigger on backslash or if autocomplete is already visible
        if event.char == '\\':
            print("Backslash detected - preparing autocomplete")  # Debug
            # Mark that we should trigger autocomplete
            self.should_trigger_autocomplete = True
        elif event.keysym == 'Escape' and self.autocomplete_window:
            self.hide_autocomplete()
            return "break"

        # Let all other keys pass through to spellcheck and other systems
        return None

    def on_key_release_targeted(self, event):
        """Handle key release - ONLY process autocomplete for relevant cases"""
        # Skip modifier keys entirely
        if event.keysym in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R', 'Caps_Lock']:
            return None

        # If we just typed a backslash, trigger autocomplete
        if getattr(self, 'should_trigger_autocomplete', False):
            self.should_trigger_autocomplete = False
            self.trigger_autocomplete_immediately()
            return None

        # If autocomplete is already visible, handle navigation
        if self.autocomplete_window and self.autocomplete_window.winfo_exists():
            if event.keysym in ['Up', 'Down', 'Return', 'Escape']:
                # These are handled by specific bindings
                return None
            # For other keys while autocomplete is visible, update suggestions
            self.parent.after(50, self.process_autocomplete_update)  # Small delay
            return None

        # ONLY process autocomplete if we're likely in a command context
        if self.selected_widget:
            cursor_pos = self.selected_widget.index("insert")
            line_start = self.selected_widget.index(f"{cursor_pos} linestart")
            line_content = self.selected_widget.get(line_start, cursor_pos)

            # ONLY trigger if we have a backslash in the current line
            if '\\' in line_content:
                self.parent.after(100, self.process_autocomplete_update)  # Debounced

        return None

    def trigger_autocomplete_immediately(self):
        """Trigger autocomplete immediately after backslash"""
        if not self.selected_widget:
            return

        widget = self.selected_widget
        cursor_pos = widget.index("insert")
        line_start = widget.index(f"{cursor_pos} linestart")
        line_content = widget.get(line_start, cursor_pos)

        # Only proceed if we actually have a backslash in the line
        if '\\' in line_content:
            self.show_suggestions(widget, '\\', int(cursor_pos.split('.')[1]))

    def detect_autocomplete_opportunity_targeted(self, widget, line_content, cursor_pos):
        """TARGETED command detection - only when clearly in command context"""
        text_before_cursor = line_content[:cursor_pos]
        last_backslash = text_before_cursor.rfind('\\')

        # Only show autocomplete if we have a backslash and it's not too far back
        if last_backslash != -1:
            # Check if backslash is reasonably close to cursor (within same "word")
            chars_since_backslash = cursor_pos - last_backslash
            if chars_since_backslash < 25:  # Reasonable command length
                command_text = text_before_cursor[last_backslash:]

                # Only update if command text changed
                if command_text != self.last_command_text:
                    self.last_command_text = command_text
                    self.show_suggestions(widget, command_text, cursor_pos)
                return

        # No relevant backslash found - hide autocomplete
        self.hide_autocomplete()

    def on_focus_in(self, event):
        """Track which widget has focus"""
        self.selected_widget = event.widget
        print(f"Focus set to: {self.selected_widget}")  # Debug

    def on_editor_click(self, event):
        """Handle click in editor - hide autocomplete immediately"""
        self.hide_autocomplete()

    def on_key_pressed(self, event):
        """Handle key press - IMMEDIATE response"""
        # Show autocomplete immediately when backslash is pressed
        if event.char == '\\':
            print("Backslash detected - showing autocomplete immediately")  # Debug
            # Schedule autocomplete to show after a tiny delay to ensure the backslash is inserted
            self.parent.after(10, self.trigger_autocomplete_immediately)

        # Also handle escape key immediately
        if event.keysym == 'Escape':
            self.hide_autocomplete()

    def trigger_autocomplete_immediately(self):
        """Trigger autocomplete immediately after backslash"""
        if not self.selected_widget:
            return

        widget = self.selected_widget
        cursor_pos = widget.index("insert")
        line_start = widget.index(f"{cursor_pos} linestart")
        line_content = widget.get(line_start, cursor_pos)

        # Look for the backslash we just typed
        if '\\' in line_content:
            self.show_suggestions(widget, '\\', int(cursor_pos.split('.')[1]))

    def on_key_release(self, event):
        """Handle key release for autocomplete - VERY AGGRESSIVE"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'on_key_release'):
            return self.enhanced_system.on_key_release(event)

        # Skip if we're already processing
        if self.update_pending:
            return

        # VERY PERMISSIVE - only skip pure modifier keys
        if event.keysym in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R']:
            return

        # IMMEDIATE processing - no debouncing for backslash and letters
        if event.char and (event.char == '\\' or event.char.isalpha()):
            self.update_pending = True
            self.parent.after(5, self.process_autocomplete_update)  # Very short delay
        else:
            # For other keys, use minimal debouncing
            current_time = time.time() * 1000
            if current_time - self.last_key_time < 10:  # Only 10ms debounce
                return
            self.last_key_time = current_time
            self.update_pending = True
            self.parent.after(5, self.process_autocomplete_update)

    def setup_coexistent_bindings(self, text_widget):
        """Setup bindings that coexist with spellcheck"""
        # Use bind tags to ensure proper ordering
        bind_tags = list(text_widget.bindtags())

        # Add our autocomplete bindtag after the main widget but before class bindings
        if "autocomplete" not in bind_tags:
            bind_tags.insert(1, "autocomplete")
            text_widget.bindtags(tuple(bind_tags))

        # Bind to our specific tag
        text_widget.bind_class("autocomplete", '<KeyPress>', self.on_key_pressed_targeted)
        text_widget.bind_class("autocomplete", '<KeyRelease>', self.on_key_release_targeted)

    def should_process_autocomplete(self, event):
        """Determine if we should process this event for autocomplete"""
        # Ignore pure modifier keys
        if event.keysym in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R']:
            return False

        # Only process if we have a text widget focused and it's editable
        if not self.selected_widget or not hasattr(self.selected_widget, 'get'):
            return False

        # Check if we're in a LaTeX command context
        cursor_pos = self.selected_widget.index("insert")
        line_start = self.selected_widget.index(f"{cursor_pos} linestart")
        line_content = self.selected_widget.get(line_start, cursor_pos)

        return '\\' in line_content

    def process_autocomplete_update(self):
        """Process autocomplete update - VERY AGGRESSIVE"""
        try:
            if not self.selected_widget:
                self.update_pending = False
                return

            widget = self.selected_widget
            cursor_pos = widget.index("insert")
            line_start = widget.index(f"{cursor_pos} linestart")
            line_end = widget.index(f"{cursor_pos} lineend")
            line_content = widget.get(line_start, line_end)
            cursor_in_line = int(cursor_pos.split('.')[1])

            print(f"Processing autocomplete: '{line_content}' at position {cursor_in_line}")  # Debug

            # ALWAYS check for commands, even if no obvious pattern
            self.detect_autocomplete_opportunity_aggressive(widget, line_content, cursor_in_line)
        except Exception as e:
            print(f"Autocomplete error: {e}")  # Debug
        finally:
            self.update_pending = False

    def detect_autocomplete_opportunity_aggressive(self, widget, line_content, cursor_pos):
        """VERY AGGRESSIVE command detection - always show if backslash present"""
        text_before_cursor = line_content[:cursor_pos]
        last_backslash = text_before_cursor.rfind('\\')

        if last_backslash != -1:
            command_text = text_before_cursor[last_backslash:]
            print(f"Found command pattern: '{command_text}'")  # Debug

            # ALWAYS show suggestions if there's a backslash, even for single \
            if command_text == '\\' or self.is_valid_command_pattern(command_text):
                if command_text != self.last_command_text:  # Only update if changed
                    self.last_command_text = command_text
                    self.show_suggestions(widget, command_text, cursor_pos)
                return
            else:
                print(f"Invalid command pattern, hiding: '{command_text}'")  # Debug
                self.hide_autocomplete()
                return

        # No backslash found - hide autocomplete
        print("No backslash found, hiding autocomplete")  # Debug
        self.hide_autocomplete()

    def is_valid_command_pattern(self, command_text):
        """VERY PERMISSIVE pattern detection"""
        if not command_text.startswith('\\'):
            return False

        # Show suggestions for ANY backslash command, even incomplete ones
        return len(command_text) >= 1  # Just having \ is enough!

    def show_suggestions(self, widget, partial_command, cursor_pos):
        """Show autocomplete suggestions - ALWAYS when backslash is present"""
        print(f"Showing suggestions for: '{partial_command}'")  # Debug

        if self.use_enhanced and hasattr(self.enhanced_system, 'show_suggestions'):
            return self.enhanced_system.show_suggestions(widget, partial_command, cursor_pos)

        self.suggestions = []

        if not hasattr(self, 'command_database') or not self.command_database:
            self.command_database = self.build_autocomplete_database()

        # Handle different command types
        if partial_command.startswith('\\begin{'):
            # Environment completion
            begin_info = self.command_database.get('\\begin', {})
            pairs = begin_info.get('pairs', {})

            if '}' not in partial_command:
                env_partial = partial_command[7:]  # Remove "\begin{" prefix
                for env_name, env_template in pairs.items():
                    if env_name.startswith(env_partial):
                        self.suggestions.append((
                            f"\\begin{{{env_name}}}",
                            {
                                'completion': env_template,
                                'description': f'{env_name} environment',
                                'type': 'environment',
                                'env_name': env_name
                            }
                        ))
            else:
                for env_name, env_template in pairs.items():
                    self.suggestions.append((
                        f"\\begin{{{env_name}}}",
                        {
                            'completion': env_template,
                            'description': f'{env_name} environment',
                            'type': 'environment',
                            'env_name': env_name
                        }
                    ))
        else:
            # Regular command completion - show ALL commands that start with the partial
            for command, info in self.command_database.items():
                if command.startswith(partial_command):
                    self.suggestions.append((command, info))

            # If we only have a single backslash, show ALL commands
            if partial_command == '\\' and not self.suggestions:
                for command, info in self.command_database.items():
                    self.suggestions.append((command, info))

        print(f"Found {len(self.suggestions)} suggestions")  # Debug

        if not self.suggestions:
            print("No suggestions found, hiding autocomplete")  # Debug
            self.hide_autocomplete()
            return

        # Create or update autocomplete window
        if self.autocomplete_window and self.autocomplete_window.winfo_exists():
            self.update_autocomplete_window(widget, self.suggestions)
        else:
            self.create_autocomplete_window(widget, self.suggestions)

    def create_autocomplete_window(self, widget, suggestions):
        """Create new autocomplete suggestions window"""
        print("Creating new autocomplete window")  # Debug

        bbox = widget.bbox("insert")
        if not bbox:
            print("No bbox available")  # Debug
            return

        x = widget.winfo_rootx() + bbox[0]
        y = widget.winfo_rooty() + bbox[1] + bbox[3]

        self.autocomplete_window = tk.Toplevel(widget)
        self.autocomplete_window.wm_overrideredirect(True)
        self.autocomplete_window.wm_geometry(f"+{x}+{y}")

        self.autocomplete_window.attributes('-topmost', True)

        self.autocomplete_window.configure(background='#2B2B2B', relief='solid', borderwidth=1)

        self.suggestion_listbox = tk.Listbox(
            self.autocomplete_window,
            background='#2B2B2B',
            foreground='white',
            selectbackground='#4A90E2',
            selectforeground='white',
            font=('Courier', 10),
            height=min(len(suggestions), 8),
            width=60,
            exportselection=False
        )
        self.suggestion_listbox.pack()

        self.populate_suggestion_listbox(suggestions)

        self.suggestion_listbox.bind('<Double-Button-1>', self.on_suggestion_selected)
        self.suggestion_listbox.bind('<<ListboxSelect>>', self.on_suggestion_highlight)
        self.suggestion_listbox.bind('<Button-1>', self.on_suggestion_click)
        self.suggestion_listbox.bind('<Escape>', self.hide_autocomplete)
        self.suggestion_listbox.selection_set(0)
        self.current_suggestion_index = 0

        self.autocomplete_window.transient(widget.winfo_toplevel())
        self.autocomplete_window.grab_release()

        print("Autocomplete window created successfully")  # Debug

    def update_autocomplete_window(self, widget, suggestions):
        """Update existing autocomplete window with new suggestions"""
        print("Updating existing autocomplete window")  # Debug

        if not self.autocomplete_window or not self.autocomplete_window.winfo_exists():
            self.create_autocomplete_window(widget, suggestions)
            return

        self.suggestion_listbox.delete(0, tk.END)
        self.populate_suggestion_listbox(suggestions)

        if suggestions:
            self.suggestion_listbox.selection_set(0)
            self.current_suggestion_index = 0
        else:
            self.hide_autocomplete()

        # Update window position to follow cursor
        bbox = widget.bbox("insert")
        if bbox:
            x = widget.winfo_rootx() + bbox[0]
            y = widget.winfo_rooty() + bbox[1] + bbox[3]
            self.autocomplete_window.wm_geometry(f"+{x}+{y}")

    def populate_suggestion_listbox(self, suggestions):
        """Populate the suggestion listbox with formatted items"""
        for command, info in suggestions:
            if info.get('type') == 'environment':
                env_name = info.get('env_name', '')
                description = info.get('description', '')
                display_text = f"{command:25} {description}"
            else:
                description = info.get('description', '')
                display_text = f"{command:25} {description}"
            self.suggestion_listbox.insert(tk.END, display_text)

    def on_suggestion_click(self, event):
        """Handle single click on suggestion - select immediately"""
        widget = event.widget
        index = widget.nearest(event.y)
        if index >= 0:
            widget.selection_clear(0, tk.END)
            widget.selection_set(index)
            widget.activate(index)
            self.current_suggestion_index = index
            self.on_suggestion_selected()

    def on_suggestion_highlight(self, event=None):
        """Handle suggestion highlighting"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'on_suggestion_highlight'):
            return self.enhanced_system.on_suggestion_highlight(event)

        if not self.suggestions or not self.autocomplete_window:
            return

        selection = self.suggestion_listbox.curselection()
        if selection:
            self.current_suggestion_index = selection[0]

    def on_suggestion_selected(self, event=None):
        """Handle suggestion selection"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'on_suggestion_selected'):
            return self.enhanced_system.on_suggestion_selected(event)

        if not self.suggestions or not self.autocomplete_window:
            return

        selection = self.suggestion_listbox.curselection()
        if selection:
            selected_index = selection[0]
            command, info = self.suggestions[selected_index]

            current_widget = self.selected_widget
            self.hide_autocomplete()

            if current_widget:
                self.apply_autocomplete_to_widget(current_widget, command, info)

    def apply_autocomplete_to_widget(self, widget, command, info):
        """Apply autocomplete to a specific widget"""
        cursor_pos = widget.index("insert")
        line_start = widget.index(f"{cursor_pos} linestart")
        line_content = widget.get(line_start, cursor_pos)

        if info.get('type') == 'environment':
            self.apply_environment_completion(widget, command, info)
        else:
            self.apply_regular_completion(widget, command, info, line_content, cursor_pos)

    def apply_environment_completion(self, widget, command, info):
        """Apply environment completion with proper formatting"""
        completion = info.get('completion', command)

        cursor_pos = widget.index("insert")
        widget.insert(cursor_pos, completion)
        self.position_cursor_at_placeholder(widget, completion)
        widget.focus_set()

    def apply_regular_completion(self, widget, command, info, line_content, cursor_pos):
        """Apply regular command completion"""
        last_backslash = line_content.rfind('\\')
        if last_backslash != -1:
            delete_start = f"{cursor_pos.split('.')[0]}.{last_backslash}"
            widget.delete(delete_start, cursor_pos)

            completion = info.get('completion', command)
            widget.insert(delete_start, completion)
            self.position_cursor_at_placeholder(widget, completion)

        widget.focus_set()

    def position_cursor_at_placeholder(self, widget, completion):
        """Position cursor at the first placeholder ($1)"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'position_cursor_at_placeholder'):
            return self.enhanced_system.position_cursor_at_placeholder(widget, completion)

        if '$1' in completion:
            cursor_pos = widget.index("insert")
            search_start = f"{cursor_pos} - {len(completion)} chars"
            placeholder_pos = widget.search('$1', search_start, cursor_pos)

            if placeholder_pos:
                widget.delete(placeholder_pos, f"{placeholder_pos}+2 chars")
                widget.mark_set("insert", placeholder_pos)
        elif '$2' in completion:
            cursor_pos = widget.index("insert")
            search_start = f"{cursor_pos} - {len(completion)} chars"
            placeholder_pos = widget.search('$1', search_start, cursor_pos)

            if placeholder_pos:
                widget.delete(placeholder_pos, f"{placeholder_pos}+2 chars")
                widget.mark_set("insert", placeholder_pos)

    def on_tab(self, event):
        """Handle tab for autocomplete selection"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'on_tab'):
            return self.enhanced_system.on_tab(event)

        if self.autocomplete_window and self.suggestions:
            self.on_suggestion_selected()
            return "break"
        return None

    def on_return(self, event):
        """Handle return key - select current suggestion"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'on_return'):
            return self.enhanced_system.on_return(event)

        if self.autocomplete_window and self.suggestions:
            self.on_suggestion_selected()
            return "break"
        return None

    def on_arrow_key(self, event):
        """Handle arrow key navigation in suggestions"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'on_arrow_key'):
            return self.enhanced_system.on_arrow_key(event)

        if not self.autocomplete_window:
            return None

        if event.keysym == 'Down':
            current = self.suggestion_listbox.curselection()[0] if self.suggestion_listbox.curselection() else 0
            next_index = min(current + 1, len(self.suggestions) - 1)
            self.suggestion_listbox.selection_clear(0, tk.END)
            self.suggestion_listbox.selection_set(next_index)
            self.suggestion_listbox.activate(next_index)
            self.current_suggestion_index = next_index
            return "break"

        elif event.keysym == 'Up':
            current = self.suggestion_listbox.curselection()[0] if self.suggestion_listbox.curselection() else 0
            next_index = max(current - 1, 0)
            self.suggestion_listbox.selection_clear(0, tk.END)
            self.suggestion_listbox.selection_set(next_index)
            self.suggestion_listbox.activate(next_index)
            self.current_suggestion_index = next_index
            return "break"

        return None

    def hide_autocomplete(self, event=None):
        """Hide the autocomplete window immediately and return focus"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'hide_autocomplete'):
            return self.enhanced_system.hide_autocomplete(event)

        if self.autocomplete_window:
            if self.selected_widget:
                self.selected_widget.focus_set()

            self.autocomplete_window.destroy()
            self.autocomplete_window = None
            self.suggestions = []
            self.current_suggestion_index = 0
            self.last_command_text = ""


    def get_suggestions(self, text: str, cursor_position: int):
        """Get autocomplete suggestions"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'get_suggestions'):
            return self.enhanced_system.get_suggestions(text, cursor_position)

        suggestions = []
        if '\\' in text:
            lines = text[:cursor_position].split('\n')
            current_line = lines[-1] if lines else ''
            last_backslash = current_line.rfind('\\')
            if last_backslash != -1:
                partial_command = current_line[last_backslash:]
                for command, info in self.command_database.items():
                    if command.startswith(partial_command):
                        suggestions.append({
                            'command': command,
                            'description': info.get('description', ''),
                            'completion': info.get('completion', command)
                        })
        return suggestions

    def complete_command(self, text: str, cursor_position: int, suggestion: str):
        """Complete command"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'complete_command'):
            return self.enhanced_system.complete_command(text, cursor_position, suggestion)

        lines = text.split('\n')
        current_line_index = len(text[:cursor_position].split('\n')) - 1
        current_line = lines[current_line_index]

        last_backslash = current_line.rfind('\\')
        if last_backslash != -1:
            new_line = current_line[:last_backslash] + suggestion
            lines[current_line_index] = new_line
            new_cursor_position = sum(len(line) + 1 for line in lines[:current_line_index]) + len(new_line)
            return '\n'.join(lines), new_cursor_position

        return text, cursor_position

    def update_command_database(self, new_commands: dict):
        """Update the command database with new commands"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'update_command_database'):
            return self.enhanced_system.update_command_database(new_commands)

        if not hasattr(self, 'command_database'):
            self.command_database = {}
        self.command_database.update(new_commands)

    def get_command_info(self, command: str):
        """Get information about a specific command"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'get_command_info'):
            return self.enhanced_system.get_command_info(command)

        if hasattr(self, 'command_database') and command in self.command_database:
            return self.command_database[command]
        return None

    def refresh_database(self):
        """Refresh the command database"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'refresh_database'):
            return self.enhanced_system.refresh_database()

        self.command_database = self.build_autocomplete_database()

    def quick_environment_insert(self, env_name):
        """Quick method to insert environment templates programmatically"""
        begin_info = self.command_database.get('\\begin', {})
        pairs = begin_info.get('pairs', {})

        if env_name in pairs:
            template = pairs[env_name]
            focused_widget = self.selected_widget or self.parent.focus_get()

            if (hasattr(self.parent, 'content_editor') and
                focused_widget == self.parent.content_editor._textbox):
                widget = self.parent.content_editor._textbox
            elif (hasattr(self.parent, 'notes_editor') and
                  focused_widget == self.parent.notes_editor._textbox):
                widget = self.parent.notes_editor._textbox
            else:
                widget = self.parent.content_editor._textbox

            cursor_pos = widget.index("insert")
            widget.insert(cursor_pos, template)
            self.position_cursor_at_placeholder(widget, template)


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

        # Threading for search operations
        self.search_queue = queue.Queue()
        self.search_thread = None
        self.search_running = False

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

        # ENHANCED: Setup autocomplete system
        self.setup_enhanced_autocomplete()
        self.enhance_search_with_autocomplete()
        self.enhance_interactive_help()
        self.create_autocomplete_quick_access()

        # Start search thread
        self.start_search_thread()

        # Initial display
        self.refresh_display()

    def start_search_thread(self):
        """Start the background search thread"""
        self.search_running = True
        self.search_thread = threading.Thread(target=self.search_worker, daemon=True)
        self.search_thread.start()

    def search_worker(self):
        """Background worker for search operations"""
        while self.search_running:
            try:
                # Get search task from queue with timeout
                task = self.search_queue.get(timeout=0.1)
                if task is None:  # Shutdown signal
                    break

                search_term, content_type = task
                self.perform_search(search_term, content_type)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Search error: {e}")

    def perform_search(self, search_term, content_type):
        """Perform search in background thread"""
        filtered_commands = {}

        for category, commands in self.commands.items():
            filtered = []
            for cmd in commands:
                # Filter by content type
                if content_type == "commands_only" and cmd.get('is_symbol', False):
                    continue
                if content_type == "symbols_only" and not cmd.get('is_symbol', False):
                    continue

                # Filter by search text
                if (not search_term or
                    search_term in cmd['command'].lower() or
                    search_term in cmd['description'].lower() or
                    search_term in cmd.get('usage', '').lower() or
                    search_term in cmd['syntax'].lower() or
                    search_term in cmd.get('category', '').lower() or
                    (cmd.get('is_symbol', False) and search_term in cmd.get('symbol', '').lower())):
                    filtered.append(cmd)

            if filtered:
                filtered_commands[category] = filtered

        # Update UI in main thread
        self.after(0, self.update_search_results, filtered_commands)

    def update_search_results(self, filtered_commands):
        """Update UI with search results (called in main thread)"""
        self.filtered_commands = filtered_commands
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
        """Build comprehensive command database with BSG and Beamer specific syntax including BeamerSlideGenerator features"""
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
                'command': '\\animategraphics',
                'syntax': '\\animategraphics[options]{framerate}{first frame}{last frame}',
                'description': 'Embeds animated graphics (GIFs, image sequences) - BSG Enhanced',
                'example': '\\animategraphics[autoplay,loop,width=0.8\\textwidth]{12}{animation}{}{}',
                'category': 'media',
                'display_options': ['static'],
                'auto_complete': '\\animategraphics[$1]{$2}{$3}{$4}',
                'usage': 'Animated graphics and GIF support',
                'is_symbol': False
            },
            {
                'command': '\\file',
                'syntax': '\\file{media_files/filename.gif}',
                'description': 'Includes an animated GIF - automatically detects and plays animation',
                'example': '\\file{media_files/animation.gif}',
                'category': 'media',
                'display_options': ['static'],
                'auto_complete': '\\file{media_files/$1}',
                'usage': 'Animated GIFs are automatically detected and played',
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
                    'command': '\\inlineimg',
                    'syntax': '\\inlineimg[options]{image} or \\inlineimg{image}{scale}',
                    'description': 'Inserts inline images within text flow',
                    'example': 'Cats are amazing \\inlineimg{cat.png} and make great pets.',
                    'category': 'formatting',
                    'display_options': ['static'],
                    'auto_complete': '\\inlineimg[$1]{$2}',
                    'usage': 'Inline images within text paragraphs',
                    'is_symbol': False
                },
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

            'BSG-IDE Special Commands': [
                {
                    'command': '\\shadowtext',
                    'syntax': '\\shadowtext[shadow_color]{text} or \\shadowtext{text}',
                    'description': 'Creates text with shadow effect - BSG-IDE Enhanced',
                    'example': '\\shadowtext[black]{Important Concept}',
                    'category': 'effects',
                    'display_options': ['static'],
                    'auto_complete': '\\shadowtext[$1]{$2}',
                    'usage': 'Text shadow effects',
                    'is_symbol': False
                },
                {
                    'command': '\\glowtext',
                    'syntax': '\\glowtext[glow_color]{text} or \\glowtext{text}',
                    'description': 'Creates text with glow effect - BSG-IDE Enhanced',
                    'example': '\\glowtext[myblue]{Highlighted Text}',
                    'category': 'effects',
                    'display_options': ['static'],
                    'auto_complete': '\\glowtext[$1]{$2}',
                    'usage': 'Text glow effects',
                    'is_symbol': False
                },
                {
                    'command': '\\hlkey',
                    'syntax': '\\hlkey[bg_color]{text} or \\hlkey{text}',
                    'description': 'Highlights key text with background color',
                    'example': '\\hlkey[myblue!20]{Key Term}',
                    'category': 'formatting',
                    'display_options': ['static'],
                    'auto_complete': '\\hlkey[$1]{$2}',
                    'usage': 'Key term highlighting',
                    'is_symbol': False
                },
                {
                    'command': '\\hlnote',
                    'syntax': '\\hlnote[bg_color]{text} or \\hlnote{text}',
                    'description': 'Highlights note text with background color',
                    'example': '\\hlnote[mygreen!20]{Important Note}',
                    'category': 'formatting',
                    'display_options': ['static'],
                    'auto_complete': '\\hlnote[$1]{$2}',
                    'usage': 'Note highlighting',
                    'is_symbol': False
                },
                {
                    'command': '\\anbg',
                    'syntax': '\\anbg[opacity]{background_image}',
                    'description': 'Sets animated background for slide',
                    'example': '\\anbg[0.2]{background.gif}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\anbg[$1]{$2}',
                    'usage': 'Slide background with animation',
                    'is_symbol': False
                },
                {
                    'command': '\\spotlight',
                    'syntax': '\\spotlight{text}',
                    'description': 'Creates spotlight effect on text',
                    'example': '\\spotlight{Main Point}',
                    'category': 'effects',
                    'display_options': ['static'],
                    'auto_complete': '\\spotlight{$1}',
                    'usage': 'Text spotlight effect',
                    'is_symbol': False
                }
            ],

            'BSG-IDE Media Layouts': [
                {
                    'command': '\\wm',
                    'syntax': '\\wm{image_file}',
                    'description': 'Watermark layout - image as background with low opacity',
                    'example': '\\wm{media_files/watermark.png}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\wm{$1}',
                    'usage': 'Watermark background layout',
                    'is_symbol': False
                },
                {
                    'command': '\\ff',
                    'syntax': '\\ff{image_file}',
                    'description': 'Fullframe layout - image fills entire slide',
                    'example': '\\ff{media_files/fullscreen.jpg}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\ff{$1}',
                    'usage': 'Fullscreen image layout',
                    'is_symbol': False
                },
                {
                    'command': '\\pip',
                    'syntax': '\\pip{image_file}',
                    'description': 'Picture-in-Picture layout - small image in corner',
                    'example': '\\pip{media_files/small_diagram.png}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\pip{$1}',
                    'usage': 'Picture-in-picture layout',
                    'is_symbol': False
                },
                {
                    'command': '\\split',
                    'syntax': '\\split{image_file}',
                    'description': 'Split layout - image and content side by side',
                    'example': '\\split{media_files/diagram.png}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\split{$1}',
                    'usage': 'Split screen layout',
                    'is_symbol': False
                },
                {
                    'command': '\\hl',
                    'syntax': '\\hl{image_file}',
                    'description': 'Highlight layout - large centered image',
                    'example': '\\hl{media_files/main_image.jpg}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\hl{$1}',
                    'usage': 'Highlight image layout',
                    'is_symbol': False
                },
                {
                    'command': '\\bg',
                    'syntax': '\\bg{image_file}',
                    'description': 'Background layout - image as subtle background',
                    'example': '\\bg{media_files/background.png}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\bg{$1}',
                    'usage': 'Subtle background layout',
                    'is_symbol': False
                },
                {
                    'command': '\\tb',
                    'syntax': '\\tb{image_file}',
                    'description': 'Top-Bottom layout - image on top, content below',
                    'example': '\\tb{media_files/top_image.png}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\tb{$1}',
                    'usage': 'Top-bottom layout',
                    'is_symbol': False
                },
                {
                    'command': '\\ol',
                    'syntax': '\\ol{image_file}',
                    'description': 'Overlay layout - semi-transparent image overlay',
                    'example': '\\ol{media_files/overlay.png}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\ol{$1}',
                    'usage': 'Image overlay layout',
                    'is_symbol': False
                },
                {
                    'command': '\\corner',
                    'syntax': '\\corner{image_file}',
                    'description': 'Corner layout - small image in corner',
                    'example': '\\corner{media_files/corner_logo.png}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\corner{$1}',
                    'usage': 'Corner image layout',
                    'is_symbol': False
                },
                {
                    'command': '\\mosaic',
                    'syntax': '\\mosaic{image1,image2,image3,...}',
                    'description': 'Intelligent mosaic layout - automatically adjusts based on number of images',
                    'example': '\\mosaic{img1.png,img2.png,img3.png,img4.png}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\mosaic{$1}',
                    'usage': 'Smart image grid layout (1-4: special layouts, 5+: dynamic grid)',
                    'is_symbol': False
                }
            ],

            'BSG-IDE Content Blocks': [
                {
                    'command': '\\begin{Content}',
                    'syntax': '\\begin{Content}{media_directive}...content...\\end{Content}',
                    'description': 'Main content block for slides with media support',
                    'example': '\\begin{Content}{\\file{media.png}}\n- Item 1\n- Item 2\n\\end{Content}',
                    'category': 'structure',
                    'display_options': ['static'],
                    'auto_complete': '\\begin{Content}{$1}\n$2\n\\end{Content}',
                    'usage': 'Slide content container',
                    'is_symbol': False
                },
                {
                    'command': '\\begin{Notes}',
                    'syntax': '\\begin{Notes}...speaker notes...\\end{Notes}',
                    'description': 'Speaker notes block for presentation',
                    'example': '\\begin{Notes}\nExplain this concept slowly\nMention related research\n\\end{Notes}',
                    'category': 'presentation',
                    'display_options': ['static'],
                    'auto_complete': '\\begin{Notes}\n$1\n\\end{Notes}',
                    'usage': 'Speaker notes container',
                    'is_symbol': False
                },
                {
                    'command': '\\begin{alertbox}',
                    'syntax': '\\begin{alertbox}[color]{title}...content...\\end{alertbox}',
                    'description': 'Alert box with colored background',
                    'example': '\\begin{alertbox}[red]{Warning}\nThis is important!\n\\end{alertbox}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\begin{alertbox}[$1]{$2}\n$3\n\\end{alertbox}',
                    'usage': 'Alert message box',
                    'is_symbol': False
                },
                {
                    'command': '\\begin{infobox}',
                    'syntax': '\\begin{infobox}[color]{title}...content...\\end{infobox}',
                    'description': 'Information box with colored background',
                    'example': '\\begin{infobox}[blue]{Information}\nAdditional details here\n\\end{infobox}',
                    'category': 'layout',
                    'display_options': ['static'],
                    'auto_complete': '\\begin{infobox}[$1]{$2}\n$3\n\\end{infobox}',
                    'usage': 'Information message box',
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
        search_entry.bind('<KeyRelease>', self.filter_commands_throttled)

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
                     "Beamer Item-by-Item Display", "Presentation Features", "Mathematical Symbols",
                     "BSG-IDE Special Commands", "BSG-IDE Media Layouts", "BSG-IDE Content Blocks"]
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
            if i < 4:
                row_frame = cat_row1
            elif i < 8:
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

        # Search status indicator
        self.search_status_label = ctk.CTkLabel(info_frame, text="Ready", font=("Arial", 10), text_color="#95A5A6")
        self.search_status_label.pack(side="left", padx=10, pady=5)

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

        ctk.CTkButton(button_frame, text="Test Command",
                     command=self.test_command, width=120).pack(side="left", padx=5)

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
            ("BSG Special Effects", "\\shadowtext[black]{Shadow Text}\n\\glowtext[myblue]{Glow Text}\n\\hlkey[myblue!20]{Key Term}"),
            ("BSG Media Layouts", "\\wm{watermark.png} - Watermark\n\\ff{fullscreen.jpg} - Fullframe\n\\pip{small.png} - Picture-in-Picture\n\\split{diagram.png} - Split Layout"),
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
            },
            {
                "name": "BSG Effects",
                "color": "#C0392B",
                "commands": ["\\shadowtext", "\\glowtext", "\\hlkey", "\\hlnote", "\\spotlight"]
            },
            {
                "name": "Media Layouts",
                "color": "#8E44AD",
                "commands": ["\\wm", "\\ff", "\\pip", "\\split", "\\hl", "\\mosaic"]
            }
        ]

        # Create three rows of button groups
        row1_frame = ctk.CTkFrame(button_groups_frame, fg_color="transparent")
        row1_frame.pack(fill="x", pady=2)

        row2_frame = ctk.CTkFrame(button_groups_frame, fg_color="transparent")
        row2_frame.pack(fill="x", pady=2)

        row3_frame = ctk.CTkFrame(button_groups_frame, fg_color="transparent")
        row3_frame.pack(fill="x", pady=2)

        # Distribute groups between three rows (4 groups per row)
        for i, group in enumerate(button_groups):
            if i < 4:
                parent_frame = row1_frame
            elif i < 8:
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
        """Handle quick access button clicks with enhanced autocomplete"""
        self.test_var.set(command)
        self.update_live_help()
        self.help_display.see("1.0")

        # Use enhanced insertion if available
        if hasattr(self, 'autocomplete_system'):
            self.quick_command_insert(command)

    def filter_commands_throttled(self, event=None):
        """Throttled command filtering to prevent UI freeze"""
        search_term = self.search_var.get().lower()
        content_type = self.content_var.get()

        # Update search status
        self.search_status_label.configure(text="Searching...", text_color="#F39C12")

        # Add search task to queue
        try:
            self.search_queue.put((search_term, content_type), timeout=0.1)
        except queue.Full:
            # Queue is full, skip this search (prevents backlog)
            pass

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
        self.search_status_label.configure(text="Ready", text_color="#27AE60")

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
            'general': '#7F8C8D',
            'effects': '#C0392B'
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

    def test_command(self):
        """Test the selected command"""
        if not self.selected_command:
            messagebox.showinfo("No Selection", "Please select a command first.")
            return

        messagebox.showinfo("Test Command",
                          f"Testing: {self.selected_command['command']}\n\n"
                          f"This would show a preview of how the command works in context.")

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

    def center_dialog(self):
        """Center the dialog on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def destroy(self):
        """Clean up threads when closing"""
        self.search_running = False
        try:
            self.search_queue.put(None, timeout=0.1)  # Signal thread to exit
        except:
            pass
        super().destroy()

#----------------Autocomplete integration-------------------
def setup_enhanced_autocomplete(self):
    """Setup enhanced autocomplete system for the dialog"""
    try:
        # Initialize the intelligent autocomplete system
        self.autocomplete_system = IntelligentAutocomplete(self)

        # Setup autocomplete for search field
        search_widgets = [
            self.search_var._entry_widget if hasattr(self.search_var, '_entry_widget') else None,
            self.test_var._entry_widget if hasattr(self.test_var, '_entry_widget') else None
        ]

        for widget in search_widgets:
            if widget and hasattr(widget, 'bind'):
                self.autocomplete_system.setup_autocomplete(widget)

        print("✓ Enhanced autocomplete integrated into command dialog")

    except Exception as e:
        print(f"Autocomplete integration warning: {e}")

def enhance_search_with_autocomplete(self):
    """Enhance search functionality with autocomplete suggestions"""
    # Update the command database with all available commands
    all_commands = {}

    for category, commands in self.commands.items():
        for cmd in commands:
            command_name = cmd['command']
            all_commands[command_name] = {
                'completion': cmd.get('auto_complete', command_name),
                'description': cmd['description'],
                'type': 'command',
                'category': category,
                'example': cmd.get('example', ''),
                'syntax': cmd.get('syntax', '')
            }

    # Update autocomplete database
    if hasattr(self, 'autocomplete_system'):
        self.autocomplete_system.update_command_database(all_commands)

    print(f"✓ Enhanced search with {len(all_commands)} commands")

def quick_command_insert(self, command_text):
    """Quick insert command from autocomplete or quick access"""
    # Find the command in our database
    target_command = None
    for category, commands in self.commands.items():
        for cmd in commands:
            if cmd['command'] == command_text:
                target_command = cmd
                break
        if target_command:
            break

    if target_command:
        self.selected_command = target_command
        self.insert_selected()
    else:
        # Fallback to basic insertion
        self.test_var.set(command_text)
        self.update_live_help()

def enhance_interactive_help(self):
    """Enhance interactive help with autocomplete integration"""
    # Update the test field to use autocomplete
    if hasattr(self, 'test_var') and hasattr(self, 'autocomplete_system'):
        test_entry = None
        # Find the test entry widget
        for widget in self.interactive_tab.winfo_children():
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkEntry) and child._placeholder_text == "Enter command (e.g., \\bsglogo, \\frac, \\alpha)":
                        test_entry = child
                        break
            if test_entry:
                break

        if test_entry:
            self.autocomplete_system.setup_autocomplete(test_entry)

            # Override the key release to update help immediately
            def enhanced_key_release(event):
                self.update_live_help()
                # Also allow autocomplete to handle it
                return self.autocomplete_system.on_key_release(event) if hasattr(self.autocomplete_system, 'on_key_release') else None

            test_entry.bind('<KeyRelease>', enhanced_key_release, add='+')

def create_autocomplete_quick_access(self):
    """Create quick access panel for autocomplete features"""
    if not hasattr(self, 'interactive_tab'):
        return

    # Find the interactive help tab and add autocomplete quick access
    for widget in self.interactive_tab.winfo_children():
        if hasattr(widget, 'winfo_children'):
            for child in widget.winfo_children():
                if "Quick Access BSG Commands" in str(child.winfo_children()):
                    # Add autocomplete info frame
                    autocomplete_frame = ctk.CTkFrame(widget)
                    autocomplete_frame.pack(fill="x", pady=10)

                    ctk.CTkLabel(autocomplete_frame,
                                text="💡 Autocomplete Tips",
                                font=("Arial", 12, "bold")).pack(anchor="w", pady=5)

                    tips_text = """• Type \\ to see all commands instantly
• Use Tab to quickly select suggestions
• Arrow keys navigate suggestions
• Enter inserts selected command
• Click suggestions for immediate insertion"""

                    tips_label = ctk.CTkLabel(autocomplete_frame,
                                            text=tips_text,
                                            font=("Arial", 10),
                                            justify="left")
                    tips_label.pack(anchor="w", padx=10, pady=5)

                    break
#-----------------------------Integration completed ----------------------
