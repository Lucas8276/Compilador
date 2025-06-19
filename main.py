from representacion_intermedia import parse_and_generate_ir
from ir_optimizer import IROptimizer

fuente = """
Che este es un comentario
Parce cont = 5
Pilas("El valor de cont es:", cont)
Pues (cont > 3) {
  Pilas("Cont es mayor a 3")
}
"""

# 1. Generar IR
ir = parse_and_generate_ir(fuente)
print("=== Código Intermedio sin optimizar ===")
for l in ir:
    print(l)

# 2. Optimizar IR
opt = IROptimizer(ir)
opt.optimize()
ir_opt = opt.get_code()

print("\n=== Código Intermedio Optimizado ===")
for l in ir_opt:
    print(l)
