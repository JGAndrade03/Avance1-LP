-- Prueba semántica de Valeria Gavela (CON errores semánticos intencionales)
-- Aporte: operaciones permitidas (compatibilidad aritmética y de concatenación)
-- Simula un inventario con matrices, funciones, bucles y reportes de texto.

local inventario = {{"lapiz", 10, 0.5}, {"cuaderno", 5, 2.25}, {"regla", 8, 1.0}}
local etiquetas = {"A", "B", "C"}
local activo = true
local descuento = nil
local iva = 0.12
local impuestos = {iva = 0.12, ice = 0.05}
local titulo = "INVENTARIO"

-- Errores directos con variables de distinto tipo
local total_iva = iva * activo                    -- número * booleano
local base = impuestos + 10                       -- tabla + número
local rebaja = 100 - descuento                    -- número - nil
local cabecera = titulo - 1                       -- cadena en aritmética
local reporte = "Impuestos: " .. impuestos        -- concatenar tabla
local estado = "Activo: " .. activo               -- concatenar booleano

-- Errores dentro de funciones (variables locales con tipo conocido)
local function valor_total(fila)
    local cantidad = fila[2] * fila[3]            -- válido: tipos desconocidos
    local pendiente = false
    local ajuste = pendiente + cantidad           -- booleano + desconocido
    return ajuste
end

local function describir(i)
    local sin_valor = nil
    return "Item " .. i .. ": " .. sin_valor      -- nil en concatenación
end

-- Errores dentro de bucles
for i = 1, #inventario do
    local linea = "Fila " .. i .. ": " .. inventario[i][1]     -- válido
    local marca = i * etiquetas                                 -- número * tabla
    local doble = -activo                                       -- menos unario sobre booleano
end

local contador = 0
while contador < 3 do
    contador = contador + 1
    local aviso = "Contador: " .. contador .. " " .. true       -- booleano
    local mal = contador .. {1, 2}                              -- tabla literal
end

repeat
    local extra = "ok"
    contador = contador - extra                                 -- cadena en aritmética
until contador <= 0

-- Propagación de tipos entre variables
local texto = "Total: " .. 10                     -- válido: texto es cadena
local numero = 5 * 2                              -- válido: numero es número
local suma_mala = texto + numero                  -- cadena + número
local lista = {1, 2, 3}
local copia = lista
local union = "Datos: " .. copia                  -- copia es tabla
local verdadero = numero > 3
local mezcla = verdadero * 2                      -- booleano (relacional) * número
local concatenado = verdadero .. "!"              -- booleano (relacional) concatenado

-- Funciones anónimas y operaciones sobre funciones
local calcular = function(x)
    return x * 2
end
local invalida = calcular + 1                     -- función + número
local imprimir = "Funcion: " .. calcular          -- función concatenada

-- Varios operandos inválidos en una misma expresión
local caos = (true + false) * {}                  -- tres operandos inválidos
local combo = "a" .. nil .. activo                -- nil y booleano

-- Un caso válido al final para comprobar que no hay falsos positivos
local final = "Listo " .. 1 .. " de " .. 2.5
local ok = 1 + 2 * 3 ^ 2 // 1 % 4