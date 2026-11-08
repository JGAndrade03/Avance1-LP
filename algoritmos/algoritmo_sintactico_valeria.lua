-- Prueba sintáctica de Valeria Gavela (sin errores)
-- Aporte: expresiones booleanas, matriz, while/repeat/break, funciones, campos y métodos

-- Expresiones booleanas relacionales y lógicas
local a, b = 10, 5
local mayor = a > b
local iguales = a == b
local distintos = a ~= b
local rango = a >= 1 and a <= 100
local alguno = (a < b) or not (b <= 0)
local compleja = (a + 2 * b > 15) and not (a == b) or false

-- Matriz (tabla de tablas)
local matriz = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}
matriz[2][3] = 60
local elemento = matriz[1][2] + matriz[3][3]
local filas = #matriz
local es_grande = matriz[2][3] >= 50 and matriz[1][1] ~= 0
local texto = "Filas: " .. filas

-- Acceso y asignación a campos
local persona = {nombre = "Valeria", edad = 20}
persona.edad = persona.edad + 1
local nombre = persona.nombre
local copia = {}
copia.nombre, copia.edad = persona.nombre, persona.edad

-- Definición de funciones y llamadas
function calcularArea(base, altura)
    return (base * altura) / 2
end
area_triangulo = calcularArea(10, 5)

local function esMayor(x, y)
    return x > y and x ~= y
end
local resultado = esMayor(a, b)

function saludar()
    print("Hola")
end
saludar()

-- Funciones como campos y métodos
local calc = {}
function calc.sumar(x, y)
    return x + y
end
function calc:limpiar()
    return 0
end
function calc.avanzado.dividir(x, y)
    return x / y
end
local suma = calc.sumar(3, 4)
calc:limpiar()
io.write("fin")
local compuesta = obtenerFuncion(1)(2)
local desde_matriz = tabla_funciones[1](5)

-- Estructuras de control: while, repeat-until, break
local i = 1
while i <= 3 and not (i == 10) do
    matriz[i][1] = i * 2
    i = i + 1
end

while a > b do
    a = a - 1
    if a == 7 then
        break
    end
    print(a, calcularArea(a, b))
end

local n = 0
repeat
    n = n + 1
until n >= 3 or matriz[1][1] == 2