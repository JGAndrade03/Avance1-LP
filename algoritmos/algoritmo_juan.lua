
inventario_personaje = { 
    armas = { espada_corta, arco_largo }, 
    pociones = { vida = 5, mana = 2 }
};

estadisticas_base = {
    [1] = 100,
    [2] = 50,
    [3] = 25
};

mapa_juego.coordenadas.x, mapa_juego.coordenadas.y = (1024), (768);

sistema_batalla:iniciar_combate(inventario_personaje, estadisticas_base, mapa_juego.coordenadas);

personaje.metodo_secreto(inventario_personaje.armas[1], estadisticas_base[2]);

end
