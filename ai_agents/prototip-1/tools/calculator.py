"""Güvenli matematik hesaplayıcısı (AST whitelist)."""
from __future__ import annotations

import ast
import math
import operator as op

_BIN_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
}

_UNARY_OPS = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}

_ALLOWED_NAMES = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
}

_ALLOWED_FUNCS = {
    "sqrt": math.sqrt,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "exp": math.exp,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "pow": pow,
}


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Sayısal olmayan sabit: {node.value!r}")
    if isinstance(node, ast.BinOp):
        if type(node.op) not in _BIN_OPS:
            raise ValueError(f"İzin verilmeyen operatör: {type(node.op).__name__}")
        return _BIN_OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in _UNARY_OPS:
            raise ValueError(f"İzin verilmeyen unary op: {type(node.op).__name__}")
        return _UNARY_OPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_NAMES:
            return _ALLOWED_NAMES[node.id]
        raise ValueError(f"Bilinmeyen isim: {node.id}")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCS:
            raise ValueError("İzin verilmeyen fonksiyon çağrısı")
        args = [_eval(a) for a in node.args]
        return _ALLOWED_FUNCS[node.func.id](*args)
    raise ValueError(f"İzin verilmeyen ifade: {type(node).__name__}")


def calculator(expression: str) -> str:
    """Matematik ifadesini değerlendirir ve sonucu string olarak döndürür."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval(tree)
        return str(result)
    except Exception as e:
        return f"HATA: {e}"


SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Matematiksel bir ifadeyi güvenli şekilde hesaplar. Örn: '2+2*3', 'sqrt(16)', 'sin(pi/2)'.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Değerlendirilecek matematiksel ifade.",
                }
            },
            "required": ["expression"],
        },
    },
}
