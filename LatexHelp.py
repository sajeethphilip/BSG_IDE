import customtkinter as ctk
import tkinter as tk
import json
import webbrowser
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from tkinter import messagebox

#---------------Latex Help --------------------------
class LatexCommandHelper:
    """LaTeX command help system with local cache and online fallback"""

    def __init__(self):
        self.commands_db = {}
        self.cache_file = Path.home() / '.bsg-ide' / 'latex_help_cache.json'
        self.cache_expiry_days = 30
        self.load_local_database()

    def load_local_database(self):
        """Load local LaTeX command database"""
        # Basic LaTeX commands database
        self.commands_db = {
            '\\title': {
                'syntax': '\\title{title text}',
                'description': 'Sets the presentation title',
                'category': 'document',
                'package': 'beamer'
            },
            '\\author': {
                'syntax': '\\author{author name}',
                'description': 'Sets the author name',
                'category': 'document',
                'package': 'beamer'
            },
            '\\institute': {
                'syntax': '\\institute{institution name}',
                'description': 'Sets the institution name',
                'category': 'document',
                'package': 'beamer'
            },
            '\\date': {
                'syntax': '\\date{date}',
                'description': 'Sets the presentation date',
                'category': 'document',
                'package': 'beamer'
            },
            '\\frametitle': {
                'syntax': '\\frametitle{slide title}',
                'description': 'Sets the frame/slide title',
                'category': 'frame',
                'package': 'beamer'
            },
            '\\file': {
                'syntax': '\\file{media_files/filename.ext}',
                'description': 'Includes an image or media file',
                'category': 'media',
                'package': 'beamer'
            },
            '\\play': {
                'syntax': '\\play{media_files/video.ext}',
                'description': 'Embeds a playable video',
                'category': 'media',
                'package': 'beamer'
            },
            '\\textcolor': {
                'syntax': '\\textcolor{color}{text} or \\textcolor[RGB]{r,g,b}{text}',
                'description': 'Changes text color',
                'category': 'formatting',
                'package': 'xcolor'
            },
            '\\textbf': {
                'syntax': '\\textbf{bold text}',
                'description': 'Makes text bold',
                'category': 'formatting',
                'package': 'latex'
            },
            '\\textit': {
                'syntax': '\\textit{italic text}',
                'description': 'Makes text italic',
                'category': 'formatting',
                'package': 'latex'
            },
            '\\begin': {
                'syntax': '\\begin{environment} ... \\end{environment}',
                'description': 'Starts an environment block',
                'category': 'structure',
                'package': 'latex'
            },
            '\\end': {
                'syntax': '\\end{environment}',
                'description': 'Ends an environment block',
                'category': 'structure',
                'package': 'latex'
            },
            '\\item': {
                'syntax': '\\item item text',
                'description': 'Creates a list item',
                'category': 'lists',
                'package': 'latex'
            },
            '\\includegraphics': {
                'syntax': '\\includegraphics[options]{filename}',
                'description': 'Includes an image file',
                'category': 'graphics',
                'package': 'graphicx'
            },
            '\\movie': {
                'syntax': '\\movie[options]{poster}{video}',
                'description': 'Embeds a multimedia file',
                'category': 'media',
                'package': 'multimedia'
            },
            '\\href': {
                'syntax': '\\href{url}{link text}',
                'description': 'Creates a hyperlink',
                'category': 'hyperlinks',
                'package': 'hyperref'
            },
            '\\note': {
                'syntax': '\\note{note content}',
                'description': 'Adds speaker notes',
                'category': 'notes',
                'package': 'beamer'
            },
            '\\pause': {
                'syntax': '\\pause',
                'description': 'Pauses between overlay items',
                'category': 'overlays',
                'package': 'beamer'
            },
            '\\only': {
                'syntax': '\\only<overlay>{content}',
                'description': 'Shows content only on specified overlays',
                'category': 'overlays',
                'package': 'beamer'
            },
            '\\alert': {
                'syntax': '\\alert{highlighted text}',
                'description': 'Highlights text for emphasis',
                'category': 'formatting',
                'package': 'beamer'
            }
        }

        # Try to load cached online data
        self.load_cached_online_data()

    def load_cached_online_data(self):
        """Load cached online command help"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)

                # Check if cache is still valid
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

    def get_command_help(self, command):
        """Get help for a LaTeX command with online fallback"""
        # Clean the command (remove arguments, etc.)
        base_command = command.split('{')[0] if '{' in command else command
        base_command = base_command.split('[')[0] if '[' in command else base_command

        if base_command in self.commands_db:
            return self.commands_db[base_command]

        # Try to fetch from online if not found locally
        return self.fetch_online_help(base_command)

    def fetch_online_help(self, command):
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
                'url': ctan_url
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
                'package': 'latex'
            }

class CommandTooltip:
    """Tooltip for LaTeX command help"""

    def __init__(self, parent):
        self.parent = parent
        self.tooltip = None
        self.helper = LatexCommandHelper()

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

        # Create content
        label = tk.Label(self.tooltip, text=content, justify='left',
                        background='#FFFFE0', font=('Arial', 10),
                        padx=10, pady=10)
        label.pack()

        # Make tooltip disappear when mouse leaves
        widget.bind('<Leave>', lambda e: self.hide_tooltip())

    def format_tooltip_content(self, command, help_info):
        """Format tooltip content"""
        lines = [
            f"Command: {command}",
            f"Syntax: {help_info.get('syntax', 'Unknown')}",
            f"Description: {help_info.get('description', 'No description available')}",
            f"Category: {help_info.get('category', 'General')}",
            f"Package: {help_info.get('package', 'LaTeX')}"
        ]

        if 'url' in help_info:
            lines.append(f"Docs: {help_info['url']}")

        return '\n'.join(lines)

    def hide_tooltip(self):
        """Hide the tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


#------------------------------------------------------------------------------------------
