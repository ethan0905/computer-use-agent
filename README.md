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
git clone https://github.com/yourname/computer-use-agent
cd computer-use-agent
python3 computer-use-agent.py
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
* - Regenerate
  - Save-as-prompt

### To-Do

* [ ] Add regenerate code button (capture mode)
* [ ] Add rule for codegen to open new window consistency

### How does it work?

1. Prompt Submission
The user enters a prompt describing a desired automation or task.

2. Code Generation
The system checks the smart cache (previous successes/failures) for similar prompts.
If a close match is found, it can reuse the cached code.
Otherwise, it generates new code using the OpenAI API, with retrieval-augmented few-shot learning:
It retrieves the most similar successful and failed examples (using embeddings and cosine distance).
These examples are included as “shots” in the prompt to the model, guiding it to produce better code.
3. Code Execution
The generated (or cached) code is executed automatically.

4. User Feedback (Reward Signal)
The user can give feedback:
👍 (Thumbs up): The code worked as intended (reward = 1).
👎 (Thumbs down): The code failed or was incorrect (reward = 0).
5. Experience Storage
Each experience (prompt, code, reward, timestamp, embedding) is saved to experiences.jsonl and to the appropriate folder (success or fail).
The embedding of the prompt is stored for fast similarity search in future runs.

6. Learning Loop
On future prompts, the system retrieves the most relevant past successes and failures (using embeddings).
These are used to:
Provide positive examples (what worked) and negative examples (what to avoid) to the model.
Avoid repeating failed attempts.
Encourage the model to generate code similar to past successes.

Summary:
This is a form of reinforcement learning from human feedback (RLHF), but implemented as a retrieval-augmented loop:

The “reward” is explicit user feedback.
The “policy” (code generation) is guided by retrieval of past experiences, not by gradient updates.
Over time, the system gets better at producing working code for similar prompts, as it learns from your feedback.
