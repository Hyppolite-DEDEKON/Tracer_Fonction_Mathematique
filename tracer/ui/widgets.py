"""Composants visuels réutilisables."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from tracer.ui.theme import AppTheme


def section_card(parent: tk.Widget, theme: AppTheme, title: str) -> ttk.Frame:
    wrapper = tk.Frame(parent, bg=theme.border, highlightthickness=0)
    wrapper.pack(fill=tk.X, pady=(0, 12))

    inner = ttk.Frame(wrapper, style="Sidebar.TFrame", padding=(12, 10))
    inner.pack(fill=tk.X, padx=1, pady=1)

    ttk.Label(inner, text=title, style="Section.TLabel").pack(anchor="w", pady=(0, 8))
    body = ttk.Frame(inner, style="Sidebar.TFrame")
    body.pack(fill=tk.X)
    return body
