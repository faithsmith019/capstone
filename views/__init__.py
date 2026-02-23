"""Render functions for app views (kept out of Streamlit `pages/` to avoid automatic page listing)."""
from .requestorview import render_requestor as render_requestor
from .workerview import render_worker as render_worker
from .supervisor import render_supervisor as render_supervisor

__all__ = ["render_requestor", "render_worker", "render_supervisor"]

#I don't believe this page is necessary anymore
