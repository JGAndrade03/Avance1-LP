"""Analizador semántico para Lua (Avance 3).

Recorre el AST que produce sintactico.py, infiere el tipo de cada expresión
y aplica las reglas semánticas del equipo. Cada integrante agrega sus reglas
dentro de su bloque "INICIO / FIN APORTE" (ver más abajo).

Uso:
    python semantico.py archivo.lua --autor usuarioGit
"""
from __future__ import annotations

import argparse
import os
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

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
    IndexedAssignment,
    IndexExpression,
    Literal,
    Matrix,
    MethodCall,
    ParseError,
    PrintStatement,
    ReadExpression,
    RepeatLoop,
    ReturnStatement,
    TargetAssignment,
    UnaryExpression,
    Variable,
    VariableDeclaration,
    WhileLoop,
    parse,
)

# ---------------------------------------------------------------------------
# Tipos del analizador
# ---------------------------------------------------------------------------
NUMERO = "número"
CADENA = "cadena"
BOOLEANO = "booleano"
NIL = "nil"
TABLA = "tabla"
FUNCION = "función"
DESCONOCIDO = "desconocido"  # no se puede saber en tiempo de análisis: no se reporta error

OPERADORES_ARITMETICOS = {"+", "-", "*", "/", "//", "%", "^"}
OPERADORES_RELACIONALES = {"==", "~=", "<", "<=", ">", ">="}

# Reglas semánticas del equipo (se muestran en el log).
# Cada integrante agrega aquí el identificador y la descripción de sus reglas.
REGLAS = {
    "OP-ARIT": "Operadores aritméticos: los operandos de + - * / // % ^ y del menos unario deben ser numéricos.",
    "OP-CONCAT": "Concatenación (..): los operandos deben ser cadenas o números; booleanos, nil, funciones y tablas son incompatibles.",
    # --- INICIO APORTE JUAN GUALOTUÑA ---
    "CTX-RETURN": "Contexto de return: la sentencia 'return' debe estar ubicada únicamente dentro del cuerpo de una función.",
    "CTX-BREAK": "Ruptura de bucle (break): la sentencia 'break' debe estar ubicada strictly dentro de una estructura iterativa (for, while, repeat).",
    # --- FIN APORTE JUAN GUALOTUÑA ---
}


@dataclass(frozen=True)
class ErrorSemantico:
    linea: int
    regla: str
    mensaje: str

    def __str__(self) -> str:
        return f"Error semántico en línea {self.linea} [{self.regla}]: {self.mensaje}"


# ---------------------------------------------------------------------------
# Tabla de símbolos (ámbitos)
# ---------------------------------------------------------------------------
def unir(a: str, b: str) -> str:
    """Tipo resultante cuando una variable pudo recibir dos tipos distintos."""
    return a if a == b else DESCONOCIDO


class Ambito:
    def __init__(self, padre: "Ambito | None" = None, es_funcion: bool = False, es_bucle: bool = False):
        self.padre = padre
        self.es_funcion = es_funcion
        self.es_bucle = es_bucle 
        self.variables: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Analizador
# ---------------------------------------------------------------------------
class AnalizadorSemantico:
    def __init__(self) -> None:
        self.errores: list[ErrorSemantico] = []
        self.global_ = Ambito()
        self.actual = self.global_

    # -- utilidades ---------------------------------------------------------
    def _error(self, linea: int, regla: str, mensaje: str) -> None:
        self.errores.append(ErrorSemantico(linea, regla, mensaje))

    @contextmanager
    def _ambito(self, es_funcion: bool = False, es_bucle: bool = False):
        nuevo = Ambito(self.actual, es_funcion=es_funcion, es_bucle=es_bucle)
        self.actual = nuevo
        try:
            yield nuevo
        finally:
            self.actual = nuevo.padre
            
    # --- INICIO APORTE JUAN GUALOTUÑA ---
    def _esta_en_funcion(self) -> bool:
        ambito = self.actual
        while ambito is not None:
            if ambito.es_funcion:
                return True
            ambito = ambito.padre
        return False

    def _esta_en_bucle(self) -> bool:
        ambito = self.actual
        while ambito is not None:
            if ambito.es_bucle:
                return True
            ambito = ambito.padre
        return False
    # --- FIN APORTE JUAN GUALOTUÑA ---

    def _tipo_variable(self, nombre: str) -> str:
        """Tipo conocido de una variable. Si se lee desde dentro de una función
        y pertenece a un ámbito externo, su valor pudo cambiar: desconocido."""
        ambito, cruzo_funcion = self.actual, False
        while ambito is not None:
            if nombre in ambito.variables:
                return DESCONOCIDO if cruzo_funcion else ambito.variables[nombre]
            if ambito.es_funcion:
                cruzo_funcion = True
            ambito = ambito.padre
        return DESCONOCIDO  # global no declarada (otra regla puede reportarla)

    def _declarar(self, nombre: str, tipo: str) -> None:
        self.actual.variables[nombre] = tipo

    def _asignar(self, nombre: str, tipo: str) -> None:
        """Asignación. En el mismo bloque donde se declaró se sobrescribe el
        tipo; desde un bloque más interno (if, while, función...) se une con el
        anterior porque no se sabe si ese camino se ejecuta."""
        ambito, cruzo_funcion = self.actual, False
        while ambito is not None:
            if nombre in ambito.variables:
                if ambito is self.actual and not cruzo_funcion:
                    ambito.variables[nombre] = tipo
                else:
                    ambito.variables[nombre] = unir(ambito.variables[nombre], tipo)
                return
            if ambito.es_funcion:
                cruzo_funcion = True
            ambito = ambito.padre
        # variable global nueva
        if self.actual is self.global_:
            self.global_.variables[nombre] = tipo
        else:
            self.global_.variables[nombre] = DESCONOCIDO

    # -- punto de entrada ---------------------------------------------------
    def analizar(self, programa) -> list[ErrorSemantico]:
        self._bloque(programa)
        return self.errores

    def _bloque(self, sentencias) -> None:
        for sentencia in sentencias:
            if sentencia is not None:
                self._sentencia(sentencia)

    # -- sentencias ---------------------------------------------------------
    def _sentencia(self, s) -> None:
        if isinstance(s, VariableDeclaration):
            tipos = [self._tipo(v) for v in s.values]
            for i, nombre in enumerate(s.names):
                tipo = self._tipo_posicional(tipos, s.values, i)
                if s.local:
                    self._declarar(nombre, tipo)
                else:
                    self._asignar(nombre, tipo)

        elif isinstance(s, Assignment):
            tipos = [self._tipo(v) for v in s.values]
            for i, nombre in enumerate(s.names):
                self._asignar(nombre, self._tipo_posicional(tipos, s.values, i))

        elif isinstance(s, IndexedAssignment):
            for v in s.values:
                self._tipo(v)
            self._tipo(s.target)

        elif isinstance(s, TargetAssignment):
            tipos = [self._tipo(v) for v in s.values]
            for i, destino in enumerate(s.targets):
                if isinstance(destino, Variable):
                    self._asignar(destino.name, self._tipo_posicional(tipos, s.values, i))
                else:
                    self._tipo(destino)

        elif isinstance(s, IfStatement):
            self._tipo(s.condition)
            with self._ambito():
                self._bloque(s.then_body)
            with self._ambito():
                self._bloque(s.else_body)

        elif isinstance(s, WhileLoop):
            self._tipo(s.condition)
            with self._ambito(es_bucle=True): 
                self._bloque(s.body)

        elif isinstance(s, RepeatLoop):
            with self._ambito(es_bucle=True):
                self._bloque(s.body)
                self._tipo(s.condition)

        elif isinstance(s, ForLoop):
            self._tipo(s.start)
            self._tipo(s.end)
            if s.step is not None:
                self._tipo(s.step)
            with self._ambito(es_bucle=True): 
                self._declarar(s.iterator, NUMERO)
                self._bloque(s.body)

        elif isinstance(s, FunctionDeclaration):
            if s.local:
                self._declarar(s.name, FUNCION)
            elif "." not in s.name and ":" not in s.name:
                self._asignar(s.name, FUNCION)
            self._cuerpo_funcion(s.parameters, s.body, es_metodo=":" in s.name)

        elif isinstance(s, ReturnStatement):
            if not self._esta_en_funcion():
                linea = getattr(s, "line", 1)
                self._error(
                    linea,
                    "CTX-RETURN",
                    "la instrucción 'return' solo es válida dentro del cuerpo de una función.",
                )
            for v in s.values:
                self._tipo(v)

        elif isinstance(s, PrintStatement):
            for a in s.arguments:
                self._tipo(a)

        elif isinstance(s, (FunctionCall, MethodCall)):
            self._tipo(s)

        elif isinstance(s, BreakStatement):
            if not self._esta_en_bucle():
                linea = getattr(s, "line", 1)
                self._error(
                    linea,
                    "CTX-BREAK",
                    "la instrucción 'break' solo se permite dentro de un bucle (for, while, repeat).",
                )
            pass

    def _cuerpo_funcion(self, parametros, cuerpo, es_metodo: bool = False) -> None:
        with self._ambito(es_funcion=True):
            for p in parametros:
                self._declarar(p, DESCONOCIDO)
            if es_metodo:
                self._declarar("self", DESCONOCIDO)
            self._bloque(cuerpo)

    @staticmethod
    def _tipo_posicional(tipos, valores, i: int) -> str:
        if i < len(tipos):
            return tipos[i]
        if valores and isinstance(valores[-1], (FunctionCall, MethodCall)):
            return DESCONOCIDO  # una llamada puede devolver varios valores
        return NIL

    # -- expresiones: devuelven el tipo inferido ----------------------------
    def _tipo(self, e) -> str:
        if isinstance(e, Literal):
            if e.value is None:
                return NIL
            if isinstance(e.value, bool):
                return BOOLEANO
            if isinstance(e.value, (int, float)):
                return NUMERO
            return CADENA

        if isinstance(e, Variable):
            return self._tipo_variable(e.name)

        if isinstance(e, ReadExpression):
            return CADENA  # io.read() devuelve texto

        if isinstance(e, UnaryExpression):
            tipo_operando = self._tipo(e.operand)
            if e.operator == "-":
                self._regla_aritmetica(e.line, "-", [("", e.operand, tipo_operando)])
                return NUMERO
            if e.operator == "not":
                return BOOLEANO
            return NUMERO  # '#'

        if isinstance(e, BinaryExpression):
            return self._binaria(e)

        if isinstance(e, (ArrayLiteral, Dictionary, Matrix)):
            self._evaluar_contenido(e)
            return TABLA

        if isinstance(e, AnonymousFunction):
            self._cuerpo_funcion(e.params, e.body)
            return FUNCION

        if isinstance(e, FunctionCall):
            if not isinstance(e.name, str):
                self._tipo(e.name)
            for a in e.arguments:
                self._tipo(a)
            return DESCONOCIDO

        if isinstance(e, MethodCall):
            self._tipo(e.target)
            for a in e.arguments:
                self._tipo(a)
            return DESCONOCIDO

        if isinstance(e, IndexExpression):
            self._tipo(e.collection)
            self._tipo(e.index)
            return DESCONOCIDO

        if isinstance(e, FieldAccess):
            self._tipo(e.target)
            return DESCONOCIDO

        return DESCONOCIDO

    def _evaluar_contenido(self, e) -> None:
        if isinstance(e, ArrayLiteral):
            for x in e.elements:
                self._tipo(x)
        elif isinstance(e, Matrix):
            for fila in e.rows:
                for x in fila:
                    self._tipo(x)
        elif isinstance(e, Dictionary):
            for campo in e.fields:
                if not isinstance(campo.key, str):
                    self._tipo(campo.key)
                self._tipo(campo.value)

    def _binaria(self, e: BinaryExpression) -> str:
        tipo_izq = self._tipo(e.left)
        tipo_der = self._tipo(e.right)
        op = e.operator
        operandos = [("izquierdo", e.left, tipo_izq), ("derecho", e.right, tipo_der)]

        if op in OPERADORES_ARITMETICOS:
            self._regla_aritmetica(e.line, op, operandos)
            return NUMERO
        if op == "..":
            self._regla_concatenacion(e.line, operandos)
            return CADENA
        if op in OPERADORES_RELACIONALES:
            return BOOLEANO
        if op in ("and", "or"):
            return unir(tipo_izq, tipo_der)
        return DESCONOCIDO

    # =======================================================================
    # INICIO APORTE VALERIA GAVELA — Operaciones permitidas
    # (compatibilidad en operaciones aritméticas y de concatenación)
    # =======================================================================
    @staticmethod
    def _describir(expr) -> str:
        """Texto corto para identificar el operando en el mensaje de error."""
        if isinstance(expr, Variable):
            return f" ('{expr.name}')"
        if isinstance(expr, Literal):
            if expr.value is None:
                return " (nil)"
            if isinstance(expr.value, bool):
                return f" ({'true' if expr.value else 'false'})"
            return f" ({expr.value})"
        return ""

    def _regla_aritmetica(self, linea: int, op: str, operandos) -> None:
        """Regla de Operadores Aritméticos.

        Los operandos de + - * / // % ^ (y del menos unario) deben ser
        estrictamente numéricos. Sumar un número con un booleano, una tabla,
        nil, una función o una cadena produce un error semántico de
        incompatibilidad. Un operando de tipo desconocido (p. ej. el resultado
        de una llamada a función) no se reporta.
        """
        invalidos = [
            (lado, expr, tipo)
            for lado, expr, tipo in operandos
            if tipo not in (NUMERO, DESCONOCIDO)
        ]
        if not invalidos:
            return
        partes = []
        for lado, expr, tipo in invalidos:
            sujeto = f"el operando {lado}" if lado else "el operando"
            partes.append(f"{sujeto}{self._describir(expr)} es de tipo {tipo}")
        self._error(
            linea,
            "OP-ARIT",
            f"operación aritmética '{op}' incompatible: {' y '.join(partes)}; "
            "se esperaban operandos numéricos.",
        )

    def _regla_concatenacion(self, linea: int, operandos) -> None:
        """Regla de Concatenación.

        El operador '..' acepta cadenas o números (los números se convierten
        de forma implícita a texto). Concatenar un booleano, nil o una función
        es un error de incompatibilidad; concatenar una tabla directamente es
        un error porque requiere el método adecuado (table.concat).
        """
        for lado, expr, tipo in operandos:
            if tipo in (CADENA, NUMERO, DESCONOCIDO):
                continue
            if tipo == TABLA:
                self._error(
                    linea,
                    "OP-CONCAT",
                    f"no se puede concatenar una tabla directamente con '..': "
                    f"el operando {lado}{self._describir(expr)} es una tabla; use table.concat().",
                )
            else:
                self._error(
                    linea,
                    "OP-CONCAT",
                    f"concatenación '..' incompatible: el operando {lado}"
                    f"{self._describir(expr)} es de tipo {tipo}; "
                    "se esperaban cadenas o números.",
                )
    # =======================================================================
    # FIN APORTE VALERIA GAVELA
    # =======================================================================


# ---------------------------------------------------------------------------
# Log y ejecución
# ---------------------------------------------------------------------------
def generar_log_semantico(
    autor: str,
    archivo: str,
    errores: list[str],
    errores_previos: list[str] | None = None,
    directorio_logs: str = "logs",
) -> str:
    """Crea logs/semantico-usuarioGit-ddmmaaaa-HHhMM.txt"""
    fecha = datetime.now().strftime("%d%m%Y-%Hh%M")
    os.makedirs(directorio_logs, exist_ok=True)
    ruta = os.path.join(directorio_logs, f"semantico-{autor}-{fecha}.txt")

    lineas = [f"ARCHIVO ANALIZADO: {archivo}", "", "REGLAS SEMÁNTICAS APLICADAS:"]
    lineas.extend(f"[{clave}] {texto}" for clave, texto in REGLAS.items())

    if errores_previos:
        lineas.extend(("", "ERRORES LÉXICOS/SINTÁCTICOS (análisis semántico omitido):"))
        lineas.extend(errores_previos)
    else:
        lineas.extend(("", "ERRORES SEMÁNTICOS:"))
        lineas.extend(errores if errores else ["Ninguno"])

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    return ruta


def main() -> int:
    ap = argparse.ArgumentParser(description="Analizador semántico de Lua (PLY).")
    ap.add_argument("archivo", help="archivo fuente Lua")
    ap.add_argument("--autor", default="Usuario", help="usuario de Git para el nombre del log")
    ap.add_argument("--logs", default="logs", help="carpeta de logs (por defecto: logs)")
    args = ap.parse_args()

    try:
        with open(args.archivo, encoding="utf-8") as f:
            fuente = f.read()
    except OSError as error:
        print(error, file=sys.stderr)
        return 1

    try:
        programa = parse(fuente)
    except ParseError as error:
        previos = str(error).splitlines()
        ruta = generar_log_semantico(args.autor, args.archivo, [], previos, args.logs)
        print(f"Log generado: {ruta}")
        print("No se puede hacer el análisis semántico: hay errores léxicos/sintácticos.", file=sys.stderr)
        print("\n".join(previos), file=sys.stderr)
        return 1

    errores = [str(e) for e in AnalizadorSemantico().analizar(programa)]
    ruta = generar_log_semantico(args.autor, args.archivo, errores, None, args.logs)
    print(f"Log generado: {ruta}")

    if errores:
        print("\n".join(errores), file=sys.stderr)
        return 1
    print("Análisis semántico correcto: sin errores.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())