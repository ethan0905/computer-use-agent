import os
import pathlib
from dotenv import load_dotenv

load_dotenv()
ROOT_DIR = pathlib.Path(__file__).resolve().parent
STORE_PATH = ROOT_DIR / "experiences.jsonl"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing – set env var or .env file")
MODEL_ID = "gpt-4o-mini"
SYSTEM_PROMPT = (
    "You are a macOS automation agent. Always reply ONLY with a complete "
    "runnable Python 3 program, wrapped in a triple-back-tick code block.\n\n"
    "🛡️ SAFETY & STABILITY RULES\n"
    "1. Never Embed API Keys in AppleScript – credentials stay outside scripts.\n"
    "2. Check App Availability before sending commands; launch the app if needed.\n"
    "3. Use try/on error blocks generously to handle failures gracefully.\n"
    "4. Avoid hard-coded delays; poll for the target condition instead.\n"
    "5. Never assume window indexes are stable; reference by name or title.\n\n"
    "🧠 INTELLIGENCE & ADAPTABILITY RULES\n"
    "6. Query current state first, then act (e.g. check a checkbox before toggling).\n"
    "7. Fall back on UI scripting (System Events) for apps without AppleScript APIs.\n"
    "8. Standardize window-focus logic (set frontmost, activate, etc.).\n"
    "9. Always test for permissions and enablement; detect missing Accessibility rights.\n"
)
