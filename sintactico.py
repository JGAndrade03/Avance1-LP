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


Statement: TypeAlias = VariableDeclaration | Assignment


class ParseError(ValueError):
    """Error léxico o sintáctico producido al analizar el código fuente."""


precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "MULTIPLY", "DIVIDE", "FLOOR_DIVIDE", "MODULO"),
    ("right", "UMINUS"),
    ("right", "POWER"),
)


def p_program(p):
    "program : statements"
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
    "statement : names ASSIGN expressions"
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


def p_expression_variable(p):
    "expression : ID"
    p[0] = Variable(p[1])


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
                  | expression POWER expression"""
    p[0] = BinaryExpression(p[2], p[1], p[3])


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

    fecha = datetime.now().strftime("%d-%m-%Y-%Hh%M")
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
