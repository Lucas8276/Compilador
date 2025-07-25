class BreakLoop(Exception): pass
class ContinueLoop(Exception): pass
class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class StackMachineSimulator:
    """
    Ejecuta el código generado por StackMachineCodeGenerator.
    Instrucciones admitidas:
      PUSH n, LOAD x, STORE x,
      ADD SUB MUL DIV,
      GT LT GE LE EQ NE,
      JNZ lbl, JMP lbl,
      LABEL lbl,
      PRINT  (imprime tope de pila)
      PRINT "texto fijo"
    """

    def __init__(self, code):
        self.code = code
        self.stack = []
        self.vars = {}
        self.labels = self._map_labels()
        self.pc = 0          # program counter

    # ---- fase de búsqueda de etiquetas ----
    def _map_labels(self):
        labels = {}
        for idx, line in enumerate(self.code):
            if line.startswith("LABEL "):
                lbl = line.split()[1]
                labels[lbl] = idx
        return labels

    # ---- helpers stack / ops ----
    def _binop(self, fn):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(fn(a, b))

    # ---- ciclo principal ----
    def run(self):
        while self.pc < len(self.code):
            line = self.code[self.pc].strip()
            parts = line.split(maxsplit=1)
            instr = parts[0]

            match instr:
                # --- pila y memoria ---
                case "PUSH":
                    self.stack.append(float(parts[1]))
                case "LOAD":
                    self.stack.append(self.vars.get(parts[1], 0.0))
                case "STORE":
                    self.vars[parts[1]] = self.stack.pop()
                
                case "GUITA":
                    # Si partes viene como ['GUITA', '"ingresa el numero 0:"']
                    if len(parts) == 2:
                        mensaje = parts[1]
                        # Elimina comillas, si están
                        if mensaje.startswith('"') and mensaje.endswith('"'):
                            mensaje = mensaje[1:-1]
                        val = input(mensaje + " ")
                        print()
                    else:
                        val = input("Ingrese un valor: ")
                        print()
                    # Conversión automática:
                    try:
                        val = int(val)
                    except ValueError:
                        try:
                            val = float(val)
                        except ValueError:
                            pass
                    self.stack.append(val)


                # --- aritmética ---
                case "ADD": self._binop(lambda a, b: a + b)
                case "SUB": self._binop(lambda a, b: a - b)
                case "MUL": self._binop(lambda a, b: a * b)
                case "DIV": self._binop(lambda a, b: a / b if b != 0 else float("inf"))

                # --- comparaciones (devuelven 1 ó 0) ---
                case "GT":  self._binop(lambda a, b: 1.0 if a >  b else 0.0)
                case "LT":  self._binop(lambda a, b: 1.0 if a <  b else 0.0)
                case "GE":  self._binop(lambda a, b: 1.0 if a >= b else 0.0)
                case "LE":  self._binop(lambda a, b: 1.0 if a <= b else 0.0)
                case "EQ":  self._binop(lambda a, b: 1.0 if a == b else 0.0)
                case "NE":  self._binop(lambda a, b: 1.0 if a != b else 0.0)

                # --- saltos ---
                case "JNZ":
                    val = self.stack.pop()
                    if val != 0:
                        self.pc = self.labels[parts[1]]
                        continue
                case "JMP":
                    self.pc = self.labels[parts[1]]
                    continue
                case "LABEL":
                    pass  # ya fueron mapeadas

                case "BREAK":
                    # salta fuera del bucle actual (puede ser usando excepciones en Python)
                    raise BreakLoop()

                case "CONTINUE":
                    raise ContinueLoop()

                case "RETURN":
                    # toma valor y lo retorna
                    ret_val = self.stack.pop()
                    raise ReturnValue(ret_val)


                # --- salida ---
                case "PRINT":
                    if len(parts) == 2:
                        # PRINT "texto fijo"
                        print(parts[1].strip('"'), end=" ")
                        print()
                    else:
                        # PRINT valor de la pila
                        if self.stack:
                            print(self.stack.pop(), end=" ")
                            print()
                        else:
                            print("[WARN] PRINT intentó hacer pop en pila vacía")


                # --- desconocido ---
                case _:
                    raise RuntimeError(f"Instr. desconocida: {line}")

            self.pc += 1
