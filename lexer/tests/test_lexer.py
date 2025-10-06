import sys
import os

# Agregar el directorio padre (lexer) al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import lexer

# Código de prueba (puedes cambiarlo)
code = """
var x = 10;
let y = 20;
if (x + 5 > y && y != 0) {
    const z = y * 2 + 1;
} else {
    y = 0;
}
"""

# Alimentar el lexer
lexer.input(code)

print("🧩 TOKENS GENERADOS POR EL LÉXICO:\n")

while True:
    tok = lexer.token()
    if not tok:
        break
    print(f"Tipo: {tok.type:<12} Valor: {tok.value:<8} Línea: {tok.lineno}")
