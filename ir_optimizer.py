"""
Optimizador de IR
-----------------
• Propagación de constantes
• Constant Folding
• Eliminación de código muerto
"""
from __future__ import annotations
import re
from typing import List

class IROptimizer:
    def __init__(self, code: List[str]):
        self.code = code          # instrucciones IR
        self.const: dict[str, float] = {}

    # -------- helpers ----------
    @staticmethod
    def _is_num(s: str) -> bool:
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def _eval(a: float, op: str, b: float) -> float:
        return {
            '+': a + b,  '-': a - b,  '*': a * b,
            '/': a / b if b != 0 else float("inf"),
            '>': int(a > b),  '<': int(a < b),
            '>=': int(a >= b), '<=': int(a <= b),
            '==': int(a == b), '!=': int(a != b)
        }[op]

    # -------- propagación y folding ----------
    def _replace_consts(self, expr: str) -> str:
        return " ".join(str(self.const.get(tok, tok)) for tok in expr.split())

    def constant_propagation_and_folding(self) -> None:
        new: List[str] = []
        assign_re = re.compile(r'^\s*(\w+)\s*=\s*(.+)$')

        for line in self.code:
            m = assign_re.match(line)
            if not m:                 # no es asignación -> copiar
                new.append(line)
                continue

            var, expr = m.group(1), m.group(2).strip()
            expr = self._replace_consts(expr)

            toks = expr.split()
            # asignación literal
            if len(toks) == 1 and self._is_num(toks[0]):
                val = float(toks[0])
                self.const[var] = val
                new.append(f"{var} = {val:g}")
                continue

            # binaria a op b con números
            if len(toks) == 3 and self._is_num(toks[0]) and self._is_num(toks[2]):
                val = self._eval(float(toks[0]), toks[1], float(toks[2]))
                self.const[var] = val
                new.append(f"{var} = {val:g}")
                continue

            # caso general
            self.const.pop(var, None)
            new.append(f"{var} = {expr}")

        self.code = new

    # -------- dead‑code elimination ----------
    def dead_code_elimination(self) -> None:
        useful: set[str] = set()
        new: List[str] = []

        for line in reversed(self.code):
            stripped = line.strip()

            # Mantener líneas de control/salida
            control = stripped.startswith(("print", "goto", "if")) or ':' in stripped
            if control:
                new.insert(0, line)
                tokens = re.findall(r'\b\w+\b', line)
                useful.update(t for t in tokens if t.isidentifier() and not t.startswith('L'))
                continue

            m = re.match(r'(\w+)\s*=\s*(.+)', line)
            if m:
                var, expr = m.group(1), m.group(2)
                if var in useful:
                    new.insert(0, line)
                    tokens = re.findall(r'\b\w+\b', expr)
                    useful.update(t for t in tokens if t.isidentifier() and not t.startswith('L'))

        self.code = new

    # -------- interfaz pública ----------
    def optimize(self) -> None:
        self.constant_propagation_and_folding()
        self.dead_code_elimination()

    def get_code(self) -> List[str]:
        return self.code
