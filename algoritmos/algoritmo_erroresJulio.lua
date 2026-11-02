-- Prueba de errores léxicos: @, $, ? y ` no son tokens definidos.

local numero = 10
local texto = "prueba"

numero = numero @ 2
texto = texto $ " con error"
local resultado = numero ? 5
local plantilla = `texto sin comillas`

if numero >= 0 then
    numero = numero + 1
end
