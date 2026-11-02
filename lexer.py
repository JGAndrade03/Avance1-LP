import ply.lex as lex
import datetime
import os

#Funcionalidad de palabras reservadas y operadores (Julio)
#
#
#---------------------------------------------------------



# Funcionalidad de tipos de datos primitivos y comentarios (Valeria)
#
#
#------------------------------------------------------------------



# Funcionalidad de Variables, Delimitadores y Tablas (Juan Andrés Gualotuña)


tokens_juan = [ 'ID', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'COMMA', 'SEMICOLON', 'DOT', 'COLON', 'END_DELIM']

#Reglas de delimitadores:

t_LAPAREN =     r'\('
t_RPAREN =      r'\)'
t_LBRACE =      r'\{'
t_RBRACE =      r'\}'
t_LBRACKET =    r'\['
t_LAPAREN =     r'\]'
t_COMMA =       r','
t_SEMICOLON =   r';'
t_DOT =         r'\.'
t_COLON =       r':'

#Reglas para identificadores y validar palabras reservadas:

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'  #Uso de expresiones regulares
    
    if t.value == 'end':
        t.type = 'END_DELIM'
    else:
        t.type = reversed.get(t.value, 'ID')  #Uso del diccionario principal creado por (Julio)
        
        
    return t


#Reglas globales:

t_ignore = '\t'

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
        
        file2.write("\n ERRORES LÉXICOS: ")
        for e in lexer.errores:
            file2.write(e+"\n")
    
    print(f"Log generado: {ruta_log}")
    
    
# Uso de algoritmo por interante

if __name__ == '__main__':
    
    #Ejecución de pruebas individuales:
    
    #algoritmo julio: 
    #algoritmo valeria:
    #algoritmo juan:
    
    pass