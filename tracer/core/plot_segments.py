"""Découpe des courbes aux discontinuités et valeurs non finies."""

from __future__ import annotations

import numpy as np


def iter_plot_segments(
    x: np.ndarray,
    y: np.ndarray,
    *,
    split_discontinuities: bool = True,
    jump_threshold: float = 50.0,
) -> list[tuple[np.ndarray, np.ndarray]]:
    if x.size == 0:
        return []

    finite = np.isfinite(y)
    segments: list[tuple[int, int]] = []
    start: int | None = None

    for index in range(len(y)):
        if finite[index]:
            if start is None:
                start = index
        elif start is not None:
            segments.append((start, index))
            start = None
    if start is not None:
        segments.append((start, len(y)))

    if not split_discontinuities:
        return [(x[a:b], y[a:b]) for a, b in segments if b - a >= 1]

    refined: list[tuple[int, int]] = []
    for a, b in segments:
        refined.extend(_split_jumps(x, y, a, b, jump_threshold))

    return [(x[a:b], y[a:b]) for a, b in refined if b - a >= 1]


def _split_jumps(
    x: np.ndarray,
    y: np.ndarray,
    start: int,
    end: int,
    jump_threshold: float,
) -> list[tuple[int, int]]:
    if end - start <= 1:
        return [(start, end)]

    chunk_y = y[start:end]
    scale = float(np.nanmedian(np.abs(chunk_y)))
    if scale < 1e-6:
        scale = 1.0
    limit = max(jump_threshold, 8.0 * scale)

    pieces: list[tuple[int, int]] = []
    piece_start = start
    for index in range(start, end - 1):
        left, right = y[index], y[index + 1]
        if not (np.isfinite(left) and np.isfinite(right)):
            continue
        if abs(right - left) > limit:
            if index + 1 - piece_start >= 1:
                pieces.append((piece_start, index + 1))
            piece_start = index + 1
        elif left * right < 0:
            if index + 1 - piece_start >= 1:
                pieces.append((piece_start, index + 1))
            piece_start = index + 1

    if end - piece_start >= 1:
        pieces.append((piece_start, end))
    return pieces or [(start, end)]
