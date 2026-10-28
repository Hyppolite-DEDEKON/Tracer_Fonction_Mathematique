"""Évaluation sécurisée d'expressions mathématiques en fonction de x."""

from __future__ import annotations

import ast
import operator

import numpy as np

ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

ALLOWED_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

ALLOWED_FUNCTIONS = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "asin": np.arcsin,
    "acos": np.arccos,
    "atan": np.arctan,
    "sinh": np.sinh,
    "cosh": np.cosh,
    "tanh": np.tanh,
    "exp": np.exp,
    "log": np.log,
    "log10": np.log10,
    "sqrt": np.sqrt,
    "abs": np.abs,
    "floor": np.floor,
    "ceil": np.ceil,
}


class ExpressionError(ValueError):
    """Expression invalide ou non autorisée."""


def _eval_node(node: ast.AST, x: np.ndarray) -> np.ndarray:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, x)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return np.full_like(x, node.value, dtype=float)
        raise ExpressionError("Seuls les nombres sont autorisés.")
    if isinstance(node, ast.Name):
        if node.id == "x":
            return x
        if node.id == "pi":
            return np.full_like(x, np.pi, dtype=float)
        if node.id == "e":
            return np.full_like(x, np.e, dtype=float)
        raise ExpressionError(f"Nom inconnu : « {node.id} ».")
    if isinstance(node, ast.BinOp):
        op = ALLOWED_BINOPS.get(type(node.op))
        if op is None:
            raise ExpressionError("Opérateur non autorisé.")
        left = _eval_node(node.left, x)
        right = _eval_node(node.right, x)
        return op(left, right)
    if isinstance(node, ast.UnaryOp):
        op = ALLOWED_UNARYOPS.get(type(node.op))
        if op is None:
            raise ExpressionError("Opérateur unaire non autorisé.")
        return op(_eval_node(node.operand, x))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ExpressionError("Appel de fonction non autorisé.")
        fn = ALLOWED_FUNCTIONS.get(node.func.id)
        if fn is None:
            raise ExpressionError(
                f"Fonction « {node.func.id} » inconnue. "
                f"Disponibles : {', '.join(sorted(ALLOWED_FUNCTIONS))}."
            )
        if node.keywords:
            raise ExpressionError("Les arguments nommés ne sont pas autorisés.")
        args = [_eval_node(arg, x) for arg in node.args]
        return fn(*args)
    raise ExpressionError("Syntaxe non supportée dans l'expression.")


def evaluate_expression(expression: str, x: np.ndarray) -> np.ndarray:
    """Calcule y = f(x) à partir d'une chaîne d'expression."""
    expr = expression.strip()
    if not expr:
        raise ExpressionError("L'expression ne peut pas être vide.")
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise ExpressionError(f"Syntaxe invalide : {exc.msg}") from exc
    return _eval_node(tree, x)
