import re

class StackMachineCodeGenerator:
    def __init__(self, ir_code):
        self.ir_code = ir_code
        self.output = []
        self.vars = set()
        
    def generate(self):
        assign_re = re.compile(r'(\w+)\s*=\s*(.+)')
        if_goto_re = re.compile(r'if\s+(\w+)\s+goto\s+(\w+)')
        goto_re = re.compile(r'goto\s+(\w+)')
        label_re = re.compile(r'(\w+):')
        print_re = re.compile(r'print\s+"([^"]*)"(?:,\s*(.*))?')

        for line in self.ir_code:
            line = line.strip()
            # Asignación simple o con operación: t0 = cont > 3
            m = assign_re.match(line)
            if m:
                var, expr = m.group(1), m.group(2)
                # detectar expresión binaria simple
                tokens = expr.split()
                if len(tokens) == 3:
                    left, op, right = tokens
                    # Generar código para binario:
                    self.emit_load_operand(left)
                    self.emit_load_operand(right)
                    self.emit_op(op)
                    self.output.append(f"STORE {var}")
                else:
                    # asignación simple: var = valor o var = var
                    self.emit_load_operand(expr)
                    self.output.append(f"STORE {var}")
                continue

            # if t0 goto L1
            m = if_goto_re.match(line)
            if m:
                var, label = m.group(1), m.group(2)
                self.emit_load_operand(var)
                self.output.append(f"JNZ {label}")
                continue

            # goto L2
            m = goto_re.match(line)
            if m:
                label = m.group(1)
                self.output.append(f"JMP {label}")
                continue

            # label L1:
            m = label_re.match(line)
            if m:
                label = m.group(1)
                self.output.append(f"LABEL {label}")
                continue

            # print "texto", var1, var2, ...
            m = print_re.match(line)
            if m:
                text = m.group(1)
                rest = m.group(2)
                if text:
                    self.output.append(f'PRINT "{text}"')
                if rest:
                    vars_to_print = [v.strip() for v in rest.split(",")]
                    for v in vars_to_print:
                        self.emit_load_operand(v)
                        self.output.append("PRINT")
                continue

            # Por defecto, agregar la línea sin cambios (o ignorar)
            # self.output.append(f"# {line}")

        return self.output

    def emit_load_operand(self, operand):
        # Si es número literal
        try:
            float(operand)
            self.output.append(f"PUSH {operand}")
        except ValueError:
            # es variable
            self.output.append(f"LOAD {operand}")

    def emit_op(self, op):
        ops_map = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MUL',
            '/': 'DIV',
            '>': 'GT',
            '<': 'LT',
            '>=': 'GE',
            '<=': 'LE',
            '==': 'EQ',
            '!=': 'NE',
        }
        if op in ops_map:
            self.output.append(ops_map[op])
        else:
            self.output.append(f"# Op no reconocido: {op}")
ir_code = [
    "cont = 5",
    'print "El valor de cont es:", cont',
    "t0 = cont > 3",
    "if t0 goto L1",
    "goto L2",
    "L1:",
    'print "Cont es mayor a 3",',
    "L2:"
]

gen = StackMachineCodeGenerator(ir_code)
code_maquina = gen.generate()


