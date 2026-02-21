"""Render functions for app views (kept out of Streamlit `pages/` to avoid automatic page listing)."""
from .requestorview import render as render_requestor
from .workerview import render as render_worker
from .supervisor import render as render_supervisor

__all__ = ["render_requestor", "render_worker", "render_supervisor"]
