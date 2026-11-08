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


@dataclass(frozen=True)
class ArrayLiteral:
    elements: tuple[Expression, ...]


@dataclass(frozen=True)
class FunctionCall:
    name: str
    arguments: tuple[Expression, ...]


@dataclass(frozen=True)
class IndexExpression:
    collection: Expression
    index: Expression


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
    body: tuple[Statement, ...]


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
    body: tuple[Statement, ...]


@dataclass(frozen=True)
class PrintStatement:
    arguments: tuple[Expression, ...]


@dataclass(frozen=True)
class ReadExpression:
    pass

#----------------------------------------------------

Expression: TypeAlias = (
    Literal
    | Variable
    | UnaryExpression
    | BinaryExpression
    | ArrayLiteral
    | FunctionCall
    | IndexExpression
    | Dictionary
    | AnonymousFunction
    | ReadExpression
)


@dataclass(frozen=True)
class IndexedAssignment:
    target: IndexExpression
    values: tuple[Expression, ...]


@dataclass(frozen=True)
class IfStatement:
    condition: Expression
    then_body: tuple[Statement, ...]
    else_body: tuple[Statement, ...]


@dataclass(frozen=True)
class FunctionDeclaration:
    name: str
    parameters: tuple[str, ...]
    body: tuple[Statement, ...]


@dataclass(frozen=True)
class ReturnStatement:
    values: tuple[Expression, ...]


Statement: TypeAlias = (
    VariableDeclaration
    | Assignment
    | IndexedAssignment
    | IfStatement
    | FunctionDeclaration
    | ReturnStatement
    | ForLoop
    | PrintStatement
)


class ParseError(ValueError):
    """Error léxico o sintáctico producido al analizar el código fuente."""


precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("nonassoc", "EQ", "NE", "LT", "LE", "GT", "GE"),
    ("left", "PLUS", "MINUS"),
    ("left", "MULTIPLY", "DIVIDE", "FLOOR_DIVIDE", "MODULO"),
    ("right", "NOT"),
    ("right", "UMINUS"),
    ("right", "POWER"),
    ("left", "INDEX"),
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


def p_statement_indexed_assignment(p):
    "statement : indexed_target ASSIGN expressions"
    p[0] = IndexedAssignment(p[1], tuple(p[3]))


#--- JUAN GUALOTUÑA -----


def p_statement_for(p):
    """statement : FOR ID ASSIGN expression COMMA expression DO statements END_DELIM
                 | FOR ID ASSIGN expression COMMA expression COMMA expression DO statements END_DELIM"""
    if len(p) == 10:
        p[0] = ForLoop(p[2], p[4], p[6], None, tuple(p[8]))
    else:
        p[0] = ForLoop(p[2], p[4], p[6], p[8], tuple(p[10]))


def p_indexed_target_single(p):
    "indexed_target : ID LBRACKET expression RBRACKET"
    p[0] = IndexExpression(Variable(p[1]), p[3])


def p_indexed_target_nested(p):
    "indexed_target : indexed_target LBRACKET expression RBRACKET"
    p[0] = IndexExpression(p[1], p[3])


def p_statement_if(p):
    "statement : IF expression THEN statements else_clause END_DELIM"
    p[0] = IfStatement(p[2], tuple(p[4]), tuple(p[5]))


def p_else_clause_else(p):
    "else_clause : ELSE statements"
    p[0] = p[2]


def p_else_clause_elseif(p):
    "else_clause : ELSEIF expression THEN statements else_clause"
    p[0] = [IfStatement(p[2], tuple(p[4]), tuple(p[5]))]


def p_else_clause_empty(p):
    "else_clause : empty"
    p[0] = []


def p_statement_function_declaration(p):
    "statement : FUNCTION ID LPAREN optional_parameters RPAREN statements END_DELIM"
    p[0] = FunctionDeclaration(p[2], tuple(p[4]), tuple(p[6]))


def p_optional_parameters(p):
    """optional_parameters : parameters
                           | empty"""
    p[0] = p[1] if p[1] is not None else []


def p_parameters_single(p):
    "parameters : ID"
    p[0] = [p[1]]


def p_parameters_multiple(p):
    "parameters : parameters COMMA ID"
    p[0] = p[1] + [p[3]]


def p_statement_return(p):
    "statement : RETURN optional_return_values"
    p[0] = ReturnStatement(tuple(p[2]))


def p_optional_return_values(p):
    """optional_return_values : expressions
                              | empty"""
    p[0] = p[1] if p[1] is not None else []


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


def p_expression_array(p):
    "expression : LBRACE optional_array_elements RBRACE"
    p[0] = ArrayLiteral(tuple(p[2]))


def p_expression_dictionary(p):
    "expression : LBRACE dictionary_fields RBRACE"
    p[0] = Dictionary(tuple(p[2]))


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


def p_optional_array_elements(p):
    """optional_array_elements : expressions
                               | empty"""
    p[0] = p[1] if p[1] is not None else []


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


def p_expression_function_call(p):
    "expression : ID LPAREN optional_arguments RPAREN"
    p[0] = FunctionCall(p[1], tuple(p[3]))


def p_optional_arguments(p):
    """optional_arguments : expressions
                          | empty"""
    p[0] = p[1] if p[1] is not None else []


def p_expression_anonymous_function(p):
    "expression : FUNCTION LPAREN optional_names RPAREN statements END_DELIM"
    p[0] = AnonymousFunction(tuple(p[3]), tuple(p[5]))


def p_optional_names(p):
    """optional_names : names
                      | empty"""
    p[0] = p[1] if p[1] is not None else []


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

def p_expression_index(p):
    "expression : expression LBRACKET expression RBRACKET %prec INDEX"
    p[0] = IndexExpression(p[1], p[3])


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


def p_expression_comparison(p):
    """expression : expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression
                  | expression AND expression
                  | expression OR expression"""
    p[0] = BinaryExpression(p[2], p[1], p[3])


def p_expression_not(p):
    "expression : NOT expression"
    p[0] = UnaryExpression("not", p[2])


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
