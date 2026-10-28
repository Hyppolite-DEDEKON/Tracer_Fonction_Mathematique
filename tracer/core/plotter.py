"""Création des figures Matplotlib."""

from __future__ import annotations

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from tracer.core.plot_segments import iter_plot_segments
from tracer.core.plot_style import PlotOptions, PlotTheme


@dataclass(frozen=True)
class PlotSeries:
    expression: str
    x: np.ndarray
    y: np.ndarray
    color: str


def build_figure(
    series_list: list[PlotSeries],
    options: PlotOptions,
    theme: PlotTheme,
) -> Figure:
    fig, ax = plt.subplots(figsize=(7.4, 5.5), dpi=100)
    fig.patch.set_facecolor(theme.figure_bg)
    ax.set_facecolor(theme.axes_bg)

    for series in series_list:
        segments = iter_plot_segments(
            series.x,
            series.y,
            split_discontinuities=options.split_discontinuities,
            jump_threshold=options.jump_threshold,
        )
        label = f"y = {series.expression}"
        for segment_index, (sx, sy) in enumerate(segments):
            ax.plot(
                sx,
                sy,
                color=series.color,
                linewidth=options.line_width,
                label=label if segment_index == 0 else "_nolegend_",
            )

    if options.show_origin_axes:
        ax.axhline(0, color=theme.axis_color, linewidth=0.8, alpha=0.65, zorder=0)
        ax.axvline(0, color=theme.axis_color, linewidth=0.8, alpha=0.65, zorder=0)

    if options.show_grid:
        ax.grid(
            True,
            color=theme.grid_color,
            linestyle="--",
            linewidth=0.6,
            alpha=0.85,
            zorder=0,
        )

    title = "Graphique de la fonction"
    if len(series_list) > 1:
        title = "Graphique des fonctions"
    ax.set_title(title, color=theme.text_color, fontsize=13, pad=12)
    ax.set_xlabel("x", color=theme.text_color)
    ax.set_ylabel("y", color=theme.text_color)
    ax.tick_params(colors=theme.text_color)
    for spine in ax.spines.values():
        spine.set_color(theme.axis_color)

    if series_list:
        ax.legend(
            frameon=True,
            facecolor=theme.axes_bg,
            edgecolor=theme.axis_color,
            labelcolor=theme.text_color,
        )

    all_y = np.concatenate([s.y[np.isfinite(s.y)] for s in series_list if np.any(np.isfinite(s.y))])
    if all_y.size:
        y_min, y_max = float(np.min(all_y)), float(np.max(all_y))
        if y_min == y_max:
            margin = 1.0 if y_min == 0 else abs(y_min) * 0.1
            ax.set_ylim(y_min - margin, y_max + margin)

    fig.tight_layout()
    return fig
