from lark import Lark, Transformer, Token
import itertools
# ------------- cargar gramática y parser -------------
with open("che_rumba.lark", encoding="utf-8") as f:
    grammar = f.read()
parser = Lark(grammar, start="program", parser="lalr")
# ------------- Transformer → IR -------------
class IRGenerator(Transformer):
    def __init__(self):
        self.tmp = itertools.count()

    def new_temp(self):
        return f"t{next(self.tmp)}"

    # ── Expresiones ───────────────────────────────────
    def number(self, items):
        return [], items[0].value            # (code, value)

    def var(self, items):
        return [], items[0].value

    def bin_expr(self, items):
        code_l, val_l = items[0]
        code_r, val_r = items[2]
        op_tok = items[1]
        t = self.new_temp()
        code = code_l + code_r + [f"{t} = {val_l} {op_tok.value} {val_r}"]
        return code, t

    # ── Sentencias ───────────────────────────────────
    def var_decl(self, items):
        name = items[0]
        code_e, val = items[1]
        return code_e + [f"{name} = {val}"]

    def print_stmt(self, items):
        text = items[0][1:-1]                       # quitar comillas
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

    # ── Bloques / programa  ───────────────────────────
    def block(self, stmts):
        code = []
        for s in stmts:
            if isinstance(s, tuple) and len(s) == 2:
                code += s[0]          # s=(code,val)
            else:
                code += s             # s es lista
        return code

    def program(self, stmts):
        code = []
        for s in stmts:
            if isinstance(s, tuple) and len(s) == 2:
                code += s[0]
            else:
                code += s
        self.ir_code = code           # lo guardo para usar fuera
        return code

# ── Función auxiliar — la que usará main.py ──────────
def parse_and_generate_ir(source_code: str):
    tree = parser.parse(source_code)
    gen = IRGenerator()
    gen.transform(tree)
    return gen.ir_code
