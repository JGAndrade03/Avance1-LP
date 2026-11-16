from __future__ import annotations

import argparse
from datetime import datetime
import os
import sys

from sintactico import (
    AnonymousFunction,
    ArrayLiteral,
    Assignment,
    BinaryExpression,
    BreakStatement,
    Dictionary,
    FieldAccess,
    ForLoop,
    FunctionCall,
    FunctionDeclaration,
    IfStatement,
    IndexExpression,
    IndexedAssignment,
    Literal,
    Matrix,
    MethodCall,
    ParseError,
    PrintStatement,
    ReadExpression,
    RepeatLoop,
    ReturnStatement,
    Statement,
    TargetAssignment,
    UnaryExpression,
    Variable,
    VariableDeclaration,
    WhileLoop,
    parse,
)


class AnalizadorSemantico:
    """Analizador semántico modular organizado por responsabilidades de integrantes."""

    def __init__(self) -> None:
        self.errores: list[str] = []
        
        # ESTADOS DE CONTEXTO: JUAN GUALOTUÑA 
        self.en_funcion: int = 0  # Contadores de profundidad
        self.en_bucle: int = 0
        
        # ESTADOS DE TABLA DE SÍMBOLOS: JULIO LLERENA 
        self.variables_declaradas: set[str] = set()
        self.constantes: set[str] = set()
        
        # ESTADOS DE COMPATIBILIDAD DE TIPOS: VALERIA GAVELA 
        self.tipos_variables: dict[str, str] = {}

    def analizar(self, statements: list[Statement]) -> list[str]:
        self.errores = []
        self.en_funcion = 0
        self.en_bucle = 0
        self.variables_declaradas.clear()
        self.constantes.clear()
        self.tipos_variables.clear()

        for statement in statements:
            self.visitar(statement)

        return self.errores

    def visitar(self, nodo: object) -> None:
        if nodo is None:
            return

        # 1. Ejecutar verificaciones semánticas por integrante
        self._analizar_juan(nodo)
        self._analizar_julio(nodo)
        self._analizar_valeria(nodo)

        # 2. Gestionar el recorrido del AST y la actualización de contextos
        self._recorrer_hijos(nodo)



# REGLAS SEMANTICAS



    # REGLAS SEMÁNTICAS: JUAN ANDRÉS GUALOTUÑA (JGAndrade03)
    def _analizar_juan(self, nodo: object) -> None:
        """Reglas de Juan:
        1. Contexto de return: Solo permitido dentro de funciones.
        2. Ruptura de bucle (break): Solo permitido dentro de bucles.
        """
        # Regla 1: Retorno de Funciones
        if isinstance(nodo, ReturnStatement):
            if self.en_funcion == 0:
                self.errores.append(
                    "Error Semántico [Juan - Contexto]: La instrucción 'return' "
                    "solo es válida dentro del cuerpo de una función."
                )

        # Regla 2: Ruptura Lógica con Break
        elif isinstance(nodo, BreakStatement):
            if self.en_bucle == 0:
                self.errores.append(
                    "Error Semántico [Juan - Estructura]: La instrucción 'break' "
                    "solo se permite dentro de un bucle (for, while, repeat)."
                )
    #-----------------------------------------------------------------------------


    # REGLAS SEMÁNTICAS: JULIO LLERENA - PLANTILLA BASE
    
    
    #------------------------------------------------------------------


    # REGLAS SEMÁNTICAS: VALERIA GAVELA - PLANTILLA BASE
    
    
    #--------------------------------------------------------------


    # GESTOR RECURSIVO DE ARBOL (Nodos Hijos y Cambios de Contexto)
    
    def _recorrer_hijos(self, nodo: object) -> None:
        # Bucles: Incrementan y decrementan la profundidad de bucle (Juan)
        if isinstance(nodo, ForLoop):
            self.visitar(nodo.start)
            self.visitar(nodo.end)
            if nodo.step:
                self.visitar(nodo.step)
            self.en_bucle += 1
            for stmt in nodo.body:
                self.visitar(stmt)
            self.en_bucle -= 1

        elif isinstance(nodo, WhileLoop):
            self.visitar(nodo.condition)
            self.en_bucle += 1
            for stmt in nodo.body:
                self.visitar(stmt)
            self.en_bucle -= 1

        elif isinstance(nodo, RepeatLoop):
            self.en_bucle += 1
            for stmt in nodo.body:
                self.visitar(stmt)
            self.en_bucle -= 1
            self.visitar(nodo.condition)

        # Funciones: Incrementan y decrementan la profundidad de función (Juan)
        elif isinstance(nodo, FunctionDeclaration):
            self.en_funcion += 1
            for stmt in nodo.body:
                self.visitar(stmt)
            self.en_funcion -= 1

        elif isinstance(nodo, AnonymousFunction):
            self.en_funcion += 1
            for stmt in nodo.body:
                self.visitar(stmt)
            self.en_funcion -= 1

        # Nodos estructurales genéricos
        elif isinstance(nodo, IfStatement):
            self.visitar(nodo.condition)
            for stmt in nodo.then_body:
                self.visitar(stmt)
            for stmt in nodo.else_body:
                self.visitar(stmt)

        elif isinstance(nodo, VariableDeclaration):
            for val in nodo.values:
                self.visitar(val)

        elif isinstance(nodo, Assignment):
            for val in nodo.values:
                self.visitar(val)

        elif isinstance(nodo, TargetAssignment):
            for target in nodo.targets:
                self.visitar(target)
            for val in nodo.values:
                self.visitar(val)

        elif isinstance(nodo, IndexedAssignment):
            self.visitar(nodo.target)
            for val in nodo.values:
                self.visitar(val)

        elif isinstance(nodo, PrintStatement):
            for arg in nodo.arguments:
                self.visitar(arg)

        elif isinstance(nodo, FunctionCall):
            if not isinstance(nodo.name, str):
                self.visitar(nodo.name)
            for arg in nodo.arguments:
                self.visitar(arg)

        elif isinstance(nodo, MethodCall):
            self.visitar(nodo.target)
            for arg in nodo.arguments:
                self.visitar(arg)

        elif isinstance(nodo, BinaryExpression):
            self.visitar(nodo.left)
            self.visitar(nodo.right)

        elif isinstance(nodo, UnaryExpression):
            self.visitar(nodo.operand)

        elif isinstance(nodo, IndexExpression):
            self.visitar(nodo.collection)
            self.visitar(nodo.index)

        elif isinstance(nodo, FieldAccess):
            self.visitar(nodo.target)

        elif isinstance(nodo, Dictionary):
            for field in nodo.fields:
                if not isinstance(field.key, str):
                    self.visitar(field.key)
                self.visitar(field.value)

        elif isinstance(nodo, ArrayLiteral):
            for elem in nodo.elements:
                self.visitar(elem)

        elif isinstance(nodo, Matrix):
            for row in nodo.rows:
                for elem in row:
                    self.visitar(elem)

        elif isinstance(nodo, ReturnStatement):
            for val in nodo.values:
                self.visitar(val)


def generar_log_semantico(
    autor: str,
    errores: list[str],
    directorio_logs: str = "logs",
) -> str:
    """Genera el log semántico en el formato exigido: semantico-usuarioGit-fecha-hora.txt."""
    fecha = datetime.now().strftime("%d%m%Y-%Hh%M")
    nombre_log = f"semantico-{autor}-{fecha}.txt"

    os.makedirs(directorio_logs, exist_ok=True)
    ruta_log = os.path.join(directorio_logs, nombre_log)

    lineas = ["RESULTADO DEL ANÁLISIS SEMÁNTICO:", ""]
    lineas.append("ERRORES SEMÁNTICOS:")
    if errores:
        lineas.extend(errores)
    else:
        lineas.append("Ninguno")

    with open(ruta_log, "w", encoding="utf-8") as archivo_log:
        archivo_log.write("\n".join(lineas) + "\n")

    return ruta_log


def main() -> int:
    parser_cli = argparse.ArgumentParser(
        description="Analizador semántico para el lenguaje Lua."
    )
    parser_cli.add_argument("archivo", help="Ruta al archivo fuente .lua")
    parser_cli.add_argument(
        "--autor", default="JGAndrade03", help="Usuario de GitHub para el log"
    )

    args = parser_cli.parse_args()

    try:
        with open(args.archivo, encoding="utf-8") as archivo_fuente:
            codigo = archivo_fuente.read()
            statements = parse(codigo)

    except OSError as error:
        print(f"Error de archivo: {error}", file=sys.stderr)
        return 1

    except ParseError as error:
        print(f"Error en fase previa (Léxica/Sintáctica):\n{error}", file=sys.stderr)
        return 1

    analizador = AnalizadorSemantico()
    errores = analizador.analizar(statements)

    ruta_log = generar_log_semantico(args.autor, errores)
    print(f"Log semántico generado: {ruta_log}")

    if errores:
        print("\n".join(errores), file=sys.stderr)
        return 1

    print("Análisis semántico finalizado sin errores.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())