# Avance1-LP

## Interfaz gráfica

Desde la raíz del proyecto, instala la dependencia PLY y ejecuta:

```sh
python -m pip install ply
python main.py
```

La interfaz está construida con Tkinter, incluido normalmente con Python. Si
Tkinter no está disponible en tu instalación, instálalo o habilítalo para tu
versión de Python.

## Analizador léxico

Desde la raíz del proyecto, ejecuta:

```sh
python lexer.py
```

El programa analiza los archivos de prueba definidos al final de `lexer.py`
(`algoritmos/algoritmo_julio.lua`, `algoritmos/algoritmo_erroresJulio.lua`,
`algoritmos/algoritmo_valeria.lua` y `algoritmos/algoritmo_juan.lua`). Para
analizar otro archivo, agrega una llamada a `probar_lexer("ruta/al/archivo.lua",
"NombreAutor")` en esa sección. Por cada archivo analizado genera un log en
`logs/` con los tokens reconocidos y los errores léxicos.

## Analizador sintáctico

El analizador en `sintactico.py` valida declaraciones locales, asignaciones
globales por defecto y expresiones aritméticas con paréntesis y precedencia.
También acepta declaraciones locales sin inicializar y listas de variables y
valores separados por comas.

El proyecto utiliza PLY (`python -m pip install ply`).

```sh
python sintactico.py archivo.lua
python sintactico.py archivo.lua --autor Nombre
```

Cada ejecución del analizador sintáctico genera un log en `logs/` con las
instrucciones reconocidas y los errores de análisis. El nombre del archivo
incluye el autor indicado con `--autor` (por defecto, `Usuario`) y la fecha.

## Analizador semántico

Desde la raíz del proyecto, ejecuta el analizador indicando el archivo Lua:

```sh
python semantico.py algoritmos/algoritmo_semantico_valido_Juan.lua
```

Puedes indicar el autor para el nombre del log y cambiar la carpeta de logs
(por defecto, `logs/`):

```sh
python semantico.py algoritmos/algoritmo_semantico_valido_Juan.lua --autor Nombre
python semantico.py algoritmos/algoritmo_semantico_valido_Juan.lua --logs otra_carpeta
```

El analizador genera un log con el resultado del análisis semántico.
