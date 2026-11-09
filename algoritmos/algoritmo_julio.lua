-- Prueba de palabras reservadas y operadores del lexer.

local numero = 10 + 3 - 2 * 4 / 2 // 1 % 3 ^ 2
local texto = "Hola" .. " mundo"
local longitud = #texto
local vacio = nil
local activo = true
local terminado = false

if longitud > 0 then
    activo = true
end

if numero == 7 and not terminado then
    numero = numero + 1
elseif numero ~= 0 or numero <= 10 then
    numero = numero - 1
else
    numero = numero * 2
end

while numero < 10 do
    numero = numero + 1
end

for indice = 1, 3 do
    numero = numero / indice
end

local datos = { primero = 1, segundo = 2 }
for clave in pares(datos) do
    if clave == "segundo" then
        break
    end
end

repeat
    numero = numero + 1
until numero >= 10

function calcular(valor)
    local resultado = valor ^ 2
    return resultado
end

goto continuar
numero = numero - 1
::continuar::


-- Ejemplos básicos de bucles for:
for i = 1, 10 do 
    print(i) 
end

for contador = 10, 0, -1 do 
    print(contador) 
end


for j = (1 + 1), (5 * 2) do 
    x = 0 
end


-- Ejemplos básicos de diccionarios:


usuario = { nombre = "Juan", edad = 23 }

puntajes = { ["nivel_1"] = 100, ["nivel_2"] = 250 }

inventario = { }


-- Ejemplos básicos de funciones ánonimas:


local saludar = function() 
    print("Hola") 
end


multiplicar = function(a, b) 
    resultado = a * b 
end

procesar = function(x) 
    x = x + 1 
    print(x) 
end


--Ejemplo simple de salida por pantalla y lectura:


print("Ingresa tu edad:")


edad_usuario = io.read()

print("Tu edad es", edad_usuario)


-- Ejemplos con errores


for i = 1, 10 --falta la palabra reservada "do"
    print(i) 
end


for contador = 10 do  --falta ";"
    print(contador) 
end


usuario = { nombre = "Juan" edad = 23 }  --faltan "," que separan los elementos


configuracion = { volumen = }  -- Expresión incompleta



multiplicar = function(a, b)  --falta palabra reservada "end"
    resultado = a * b


    