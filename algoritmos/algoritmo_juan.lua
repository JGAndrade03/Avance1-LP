

configuracion_juego = { 
    resolucion = "1080p", 
    fps = 60,
    modo_ventana = false
};

inventario_personaje = { 
    armas = { espada_corta, arco_largo }, 
    pociones = { vida = 5, mana = 2 }
};


estadisticas_base = {
    [1] = 100,
    [2] = 50 @nivel, 
    [3] = 25
};

oro_total = 1500 $; 


mapa_juego.coordenadas.x, mapa_juego.coordenadas.y = (1024), (768);
posicion_actual[1] = mapa_juego.coordenadas.x;


sistema_batalla:iniciar_combate(inventario_personaje, estadisticas_base, mapa_juego.coordenadas);

personaje.metodo_secreto!(inventario_personaje.armas[1] & estadisticas_base[2]); 

recompensas = {
    cofre_oro = { x = 10, y = 20 },
    cofre_plata = { x = 30, y = 40 }
};

jugador_principal:abrir(recompensas.cofre_oro); ? 

end
