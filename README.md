# Computer Use Agent

This repository contains a small example of a "computer use" agent for macOS.
The agent is written in Python and displays a minimal overlay similar to the
Spotlight search bar. When you type a natural language request in the overlay,
it generates AppleScript code and executes it using `osascript`.

## Requirements

- macOS system with Python 3.
- Tkinter (usually included with Python on macOS).

## Usage

Run the agent with:

```bash
python mac_overlay_agent.py
```

An overlay window will appear. Type a simple command such as `open Safari` or
`new note`. The agent will display the generated AppleScript and attempt to run
it. The included `nl_to_applescript` function supports only a few basic
examples, but you can extend it or integrate a language model API for more
advanced behavior.

The entry field is automatically focused when the overlay appears, so you can
start typing right away.
