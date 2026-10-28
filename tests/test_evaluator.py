"""Tests de l'évaluateur d'expressions."""

import numpy as np
import pytest

from tracer.core.evaluator import ExpressionError, evaluate_expression
from tracer.core.plot_segments import iter_plot_segments


def test_polynomial():
    x = np.linspace(-2, 2, 50)
    y = evaluate_expression("x**3 - 2*x", x)
    assert np.allclose(y, x**3 - 2 * x)


def test_trig_and_constants():
    x = np.array([0.0, np.pi / 2])
    y = evaluate_expression("sin(x) + pi", x)
    assert np.allclose(y[0], np.pi)
    assert np.allclose(y[1], 1 + np.pi)


def test_rejects_unsafe_code():
    x = np.linspace(0, 1, 3)
    with pytest.raises(ExpressionError):
        evaluate_expression("__import__('os')", x)


def test_plot_segments_split_asymptote():
    x = np.array([-2.0, -1.0, 1.0, 2.0])
    y = 1 / x
    segments = iter_plot_segments(x, y, split_discontinuities=True, jump_threshold=10)
    assert len(segments) >= 2
