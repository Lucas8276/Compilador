"""
Generador de Representación Intermedia (IR) para Parce‑Lang
----------------------------------------------------------
• Usa Lark para parsear `che_rumba.lark`
• Convierte el AST en código de 3‑direcciones (lista[str])
• Retorna esa lista para que el optimizador la consuma
"""

from pathlib import Path
from typing import List, Tuple
import itertools
from lark import Lark, Transformer, Token

# ─────────────────────────  Cargar gramática  ──────────────────────────
grammar_path = Path(__file__).with_name("che_rumba.lark")
grammar = grammar_path.read_text(encoding="utf-8")
parser = Lark(grammar, start="program", parser="lalr")


# ─────────────────────────  Transformer → IR  ──────────────────────────
Code = List[str]
Expr = Tuple[Code, str]          # (código acumulado, valor/temporal)

class IRGenerator(Transformer):
    def __init__(self):
        self.tmp = itertools.count()

    def new_temp(self):
        return f"t{next(self.tmp)}"

    def number(self, items):
        return [], items[0].value

    def var(self, items):
        return [], items[0].value

    def bin_expr(self, items):
        code_l, val_l = items[0]
        code_r, val_r = items[2]
        op_tok = items[1]
        t = self.new_temp()
        code = code_l + code_r + [f"{t} = {val_l} {op_tok.value} {val_r}"]
        return code, t

    def var_decl(self, items):
        name = items[0].value if isinstance(items[0], Token) else items[0]
        code_e, val = items[1]
        return code_e + [f"{name} = {val}"]

    def print_stmt(self, items):
        text = items[0][1:-1]  # quitar comillas
        args_code, args_vals = [], []
        for e in items[1:]:
            c, v = e
            args_code += c
            args_vals.append(v)
        return args_code + [f'print "{text}", ' + ", ".join(args_vals)]

    def if_stmt(self, items):
        cond_code, cond_val = items[0]
        block_code = items[1]
        Ltrue = self.new_temp().replace("t", "L")
        Lend  = self.new_temp().replace("t", "L")
        return (cond_code +
                [f"if {cond_val} goto {Ltrue}",
                 f"goto {Lend}",
                 f"{Ltrue}:"] +
                block_code +
                [f"{Lend}:"])

    def block(self, stmts):
        code = []
        for s in stmts:
            if isinstance(s, tuple) and len(s) == 2:
                code += s[0]
            else:
                code += s
        return code

    def program(self, children):
        code = []
        for stmt in children:
            if isinstance(stmt, list):
                code.extend(stmt)
            else:
                code.append(stmt)
        return code
def flatten_and_str(code):
    result = []
    for c in code:
        if isinstance(c, list) or isinstance(c, tuple):
            result.extend(flatten_and_str(c))
        else:
            result.append(str(c))
    return result

def parse_and_generate_ir(source_code: str) -> list:
    tree = parser.parse(source_code)
    gen = IRGenerator()
    ir_code = gen.transform(tree)
    ir_code = flatten_and_str(ir_code)
    return ir_code

def true(self, items):
    return [], "1"

def false(self, items):
    return [], "0"

def break_stmt(self, items):
    return ["BREAK"]

def continue_stmt(self, items):
    return ["CONTINUE"]

def return_stmt(self, items):
    if items:
        code_e, val = items[0]
        return code_e + [f"RETURN {val}"]
    else:
        return ["RETURN"]



