# Guarda este archivo como lexico_corregido.py
import ply.lex as lex

# -----------------------------
# Palabras reservadas (sin cambios)
# -----------------------------
reserved = {
    "if": "IF",
    "else": "ELSE",
    "for": "FOR",
    "while": "WHILE",
    "function": "FUNCTION",
    "return": "RETURN",
    "var": "VAR",
    "let": "LET",
    "const": "CONST"
}

# -----------------------------
# Lista de tokens CORREGIDA
# -----------------------------
tokens = [
    'ID', 'NUMBER',
    # --- Tokens de operadores separados por precedencia ---
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'ASSIGN',
    # --- Tokens agrupados (sin precedencia conflictiva) ---
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'COMMA', 'SEMICOLON',
    'LOGIC_OP',   # &&, ||
    'REL_OP',     # ==, !=, <, >, <=, >=
] + list(reserved.values())

# -----------------------------
# Expresiones regulares CORREGIDAS
# -----------------------------
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_ASSIGN = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_SEMICOLON = r';'
t_LOGIC_OP = r'&&|\|\|'
t_REL_OP = r'==|!=|<=|>=|<|>'

# -----------------------------
# Ignorar espacios, tabs y comentarios
# -----------------------------
t_ignore = ' \t\r'
t_ignore_COMMENT = r'//.*'
def t_ignore_MCOMMENT(t):
    r'/\*[\s\S]*?\*/'
    t.lexer.lineno += t.value.count('\n')

# -----------------------------
# Identificadores y palabras reservadas
# -----------------------------
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# -----------------------------
# Números
# -----------------------------
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# -----------------------------
# Contador de líneas
# -----------------------------
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# -----------------------------
# Manejo de errores
# -----------------------------
def t_error(t):
    print(f"❌ Caracter ilegal '{t.value[0]}' en línea {t.lexer.lineno}")
    t.lexer.skip(1)

# -----------------------------
# Construcción del lexer
# -----------------------------
lexer = lex.lex()


