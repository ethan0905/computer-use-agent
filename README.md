# Computer Use Agent for MacOS

Computer use agent that runs on MacOS under GPT-4o-mini, with smart cache system, and embedded inside a python app. Please drop a star to support my work ⭐️

### Features

* **Ask & Run:** Type a prompt, hit **Run**, and GPT‑4o-mini generates + executes Python code.
* **Smart Cache:** Detects and reuses previously successful scripts using fuzzy matching and GPT validation.
* **Live Feedback Loop:** Instantly archive outputs as success or fail, with 1-click thumbs up/down.
* **Lightweight UI:** Built with native macOS Cocoa via `pyobjc`.
* **Cost-efficient:** Uses OpenAI’s cheapest GPT‑4-class model (`gpt-4o-mini`).

### Example Use Cases

* Automate Mac tasks (scripts, file operations, UI actions)
* Prototype Python snippets rapidly
* Learn by doing: GPT-generated code is visible and editable

### Requirements

* macOS
* Python 3.8+
* `pip install openai python-dotenv pyobjc`
* `brew install cliclick`
* `.env` file with:

  ```
  OPENAI_API_KEY=sk-...
  ```

### Getting Started

```bash
git clone https://github.com/yourname/mini-focus
cd mini-focus
python3 mini_focus_openai.py
```

Make sure your `.env` file contains a valid OpenAI API key.

### How It Works

1. **Prompt Input:** You describe what you want.
2. **Smart Cache:** Reuses previously successful code if matched.
3. **Code Generation:** GPT‑4o-mini returns a valid Python script.
4. **Execution:** The script runs live in a subprocess.
5. **Feedback:** Rate the output. The script is stored to `./success/` or `./fail/`.

### Output Folders

* `success/`: Scripts that executed successfully
* `fail/`: Failed or rejected ones
* Scripts are saved with timestamped filenames and the original prompt as a header

### Developer Notes

* GUI: Native macOS via PyObjC
* Cache: Fuzzy-matched based on prompt + validated by GPT
* Feedback: Saves reusable snippets to disk

### Revision History

* **2025‑06‑24 a** — Initial GUI code-runner.
* **2025‑06‑24 b** — Smart cache logic and feedback archive bug-fix.
* **2025‑06‑24 c** — Fixed GUI button wiring and feedback toggle restore.
* — Reinforcement learning
* — Thumbs up/down
* — Smart cache codegen logic
* — Capture mode
* — Fix capture mode datas stored
* — Fix codegen prompt + format for auto exec

### To-Do

* [ ] Add regenerate code button (capture mode)
