-- Comentario de una línea
--[[ Comentario
     multilínea ]]

local entero = 42
local flotante = 3.14
local cientifico = 2e5
local sin_cero = .5
local hexa = 0xFF
local hexa2 = 0x1a2B
local saludo = "Hola, mundo"
local otro = 'Lua \'simple\''
local larga = [[Cadena
larga de varias líneas]]
local activo = true
local inactivo = false
local nada = nil

--[[ otro bloque
con varias líneas ]]
local suma = entero + flotante -- comentario al final
-- Errores léxicos
local h = 0xZZ
local x = "sin cerrar
local y = 'comillas distintas"
local z = 5

--[[ comentario que nunca se cierra
local w = 10