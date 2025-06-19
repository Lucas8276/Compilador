from representacion_intermedia import parse_and_generate_ir
from ir_optimizer import IROptimizer
from sim_maquina_pila import StackMachineCodeGenerator  # archivo con tu clase StackMachineCodeGenerator
from sim_instrucciones_pila import StackMachineSimulator  
def compile_source(source_code):
     # 1. Generar IR
    ir_code = parse_and_generate_ir(source_code)
    print("=== Código Intermedio sin optimizar ===")
    print("\n".join(ir_code))

    # 2. Optimizar IR
    optimizer = IROptimizer(ir_code)
    optimizer.optimize()
    optimized_ir = optimizer.get_code()
    print("\n=== Código Intermedio Optimizado ===")
    print("\n".join(optimized_ir))

    # 3. Generar código máquina
    gen = StackMachineCodeGenerator(optimized_ir)
    machine_code = gen.generate()
    print("\n=== Código Máquina ===")
    print("\n".join(machine_code))

    # 4. Ejecutar código máquina con simulador
    print("\n=== Ejecución del Programa ===")
    sim = StackMachineSimulator(machine_code)
    sim.run()

if __name__ == "__main__":
    source = """
    Parce cont = 5
Pilas("El valor de cont es:", cont)
Pues (cont > 3) {
  Pilas("Cont es mayor a 3")
}
    """
    compile_source(source)
