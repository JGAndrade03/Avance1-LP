from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import os
import sys
from typing import TypeAlias

import ply.yacc as yacc

from lexer import lexer as _lexer, tokens


@dataclass(frozen=True)
class Literal:
    value: int | float | str | bool | None


@dataclass(frozen=True)
class Variable:
    name: str


@dataclass(frozen=True)
class UnaryExpression:
    operator: str
    operand: Expression


@dataclass(frozen=True)
class BinaryExpression:
    operator: str
    left: Expression
    right: Expression


Expression: TypeAlias = Literal | Variable | UnaryExpression | BinaryExpression


@dataclass(frozen=True)
class VariableDeclaration:
    names: tuple[str, ...]
    values: tuple[Expression, ...]
    local: bool


@dataclass(frozen=True)
class Assignment:
    names: tuple[str, ...]
    values: tuple[Expression, ...]
    
    

# --- JUAN GUALOTUÑA ---
@dataclass(frozen=True)
class ForLoop:
    iterator: str
    start: Expression
    end: Expression
    step: Expression | None
    body: list[Statement]

@dataclass(frozen=True)
class DictionaryField:
    key: str | Expression
    value: Expression

@dataclass(frozen=True)
class Dictionary:
    fields: tuple[DictionaryField, ...]

@dataclass(frozen=True)
class AnonymousFunction:
    params: tuple[str, ...]
    body: list[Statement]

@dataclass(frozen=True)
class PrintStatement:
    arguments: tuple[Expression, ...]

@dataclass(frozen=True)
class ReadExpression:
    pass


#----------------------------------------------------


# --- INICIO APORTE VALERIA GAVELA: (matriz, acceso, función, return, while) ---
@dataclass(frozen=True)
class Index:
    """Acceso por índice: m[i], m[i][j]."""
    table: Expression
    key: Expression


@dataclass(frozen=True)
class Matrix:
    """Matriz como tabla de tablas: {{1, 2}, {3, 4}}."""
    rows: tuple[tuple[Expression, ...], ...]


@dataclass(frozen=True)
class FunctionCall:
    function: Expression
    args: tuple[Expression, ...]


@dataclass(frozen=True)
class FunctionDefinition:
    name: str
    params: tuple[str, ...]
    body: tuple[Statement, ...]
    local: bool


@dataclass(frozen=True)
class Return:
    values: tuple[Expression, ...]


@dataclass(frozen=True)
class While:
    condition: Expression
    body: tuple[Statement, ...]
# --- FIN APORTE VALERIA GAVELA ---


Expression: TypeAlias = (
    Literal | Variable | UnaryExpression | BinaryExpression | Dictionary
    | AnonymousFunction | ReadExpression | Index | Matrix | FunctionCall
)

Statement: TypeAlias = (
    VariableDeclaration | Assignment | ForLoop | PrintStatement
    | FunctionDefinition | Return | While | FunctionCall
)


class ParseError(ValueError):
    """Error léxico o sintáctico producido al analizar el código fuente."""


precedence = (
    ("left", "OR"),  # Valeria
    ("left", "AND"),  # Valeria
    ("left", "LT", "LE", "GT", "GE", "EQ", "NE"),  # Valeria: relacionales
    ("right", "CONCAT"),  # Valeria
    ("left", "PLUS", "MINUS"),
    ("left", "MULTIPLY", "DIVIDE", "FLOOR_DIVIDE", "MODULO"),
    ("right", "UMINUS"),  # también usado por NOT y # (Valeria)
    ("right", "POWER"),
)


def p_program(p):
    "program : block"
    p[0] = p[1]


def p_statements_append(p):
    "statements : statements statement"
    p[0] = p[1] + [p[2]]


def p_statements_empty(p):
    "statements : empty"
    p[0] = []


def p_statement_local_declaration(p):
    "statement : LOCAL names optional_initializer"
    p[0] = VariableDeclaration(tuple(p[2]), tuple(p[3]), local=True)


def p_statement_assignment(p):
    "statement : varlist ASSIGN expressions"  # Valeria: antes "names"; admite m[i][j] = x
    p[0] = Assignment(tuple(p[1]), tuple(p[3]))


def p_statement_semicolon(p):
    "statement : SEMICOLON"
    p[0] = None


def p_optional_initializer(p):
    """optional_initializer : ASSIGN expressions
                            | empty"""
    p[0] = p[2] if len(p) == 3 else []


def p_names_single(p):
    "names : ID"
    p[0] = [p[1]]


def p_names_multiple(p):
    "names : names COMMA ID"
    p[0] = p[1] + [p[3]]


def p_expressions_single(p):
    "expressions : expression"
    p[0] = [p[1]]


def p_expressions_multiple(p):
    "expressions : expressions COMMA expression"
    p[0] = p[1] + [p[3]]


def p_expression_literal(p):
    """expression : ENTERO
                  | FLOTANTE
                  | HEXADECIMAL
                  | CADENA"""
    p[0] = Literal(p[1])


def p_expression_boolean_nil(p):
    """expression : TRUE
                  | FALSE
                  | NIL"""
    p[0] = Literal({"TRUE": True, "FALSE": False, "NIL": None}[p.slice[1].type])


def p_expression_grouped(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]


def p_expression_unary_minus(p):
    "expression : MINUS expression %prec UMINUS"
    p[0] = UnaryExpression("-", p[2])


def p_expression_binary(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULTIPLY expression
                  | expression DIVIDE expression
                  | expression FLOOR_DIVIDE expression
                  | expression MODULO expression
                  | expression POWER expression
                  | expression CONCAT expression
                  | expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression
                  | expression AND expression
                  | expression OR expression"""
    p[0] = BinaryExpression(p[2], p[1], p[3])
    
    
#--- JUAN GUALOTUÑA -----

# Bucle FOR:
def p_statement_for(p):
    """statement : FOR ID ASSIGN expression COMMA expression DO statements END_DELIM
                 | FOR ID ASSIGN expression COMMA expression COMMA expression DO statements END_DELIM"""
    if len(p) == 10:
        p[0] = ForLoop(p[2], p[4], p[6], None, p[8])
    else:
        p[0] = ForLoop(p[2], p[4], p[6], p[8], p[9])

# Diccionarios:
def p_expression_dictionary(p):
    """expression : LBRACE dictionary_fields RBRACE
                  | LBRACE RBRACE"""
    p[0] = Dictionary(tuple(p[2])) if len(p) == 4 else Dictionary(())

def p_dictionary_fields_single(p):
    "dictionary_fields : dictionary_field"
    p[0] = [p[1]]

def p_dictionary_fields_multiple(p):
    "dictionary_fields : dictionary_fields COMMA dictionary_field"
    p[0] = p[1] + [p[3]]

def p_dictionary_field_id(p):
    "dictionary_field : ID ASSIGN expression"
    p[0] = DictionaryField(p[1], p[3])

def p_dictionary_field_bracket(p):
    "dictionary_field : LBRACKET expression RBRACKET ASSIGN expression"
    p[0] = DictionaryField(p[2], p[5])

# Funciones Anónimas:
def p_expression_anonymous_function(p):
    "expression : FUNCTION LPAREN optional_names RPAREN block END_DELIM"
    p[0] = AnonymousFunction(tuple(p[3]), p[5])

def p_optional_names(p):
    """optional_names : names
                      | empty"""
    p[0] = p[1] if p[1] is not None else []

# Print y IO.Read:
def p_statement_print(p):
    "statement : PRINT LPAREN optional_expressions RPAREN"
    p[0] = PrintStatement(tuple(p[3]))

def p_optional_expressions(p):
    """optional_expressions : expressions
                            | empty"""
    p[0] = p[1] if p[1] is not None else []

def p_expression_io_read(p):
    "expression : IO_READ LPAREN RPAREN"
    p[0] = ReadExpression()
    
# ---------------------------------------------------------------------


# --- INICIO APORTE VALERIA GAVELA ---
# Reglas: expresiones booleanas (relacionales y lógicas), matrices,
# definición de funciones (declaración y llamada) y estructura de control while.

# Operadores unarios: not, # (longitud)
def p_expression_unary_not_length(p):
    """expression : NOT expression %prec UMINUS
                  | LENGTH expression %prec UMINUS"""
    p[0] = UnaryExpression(p[1], p[2])


# Variables y acceso por índice: x, m[i], m[i][j]
def p_var_name(p):
    "var : ID"
    p[0] = Variable(p[1])


def p_var_index(p):
    "var : prefixexp LBRACKET expression RBRACKET"
    p[0] = Index(p[1], p[3])


def p_varlist(p):
    """varlist : var
               | varlist COMMA var"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]


def p_prefixexp(p):
    """prefixexp : var
                 | functioncall"""
    p[0] = p[1]


def p_expression_prefixexp(p):
    "expression : prefixexp"
    p[0] = p[1]


# Matriz: {{1, 2, 3}, {4, 5, 6}}
def p_expression_matrix(p):
    "expression : LBRACE matrix_rows RBRACE"
    p[0] = Matrix(tuple(p[2]))


def p_matrix_rows(p):
    """matrix_rows : matrix_row
                   | matrix_rows COMMA matrix_row"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]


def p_matrix_row(p):
    "matrix_row : LBRACE expressions RBRACE"
    p[0] = tuple(p[2])


# Llamada a función: calcularArea(10, 5)
def p_functioncall(p):
    "functioncall : prefixexp LPAREN optional_expressions RPAREN"
    p[0] = FunctionCall(p[1], tuple(p[3]))


def p_statement_functioncall(p):
    "statement : functioncall"
    p[0] = p[1]


# Bloque: instrucciones con return opcional al final
def p_block(p):
    "block : statements optional_return"
    p[0] = [s for s in p[1] if s is not None] + ([p[2]] if p[2] is not None else [])


def p_optional_return(p):
    """optional_return : return_statement
                       | empty"""
    p[0] = p[1]


def p_return_statement(p):
    """return_statement : RETURN optional_expressions
                        | RETURN optional_expressions SEMICOLON"""
    p[0] = Return(tuple(p[2]))


# Definición de funciones: function nombre(params) ... end
def p_funcname(p):
    """funcname : ID
                | funcname DOT ID"""
    p[0] = p[1] if len(p) == 2 else f"{p[1]}.{p[3]}"


def p_statement_function_def(p):
    "statement : FUNCTION funcname LPAREN optional_names RPAREN block END_DELIM"
    p[0] = FunctionDefinition(p[2], tuple(p[4]), tuple(p[6]), local=False)


def p_statement_local_function_def(p):
    "statement : LOCAL FUNCTION ID LPAREN optional_names RPAREN block END_DELIM"
    p[0] = FunctionDefinition(p[3], tuple(p[5]), tuple(p[7]), local=True)


# Estructura de control: while
def p_statement_while(p):
    "statement : WHILE expression DO block END_DELIM"
    p[0] = While(p[2], tuple(p[4]))
# --- FIN APORTE VALERIA GAVELA ---


def p_empty(p):
    "empty :"
    p[0] = None


_syntax_errors: list[str] = []


def p_error(token):
    if token is None:
        _syntax_errors.append("Error sintáctico: fin de archivo inesperado.")
    else:
        _syntax_errors.append(
            f"Error sintáctico en línea {token.lineno}: "
            f"token {token.type} ({token.value!r}) inesperado."
        )


_parser = yacc.yacc(
    start="program",
    debug=False,
    write_tables=False,
    errorlog=yacc.NullLogger(),
)


def parse(source: str) -> list[Statement]:
    global _syntax_errors

    _syntax_errors = []
    _lexer.lineno = 1
    _lexer.errores = []
    statements = _parser.parse(source, lexer=_lexer)

    errors = _lexer.errores + _syntax_errors
    if errors:
        raise ParseError("\n".join(errors))
    return [statement for statement in statements if statement is not None]


def generar_log_sintactico(
    autor: str,
    statements: list[Statement],
    errores: list[str],
    directorio_logs: str = "logs",
) -> str:

    fecha = datetime.now().strftime("%d%m%Y-%Hh%M")
    nombre_log = f"sintactico-{autor}-{fecha}.txt"
    os.makedirs(directorio_logs, exist_ok=True)
    ruta_log = os.path.join(directorio_logs, nombre_log)

    lineas = ["INSTRUCCIONES RECONOCIDAS:"]
    if statements:
        lineas.extend(str(statement) for statement in statements)
    else:
        lineas.append("Ninguna")

    lineas.extend(("", "ERRORES DE ANÁLISIS:"))
    lineas.extend(errores if errores else ["Ninguno"])
    with open(ruta_log, "w", encoding="utf-8") as archivo_log:
        archivo_log.write("\n".join(lineas) + "\n")
    return ruta_log


def main() -> int:

    argument_parser = argparse.ArgumentParser(
        description="Analiza declaraciones de variables y expresiones aritméticas."
    )

    argument_parser.add_argument("archivo", help="archivo fuente Lua")
    argument_parser.add_argument(
        "--autor", default="Usuario", help="nombre usado en el archivo de log"
    )

    args = argument_parser.parse_args()

    try:
        with open(args.archivo, encoding="utf-8") as archivo_fuente:
            statements = parse(archivo_fuente.read())

    except OSError as error:
        print(error, file=sys.stderr)
        return 1
    
    except ParseError as error:
        errores = str(error).splitlines()
        statements = []
        
    else:
        errores = []

    ruta_log = generar_log_sintactico(args.autor, statements, errores)
    print(f"Log generado: {ruta_log}")

    if errores:
        print("\n".join(errores), file=sys.stderr)
        return 1

    print(f"Análisis sintáctico correcto: {len(statements)} instrucción(es).")
    for statement in statements:
        print(statement)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())