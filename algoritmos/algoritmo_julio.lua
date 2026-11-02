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
