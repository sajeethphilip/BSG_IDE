#----------------------------------------------Interactive Terminal ------------------------------------
import customtkinter as ctk
import tkinter as tk
import threading
import queue
import socket
import os

class InteractiveTerminal(ctk.CTkFrame):
    """Interactive terminal with proper input capture and validation"""
    def __init__(self, master, initial_directory=None, **kwargs):
        super().__init__(master, **kwargs)

        # Initialize variables
        self.working_dir = initial_directory or os.getcwd()
        self.command_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.waiting_for_input = False
        self.input_response = None
        self.input_event = threading.Event()
        self.current_prompt = None

        # Create UI
        self._create_ui()

        # Start command processor
        self.running = True
        self.process_thread = threading.Thread(target=self._process_commands, daemon=True)
        self.process_thread.start()

    def _create_ui(self):
        """Create terminal UI with improved input handling"""
        # Header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=2, pady=2)

        # Directory label
        self.dir_label = ctk.CTkLabel(header, text=f"📁 {self.working_dir}")
        self.dir_label.pack(side="left", padx=5)

        # Control buttons
        ctk.CTkButton(header, text="Clear",
                     command=self.clear).pack(side="right", padx=5)

        # Terminal display
        self.display = ctk.CTkTextbox(
            self,
            wrap="none",
            font=("Courier", 10)
        )
        self.display.pack(fill="both", expand=True, padx=2, pady=2)

        # Set up text tags for colors
        self.display._textbox.tag_configure("red", foreground="red")
        self.display._textbox.tag_configure("green", foreground="green")
        self.display._textbox.tag_configure("yellow", foreground="yellow")
        self.display._textbox.tag_configure("white", foreground="white")
        self.display._textbox.tag_configure("prompt", foreground="cyan")
        self.display._textbox.tag_configure("input", foreground="white")

        # Enhanced input handling
        self.display.bind("<Return>", self._handle_input)
        self.display.bind("<Key>", self._handle_key)
        self.display.bind("<BackSpace>", self._handle_backspace)

        # Initial prompt
        self.show_prompt()

    def _get_input_start(self):
        """Get the starting position of current input"""
        if self.waiting_for_input:
            # Find the last prompt position
            last_prompt = self.display._textbox.search(
                self.current_prompt or "$ ",
                "1.0",
                stopindex="end",
                backwards=True
            )
            if last_prompt:
                return f"{last_prompt}+{len(self.current_prompt or '$ ')}c"
        return "insert"

    def _handle_key(self, event):
        """Handle regular key input"""
        if self.waiting_for_input:
            if event.char and ord(event.char) >= 32:  # Printable characters
                self.display._textbox.insert("insert", event.char)
                return "break"
        return None

    def _handle_backspace(self, event):
        """Handle backspace key"""
        if self.waiting_for_input:
            input_start = self._get_input_start()
            if self.display._textbox.compare("insert", ">", input_start):
                self.display._textbox.delete("insert-1c", "insert")
            return "break"
        return None

    def terminal_input(self, prompt: str) -> str:
        """Get input synchronously using keyboard event handler"""
        try:
            self.current_prompt = prompt
            self.waiting_for_input = True
            self.input_done = False  # Flag to track input completion
            self.input_result = None  # Store input result

            # Show prompt
            self.write(prompt, "yellow")

            # Focus the display
            self.display.focus_set()

            # Wait for input with active event handling
            while not self.input_done:
                self.update()  # Process events
                self.master.update()  # Allow window updates

            # Get result and reset state
            result = self.input_result
            self.waiting_for_input = False
            self.current_prompt = None
            self.input_done = False
            self.input_result = None

            return result if result is not None else ""

        except Exception as e:
            self.write(f"\nError getting input: {str(e)}\n", "red")
            return ""

    def _handle_input(self, event):
        """Handle Return key for input completion"""
        try:
            if self.waiting_for_input:
                # Get current line
                current_line = self.display._textbox.get("insert linestart", "insert lineend")

                # Extract input after prompt
                if self.current_prompt:
                    input_text = current_line[len(self.current_prompt):].strip()
                else:
                    input_text = current_line.strip()

                # Store result and signal completion
                self.input_result = input_text
                self.input_done = True

                # Add newline for visual feedback
                self.write("\n")
                return "break"

            # Handle regular command input
            current_line = self.display._textbox.get("insert linestart", "insert lineend")
            if current_line.startswith("$ "):
                command = current_line[2:]
                if command.strip():
                    self.command_queue.put(command)
                self.write("\n")
                self.show_prompt()
                return "break"

        except Exception as e:
            self.write(f"\nInput error: {str(e)}\n", "red")

        return "break"

    def write(self, text, color="white"):
        """Write text to terminal with proper scroll"""
        try:
            # Insert text with color tag
            self.display._textbox.insert("end", text, color)
            self.display.see("end")
            self.update_idletasks()

            # Move cursor to end
            self.display._textbox.mark_set("insert", "end")

        except Exception as e:
            print(f"Write error: {e}", file=sys.__stdout__)

    def clear(self):
        """Clear terminal content"""
        self.display._textbox.delete("1.0", "end")
        self.show_prompt()

    def _process_commands(self):
        """Process commands in background"""
        while self.running:
            try:
                command = self.command_queue.get(timeout=0.1)
                if command.startswith("cd "):
                    path = command[3:].strip()
                    self._change_directory(path)
                else:
                    try:
                        process = subprocess.Popen(
                            command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=self.working_dir,
                            text=True
                        )
                        out, err = process.communicate()
                        if out:
                            self.after(0, lambda: self.write(out))
                        if err:
                            self.after(0, lambda: self.write(err, "red"))
                    except Exception as e:
                        self.after(0, lambda: self.write(f"\nError: {str(e)}\n", "red"))
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Command processing error: {e}", file=sys.__stdout__)

    def show_prompt(self):
        """Show command prompt if not waiting for input"""
        if not self.waiting_for_input:
            self.write("\n$ ", "prompt")

    def set_working_directory(self, directory):
        """Set working directory"""
        if os.path.exists(directory):
            self.working_dir = directory
            os.chdir(directory)
            self.dir_label.configure(text=f"📁 {self.working_dir}")
    def _change_directory(self, path):
        """Change working directory"""
        try:
            os.chdir(path)
            self.working_dir = os.getcwd()
            self.dir_label.configure(text=f"📁 {self.working_dir}")
            self.write(f"Changed directory to: {self.working_dir}\n", "green")
        except Exception as e:
            self.write(f"Error changing directory: {str(e)}\n", "red")

#------------------------------------------End Interactive Terminal -----------------------------------------
