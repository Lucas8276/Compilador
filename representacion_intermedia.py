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
from lark import Tree

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

    def import_stmt(self, items):
        archivo = items[0][1:-1]  # quita comillas
        return [f'# Labura "{archivo}"']


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

    def reassign(self, items):
        name = items[0].value if hasattr(items[0], 'value') else items[0]
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

    def guita_read(self, items):
        mensaje = items[0][1:-1]
        t = self.new_temp()
        code = [f'{t} = GUITA "{mensaje}"']
        return code, t




    def if_stmt(self, items):
        cond_code, cond_val = items[0]
        block_code = items[1]
        return (cond_code, cond_val, block_code)

    def elif_stmt(self, items):
        cond_code, cond_val = items[0]
        block_code = items[1]
        return (cond_code, cond_val, block_code)

    def else_stmt(self, items):
        block_code = items[0]
        return block_code


    def if_chain(self, items):
        # items: [if_stmt, elif_stmt, ..., else_stmt?]
        Lend = self.new_temp().replace("t", "L")
        code = []
        jump_labels = []
        for branch in items:
            if hasattr(branch, "__len__") and len(branch) == 3:
                # if o elif: (cond_code, cond_val, block_code)
                cond_code, cond_val, block_code = branch
                Lbranch = self.new_temp().replace("t", "L")
                code += cond_code
                code += [f"if {cond_val} goto {Lbranch}"]
                # Si la condición no se cumple, sigue al próximo branch
                jump_labels.append(Lbranch)
                continue
            # else: solo bloque de código
            else_block = branch
            Lelse = self.new_temp().replace("t", "L")
            jump_labels.append(Lelse)
            code += [f"goto {Lelse}"]

        # Ahora pega los bloques reales
        for branch, Lbranch in zip(items, jump_labels):
            if hasattr(branch, "__len__") and len(branch) == 3:
                # if o elif
                _, _, block_code = branch
                code += [f"{Lbranch}:"] + block_code + [f"goto {Lend}"]
            else:
                # else
                code += [f"{Lbranch}:"] + branch
        code += [f"{Lend}:"]
        return code

    def block(self, stmts):
        code = []
        for s in stmts:
            if isinstance(s, tuple) and len(s) == 2:
                code += s[0]
            elif isinstance(s, list):
                code += s
            elif isinstance(s, str):
                code.append(s)
            elif isinstance(s, Tree):
                # Puede loguear o ignorar, pero no sumar
                print(f"[WARN] block(): se ignoró Tree inesperado: {s.data if hasattr(s, 'data') else s}")
            else:
                print(f"[WARN] block(): tipo no esperado {type(s)}: {s}")
        return code


    def program(self, children):
        code = []
        for stmt in children:
            if isinstance(stmt, list):
                code.extend(stmt)
            else:
                code.append(stmt)
        return code
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

    def for_stmt(self, items):
        var = items[0].value if hasattr(items[0], 'value') else items[0]
        times = items[1][1] if isinstance(items[1], tuple) else items[1]
        block_code = items[2]
        Lstart = self.new_temp().replace("t", "L")
        Lcond = self.new_temp().replace("t", "L")
        Lend  = self.new_temp().replace("t", "L")
        t_iter = self.new_temp()
        code = [
            f"{t_iter} = 0",
            f"{Lstart}:",
            f"if {t_iter} >= {times} goto {Lend}",
            f"{var} = {t_iter}",
        ]
        code += block_code
        code += [
            f"{t_iter} = {t_iter} + 1",
            f"goto {Lstart}",
            f"{Lend}:"
        ]
        return code



    def while_stmt(self, items):
        cond_code, cond_val = items[0]
        block_code = items[1]
        Lstart = self.new_temp().replace("t", "L")
        Lbody = self.new_temp().replace("t", "L")
        Lend  = self.new_temp().replace("t", "L")
        return (
            [f"{Lstart}:"] +
            cond_code +
            [f"if {cond_val} goto {Lbody}",
            f"goto {Lend}",
            f"{Lbody}:"] +
            block_code +
            [f"goto {Lstart}",
            f"{Lend}:"]
        )


    
    def dowhile_stmt(self, items):
        block_code = items[0]              # el bloque { ... }
        cond_code, cond_val = items[1]     # la condición tras Rumba (expr)
        Lstart = self.new_temp().replace("t", "L")
        Lcond = self.new_temp().replace("t", "L")
        Lend = self.new_temp().replace("t", "L")
        # IR:
        # Lstart: block_code
        # Lcond:  cond_code
        #         if cond_val goto Lstart
        #         goto Lend
        # Lend:
        return (
            [f"{Lstart}:"] +
            block_code +
            [f"{Lcond}:"] +
            cond_code +
            [f"if {cond_val} goto {Lstart}",
            f"{Lend}:"]
        )

    
def flatten_and_str(code):
    result = []
    for c in code:
        if isinstance(c, list) or isinstance(c, tuple):
            result.extend(flatten_and_str(c))
        elif isinstance(c, str):
            result.append(str(c))
        elif isinstance(c, Tree):
            print(f"[WARN] flatten_and_str(): Tree no esperado: {c.data if hasattr(c, 'data') else c}")
        else:
            print(f"[WARN] flatten_and_str(): tipo no esperado {type(c)}: {c}")
    return result


def parse_and_generate_ir(source_code: str) -> list:
    tree = parser.parse(source_code)
    gen = IRGenerator()
    ir_code = gen.transform(tree)
    ir_code = flatten_and_str(ir_code)
    return ir_code


def parse_and_generate_ir(source_code: str) -> list:
    tree = parser.parse(source_code)
    gen = IRGenerator()
    ir_code = gen.transform(tree)
    ir_code = flatten_and_str(ir_code)
    return ir_code




