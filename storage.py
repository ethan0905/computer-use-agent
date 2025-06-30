import json
import pathlib
from typing import List
from config import STORE_PATH, ROOT_DIR
from embeddings import get_embedding

(ROOT_DIR / "success").mkdir(exist_ok=True)
(ROOT_DIR / "fail").mkdir(exist_ok=True)


def load_cache():
    successes: List[dict] = []
    failures: List[dict] = []
    if STORE_PATH.exists():
        with open(STORE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                rec = json.loads(line)
                if rec.get("reward") == 1:
                    successes.append(rec)
                else:
                    failures.append(rec)
    for rec in successes + failures:
        if "embedding" not in rec:
            try:
                rec["embedding"] = get_embedding(rec["prompt"])
            except Exception:
                rec["embedding"] = []
    return successes, failures

successes, failures = load_cache()

def save_flow(prompt, code, reward, folder_name):
    import datetime, re
    folder = ROOT_DIR / folder_name
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")[:60] or "untitled"
    fp = folder / f"{slug}__{ts}.py"
    header = f"# Prompt: {prompt}\n# Outcome: {'success' if reward == 1 else 'fail'}\n\n"
    fp.write_text(header + code, encoding="utf-8")
    rec = {"prompt": prompt, "code": code, "reward": reward, "timestamp": datetime.datetime.now().isoformat()}
    try:
        rec["embedding"] = get_embedding(prompt)
    except Exception:
        rec["embedding"] = []
    with open(STORE_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec) + "\n")
    if reward == 1:
        successes.append(rec)
    else:
        failures.append(rec)
