# config.py
from pathlib import Path
from dotenv import load_dotenv
import os
import streamlit as st

# 1. Dynamically detect project root
PROJECT_ROOT = Path(__file__).resolve().parent

ENV_PATH = PROJECT_ROOT / '.env'

print(f"\n📁 PROJECT_ROOT: {PROJECT_ROOT}")
print(f"🧪 .env found: {ENV_PATH.exists()}")

# ✅ 2. Force-load .env with override=True
load_dotenv(dotenv_path=str(ENV_PATH), override=True)
assert os.getenv("GROQ_API_KEY") is not None, "❌ load_dotenv failed to load GROQ_API_KEY!"


# 3. Detect run mode
mode = "cloud" if st.secrets else "local"
print(f"🔧 Mode: {mode}")

# 4. Try to fetch GROQ_API_KEY
API_KEY = (
    os.getenv("GROQ_API_KEY") or
    st.secrets.get("GROQ_API_KEY", None)
)

# Debugging
print(f"🔑 From os.getenv: {os.getenv('GROQ_API_KEY')}")
print(f"🔐 From st.secrets: {st.secrets.get('GROQ_API_KEY', None) if st.secrets else None}")

if not API_KEY:
    print("🚫 GROQ_API_KEY NOT FOUND!")

# Final export
GROQ_API_KEY = API_KEY

def get_model_path(model_name: str):
    return PROJECT_ROOT / 'models' / model_name


