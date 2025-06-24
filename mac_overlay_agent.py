import tkinter as tk
import subprocess


def nl_to_applescript(request: str) -> str:
    """Naive translator from natural language request to AppleScript.

    This placeholder function implements a couple of example commands. In a real
    agent you might integrate a language model API or a more sophisticated
    parser to generate AppleScript dynamically.
    """
    lower = request.lower()
    if "open safari" in lower:
        return 'tell application "Safari" to activate'
    if "new note" in lower:
        return 'tell application "Notes" to make new note with properties {body:""}'
    # Default fallback script shows a dialog
    return f'display dialog "Cannot handle request: {request}"'


class OverlayAgent(tk.Tk):
    """Simple overlay agent similar to Spotlight search."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Overlay Agent")
        self.attributes('-topmost', True)
        self.configure(bg='black')
        self.overrideredirect(True)
        self.geometry('600x50+400+200')

        self.entry = tk.Entry(self, bg='black', fg='white', insertbackground='white', font=('Helvetica', 14))
        self.entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.entry.bind('<Return>', self.process_request)
        # Ensure the entry has keyboard focus so typing works immediately
        self.entry.focus_set()

        self.output = tk.Text(self, height=10, bg='black', fg='white', insertbackground='white', font=('Helvetica', 12))
        self.output.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.output.config(state=tk.DISABLED)

    def process_request(self, event=None) -> None:
        request = self.entry.get()
        self.entry.delete(0, tk.END)
        applescript = nl_to_applescript(request)
        self.display_applescript(applescript)
        self.run_applescript(applescript)

    def display_applescript(self, script: str) -> None:
        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, script)
        self.output.config(state=tk.DISABLED)

    def run_applescript(self, script: str) -> None:
        # Execute the generated AppleScript using osascript
        try:
            subprocess.run(["osascript", "-e", script], check=False)
        except FileNotFoundError:
            # On non-macOS platforms osascript will not exist. Ignore errors.
            pass


def main() -> None:
    agent = OverlayAgent()
    agent.mainloop()


if __name__ == "__main__":
    main()
