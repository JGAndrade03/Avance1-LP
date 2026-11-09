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
