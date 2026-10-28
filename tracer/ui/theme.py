"""Palette et styles Tkinter / Matplotlib."""

from __future__ import annotations

from dataclasses import dataclass, field

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from tracer.core.plot_style import PlotTheme


def _pick_font(preferred: str, fallback: str = "TkDefaultFont") -> str:
    families = set(tkfont.families())
    return preferred if preferred in families else fallback


@dataclass(frozen=True)
class AppTheme:
    name: str = "Clair"
    bg: str = "#eef2f7"
    surface: str = "#ffffff"
    sidebar: str = "#f8fafc"
    border: str = "#e2e8f0"
    text: str = "#0f172a"
    text_muted: str = "#64748b"
    accent: str = "#1d4ed8"
    accent_hover: str = "#1e40af"
    danger: str = "#b91c1c"
    font_ui: str = "Ubuntu"
    font_mono: str = "DejaVu Sans Mono"
    plot: PlotTheme = field(default_factory=PlotTheme)


LIGHT_THEME = AppTheme()

DARK_THEME = AppTheme(
    name="Sombre",
    bg="#0b1220",
    surface="#1e293b",
    sidebar="#111827",
    border="#334155",
    text="#f1f5f9",
    text_muted="#94a3b8",
    accent="#3b82f6",
    accent_hover="#2563eb",
    danger="#f87171",
    plot=PlotTheme(
        figure_bg="#0f172a",
        axes_bg="#1e293b",
        curve_color="#60a5fa",
        grid_color="#334155",
        axis_color="#475569",
        text_color="#e2e8f0",
    ),
)


def apply_theme(root: tk.Tk, theme: AppTheme | None = None) -> AppTheme:
    theme = theme or LIGHT_THEME
    ui_font = _pick_font(theme.font_ui)
    mono_font = _pick_font(theme.font_mono, "TkFixedFont")
    theme = AppTheme(
        name=theme.name,
        bg=theme.bg,
        surface=theme.surface,
        sidebar=theme.sidebar,
        border=theme.border,
        text=theme.text,
        text_muted=theme.text_muted,
        accent=theme.accent,
        accent_hover=theme.accent_hover,
        danger=theme.danger,
        font_ui=ui_font,
        font_mono=mono_font,
        plot=theme.plot,
    )

    root.configure(bg=theme.bg)

    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    common_label = {"background": theme.bg, "foreground": theme.text}
    style.configure("App.TFrame", background=theme.bg)
    style.configure("Sidebar.TFrame", background=theme.sidebar)
    style.configure("Card.TFrame", background=theme.surface, relief="flat")
    style.configure(
        "Header.TLabel",
        background=theme.bg,
        foreground=theme.text,
        font=(theme.font_ui, 20, "bold"),
    )
    style.configure(
        "HeaderMuted.TLabel",
        background=theme.bg,
        foreground=theme.text_muted,
        font=(theme.font_ui, 10),
    )
    style.configure(
        "Section.TLabel",
        background=theme.sidebar,
        foreground=theme.text,
        font=(theme.font_ui, 10, "bold"),
    )
    style.configure(
        "Field.TLabel",
        background=theme.sidebar,
        foreground=theme.text_muted,
        font=(theme.font_ui, 9),
    )
    style.configure(
        "Status.TLabel",
        background=theme.bg,
        foreground=theme.text_muted,
        font=(theme.font_ui, 9),
    )
    style.configure(
        "StatusError.TLabel",
        background=theme.bg,
        foreground=theme.danger,
        font=(theme.font_ui, 9),
    )
    style.configure(
        "TEntry",
        fieldbackground=theme.surface,
        foreground=theme.text,
        bordercolor=theme.border,
        lightcolor=theme.border,
        darkcolor=theme.border,
        padding=6,
    )
    style.configure(
        "Mono.TEntry",
        fieldbackground=theme.surface,
        foreground=theme.text,
        font=(theme.font_mono, 11),
        padding=8,
    )
    style.configure(
        "TSpinbox",
        fieldbackground=theme.surface,
        foreground=theme.text,
        arrowcolor=theme.text_muted,
        bordercolor=theme.border,
        padding=4,
    )
    style.configure(
        "TCombobox",
        fieldbackground=theme.surface,
        foreground=theme.text,
        bordercolor=theme.border,
        padding=4,
    )
    style.configure(
        "TCheckbutton",
        background=theme.sidebar,
        foreground=theme.text,
        font=(theme.font_ui, 9),
    )
    style.map("TCheckbutton", background=[("active", theme.sidebar)])
    style.configure(
        "Accent.TButton",
        background=theme.accent,
        foreground="#ffffff",
        borderwidth=0,
        focuscolor=theme.accent,
        padding=(12, 8),
        font=(theme.font_ui, 10, "bold"),
    )
    style.map(
        "Accent.TButton",
        background=[("active", theme.accent_hover), ("disabled", "#64748b")],
        foreground=[("disabled", "#e2e8f0")],
    )
    style.configure(
        "Ghost.TButton",
        background=theme.surface,
        foreground=theme.text,
        bordercolor=theme.border,
        lightcolor=theme.border,
        darkcolor=theme.border,
        padding=(10, 7),
        font=(theme.font_ui, 9),
    )
    style.configure(
        "InlineError.TLabel",
        background=theme.sidebar,
        foreground=theme.danger,
        font=(theme.font_ui, 8),
    )
    style.configure(
        "InlineOk.TLabel",
        background=theme.sidebar,
        foreground="#15803d" if theme.name == "Clair" else "#4ade80",
        font=(theme.font_ui, 8),
    )
    style.configure(
        "InlineMuted.TLabel",
        background=theme.sidebar,
        foreground=theme.text_muted,
        font=(theme.font_ui, 8),
    )
    style.configure(
        "SidebarFooter.TFrame",
        background=theme.sidebar,
    )
    style.map("Ghost.TButton", background=[("active", theme.sidebar)])
    style.configure(
        "Toolbar.TButton",
        background=theme.bg,
        foreground=theme.text_muted,
        padding=(8, 4),
        font=(theme.font_ui, 9),
    )
    style.map("Toolbar.TButton", background=[("active", theme.sidebar)])

    return theme
