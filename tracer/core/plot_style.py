"""Styles et options de rendu Matplotlib."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PlotTheme:
    figure_bg: str = "#ffffff"
    axes_bg: str = "#fafbfc"
    curve_color: str = "#1d4ed8"
    grid_color: str = "#cbd5e1"
    axis_color: str = "#94a3b8"
    text_color: str = "#0f172a"


@dataclass(frozen=True)
class PlotThemeDark:
    figure_bg: str = "#0f172a"
    axes_bg: str = "#1e293b"
    curve_color: str = "#60a5fa"
    grid_color: str = "#334155"
    axis_color: str = "#475569"
    text_color: str = "#e2e8f0"


CURVE_PALETTE = ("#1d4ed8", "#dc2626", "#059669", "#7c3aed", "#ea580c")

PRESET_COLORS = {
    "Bleu": "#1d4ed8",
    "Rouge": "#dc2626",
    "Vert": "#059669",
    "Violet": "#7c3aed",
    "Orange": "#ea580c",
}


@dataclass
class PlotOptions:
    sample_count: int = 400
    line_width: float = 2.2
    primary_color: str = "#1d4ed8"
    show_grid: bool = True
    show_origin_axes: bool = True
    split_discontinuities: bool = True
    jump_threshold: float = 50.0
