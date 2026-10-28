"""Fenêtre d'aide détaillée."""

from __future__ import annotations

import tkinter as tk
from tkinter import scrolledtext, ttk

from tracer.ui.theme import AppTheme

HELP_CONTENT = """Traceur de fonctions — aide

Étapes
1. Saisissez une ou plusieurs expressions f(x).
2. Définissez l'intervalle [x min, x max].
3. Ajustez le style du graphique si besoin.
4. Cliquez sur « Tracer » (ou Ctrl+Entrée).

Expressions
• Variable : x
• Constantes : pi, e
• Opérations : +, -, *, /, **, %

Fonctions
sin, cos, tan, asin, acos, atan,
sinh, cosh, tanh,
exp, log, log10, sqrt, abs, floor, ceil

Exemples
  x**2
  sin(x) * cos(x)
  exp(-x**2)
  log(abs(x) + 1)
  1/x   (les asymptotes sont séparées automatiquement)

Comparaison
Renseignez les champs « Fonction 2 » et « Fonction 3 » pour superposer
plusieurs courbes (couleurs distinctes).

Export
PNG, PDF ou SVG via le bouton d'export (Ctrl+E).

Raccourcis
Ctrl+Entrée — tracer
Ctrl+E — exporter
Ctrl+L — effacer le graphique
"""


class HelpDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, theme: AppTheme) -> None:
        super().__init__(parent)
        self.title("Aide")
        self.geometry("520x480")
        self.configure(bg=theme.bg)
        self.transient(parent)
        self.grab_set()

        frame = ttk.Frame(self, style="App.TFrame", padding=16)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Aide", style="Header.TLabel").pack(anchor="w")
        text = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            font=(theme.font_mono, 10),
            bg=theme.surface,
            fg=theme.text,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=theme.border,
            padx=10,
            pady=10,
        )
        text.pack(fill=tk.BOTH, expand=True, pady=(12, 12))
        text.insert("1.0", HELP_CONTENT)
        text.configure(state=tk.DISABLED)

        ttk.Button(frame, text="Fermer", style="Accent.TButton", command=self.destroy).pack(
            anchor="e"
        )
