-- Algoritmo sintactico de Julio: calcula el promedio de tres calificaciones.

local calificacion1 = 8
local calificacion2 = 9
local calificacion3 = 7
local total = 0

function sumarCalificacion(valor)
    return total + valor
end

total = sumarCalificacion(calificacion1)
total = sumarCalificacion(calificacion2)
total = sumarCalificacion(calificacion3)

local promedio = total / 3
local resultado = "Reprobado"

if promedio >= 7 then
    resultado = "Aprobado"
else
    resultado = "Reprobado"
end

print("Promedio:", promedio)
print("Resultado:", resultado)