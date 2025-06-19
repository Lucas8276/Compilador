# main.py
"""
Uso:
    python main.py -i entrada.parce -o salida
"""

from pathlib import Path
import argparse
import contextlib
import io

# ---- Importar tu pipeline ----
from representacion_intermedia import parse_and_generate_ir
from ir_optimizer import IROptimizer
from sim_maquina_pila import StackMachineCodeGenerator
from sim_instrucciones_pila import StackMachineSimulator


# ---------- Pipeline reusable ----------
def run_pipeline(source_code: str):
    # 1) IR sin optimizar
    ir = parse_and_generate_ir(source_code)

    # 2) Optimización
    opt = IROptimizer(ir)
    opt.optimize()
    ir_opt = opt.get_code()

    # 3) Código para máquina de pila
    gen = StackMachineCodeGenerator(ir_opt)
    machine_code = gen.generate()

    # 4) Simulación (capturamos stdout)
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        sim = StackMachineSimulator(machine_code)
        sim.run()
    simulation_output = buffer.getvalue().strip()

    return ir_opt, machine_code, simulation_output


# ---------- Helpers ----------
def save(path: Path, content):
    text = "\n".join(content) if isinstance(content, (list, tuple)) else str(content)
    path.write_text(text, encoding="utf-8")


# ---------- CLI principal ----------
def main():
    ap = argparse.ArgumentParser(description="Compilador Parce‑Lang")
    ap.add_argument("-i", "--input", required=True, help="Archivo de entrada .parce")
    ap.add_argument("-o", "--output", default="output", help="Directorio de salida")
    args = ap.parse_args()

    src_path = Path(args.input)
    if not src_path.is_file():
        ap.error(f"No existe el archivo: {src_path}")

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    source_code = src_path.read_text(encoding="utf-8")
    ir, machine, sim_out = run_pipeline(source_code)

    save(out_dir / "ir.txt", ir)
    save(out_dir / "codigo_maquina.txt", machine)
    save(out_dir / "salida_simulacion.txt", sim_out)

    print(f"✅ Proceso completado. Resultados en {out_dir.resolve()}")


if __name__ == "__main__":
    main()
