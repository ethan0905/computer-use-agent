from config import SYSTEM_PROMPT, MODEL_ID
from embeddings import get_embedding, distances_from_embeddings
from storage import successes, failures
import openai
import re
from config import OPENAI_API_KEY

CLIENT = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_python_code(prompt: str) -> str:
    prompt_emb = get_embedding(prompt)
    succ_embs = [r["embedding"] for r in successes]
    succ_dists = distances_from_embeddings(prompt_emb, succ_embs)
    top_succ = sorted(zip(succ_dists, successes), key=lambda x: x[0])[:3]
    fail_embs = [r["embedding"] for r in failures]
    fail_dists = distances_from_embeddings(prompt_emb, fail_embs)
    top_fail = sorted(zip(fail_dists, failures), key=lambda x: x[0])[:2]

    shots = ""
    for _, ex in top_succ:
        shots += f"### Good Example\nUser: {ex['prompt']}\nAssistant:\n```python\n{ex['code']}```\n\n"
    if top_fail:
        shots += "### Avoid These Patterns\n"
        for _, ex in top_fail:
            shots += f"- {ex['prompt']}\n"
        shots += "\n"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": shots + f"### New Request\n{prompt}"},
    ]
    rsp = CLIENT.chat.completions.create(
        model=MODEL_ID,
        temperature=0.1,
        max_tokens=1024,
        messages=messages,
    )
    msg = rsp.choices[0].message.content
    m = re.search(r"```(?:python)?\s*(.+?)\s*```", msg, re.DOTALL)
    if not m:
        raise ValueError("Model reply lacked a Python code block:\n" + msg)
    return m.group(1)
