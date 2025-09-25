import re
from dataclasses import dataclass
from typing import Iterator

@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

KEYWORDS = {
    "if", "else", "for", "while", "function", "return", "var", "let", "const"
}

token_specification = [
    ("COMMENT",   r"//[^\n]*"),                # comentario de línea
    ("MCOMMENT",  r"/\*[\s\S]*?\*/"),          # comentario multilínea (captura \n)
    ("NEWLINE",   r"\n"),                      # salto de línea (para contar líneas)
    ("SKIP",      r"[ \t\r]+"),                # espacios y tabs (ignorados)
    ("ID",        r"[A-Za-z_$][A-Za-z0-9_$]*"),# identificadores
    ("NUMBER",    r"\d+"),                     # enteros (solo dígitos)
    # operadores lógicos (multi-char primero)
    ("LOGIC_OP",  r"&&|\|\||!"),
    # operadores aritméticos / asignación (multi-char primero)
    ("ARITH_OP",  r"\+\+|--|\+|-|\*|/|%|="),
    ("MISMATCH",  r"."),                       # cualquier otro carácter -> error
    ("ASSIGN",    r"="),                         # operador de asignación
]

master_pattern = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in token_specification))

def tokenize(code: str) -> Iterator[Token]:
    line = 1
    line_start = 0
    for mo in master_pattern.finditer(code):
        kind = mo.lastgroup
        value = mo.group(kind)
        start = mo.start()
        column = start - line_start + 1

        if kind == "NEWLINE":
            line += 1
            line_start = mo.end()
            continue
        elif kind == "SKIP" or kind == "COMMENT":
            # espacios y comentarios de línea: ignorar
            continue
        elif kind == "MCOMMENT":
            # comentario multilínea: actualizar líneas y line_start
            n_newlines = value.count("\n")
            if n_newlines:
                line += n_newlines
                # posicion del último salto dentro del comentario
                last_nl = value.rfind("\n")
                line_start = mo.start() + last_nl + 1
            continue
        elif kind == "ID":
            if value in KEYWORDS:
                kind = "KEYWORD"
        elif kind == "MISMATCH":
            raise SyntaxError(f"Caracter inesperado {value!r} en línea {line} columna {column}")

        yield Token(kind, value, line, column)

def lex_to_list(code: str):
    """Devuelve la lista de tokens a partir de un string de código JS."""
    return list(tokenize(code))
