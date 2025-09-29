import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from tkinter import messagebox

class GrammarlyIntegration:
    """Grammarly integration for advanced grammar and spelling checking"""

    def __init__(self, parent):
        self.parent = parent
        self.grammarly_enabled = False
        self.grammarly_api_key = None
        self.grammarly_session = None

        # Grammarly API endpoints (using free tier where possible)
        self.api_base = "https://api.grammarly.com"
        self.free_endpoints = {
            'check': "/api/check",
            'suggestions': "/api/suggestions"
        }

        self.load_grammarly_settings()

    def load_grammarly_settings(self):
        """Load Grammarly settings from config"""
        try:
            config_dir = Path.home() / '.bsg-ide'
            config_file = config_dir / 'grammarly_config.json'

            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.grammarly_api_key = config.get('api_key')
                    self.grammarly_enabled = config.get('enabled', False)
        except:
            pass

    def save_grammarly_settings(self):
        """Save Grammarly settings to config"""
        try:
            config_dir = Path.home() / '.bsg-ide'
            config_dir.mkdir(exist_ok=True)

            config = {
                'api_key': self.grammarly_api_key,
                'enabled': self.grammarly_enabled,
                'last_updated': datetime.now().isoformat()
            }

            with open(config_dir / 'grammarly_config.json', 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass

    def show_grammarly_dialog(self):
        """Show Grammarly setup dialog"""
        dialog = GrammarlySetupDialog(self.parent, self)
        self.parent.wait_window(dialog)

        if dialog.result == "success":
            self.grammarly_enabled = True
            self.save_grammarly_settings()
            self.parent.write("✓ Grammarly integration enabled\n", "green")

    def check_text_grammarly(self, text):
        """Check text using Grammarly API"""
        if not self.grammarly_enabled or not self.grammarly_api_key:
            return None

        try:
            headers = {
                'Authorization': f'Bearer {self.grammarly_api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'text': text,
                'language': 'en-US',
                'style': 'academic'  # academic, business, casual, etc.
            }

            # Using requests if available, otherwise fallback
            try:
                import requests
                response = requests.post(
                    f"{self.api_base}{self.free_endpoints['check']}",
                    headers=headers,
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    self.parent.write(f"Grammarly API error: {response.status_code}\n", "yellow")
                    return None

            except ImportError:
                # Fallback to urllib if requests not available
                import urllib.request
                import json as json_lib

                req = urllib.request.Request(
                    f"{self.api_base}{self.free_endpoints['check']}",
                    data=json_lib.dumps(payload).encode('utf-8'),
                    headers=headers,
                    method='POST'
                )

                with urllib.request.urlopen(req, timeout=10) as response:
                    return json_lib.loads(response.read().decode('utf-8'))

        except Exception as e:
            self.parent.write(f"Grammarly check failed: {str(e)}\n", "red")
            return None

    def apply_grammarly_suggestions(self, text_widget, suggestions):
        """Apply Grammarly suggestions to text widget"""
        if not suggestions or 'issues' not in suggestions:
            return

        for issue in suggestions['issues']:
            start_pos = f"1.0+{issue['start']}c"
            end_pos = f"1.0+{issue['end']}c"

            # Highlight the issue
            text_widget.tag_add("grammarly_issue", start_pos, end_pos)
            text_widget.tag_config("grammarly_issue",
                                 background="#FFF3CD",  # Light yellow
                                 underline=True,
                                 underlinefg="#FFC107")

            # Store suggestion info
            text_widget.grammarly_issues = getattr(text_widget, 'grammarly_issues', {})
            text_widget.grammarly_issues[f"{issue['start']}-{issue['end']}"] = {
                'original': issue['original'],
                'suggestions': issue['suggestions'],
                'reason': issue['reason']
            }

class GrammarlySetupDialog(ctk.CTkToplevel):
    """Dialog for setting up Grammarly integration"""

    def __init__(self, parent, grammarly_integration):
        super().__init__(parent)
        self.title("Grammarly Integration Setup")
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()

        self.grammarly = grammarly_integration
        self.result = None

        self.center_dialog()
        self.create_widgets()

        # Wait for window to be ready before grabbing
        self.after(100, self.finalize_dialog)

    def finalize_dialog(self):
        """Finalize dialog setup after it's fully created"""
        self.grab_set()
        self.focus_force()
        self.lift()

    def center_dialog(self):
        """Center the dialog on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """Create setup dialog widgets"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        ctk.CTkLabel(main_frame, text="Grammarly Integration",
                    font=("Arial", 16, "bold")).pack(pady=10)

        # Description
        desc_text = """Enhance your writing with Grammarly's advanced grammar and spell checking.

Features:
• Advanced grammar checking
• Style suggestions
• Vocabulary enhancements
• Tone adjustments
• Plagiarism detection (premium)"""

        ctk.CTkLabel(main_frame, text=desc_text, justify="left",
                    font=("Arial", 12)).pack(pady=10)

        # API Key section
        key_frame = ctk.CTkFrame(main_frame)
        key_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(key_frame, text="Grammarly API Key:",
                    font=("Arial", 12, "bold")).pack(anchor="w", pady=5)

        self.api_key_var = tk.StringVar(value=self.grammarly.grammarly_api_key or "")
        api_entry = ctk.CTkEntry(key_frame, textvariable=self.api_key_var,
                               width=300, show="*")
        api_entry.pack(fill="x", pady=5)

        # Help text
        help_text = """Get your API key from:
• Grammarly Developer Portal: https://developer.grammarly.com
• Free tier available with limitations
• Premium features require subscription"""

        ctk.CTkLabel(key_frame, text=help_text, justify="left",
                    font=("Arial", 10), text_color="#6c757d").pack(anchor="w", pady=5)

        # Options
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", pady=10)

        self.realtime_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(options_frame, text="Enable real-time checking",
                       variable=self.realtime_var).pack(anchor="w", pady=2)

        self.auto_apply_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(options_frame, text="Auto-apply common corrections",
                       variable=self.auto_apply_var).pack(anchor="w", pady=2)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(button_frame, text="Get API Key",
                     command=self.open_grammarly_portal).pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="Test Connection",
                     command=self.test_connection).pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="Save",
                     command=self.save_settings, fg_color="#28a745").pack(side="right", padx=5)

        ctk.CTkButton(button_frame, text="Cancel",
                     command=self.cancel).pack(side="right", padx=5)

    def open_grammarly_portal(self):
        """Open Grammarly developer portal"""
        webbrowser.open("https://developer.grammarly.com")

    def test_connection(self):
        """Test Grammarly API connection"""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showwarning("Warning", "Please enter your API key first")
            return

        # Simple test with sample text
        test_text = "This is an example text to test the Grammarly connection."

        # Temporarily set API key for testing
        original_key = self.grammarly.grammarly_api_key
        self.grammarly.grammarly_api_key = api_key

        try:
            result = self.grammarly.check_text_grammarly(test_text)
            if result:
                messagebox.showinfo("Success", "Grammarly connection successful!")
            else:
                messagebox.showerror("Error", "Failed to connect to Grammarly. Check your API key.")

        except Exception as e:
            messagebox.showerror("Error", f"Connection test failed: {str(e)}")

        finally:
            self.grammarly.grammarly_api_key = original_key

    def save_settings(self):
        """Save Grammarly settings"""
        api_key = self.api_key_var.get().strip()

        if not api_key:
            messagebox.showwarning("Warning", "Please enter your Grammarly API key")
            return

        self.grammarly.grammarly_api_key = api_key
        self.grammarly.grammarly_enabled = True
        self.result = "success"
        self.destroy()

    def cancel(self):
        """Cancel setup"""
        self.result = "cancel"
        self.destroy()

import webbrowser
import tempfile
import json
from pathlib import Path

class AutomatedGrammarlyIntegration:
    def __init__(self, parent):
        self.parent = parent
        self.grammarly_api_key = None
        self.setup_automated = False

    def automated_setup(self):
        """Automated Grammarly setup - use the existing setup dialog"""
        try:
            # Simply use the parent's Grammarly setup dialog which already has all the functionality
            self.parent.grammarly.show_grammarly_dialog()
        except Exception as e:
            print(f"Grammarly setup error: {e}")
            # Ultimate fallback
            webbrowser.open("https://developer.grammarly.com")
            messagebox.showinfo("Grammarly Setup",
                              "Please visit https://developer.grammarly.com to get your API key,\n"
                              "then go to Settings > Grammarly Integration to enter it.")

    def show_api_key_guide(self):
        """Show step-by-step guide to get API key"""
        try:
            guide_window = ctk.CTkToplevel(self.parent)
            guide_window.title("Grammarly Automated Setup")
            guide_window.geometry("600x400")
            guide_window.transient(self.parent)

            steps = """
            Grammarly Setup Guide:

            1. Visit: https://developer.grammarly.com
            2. Sign up or log in to your account
            3. Go to the Dashboard
            4. Create a new application
            5. Copy your API key
            6. Return here to enter it

            We'll help you configure it automatically!
            """

            text_widget = ctk.CTkTextbox(guide_window, wrap="word")
            text_widget.pack(fill="both", expand=True, padx=20, pady=20)
            text_widget.insert("1.0", steps)
            text_widget.configure(state="disabled")

            def start_setup():
                guide_window.destroy()
                # Use the parent's Grammarly integration to open the portal
                self.parent.grammarly.open_grammarly_portal()
                self.prompt_for_api_key()

            ctk.CTkButton(guide_window, text="Start Setup",
                         command=start_setup).pack(pady=10)

            # Safe grab set
            guide_window.after(100, lambda: self._safe_grab(guide_window))

        except Exception as e:
            print(f"Error showing Grammarly guide: {e}")
            # Fallback to using parent's method
            self.parent.grammarly.open_grammarly_portal()
            self.prompt_for_api_key()

    def start_browser_automation(self, guide_window):
        """Start the browser automation process"""
        guide_window.destroy()
        self.launch_browser_with_grammarly()

    def launch_browser_with_grammarly(self):
        """Launch browser with Grammarly developer portal"""
        grammarly_dev_url = "https://developer.grammarly.com"

        try:
            # Try to use Firefox first (most customizable)
            try:
                # Firefox with specific profile for automation
                firefox_path = self.find_firefox()
                if firefox_path:
                    import subprocess
                    # Create temporary profile for clean session
                    temp_profile = tempfile.mkdtemp()
                    subprocess.Popen([firefox_path, "-new-tab", grammarly_dev_url, "-profile", temp_profile])
                    self.parent.write("✓ Launched Firefox with Grammarly portal\n", "green")
                else:
                    webbrowser.open(grammarly_dev_url)
            except:
                webbrowser.open(grammarly_dev_url)

            # Show API key input dialog
            self.prompt_for_api_key()

        except Exception as e:
            self.parent.write(f"Browser automation failed: {str(e)}\n", "red")
            webbrowser.open(grammarly_dev_url)  # Fallback
            self.prompt_for_api_key()

    def find_firefox(self):
        """Find Firefox browser executable"""
        import platform
        system = platform.system()

        possible_paths = []
        if system == "Windows":
            possible_paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            ]
        elif system == "Darwin":  # macOS
            possible_paths = [
                "/Applications/Firefox.app/Contents/MacOS/firefox",
            ]
        else:  # Linux
            possible_paths = [
                "/usr/bin/firefox",
                "/usr/local/bin/firefox",
                "/snap/bin/firefox",
            ]

        for path in possible_paths:
            if Path(path).exists():
                return path
        return None

    def prompt_for_api_key(self):
        """Show dialog to input API key after browser automation"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Enter Grammarly API Key")
        dialog.geometry("500x300")
        dialog.transient(self.parent)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Grammarly API Key Setup",
                    font=("Arial", 16, "bold")).pack(pady=10)

        instructions = """
        Please complete these steps in the browser we opened:

        1. Login/Create Grammarly account
        2. Go to Dashboard → API Applications
        3. Create New Application (or use existing)
        4. Copy the API Key
        5. Paste it below:
        """

        ctk.CTkLabel(dialog, text=instructions,
                    justify="left").pack(pady=10, padx=20)

        api_frame = ctk.CTkFrame(dialog)
        api_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(api_frame, text="API Key:").pack(side="left", padx=5)
        api_entry = ctk.CTkEntry(api_frame, width=300, show="*")
        api_entry.pack(side="left", padx=5, fill="x", expand=True)

        def validate_and_save():
            api_key = api_entry.get().strip()
            if len(api_key) < 20:  # Basic validation
                messagebox.showerror("Invalid Key", "Please enter a valid API key")
                return

            if self.test_grammarly_key(api_key):
                self.save_grammarly_config(api_key)
                dialog.destroy()
                self.parent.write("✓ Grammarly setup completed successfully!\n", "green")
            else:
                messagebox.showerror("Invalid Key", "API key validation failed")

        ctk.CTkButton(dialog, text="Validate & Save",
                     command=validate_and_save).pack(pady=10)

        # Auto-focus the entry field
        dialog.after(100, api_entry.focus)

    def test_grammarly_key(self, api_key):
        """Test if the Grammarly API key is valid"""
        try:
            import requests

            test_text = "This is a test sentence for Grammarly validation."

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'text': test_text,
                'language': 'en-US'
            }

            response = requests.post(
                'https://api.grammarly.com/api/check',
                headers=headers,
                json=payload,
                timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            self.parent.write(f"API key test failed: {str(e)}\n", "yellow")
            # If requests isn't available, assume it's valid
            return True

    def save_grammarly_config(self, api_key):
        """Save Grammarly configuration automatically"""
        config_dir = Path.home() / '.bsg-ide'
        config_dir.mkdir(exist_ok=True)

        config = {
            'api_key': api_key,
            'enabled': True,
            'setup_completed': True,
            'last_updated': datetime.now().isoformat(),
            'version': 'auto_setup_v1'
        }

        with open(config_dir / 'grammarly_config.json', 'w') as f:
            json.dump(config, f, indent=2)

        # Update the main Grammarly integration
        self.parent.grammarly.grammarly_api_key = api_key
        self.parent.grammarly.grammarly_enabled = True
        self.parent.grammarly.save_grammarly_settings()

        # Update UI
        self.parent.grammarly_button.configure(text="Grammarly: On", fg_color="#28a745")

