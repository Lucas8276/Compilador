import re

class IROptimizer:
    """
    – Propagación de constantes
    – Constant folding con operadores aritméticos y relacionales
    """
    def __init__(self, code):
        self.code = code              # lista de strings con IR
        self.const = {}               # var -> valor numérico

    # — helpers —
    def _is_num(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def _eval(self, a, op, b):
        if op == '+':  return a + b
        if op == '-':  return a - b
        if op == '*':  return a * b
        if op == '/':  return a / b if b != 0 else float("inf")
        if op == '>':  return int(a >  b)
        if op == '<':  return int(a <  b)
        if op == '>=': return int(a >= b)
        if op == '<=': return int(a <= b)
        if op == '==': return int(a == b)
        if op == '!=': return int(a != b)
        return None

    # — constante → reemplazo en expresiones sencillas —
    def _replace_consts(self, expr: str) -> str:
        toks = expr.split()
        return " ".join(str(self.const.get(t, t)) for t in toks)

    # — optimización principal —
    def constant_propagation_and_folding(self):
        new = []
        assign_re = re.compile(r'^\s*(\w+)\s*=\s*(.+)$')

        for line in self.code:
            m = assign_re.match(line)
            if not m:                         # línea que no es asignación
                new.append(line)
                continue

            var, expr = m.group(1), m.group(2).strip()
            expr = self._replace_consts(expr) # sustituir var const → valor

            toks = expr.split()
            # caso 1: asignación de número literal
            if len(toks) == 1 and self._is_num(toks[0]):
                val = float(toks[0])
                self.const[var] = val
                new.append(f"{var} = {val:g}")
                continue

            # caso 2: expr binaria simple  a op b
            if len(toks) == 3 and self._is_num(toks[0]) and self._is_num(toks[2]):
                val = self._eval(float(toks[0]), toks[1], float(toks[2]))
                self.const[var] = val
                new.append(f"{var} = {val:g}")
                continue

            # caso general: no es constante
            self.const.pop(var, None)         # ya no es constante
            new.append(f"{var} = {expr}")

        self.code = new
    def dead_code_elimination(self):
        useful_vars = set()
        new_code = []
        # Recorrer en orden inverso
        for line in reversed(self.code):
            stripped = line.strip()
            # Instrucciones que deben mantenerse siempre
            if stripped.startswith("print") or stripped.startswith("goto") or ':' in stripped or stripped.startswith("if"):
                new_code.insert(0, line)
                # Agregar variables usadas en estas instrucciones
                tokens = re.findall(r'\b\w+\b', line)
                for t in tokens:
                    if t.isidentifier() and t != 'goto' and not t.startswith('L'):
                        useful_vars.add(t)
                continue

            m = re.match(r'(\w+)\s*=\s*(.+)', line)
            if m:
                var, expr = m.group(1), m.group(2)
                tokens = re.findall(r'\b\w+\b', expr)
                # Si la variable se usa luego, conservar
                if var in useful_vars:
                    new_code.insert(0, line)
                    for t in tokens:
                        if t.isidentifier() and t != 'goto' and not t.startswith('L'):
                            useful_vars.add(t)
        self.code = new_code

    # — interfaz pública —
    def optimize(self):
        self.constant_propagation_and_folding()
        self.dead_code_elimination()
    def get_code(self):
        return self.code
