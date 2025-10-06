# sintactico_corregido.py
import sys
import os

# Agregar la carpeta lexer al path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lexer'))

import ply.yacc as yacc
from lexer import tokens, lexer
from colorama import Fore, Style, init

# Inicializa colorama (para Windows también funciona)
init(autoreset=True)

# -----------------------------
# Clase Node (nodo del AST)
# -----------------------------
class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children if children else []
        self.value = value

    def __repr__(self):
        # Evita la recursión infinita y duplicaciones al imprimir
        return f"<Node {self.type} {self.value if self.value else ''}>"

    def pretty(self, level=0, last=True, prefix=""):
        """Imprime el árbol en consola con colores y líneas jerárquicas."""
        # Asignar colores por tipo de nodo
        color_map = {
            "program": Fore.CYAN + Style.BRIGHT,
            "statement_list": Fore.MAGENTA + Style.BRIGHT,
            "declaration": Fore.GREEN + Style.BRIGHT,
            "assignment": Fore.YELLOW + Style.BRIGHT,
            "if": Fore.BLUE + Style.BRIGHT,
            "if-else": Fore.BLUE + Style.BRIGHT,
            "binary_op": Fore.RED + Style.BRIGHT,
            "number": Fore.WHITE + Style.BRIGHT,
            "identifier": Fore.WHITE + Style.BRIGHT,
            "expression_statement": Fore.CYAN + Style.BRIGHT
        }
        color = color_map.get(self.type, Fore.WHITE)

        # Dibujar líneas jerárquicas
        branch = "└── " if last else "├── "
        line = prefix + branch + color + f"<{self.type}> " + (str(self.value) if self.value else "")
        ret = line + Style.RESET_ALL + "\n"

        # Ajustar prefijo para los hijos
        new_prefix = prefix + ("    " if last else "│   ")

        for i, child in enumerate(self.children):
            ret += child.pretty(level + 1, i == len(self.children) - 1, new_prefix)
        return ret

# -----------------------------
# Precedencia de operadores
# -----------------------------
precedence = (
    ('left', 'LOGIC_OP'),
    ('left', 'REL_OP'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

# -----------------------------
# Gramática Principal
# -----------------------------
def p_program(p):
    """program : statement_list"""
    p[0] = Node("program", [p[1]])

def p_statement_list(p):
    """statement_list : statement
                      | statement_list statement"""
    if len(p) == 2:
        p[0] = Node("statement_list", [p[1]])
    else:
        p[1].children.append(p[2])
        p[0] = p[1]

# -----------------------------
# Tipos de Sentencias
# -----------------------------
def p_statement(p):
    """statement : assignment_stmt
                 | expression_stmt
                 | if_stmt
                 | block_stmt"""
    p[0] = p[1]

def p_expression_stmt(p):
    """expression_stmt : expression SEMICOLON"""
    p[0] = Node("expression_statement", [p[1]])

def p_assignment_stmt(p):
    """assignment_stmt : VAR ID ASSIGN expression SEMICOLON
                       | LET ID ASSIGN expression SEMICOLON
                       | CONST ID ASSIGN expression SEMICOLON
                       | ID ASSIGN expression SEMICOLON"""
    if len(p) == 6:
        p[0] = Node("declaration", children=[p[4]], value=f"{p[1]} {p[2]}")
    else:
        p[0] = Node("assignment", children=[p[3]], value=p[1])

def p_block_stmt(p):
    """block_stmt : LBRACE statement_list RBRACE"""
    p[0] = p[2]

def p_if_stmt(p):
    """if_stmt : IF LPAREN expression RPAREN statement
               | IF LPAREN expression RPAREN statement ELSE statement"""
    if len(p) == 6:
        p[0] = Node("if", children=[p[3], p[5]], value="")
    else:
        p[0] = Node("if-else", children=[p[3], p[5], p[7]], value="")

# -----------------------------
# Expresiones
# -----------------------------
def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression REL_OP expression
                  | expression LOGIC_OP expression"""
    p[0] = Node("binary_op", children=[p[1], p[3]], value=p[2])

def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]

def p_expression_terminals(p):
    """expression : NUMBER
                  | ID"""
    if p.slice[1].type == 'NUMBER':
        p[0] = Node("number", value=p[1])
    else:
        p[0] = Node("identifier", value=p[1])

# -----------------------------
# Manejo de errores
# -----------------------------
def p_error(p):
    if p:
        print(f"❌ Error de sintaxis en '{p.value}' (tipo: {p.type}) en la línea {p.lineno}")
    else:
        print("❌ Error de sintaxis: fin de archivo inesperado")

# -----------------------------
# Construir el parser
# -----------------------------
parser = yacc.yacc()

# -----------------------------
# Prueba del parser
# -----------------------------
if __name__ == "__main__":
    code = """
    var x = 10;
    let y = 20;

    if (x + 5 > y && y != 0) {
        const z = y * 2 + 1;
    } else {
        y = 0;
    }
    """

    # 🔧 Compilar parser una sola vez
    parser = yacc.yacc(optimize=True, write_tables=False)

    print(Fore.CYAN + Style.BRIGHT + "\n🌳 Árbol Sintáctico Abstracto (AST) Generado:\n" + Style.RESET_ALL)
    tree = parser.parse(code, lexer=lexer)
    if tree:
        print(tree.pretty())
    else:
        print("❌ No se pudo generar el árbol sintáctico.")

