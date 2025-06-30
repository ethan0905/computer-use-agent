# --- UI LOG BUTTON EXAMPLES ---
def log_test_button(idx, desc):
    print(f"[UI LOG] Test button pressed for step {idx+1} | Description: {desc}")

def log_regenerate_button(idx, desc, code):
    print(f"[UI LOG] Regenerate button pressed for step {idx+1} | Description: {desc}")
    print(f"[UI LOG] Step {idx+1} regenerated code: {code[:80]}{'...' if len(code) > 80 else ''}")

def log_validate_button(idx, desc):
    print(f"[UI LOG] Validate button pressed for step {idx+1} | Description: {desc}")
    print(f"[UI LOG] Step {idx+1} validated.")

# Example usage:
if __name__ == "__main__":
    # Simulate three steps
    steps = ["Open Perplexity", "Search for AI research", "Copy first result"]
    codes = ["code1()", "code2()", "code3()"]
    for idx, desc in enumerate(steps):
        log_test_button(idx, desc)
        log_regenerate_button(idx, desc, codes[idx])
        log_validate_button(idx, desc)
"""
complex.py – Decompose complex user requests into small, verifiable steps with user validation.

This module provides a function to break down a user request into atomic steps, execute each step (with retries and user validation), and store the full working flow only if all steps succeed.
"""

from typing import List, Callable

class Step:
    def __init__(self, description: str, action: Callable[[], bool]):
        self.description = description
        self.action = action
        self.success = False
        self.attempts = 0

    def run(self, max_retries=3, validate_fn=None):
        for _ in range(max_retries):
            self.attempts += 1
            print(f"[Step] {self.description} (Attempt {self.attempts})")
            ok = self.action()
            if validate_fn:
                ok = validate_fn(self.description, ok)
            if ok:
                self.success = True
                print(f"[Step] Success: {self.description}")
                return True
            else:
                print(f"[Step] Failed: {self.description}")
        return False

def decompose_request(request: str) -> List[str]:
    """Decompose a complex request into actionable steps using OpenAI GPT-4o-mini."""
    import openai
    from config import OPENAI_API_KEY, MODEL_ID
    CLIENT = openai.OpenAI(api_key=OPENAI_API_KEY)
    system_prompt = (
        "You are an expert macOS automation agent. Given a user request, break it down into a numbered list of the smallest possible actionable steps, each step being a single, verifiable user action. Do not combine actions. Only output the list, no explanations."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Request: {request}\nList:"},
    ]
    rsp = CLIENT.chat.completions.create(
        model=MODEL_ID,
        temperature=0.1,
        max_tokens=512,
        messages=messages,
    )
    msg = rsp.choices[0].message.content
    # Parse numbered list (e.g., 1. Do X\n2. Do Y...)
    import re
    steps = re.findall(r"\d+\.\s*(.+)", msg)
    # Fallback: if not numbered, split by lines
    if not steps:
        steps = [line.strip("- ") for line in msg.strip().splitlines() if line.strip()]
    return steps

def execute_complex_flow(request: str, codegen_fn, validate_fn=None, max_retries=3, store_fn=None):
    """
    Decompose the request, execute each step with user validation, and store the flow if all succeed.
    - codegen_fn: function that takes a step description and returns a callable action.
    - validate_fn: function that takes (step_description, result) and returns True/False.
    - store_fn: function to store the full flow (list of steps) on success.
    """
    steps_text = decompose_request(request)
    steps = [Step(desc, codegen_fn(desc)) for desc in steps_text]
    for step in steps:
        if not step.run(max_retries=max_retries, validate_fn=validate_fn):
            print(f"[Flow] Aborted at step: {step.description}")
            return False
    print("[Flow] All steps succeeded!")
    if store_fn:
        store_fn(request, steps)
    return True
