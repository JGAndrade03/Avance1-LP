import ply.lex as lex
import datetime
import os

#Funcionalidad de palabras reservadas y operadores (Julio)

reserved = {
    'if': 'IF',
    'then': 'THEN',
    'elseif': 'ELSEIF',
    'else': 'ELSE',
    'end': 'END_DELIM',
    'while': 'WHILE',
    'do': 'DO',
    'for': 'FOR',
    'in': 'IN',
    'repeat': 'REPEAT',
    'until': 'UNTIL',
    'break': 'BREAK',
    'function': 'FUNCTION',
    'return': 'RETURN',
    'local': 'LOCAL',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'true': 'TRUE',
    'false': 'FALSE',
    'nil': 'NIL',
    'goto': 'GOTO',
}

tokens_julio = [
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'FLOOR_DIVIDE', 'MODULO',
    'POWER', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE', 'ASSIGN', 'CONCAT',
    'LENGTH',
]

t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_FLOOR_DIVIDE = r'//'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_POWER = r'\^'
t_EQ = r'=='
t_NE = r'~='
t_LE = r'<='
t_LT = r'<'
t_GE = r'>='
t_GT = r'>'
t_ASSIGN = r'='
t_CONCAT = r'\.\.'
t_LENGTH = r'\#'

#---------------------------------------------------------



# Funcionalidad de tipos de datos primitivos y comentarios (Valeria)
tokens_valeria = [
    'FLOTANTE', 'ENTERO', 'CADENA','HEXADECIMAL'
]

# Regla para comentarios multilínea (debe ir antes que el de una línea)
def t_COMMENT_BLOCK(t):
    r'--\[\[[\s\S]*?\]\]'
    t.lexer.lineno += t.value.count('\n')   # mantener el conteo de líneas
    pass # Se ignora, no devuelve token

# Regla para comentarios de una sola línea
def t_COMMENT_LINE(t):
    r'--.*'
    pass # Se ignora, no devuelve token

# Tipos de datos primitivos (Valeria)
def t_HEXADECIMAL(t):
    r'0[xX][0-9a-fA-F]+'
    t.value = int(t.value, 16)
    return t

def t_FLOTANTE(t):
    r'(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+'
    t.value = float(t.value)
    return t

def t_ENTERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_CADENA(t):
    r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'|\[\[[\s\S]*?\]\]'
    t.value = str(t.value)
    return t

#------------------------------------------------------------------



# Funcionalidad de Variables, Delimitadores y Tablas (Juan Andrés Gualotuña)


tokens_juan = [ 'ID', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET', 'COMMA', 'SEMICOLON', 'DOT', 'COLON', 'END_DELIM']

tokens = list(dict.fromkeys(
    list(reserved.values()) + tokens_julio + tokens_juan + tokens_valeria
))

#Reglas de delimitadores:

t_LPAREN =      r'\('
t_RPAREN =      r'\)'
t_LBRACE =      r'\{'
t_RBRACE =      r'\}'
t_LBRACKET =    r'\['
t_RBRACKET =    r'\]'
t_COMMA =       r','
t_SEMICOLON =   r';'
t_DOT =         r'\.'
t_COLON =       r':'

#Reglas para identificadores y validar palabras reservadas:

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'  #Uso de expresiones regulares

    t.type = reserved.get(t.value, 'ID')

    return t


#Reglas globales:

t_ignore = ' \t\r'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    
def t_error(t):
    mensaje = f"Error léxico en línea {t.lexer.lineno}: carácter no reconocido '{t.value[0]}'"
    
    t.lexer.errores.append(mensaje)
    t.lexer.skip(1)

lexer = lex.lex()
lexer.errores = []



#Función de prueba:


def probar_lexer(archivo_prueba, autor):
    with open(archivo_prueba, 'r', encoding='utf-8') as file:
        data = file.read()
    
    lexer.lineno = 1        # reiniciar entre pruebas
    lexer.errores = []
    lexer.input(data)
    
    logs = []
    
    while True:
        tok = lexer.token()
        
        if not tok:
            break
        logs.append(f"Linea {tok.lineno} \t Tipo: {tok.type} \t Valor: {tok.value}")
        
    ahora = datetime.datetime.now()
    
    date = ahora.strftime("%d-%m-%Y-%Hh%M")
    
    log_name = f"lexico-{autor}-{date}.txt"
    
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    ruta_log = os.path.join('logs', log_name)
    
    with open(ruta_log, 'w', encoding='utf-8') as file2:
        
        file2.write("TOKENS RECONOCIDOS:\n")
        for linea in logs:
            file2.write(linea + "\n")

        file2.write("\nERRORES LÉXICOS:\n")
        if lexer.errores:
            for e in lexer.errores:
                file2.write(e + "\n")
        else:
            file2.write("Ninguno\n")
    
    print(f"Log generado: {ruta_log}")
    
    
# Uso de algoritmo por integrante

if __name__ == '__main__':
    
    #Ejecución de pruebas individuales:
    
    #algoritmo julio:
    probar_lexer('algoritmos/algoritmo_julio.lua', 'JulioLlerena')
    probar_lexer('algoritmos/algoritmo_erroresJulio.lua', 'JulioLlerena')
    #algoritmo valeria:
    probar_lexer('algoritmos/algoritmo_valeria.lua', 'ValeriaGavela')
    #algoritmo juan:
    probar_lexer('algoritmos/algoritmo_juan.lua','JuanGualotuna')
    
    pass