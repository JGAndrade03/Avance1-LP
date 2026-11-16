-- Prueba semántica de Valeria Gavela (SIN errores semánticos)
-- Aporte: operaciones permitidas (compatibilidad aritmética y de concatenación)
-- Simula un sistema de notas con matrices, funciones, bucles y reportes de texto.

-- Datos: matriz de notas (filas = estudiantes, columnas = parciales)
local notas = {{8, 9.5, 7}, {6, 7, 5.5}, {10, 9, 9.5}}
local nombres = {"Ana", "Luis", "Eva"}
local pesos = {0.3, 0.3, 0.4}
local aprobado_min = 7
local titulo = "REPORTE " .. 2026 .. "-II"

-- Función con aritmética sobre parámetros y elementos de tabla (tipos desconocidos)
local function promedio(fila)
    local suma = 0
    for j = 1, #fila do
        suma = suma + fila[j] * pesos[j]
    end
    return suma
end

-- Aritmética mixta: enteros, flotantes, hexadecimales, potencias, módulo y división entera
local function normalizar(valor, maximo)
    local base = (valor / maximo) * 100
    local ajuste = base // 1 + base % 1 ^ 2
    return -ajuste + 0xFF - 0xFF
end

-- Funciones que devuelven cadenas armadas con números
local function etiqueta(i, prom)
    local estado = "reprobado"
    if prom >= aprobado_min then
        estado = "aprobado"
    end
    return i .. ". " .. nombres[i] .. " -> " .. prom .. " (" .. estado .. ")"
end

print(titulo)
local acumulado = 0
local mejor = 0
local indice_mejor = 1
for i = 1, #notas do
    local p = promedio(notas[i])
    acumulado = acumulado + p
    if p > mejor then
        mejor = p
        indice_mejor = i
    end
    print(etiqueta(i, p))
end

local general = acumulado / #notas
print("Promedio general: " .. general)
print("Mejor: " .. nombres[indice_mejor] .. " con " .. mejor)

-- Bucles while y repeat con contadores y conversión de lectura
local intentos = 0
local limite = 3
while intentos < limite do
    intentos = intentos + 1
    local dato = tonumber(io.read())
    notas[1][intentos] = dato * 1.1
end

local ronda = 0
repeat
    ronda = ronda + 1
    local mensaje = "Ronda " .. ronda .. " de " .. limite
    print(mensaje)
until ronda >= limite

-- Tabla con campos y métodos: la aritmética sobre campos no se reporta (tipo desconocido)
local cuenta = {saldo = 100, interes = 0.05}
function cuenta.proyectar(anios)
    return cuenta.saldo * (1 + cuenta.interes) ^ anios
end
function cuenta:depositar(monto)
    self.saldo = self.saldo + monto
    return "Nuevo saldo: " .. self.saldo
end
cuenta:depositar(50)
local futuro = cuenta.proyectar(3) + 1

-- Variable que cambia de tipo en una rama: se vuelve desconocida y no se reporta
local resultado = 0
if general > 8 then
    resultado = "excelente"
else
    resultado = general * 10
end
local salida = "Resultado: " .. resultado

-- Funciones anónimas y cierres
local multiplicador = function(factor)
    return function(x)
        return x * factor
    end
end
local doble = multiplicador(2)
local valor_doble = doble(21) + 1

-- Expresiones booleanas combinadas con aritmética
local bono = (general > 8 and 10 or 0) + 5
local valido = general >= 0 and general <= 10 and not (bono < 0)
print("Bono: " .. bono .. " valido: " .. tostring(valido))