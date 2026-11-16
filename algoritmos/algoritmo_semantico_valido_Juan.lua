
local LIMITE <const> = 50
local mensaje = "Procesamiento de datos semánticos"

local function calcularPromedio(suma, total)
    if total == 0 then
        return 0
    end
    local resultado = suma / total
    return resultado
end

local function evaluarMatriz()
    local sumaTotal = 0
    local contador = 0
    
    
    for i = 1, 10 do
        if i > 8 then
            break
        end
        
    
        local valor = i * 2 + 5
        sumaTotal = sumaTotal + valor
        contador = contador + 1
    end
    
    
    local j = 0
    while j < 5 do
        j = j + 1
        if j == 4 then
            break
        end
    end
    
    
    local k = 0
    repeat
        k = k + 1
        if k == 3 then
            break
        end
    until k >= 5
    
    local prom = calcularPromedio(sumaTotal, contador)
    local reporte = mensaje .. " - Promedio final: " .. prom
    print(reporte)
    
    return prom
end

local resultadoFinal = evaluarMatriz()
print(resultadoFinal)