from lark import Lark

with open("che_rumba.lark") as f:
    grammar = f.read()

parser = Lark(grammar, start="program", parser="lalr")

codigo = """
Che esto es un comentario
Parce cont = 0
Pilas("los números a imprimir son estos:")
Pues (5 > 4) {
    Pilas("esto es un si o un if")
}
Orale pues(4 > 3) {
    Pilas("esto es un sino si")
}
Orale {
    Pilas("esto es un else")
}
"""

tree = parser.parse(codigo)
print(tree.pretty())
