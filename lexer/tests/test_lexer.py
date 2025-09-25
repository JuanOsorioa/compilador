import pytest
from compilador.lexer import lex_to_list, Token

def test_variable_assignment():
    code = "var x = 5;"
    tokens = lex_to_list(code)

    # El primer token debería ser la palabra reservada "var"
    assert tokens[0].type == "KEYWORD"
    assert tokens[0].value == "var"

    # Luego un identificador
    assert tokens[1].type == "ID"
    assert tokens[1].value == "x"

    # Luego el operador de asignación
    assert tokens[2].type == "ASSIGN"
    assert tokens[2].value == "="

    # Y un número entero
    assert tokens[3].type == "NUMBER"
    assert tokens[3].value == "5"

def test_arithmetic_expression():
    code = "x = x + 1;"
    tokens = lex_to_list(code)

    assert any(t.type == "ARITH_OP" and t.value == "+" for t in tokens)
    assert any(t.type == "NUMBER" and t.value == "1" for t in tokens)

def test_logical_expression():
    code = "if (x && y) { return x || y; }"
    tokens = lex_to_list(code)

    # Verifica que detecta operadores lógicos
    assert any(t.type == "LOGIC_OP" and t.value == "&&" for t in tokens)
    assert any(t.type == "LOGIC_OP" and t.value == "||" for t in tokens)
