"""Fenêtre principale de l'application."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from tracer.core.evaluator import ExpressionError, evaluate_expression
from tracer.core.plot_style import CURVE_PALETTE, PRESET_COLORS, PlotOptions
from tracer.core.plotter import PlotSeries, build_figure
from tracer.services.export import ExportError, export_figure
from tracer.ui.help_dialog import HelpDialog
from tracer.ui.theme import DARK_THEME, LIGHT_THEME, AppTheme, apply_theme
from tracer.ui.widgets import section_card

DEFAULT_EXPRESSION = "x**2"
DEFAULT_X_MIN = "-10"
DEFAULT_X_MAX = "10"


class MainWindow:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Traceur de fonctions")
        self.root.minsize(980, 660)
        self.root.geometry("1180x760")

        self._dark_mode = False
        self.theme = apply_theme(self.root, LIGHT_THEME)
        self._figure: Figure | None = None
        self._canvas: FigureCanvasTkAgg | None = None
        self._toolbar: NavigationToolbar2Tk | None = None
        self._surface_frames: list[tk.Widget] = []
        self._refresh_job: str | None = None
        self._validation_job: str | None = None
        self._sidebar_canvas: tk.Canvas | None = None

        self._build_layout()
        self._bind_shortcuts()
        self._wire_live_refresh()
        self._set_status("Prêt — saisissez une fonction et cliquez sur Tracer.")

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-Return>", lambda _e: self.plot_function())
        self.root.bind("<Control-e>", lambda _e: self.export_graph())
        self.root.bind("<Control-l>", lambda _e: self.clear_plot())

    def _build_layout(self) -> None:
        self.root_frame = ttk.Frame(self.root, style="App.TFrame", padding=(16, 12))
        self.root_frame.pack(fill=tk.BOTH, expand=True)
        self.root_frame.columnconfigure(1, weight=1)
        self.root_frame.rowconfigure(1, weight=1)

        self._build_header(self.root_frame)
        self._build_sidebar(self.root_frame)
        self._build_plot_area(self.root_frame)

        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            self.root_frame,
            textvariable=self.status_var,
            style="Status.TLabel",
        )
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def _build_header(self, parent: ttk.Frame) -> None:
        header = ttk.Frame(parent, style="App.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        header.columnconfigure(0, weight=1)

        title_block = ttk.Frame(header, style="App.TFrame")
        title_block.grid(row=0, column=0, sticky="w")
        ttk.Label(title_block, text="Traceur de fonctions", style="Header.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            title_block,
            text="Analyse visuelle de f(x) — comparaison et export",
            style="HeaderMuted.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        tools = ttk.Frame(header, style="App.TFrame")
        tools.grid(row=0, column=1, sticky="e")
        self.theme_button = ttk.Button(
            tools,
            text="Mode sombre",
            style="Toolbar.TButton",
            command=self.toggle_theme,
        )
        self.theme_button.pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(
            tools,
            text="Aide",
            style="Toolbar.TButton",
            command=self.show_help,
        ).pack(side=tk.RIGHT)

        accent = tk.Frame(header, bg=self.theme.accent, height=3)
        accent.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self._accent_bar = accent

    def _build_sidebar(self, parent: ttk.Frame) -> None:
        sidebar_shell = ttk.Frame(parent, style="Sidebar.TFrame")
        sidebar_shell.grid(row=1, column=0, sticky="nsew", padx=(0, 14))
        sidebar_shell.rowconfigure(0, weight=1)
        sidebar_shell.columnconfigure(0, weight=1)

        scroll_host = ttk.Frame(sidebar_shell, style="Sidebar.TFrame")
        scroll_host.grid(row=0, column=0, columnspan=2, sticky="nsew")
        scroll_host.rowconfigure(0, weight=1)
        scroll_host.columnconfigure(0, weight=1)

        canvas = tk.Canvas(
            scroll_host,
            width=340,
            highlightthickness=0,
            bg=self.theme.sidebar,
        )
        self._sidebar_canvas = canvas
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(scroll_host, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.sidebar_inner = ttk.Frame(canvas, style="Sidebar.TFrame")
        window_id = canvas.create_window((0, 0), window=self.sidebar_inner, anchor="nw")

        def _on_configure(_event: tk.Event) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(window_id, width=canvas.winfo_width())

        self.sidebar_inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window_id, width=e.width))

        def _on_mousewheel(event: tk.Event) -> None:
            if getattr(event, "num", None) == 5:
                canvas.yview_scroll(1, "units")
            elif getattr(event, "num", None) == 4:
                canvas.yview_scroll(-1, "units")
            elif event.delta:
                canvas.yview_scroll(int(-event.delta / 120), "units")

        def _activate_scroll(_event: tk.Event) -> None:
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)

        def _deactivate_scroll(_event: tk.Event) -> None:
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        canvas.bind("<Enter>", _activate_scroll)
        canvas.bind("<Leave>", _deactivate_scroll)

        self._build_expression_section()
        self._build_interval_section()
        self._build_style_section()
        self._build_actions_section()
        self._build_examples_section()
        self._build_sidebar_footer(sidebar_shell)

    def _wire_live_refresh(self) -> None:
        """Recalcule le graphique quand les réglages changent (si un tracé existe)."""
        watched: list[tk.Variable] = [
            *self.expr_vars,
            self.x_min_var,
            self.x_max_var,
            self.sample_var,
            self.width_var,
            self.color_var,
            self.grid_var,
            self.origin_var,
            self.split_var,
        ]
        for var in watched:
            var.trace_add("write", lambda *_args: self._schedule_live_refresh())

        for var in self.expr_vars:
            var.trace_add("write", lambda *_args: self._schedule_expression_validation())

        self.x_min_var.trace_add("write", lambda *_args: self._schedule_expression_validation())
        self.x_max_var.trace_add("write", lambda *_args: self._schedule_expression_validation())
        self.root.after_idle(self._update_expression_feedback)

    def _schedule_expression_validation(self, delay_ms: int = 280) -> None:
        if self._validation_job is not None:
            self.root.after_cancel(self._validation_job)
        self._validation_job = self.root.after(delay_ms, self._run_expression_validation)

    def _run_expression_validation(self) -> None:
        self._validation_job = None
        self._update_expression_feedback()

    def _update_expression_feedback(self) -> None:
        probe_x = np.linspace(-2, 2, 9)
        try:
            x_min, x_max = self._parse_interval()
            probe_x = np.linspace(x_min, x_max, min(9, max(3, 9)))
        except ExpressionError:
            pass

        any_primary = False
        for index, (var, label) in enumerate(zip(self.expr_vars, self.expr_feedback_labels)):
            expression = var.get().strip()
            if not expression:
                if index == 0:
                    label.configure(text="Expression requise pour tracer.", style="InlineError.TLabel")
                else:
                    label.configure(text="Optionnel — laisser vide si inutilisé.", style="InlineMuted.TLabel")
                continue

            any_primary = True
            try:
                y = evaluate_expression(expression, probe_x)
                if not np.any(np.isfinite(y)):
                    raise ExpressionError("Aucune valeur finie sur l'intervalle choisi.")
                label.configure(text="Expression valide.", style="InlineOk.TLabel")
            except ExpressionError as exc:
                label.configure(text=str(exc), style="InlineError.TLabel")

        if not any_primary and self.expr_vars[0].get().strip() == "":
            self.expr_feedback_labels[0].configure(
                text="Expression requise pour tracer.",
                style="InlineError.TLabel",
            )

    def _build_sidebar_footer(self, parent: ttk.Frame) -> None:
        separator = tk.Frame(parent, bg=self.theme.border, height=1)
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self._sidebar_separator = separator

        footer = ttk.Frame(parent, style="SidebarFooter.TFrame", padding=(0, 10, 0, 0))
        footer.grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Button(footer, text="Tracer", style="Accent.TButton", command=self.plot_function).pack(
            fill=tk.X, pady=(0, 8)
        )
        ttk.Button(footer, text="Effacer le graphique", style="Ghost.TButton", command=self.clear_plot).pack(
            fill=tk.X
        )
        self._sidebar_footer = footer

    def _schedule_live_refresh(self, delay_ms: int = 320) -> None:
        if self._figure is None:
            return
        if self._refresh_job is not None:
            self.root.after_cancel(self._refresh_job)
        self._refresh_job = self.root.after(delay_ms, self._live_refresh)

    def _live_refresh(self) -> None:
        self._refresh_job = None
        self.plot_function(silent=True)

    def _build_expression_section(self) -> None:
        body = section_card(self.sidebar_inner, self.theme, "Fonctions")
        ttk.Label(
            body,
            text="Jusqu'à 3 courbes sur le même graphique.",
            style="Field.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        self.expr_vars: list[tk.StringVar] = []
        self.expr_feedback_labels: list[ttk.Label] = []
        labels = ("Fonction 1", "Fonction 2 (optionnel)", "Fonction 3 (optionnel)")
        defaults = (DEFAULT_EXPRESSION, "", "")
        for label, default in zip(labels, defaults):
            ttk.Label(body, text=label, style="Field.TLabel").pack(anchor="w", pady=(4, 2))
            var = tk.StringVar(value=default)
            entry = ttk.Entry(body, textvariable=var, style="Mono.TEntry")
            entry.pack(fill=tk.X)
            feedback = ttk.Label(body, text="", style="InlineMuted.TLabel", wraplength=280)
            feedback.pack(anchor="w", pady=(2, 6))
            entry.bind("<Control-Return>", lambda _e: self.plot_function())
            if not self.expr_vars:
                entry.focus_set()
            self.expr_vars.append(var)
            self.expr_feedback_labels.append(feedback)

    def _build_interval_section(self) -> None:
        body = section_card(self.sidebar_inner, self.theme, "Intervalle")
        grid = ttk.Frame(body, style="Sidebar.TFrame")
        grid.pack(fill=tk.X)
        grid.columnconfigure(1, weight=1)

        ttk.Label(grid, text="x minimum", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        self.x_min_var = tk.StringVar(value=DEFAULT_X_MIN)
        ttk.Entry(grid, textvariable=self.x_min_var).grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ttk.Label(grid, text="x maximum", style="Field.TLabel").grid(
            row=1, column=0, sticky="w", pady=(8, 0)
        )
        self.x_max_var = tk.StringVar(value=DEFAULT_X_MAX)
        ttk.Entry(grid, textvariable=self.x_max_var).grid(
            row=1, column=1, sticky="ew", padx=(8, 0), pady=(8, 0)
        )

    def _build_style_section(self) -> None:
        body = section_card(self.sidebar_inner, self.theme, "Style du graphique")
        grid = ttk.Frame(body, style="Sidebar.TFrame")
        grid.pack(fill=tk.X)
        grid.columnconfigure(1, weight=1)

        ttk.Label(grid, text="Points d'échantillonnage", style="Field.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.sample_var = tk.IntVar(value=400)
        ttk.Spinbox(grid, from_=100, to=5000, increment=100, textvariable=self.sample_var, width=8).grid(
            row=0, column=1, sticky="w", padx=(8, 0)
        )

        ttk.Label(grid, text="Épaisseur de courbe", style="Field.TLabel").grid(
            row=1, column=0, sticky="w", pady=(8, 0)
        )
        self.width_var = tk.DoubleVar(value=2.2)
        ttk.Spinbox(
            grid,
            from_=0.8,
            to=5.0,
            increment=0.2,
            textvariable=self.width_var,
            width=8,
        ).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(8, 0))

        ttk.Label(grid, text="Couleur principale", style="Field.TLabel").grid(
            row=2, column=0, sticky="w", pady=(8, 0)
        )
        self.color_var = tk.StringVar(value="Bleu")
        ttk.Combobox(
            grid,
            textvariable=self.color_var,
            values=list(PRESET_COLORS.keys()),
            state="readonly",
            width=14,
        ).grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(8, 0))

        checks = ttk.Frame(body, style="Sidebar.TFrame")
        checks.pack(fill=tk.X, pady=(10, 0))
        self.grid_var = tk.BooleanVar(value=True)
        self.origin_var = tk.BooleanVar(value=True)
        self.split_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(checks, text="Grille", variable=self.grid_var).pack(anchor="w")
        ttk.Checkbutton(checks, text="Axes x = 0 et y = 0", variable=self.origin_var).pack(
            anchor="w", pady=(4, 0)
        )
        ttk.Checkbutton(
            checks,
            text="Couper aux discontinuités",
            variable=self.split_var,
        ).pack(anchor="w", pady=(4, 0))

    def _build_actions_section(self) -> None:
        body = section_card(self.sidebar_inner, self.theme, "Export")
        ttk.Button(
            body,
            text="Exporter PNG / PDF / SVG…",
            style="Ghost.TButton",
            command=self.export_graph,
        ).pack(fill=tk.X)
        ttk.Label(
            body,
            text="Raccourci : Ctrl+E",
            style="Field.TLabel",
        ).pack(anchor="w", pady=(6, 0))

    def _build_examples_section(self) -> None:
        body = section_card(self.sidebar_inner, self.theme, "Exemples rapides")
        examples = (
            ("Parabole", ("x**2", "", "")),
            ("Sinus / Cosinus", ("sin(x)", "cos(x)", "")),
            ("Hyperbole", ("1/x", "", "")),
            ("Gaussienne", ("exp(-x**2)", "", "")),
        )
        for label, exprs in examples:
            ttk.Button(
                body,
                text=label,
                style="Ghost.TButton",
                command=lambda e=exprs: self._load_examples(e),
            ).pack(fill=tk.X, pady=(0, 6))

    def _build_plot_area(self, parent: ttk.Frame) -> None:
        self.plot_card = tk.Frame(
            parent,
            bg=self.theme.surface,
            highlightbackground=self.theme.border,
            highlightthickness=1,
        )
        self.plot_card.grid(row=1, column=1, sticky="nsew")
        self.plot_card.rowconfigure(0, weight=1)
        self.plot_card.columnconfigure(0, weight=1)
        self._surface_frames.append(self.plot_card)

        self.plot_container = tk.Frame(self.plot_card, bg=self.theme.surface)
        self.plot_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.plot_container.rowconfigure(0, weight=1)
        self.plot_container.columnconfigure(0, weight=1)
        self._surface_frames.append(self.plot_container)

        self.placeholder = tk.Label(
            self.plot_container,
            text="Aucun graphique pour l'instant.\n\nSaisissez f(x) et l'intervalle,\npuis « Tracer » en bas du panneau.",
            bg=self.theme.surface,
            fg=self.theme.text_muted,
            font=(self.theme.font_ui, 11),
            justify=tk.CENTER,
        )
        self.placeholder.grid(row=0, column=0, sticky="nsew")

    def _load_examples(self, expressions: tuple[str, str, str]) -> None:
        for var, value in zip(self.expr_vars, expressions):
            var.set(value)
        self.plot_function()

    def _parse_interval(self) -> tuple[float, float]:
        try:
            x_min = float(self.x_min_var.get().strip().replace(",", "."))
            x_max = float(self.x_max_var.get().strip().replace(",", "."))
        except ValueError as exc:
            raise ExpressionError("Les bornes de l'intervalle doivent être des nombres.") from exc
        if x_min >= x_max:
            raise ExpressionError("x min doit être strictement inférieur à x max.")
        return x_min, x_max

    def _collect_plot_options(self) -> PlotOptions:
        color_name = self.color_var.get()
        primary = PRESET_COLORS.get(color_name, PRESET_COLORS["Bleu"])
        try:
            sample = int(self.sample_var.get())
            sample = max(100, min(5000, sample))
        except tk.TclError:
            sample = 400
        try:
            width = float(self.width_var.get())
            width = max(0.5, min(6.0, width))
        except tk.TclError:
            width = 2.2
        return PlotOptions(
            sample_count=sample,
            line_width=width,
            primary_color=primary,
            show_grid=self.grid_var.get(),
            show_origin_axes=self.origin_var.get(),
            split_discontinuities=self.split_var.get(),
        )

    def _collect_series(self, x: np.ndarray, options: PlotOptions) -> list[PlotSeries]:
        series: list[PlotSeries] = []
        color_index = 0
        for var in self.expr_vars:
            expression = var.get().strip()
            if not expression:
                continue
            y = evaluate_expression(expression, x)
            if not np.any(np.isfinite(y)):
                raise ExpressionError(
                    f"« {expression} » ne renvoie aucune valeur finie sur cet intervalle."
                )
            if color_index == 0:
                color = options.primary_color
            else:
                color = CURVE_PALETTE[color_index % len(CURVE_PALETTE)]
            series.append(PlotSeries(expression=expression, x=x, y=y, color=color))
            color_index += 1
        if not series:
            raise ExpressionError("Saisissez au moins une expression.")
        return series

    def _set_status(self, message: str, *, error: bool = False) -> None:
        self.status_var.set(message)
        self.status_label.configure(style="StatusError.TLabel" if error else "Status.TLabel")

    def _clear_plot_widgets(self) -> None:
        if self._toolbar is not None:
            self._toolbar.destroy()
            self._toolbar = None
        if self._canvas is not None:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None
        if self._figure is not None:
            import matplotlib.pyplot as plt

            plt.close(self._figure)
            self._figure = None

    def clear_plot(self) -> None:
        if self._refresh_job is not None:
            self.root.after_cancel(self._refresh_job)
            self._refresh_job = None
        self._clear_plot_widgets()
        self.placeholder.grid(row=0, column=0, sticky="nsew")
        self._set_status("Graphique effacé.")

    def _capture_view_limits(self) -> tuple[tuple[float, float], tuple[float, float]] | None:
        if self._figure is None or not self._figure.axes:
            return None
        ax = self._figure.axes[0]
        return ax.get_xlim(), ax.get_ylim()

    def _apply_view_limits(
        self,
        limits: tuple[tuple[float, float], tuple[float, float]] | None,
    ) -> None:
        if limits is None or self._figure is None or not self._figure.axes:
            return
        ax = self._figure.axes[0]
        ax.set_xlim(limits[0])
        ax.set_ylim(limits[1])

    def plot_function(self, *, silent: bool = False, preserve_view: bool | None = None) -> None:
        if preserve_view is None:
            preserve_view = silent

        saved_limits = self._capture_view_limits() if preserve_view else None
        options = self._collect_plot_options()
        try:
            x_min, x_max = self._parse_interval()
            x = np.linspace(x_min, x_max, options.sample_count)
            series = self._collect_series(x, options)

            self._clear_plot_widgets()
            self.placeholder.grid_forget()

            self._figure = build_figure(series, options, self.theme.plot)
            self._apply_view_limits(saved_limits)
            self._canvas = FigureCanvasTkAgg(self._figure, master=self.plot_container)
            canvas_widget = self._canvas.get_tk_widget()
            canvas_widget.configure(bg=self.theme.surface)
            canvas_widget.grid(row=0, column=0, sticky="nsew")
            self._canvas.draw()

            self._toolbar = NavigationToolbar2Tk(
                self._canvas, self.plot_container, pack_toolbar=False
            )
            self._toolbar.update()
            self._toolbar.grid(row=1, column=0, sticky="ew", pady=(6, 0))

            if len(series) == 1:
                expr_text = series[0].expression
                self._set_status(
                    f"Tracé de f(x) = {expr_text} sur [{x_min:g} ; {x_max:g}] "
                    f"({options.sample_count} points)."
                )
            else:
                self._set_status(
                    f"{len(series)} courbes tracées sur [{x_min:g} ; {x_max:g}] "
                    f"({options.sample_count} points)."
                )
            self._update_expression_feedback()
        except ExpressionError as exc:
            self._set_status(str(exc), error=True)
            if not silent:
                messagebox.showerror("Expression invalide", str(exc))
        except Exception as exc:
            self._set_status("Erreur inattendue lors du tracé.", error=True)
            if not silent:
                messagebox.showerror("Erreur", str(exc))

    def export_graph(self) -> None:
        if self._figure is None:
            messagebox.showinfo(
                "Rien à exporter",
                "Tracez d'abord une fonction, puis exportez le graphique.",
            )
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("PDF", "*.pdf"),
                ("SVG", "*.svg"),
            ],
        )
        if not file_path:
            return

        try:
            export_figure(self._figure, file_path)
            self._set_status(f"Graphique enregistré : {file_path}")
            messagebox.showinfo("Export réussi", f"Fichier enregistré :\n{file_path}")
        except ExportError as exc:
            self._set_status(str(exc), error=True)
            messagebox.showerror("Export impossible", str(exc))

    def show_help(self) -> None:
        HelpDialog(self.root, self.theme)

    def toggle_theme(self) -> None:
        self._dark_mode = not self._dark_mode
        base = DARK_THEME if self._dark_mode else LIGHT_THEME
        self.theme = apply_theme(self.root, base)
        self.theme_button.configure(text="Mode clair" if self._dark_mode else "Mode sombre")
        self._accent_bar.configure(bg=self.theme.accent)

        for frame in self._surface_frames:
            frame.configure(bg=self.theme.surface)
        self.placeholder.configure(bg=self.theme.surface, fg=self.theme.text_muted)

        canvas = self._sidebar_canvas
        if canvas is not None:
            canvas.configure(bg=self.theme.sidebar)
        if hasattr(self, "_sidebar_separator"):
            self._sidebar_separator.configure(bg=self.theme.border)

        if self._figure is not None:
            self.plot_function(preserve_view=True)

    def run(self) -> None:
        self.root.mainloop()
