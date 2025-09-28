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

# Example usage and integration
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

#------------------------------------------------------------------------------------------

# Example of how to use the library
if __name__ == "__main__":
    # Create the library instance
    latex_lib = LatexHelpLibrary()

    # Example: Get help for a command
    help_info = latex_lib.helper.get_command_help('\\frac')
    print("Help for \\frac:", help_info)

    # Example: Get autocomplete suggestions
    suggestions = latex_lib.helper.get_autocomplete_suggestions('\\alp')
    print("Autocomplete for '\\alp':", suggestions)

    # Example: Search commands
    results = latex_lib.helper.search_commands('arrow')
    print("Search results for 'arrow':", [(cmd, info['description']) for cmd, info in results[:3]])

    # Example: Get symbols by category
    greek_symbols = latex_lib.helper.get_symbols_by_category('greek')
    print("Greek symbols:", greek_symbols[:5])
