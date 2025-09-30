#-------------------------------------------Session Manager ------------------------------------------
import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from BeamerSlideGenerator import get_beamer_preamble
from tkinter import messagebox

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
            'textcolor': '#BD93F9'    # textcolor commands
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
            (r'\[RGB\]\{[^\}]*\}', 'rgb')
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

        # Templates
        self.templates = {
            "Key Points": "• Key points:\n  - \n  - \n  - \n",
            "Time Markers": "• Timing guide:\n  0:00 - Introduction\n  0:00 - Main points\n  0:00 - Conclusion",
            "Questions": "• Potential questions:\nQ1: \nA1: \n\nQ2: \nA2: ",
            "References": "• Additional references:\n  - Title:\n    Author:\n    Page: ",
            "Technical Details": "• Technical details:\n  - Specifications:\n  - Parameters:\n  - Requirements:",
        }

        self.create_toolbar()

    def create_toolbar(self):
        """Create the notes toolbar"""
        # Template dropdown
        template_frame = ctk.CTkFrame(self)
        template_frame.pack(side="left", padx=5, pady=2)

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

        # Separator
        ttk.Separator(self, orient="vertical").pack(side="left", padx=5, fill="y", pady=2)

        # Formatting buttons
        formatting_frame = ctk.CTkFrame(self)
        formatting_frame.pack(side="left", padx=5, pady=2)

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
            self.create_tooltip(btn, tooltip)

    def create_tooltip(self, widget, text):
        """Create tooltip for buttons"""
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
        """Insert selected template"""
        if choice in self.templates:
            self.notes_editor.insert('insert', self.templates[choice])
            self.template_var.set("Select Template")  # Reset dropdown

    def add_bold(self):
        """Add bold text"""
        self.wrap_selection(r'\textbf{', '}')

    def add_italic(self):
        """Add italic text"""
        self.wrap_selection(r'\textit{', '}')

    def add_color(self):
        """Add colored text"""
        colors = ['red', 'blue', 'green', 'orange', 'purple']
        color = simpledialog.askstring(
            "Color",
            "Enter color name or RGB values:",
            initialvalue=colors[0]
        )
        if color:
            self.wrap_selection(f'\\textcolor{{{color}}}{{', '}')

    def add_highlight(self):
        """Add highlighted text"""
        self.wrap_selection('\\hl{', '}')

    def add_bullet(self):
        """Add bullet point"""
        self.notes_editor.insert('insert', '\n• ')

    def add_timestamp(self):
        """Add timestamp"""
        timestamp = simpledialog.askstring(
            "Timestamp",
            "Enter timestamp (MM:SS):",
            initialvalue="00:00"
        )
        if timestamp:
            self.notes_editor.insert('insert', f'[{timestamp}] ')

    def add_alert(self):
        """Add alert note"""
        self.notes_editor.insert('insert', '⚠ Important: ')

    def add_tip(self):
        """Add tip"""
        self.notes_editor.insert('insert', '💡 Tip: ')

    def wrap_selection(self, prefix, suffix):
        """Wrap selected text with prefix and suffix"""
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
        """Create Linux launcher script and desktop entry"""
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
            # Write launcher script
            launcher_path.write_text(launcher_content)
            launcher_path.chmod(0o755)  # Make executable

            if self.dialog:
                self.dialog.write(f"✓ Created launcher script: {launcher_path}", "green")
            else:
                print(f"✓ Created launcher script: {launcher_path}")

            # Create desktop entry
            desktop_entry_content = f"""[Desktop Entry]
Version=4.0
Type=Application
Name=BSG-IDE
Comment=Beamer Slide Generator IDE
Exec={launcher_path}
Icon=bsg-ide
Terminal=false
Categories=Office;Development;Education;
Keywords=presentation;latex;beamer;slides;
"""
            desktop_path = self.install_paths['applications'] / 'bsg-ide.desktop'
            desktop_path.write_text(desktop_entry_content)
            desktop_path.chmod(0o755)

            if self.dialog:
                self.dialog.write("✓ Created desktop entry", "green")
            else:
                print("✓ Created desktop entry")

            return True

        except Exception as e:
            if self.dialog:
                self.dialog.write(f"✗ Error creating Linux launcher: {str(e)}", "red")
            else:
                print(f"✗ Error creating Linux launcher: {str(e)}")
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
            '\\ddots': {
                'completion': '\\ddots',
                'description': 'Diagonal dots'
            }
        }

    def setup_autocomplete(self, text_widget):
        """Setup autocomplete for a text widget - MORE AGGRESSIVE"""
        if self.use_enhanced and hasattr(self.enhanced_system, 'setup_autocomplete'):
            self.enhanced_system.setup_autocomplete(text_widget)
        else:
            # More aggressive binding - trigger on every key press
            text_widget.bind('<Key>', self.on_key_pressed, add='+')
            text_widget.bind('<KeyRelease>', self.on_key_release, add='+')
            text_widget.bind('<Tab>', self.on_tab)
            text_widget.bind('<Return>', self.on_return)
            text_widget.bind('<Escape>', self.hide_autocomplete)
            text_widget.bind('<Up>', self.on_arrow_key)
            text_widget.bind('<Down>', self.on_arrow_key)
            text_widget.bind('<Button-1>', self.on_editor_click)
            text_widget.bind('<FocusIn>', self.on_focus_in)

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
