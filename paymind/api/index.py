"""Vercel serverless entry point — wraps the FastAPI app from backend/."""
import sys
import pathlib

# Make backend/ importable
BACKEND_DIR = pathlib.Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from api.main import app  # noqa: E402,F401  — re-exported for Vercel
