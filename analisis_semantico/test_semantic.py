import sys
import os
import importlib.util

# Cargar dinámicamente lexer.py y parser.py desde la raíz del repo
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Asegurar que la raíz del repo esté en sys.path para poder importar el paquete analisis_semantico
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

lexer_path = os.path.join(repo_root, 'lexer', 'lexer.py')
spec_lexer = importlib.util.spec_from_file_location('lexer', lexer_path)
lexer_mod = importlib.util.module_from_spec(spec_lexer)
sys.modules['lexer'] = lexer_mod
spec_lexer.loader.exec_module(lexer_mod)

parser_path = os.path.join(repo_root, 'parser', 'parser.py')
spec_parser = importlib.util.spec_from_file_location('parser', parser_path)
parser_mod = importlib.util.module_from_spec(spec_parser)
sys.modules['parser'] = parser_mod
spec_parser.loader.exec_module(parser_mod)

from analisis_semantico.semantic import SemanticAnalyzer


def test_semantic_basic():
    code = (
        "var x = 10;\n"
        "let y = 20;\n\n"
        "if (x + 5 > y && y != 0) {\n"
        "    const z = y * 2 + 1;\n"
        "} else {\n"
        "    y = 0;\n"
        "}\n"
    )

    tree = parser_mod.parser.parse(code, lexer=lexer_mod.lexer)
    assert tree is not None

    analyzer = SemanticAnalyzer()
    table = analyzer.analyze(tree)

    # No errors expected in this example
    assert analyzer.errors == []

    # Check that 'x' and 'y' are in the table
    sx = table.lookup('x')
    sy = table.lookup('y')
    assert sx is not None and sx.name == 'x'
    assert sy is not None and sy.name == 'y'

    # 'z' was declared in an inner scope; it should still appear in all_symbols
    sz = None
    for sym in table.all_symbols():
        if sym.name == 'z':
            sz = sym
            break
    assert sz is not None and sz.kind == 'const'


if __name__ == '__main__':
    test_semantic_basic()
    print('Test semántico básico ejecutado correctamente')
