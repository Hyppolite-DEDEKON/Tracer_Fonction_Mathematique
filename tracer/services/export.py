"""Export PNG / PDF des graphiques."""

from __future__ import annotations

from pathlib import Path

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure


class ExportError(OSError):
    """Échec de l'export du fichier."""


def export_figure(fig: Figure, file_path: str) -> None:
    path = Path(file_path)
    suffix = path.suffix.lower()
    try:
        if suffix == ".pdf":
            with PdfPages(path) as pdf:
                pdf.savefig(fig, bbox_inches="tight")
        elif suffix in {".png", ".jpg", ".jpeg", ".svg"}:
            fig.savefig(path, bbox_inches="tight", dpi=150)
        else:
            fig.savefig(path, bbox_inches="tight", dpi=150)
    except OSError as exc:
        raise ExportError(str(exc)) from exc
