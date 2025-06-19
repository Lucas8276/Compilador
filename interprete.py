from lark import Lark, Transformer, Token

with open("che_rumba.lark") as f:
    grammar = f.read()

parser = Lark(grammar, start="program", parser="lalr")

class CheRumbaInterpreter(Transformer):
    def __init__(self):
        self.vars = {}

    # ---------- litterales ----------
    def number(self, items):
        return int(items[0])

    def var(self, items):
        name = items[0]
        return self.vars.get(name, 0)

    def bin_expr(self, items):
        left, op_tok, right = items
        op = op_tok.value
        return self.eval_op(left, op, right)
    
    def true(self, _):
        return True

    def false(self, _):
        return False


    # ---------- sentencias ----------
    def var_decl(self, items):
        name, value = items
        self.vars[name] = value

    def print_stmt(self, items):
        text = items[0][1:-1]   # quitar comillas
        args = items[1:]
        print(text, *args)

    def if_stmt(self, items):
        cond, block = items
        if cond:
            for stmt in block.children:
                self.transform(stmt)

    def elif_stmt(self, items):
        cond, block = items
        if cond:
            for stmt in block.children:
                self.transform(stmt)

    def else_stmt(self, items):
        block, = items
        for stmt in block.children:
            self.transform(stmt)

    def comment(self, _):
        pass

    # ---------- helpers ----------
    def eval_op(self, l, op, r):
        return {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
            '>': lambda a, b: a >  b,
            '<': lambda a, b: a <  b,
            '>=':lambda a, b: a >= b,
            '<=':lambda a, b: a <= b,
            '==':lambda a, b: a == b,
            '!=':lambda a, b: a != b
        }[op](l, r)

# ---------- DEMO ----------
codigo = """
Che este es un comentario
Parce cont = 5
Pilas("El valor de cont es:", cont)

Pues (cont > 3) {
  Pilas("Cont es mayor a 3")
}
Orale {
  Pilas("Cont es menor o igual a 3")
}
"""

arbol = parser.parse(codigo)
CheRumbaInterpreter().transform(arbol)
