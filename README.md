# Avance1-LP

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
