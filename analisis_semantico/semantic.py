import sys
import os
from typing import List, Dict, Optional

# Asegurar que el proyecto raíz esté en sys.path para importar el parser y el lexer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # importamos el módulo parser (archivo parser/parser.py) como se hace en las pruebas del lexer
    from parser import parser as parser_module
    from lexer import lexer as lexer_module
except Exception:
    # Si la importación falla no queremos romper el módulo al importarlo; las funciones CLI manejarán esto.
    parser_module = None
    lexer_module = None


class Symbol:
    def __init__(self, name: str, kind: str, scope_level: int):
        self.name = name
        self.kind = kind
        self.scope_level = scope_level

    def to_dict(self):
        return {"name": self.name, "kind": self.kind, "scope_level": self.scope_level}

    def __repr__(self):
        return f"Symbol(name={self.name}, kind={self.kind}, scope_level={self.scope_level})"


class SymbolTable:
    """Tabla de símbolos con soporte para ámbitos (stack de diccionarios).

    Además guarda ámbitos completados para poder reportar todas las declaraciones
    incluso si el scope fue cerrado durante el análisis.
    """

    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = []
        self.completed_scopes: List[Dict[str, Symbol]] = []

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if self.scopes:
            popped = self.scopes.pop()
            # conservar el scope cerrado para reportes posteriores
            self.completed_scopes.append(popped)
            return popped
        return None

    def declare(self, name: str, kind: str) -> Optional[str]:
        """Declara un símbolo en el ámbito actual. Devuelve mensaje de error si redeclaración."""
        if not self.scopes:
            self.push_scope()
        current = self.scopes[-1]
        if name in current:
            return f"Redeclaración de '{name}' en el mismo ámbito"
        sym = Symbol(name, kind, len(self.scopes) - 1)
        current[name] = sym
        return None

    def lookup(self, name: str) -> Optional[Symbol]:
        """Busca el símbolo en los ámbitos desde el más interno al externo."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        # buscar también en ámbitos ya cerrados (opcional)
        for scope in reversed(self.completed_scopes):
            if name in scope:
                return scope[name]
        return None

    def current_scope_symbols(self) -> List[Symbol]:
        if not self.scopes:
            return []
        return list(self.scopes[-1].values())

    def all_symbols(self) -> List[Symbol]:
        out = []
        for i, scope in enumerate(self.scopes):
            for s in scope.values():
                out.append(s)
        for i, scope in enumerate(self.completed_scopes):
            for s in scope.values():
                out.append(s)
        return out


class SemanticAnalyzer:
    """Analizador semántico simple que construye una tabla de símbolos y detecta errores básicos.

    - declara variables (var/let/const)
    - detecta redeclaraciones en el mismo ámbito
    - detecta asignaciones o usos de variables no declaradas
    - maneja ámbitos por bloques (cada `statement_list` dentro de un bloque crea un nuevo scope)
    """

    def __init__(self):
        self.table = SymbolTable()
        self.errors: List[str] = []

    def analyze(self, node):
        """Punto de entrada: recibe el AST (Node) construido por `parser`."""
        # el `program` crea el scope global
        self.table.push_scope()
        self._analyze_node(node, in_program_root=True)
        return self.table

    def _analyze_node(self, node, in_program_root=False):
        if node is None:
            return
        t = getattr(node, 'type', None)
        if t == 'program':
            # program -> statement_list
            self._analyze_node(node.children[0], in_program_root=True)

        elif t == 'statement_list':
            # Si es root del programa ya tenemos el scope global; si es bloque (no root) creamos nuevo scope
            if in_program_root:
                for child in node.children:
                    self._analyze_node(child)
            else:
                # nuevo scope para este statement_list
                self.table.push_scope()
                for child in node.children:
                    self._analyze_node(child)
                self.table.pop_scope()

        elif t == 'declaration':
            # value: "var x" o "let y" etc.
            if not node.value:
                return
            parts = node.value.split()
            if len(parts) >= 2:
                kind = parts[0]
                name = parts[1]
            else:
                # defensa simple
                return
            err = self.table.declare(name, kind)
            if err:
                self.errors.append(err)
            # analizar la expresión de inicialización
            for child in node.children:
                self._analyze_node(child)

        elif t == 'assignment':
            # value: nombre de variable asignada
            name = node.value
            if not self.table.lookup(name):
                self.errors.append(f"Asignación a variable no declarada '{name}'")
            for child in node.children:
                self._analyze_node(child)

        elif t == 'expression_statement':
            for child in node.children:
                self._analyze_node(child)

        elif t == 'if':
            # children: [condition, consequent]
            cond = node.children[0]
            cons = node.children[1]
            self._analyze_node(cond)
            # si el consequent es un statement_list, creamos scope; lo manejamos pasando flag
            if getattr(cons, 'type', None) == 'statement_list':
                self._analyze_node(cons, in_program_root=False)
            else:
                self._analyze_node(cons)

        elif t == 'if-else':
            # children: [condition, consequent, alternate]
            cond = node.children[0]
            cons = node.children[1]
            alt = node.children[2]
            self._analyze_node(cond)
            if getattr(cons, 'type', None) == 'statement_list':
                self._analyze_node(cons, in_program_root=False)
            else:
                self._analyze_node(cons)
            if getattr(alt, 'type', None) == 'statement_list':
                self._analyze_node(alt, in_program_root=False)
            else:
                self._analyze_node(alt)

        elif t == 'binary_op':
            # children: left, right
            left, right = node.children
            self._analyze_node(left)
            self._analyze_node(right)

        elif t == 'identifier':
            name = node.value
            if not self.table.lookup(name):
                self.errors.append(f"Uso de variable no declarada '{name}'")

        elif t == 'number':
            return

        else:
            # Para cualquier otro tipo, intentar analizar hijos
            for child in getattr(node, 'children', []) or []:
                self._analyze_node(child)


def pretty_print_table(table: SymbolTable):
    headers = ["name", "kind", "scope_level"]
    print("\nTabla de símbolos:")
    for s in table.all_symbols():
        print(f" - {s.name:10} kind={s.kind:6} scope={s.scope_level}")


def get_parser_and_lexer():
    """Normaliza y devuelve (parser_obj, lexer_obj) listos para usarse.

    parser_module y lexer_module vienen del import_try arriba y pueden ser el módulo
    o el objeto con los atributos necesarios.
    """
    if parser_module is None or lexer_module is None:
        print("No se pudo importar parser o lexer. Ejecuta este script desde la raíz del proyecto.")
        return None, None

    if hasattr(parser_module, 'parse'):
        parser_obj = parser_module
    else:
        parser_obj = getattr(parser_module, 'parser', None)

    if hasattr(lexer_module, 'input') or hasattr(lexer_module, 'token'):
        lexer_obj = lexer_module
    else:
        lexer_obj = getattr(lexer_module, 'lexer', None)

    return parser_obj, lexer_obj


def analyze_code(code: str):
    parser_obj, lexer_obj = get_parser_and_lexer()
    if parser_obj is None or lexer_obj is None:
        raise SystemExit(1)
    tree = parser_obj.parse(code, lexer=lexer_obj)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(tree)
    return tree, analyzer


def run_file(path: str):
    path = os.path.abspath(path)
    if not os.path.exists(path):
        print(f"Archivo no encontrado: {path}")
        return
    code = open(path, 'r', encoding='utf8').read()
    try:
        tree, analyzer = analyze_code(code)
    except Exception as e:
        print(f"Error analizando {path}: {e}")
        return

    print(f"\n==> {path}\n")
    if tree:
        print(tree.pretty())
    else:
        print("No se pudo generar el AST (error de sintaxis probable).\n")

    pretty_print_table(analyzer.table)
    if analyzer.errors:
        print('\nErrores semánticos:')
        for e in analyzer.errors:
            print(' -', e)
    else:
        print('\nNo se encontraron errores semánticos.')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Analizador semántico básico - demo')
    parser.add_argument('file', nargs='?', help='Archivo JS a analizar dentro de ejemplos/')
    args = parser.parse_args()

    if args.file:
        run_file(args.file)
    else:
        # Mantener demo anterior si no se pasa archivo
        demo_code = """
        var x = 10;
        let y = 20;

        if (x + 5 > y && y != 0) {
            const z = y * 2 + 1;
        } else {
            y = 0;
        }
        """
        tree, analyzer = analyze_code(demo_code)
        print("AST generado:\n")
        if tree:
            print(tree.pretty())
        pretty_print_table(analyzer.table)
        if analyzer.errors:
            print('\nErrores semánticos:')
            for e in analyzer.errors:
                print(' -', e)
        else:
            print('\nNo se encontraron errores semánticos.')
