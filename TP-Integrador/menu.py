import pygame
import time 
from utils import imagenes_personajes
from globals import ALTO, ANCHO, pantalla, reloj, BLANCO, NEGRO


#  Función para mostrar la pantalla de portada
def mostrar_portada():
    """Muestra la pantalla de portada con un botón para iniciar el juego."""
    portada_activa = True
    fuente_titulo = pygame.font.SysFont(None, 72)
    fuente_boton = pygame.font.SysFont(None, 48)
    ancho_boton = 200
    alto_boton = 80

    # Posición del botón "Jugar"
    x_boton = (ANCHO // 2) - (ancho_boton // 2)
    y_boton = (ALTO // 2) - (alto_boton // 2)

    boton_jugar = pygame.Rect(x_boton, y_boton, ancho_boton, alto_boton)

    while portada_activa:
        pantalla.fill(BLANCO)  # Fondo blanco
        texto_titulo = fuente_titulo.render("Atrapa las Comidas", True, NEGRO)
        pantalla.blit(texto_titulo, (ANCHO // 2 - texto_titulo.get_width() // 2, 100))

        # Dibujar el botón "Jugar"
        pygame.draw.rect(pantalla, (0, 150, 0), boton_jugar)
        texto_boton = fuente_boton.render("Jugar", True, BLANCO)
        texto_boton_rect = texto_boton.get_rect(center=boton_jugar.center)
        pantalla.blit(texto_boton, texto_boton_rect)

        # Manejo de eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_jugar.collidepoint(evento.pos):
                    portada_activa = False

        pygame.display.flip()
        reloj.tick(30)

# Función para mostrar la pantalla de final del juego
def mostrar_pantalla_fin():
    """Muestra la pantalla final del juego con las opciones de 'Volver a Jugar' o 'Salir'."""
    fin_activo = True
    fuente_titulo = pygame.font.SysFont(None, 72)
    fuente_boton = pygame.font.SysFont(None, 48)
    ancho_boton = 200
    alto_boton = 80

    # Posiciones de los botones
    x_boton_volver = (ANCHO // 2) - (ancho_boton // 2)
    y_boton_volver = (ALTO // 2) - (alto_boton) - 20

    x_boton_salir = (ANCHO // 2) - (ancho_boton // 2)
    y_boton_salir = (ALTO // 2) + 20

    boton_volver = pygame.Rect(x_boton_volver, y_boton_volver, ancho_boton, alto_boton)
    boton_salir = pygame.Rect(x_boton_salir, y_boton_salir, ancho_boton, alto_boton)

    while fin_activo:
        pantalla.fill(BLANCO)  # Fondo blanco
        texto_titulo = fuente_titulo.render("¡Juego Terminado!", True, NEGRO)
        pantalla.blit(texto_titulo, (ANCHO // 2 - texto_titulo.get_width() // 2, 100))

        # Dibujar el botón "Volver a Jugar"
        pygame.draw.rect(pantalla, (0, 150, 0), boton_volver)
        texto_boton_volver = fuente_boton.render("Volver a Jugar", True, BLANCO)
        texto_boton_volver_rect = texto_boton_volver.get_rect(center=boton_volver.center)
        pantalla.blit(texto_boton_volver, texto_boton_volver_rect)

        # Dibujar el botón "Salir"
        pygame.draw.rect(pantalla, (150, 0, 0), boton_salir)
        texto_boton_salir = fuente_boton.render("Salir", True, BLANCO)
        texto_boton_salir_rect = texto_boton_salir.get_rect(center=boton_salir.center)
        pantalla.blit(texto_boton_salir, texto_boton_salir_rect)

        # Manejo de eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_volver.collidepoint(evento.pos):
                    return "volver"
                elif boton_salir.collidepoint(evento.pos):
                    return "salir"

        pygame.display.flip()
        reloj.tick(30)


# Función para mostrar el menú de selección
def mostrar_menu():
    """Muestra el menú de selección de comidas buenas y malas.
    """
    while True:
        menu_activo = True
        opciones = ['Pizza', 'Pancho', 'Torta']
        seleccionadas_buenas = []
        seleccionadas_malas = []
        fuente = pygame.font.SysFont(None, 36)
        ancho_boton = 200
        alto_boton = 50

        # Calculamos la posición 'x' centrada para los botones de las formas buenas y malas
        x_centrada_buena = (ANCHO // 4) - (ancho_boton // 2)
        x_centrada_mala = (3 * ANCHO // 4) - (ancho_boton // 2)

        # Definimos las posiciones y tamaños de los botones
        botones_buenas = [
            (pygame.Rect(x_centrada_buena, 200 + idx * 60, ancho_boton, alto_boton), opcion)
            for idx, opcion in enumerate(opciones)
        ]
        botones_malas = [
            (pygame.Rect(x_centrada_mala, 200 + idx * 60, ancho_boton, alto_boton), opcion)
            for idx, opcion in enumerate(opciones)
        ]

        while menu_activo:
            pantalla.fill(BLANCO)
            texto_titulo = fuente.render("Selecciona las comidas buenas y malas", True, NEGRO)
            pantalla.blit(texto_titulo, (ANCHO // 2 - texto_titulo.get_width() // 2, 50))

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    # Verificar clic en botones de formas buenas
                    manejar_seleccion(pos, botones_buenas, seleccionadas_buenas)
                    # Verificar clic en botones de formas malas
                    manejar_seleccion(pos, botones_malas, seleccionadas_malas)
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                    menu_activo = False

            # Dibujar los botones y mostrar el texto correspondiente
            mostrar_botones(botones_buenas, seleccionadas_buenas, "Comidas Buenas:", x_centrada_buena, 150, (0, 200, 0))
            mostrar_botones(botones_malas, seleccionadas_malas, "Comidas Malas:", x_centrada_mala, 150, (200, 0, 0))

            # Mostrar instrucciones
            instrucciones = [
                "Haz clic en las comidas para seleccionar/deseleccionar.",
                "Presiona ENTER para comenzar el juego."
            ]
            for idx, instruccion in enumerate(instrucciones):
                texto_instruccion = fuente.render(instruccion, True, NEGRO)
                pantalla.blit(texto_instruccion, (ANCHO // 2 - texto_instruccion.get_width() // 2, 450 + idx * 30))

            pygame.display.flip()
            reloj.tick(30)

        # Validar que al menos haya una forma buena y una mala seleccionada
        if seleccionadas_buenas and seleccionadas_malas:
            return seleccionadas_buenas, seleccionadas_malas
        else:
            # Mostrar mensaje de error si no se seleccionó ninguna opción válida
            fuente_error = pygame.font.SysFont(None, 48)
            texto_error = fuente_error.render("Debe seleccionar al menos una forma buena y una forma mala.", True, (255, 0, 0)) # Ajustar para que se vea bien
            pantalla.blit(texto_error, (ANCHO // 2 - texto_error.get_width() // 2, ALTO // 2))
            pygame.display.flip()
            time.sleep(2)  # Pausa para que el usuario vea el mensaje

# Función para manejar la selección de opciones del menú
def manejar_seleccion(pos, botones, seleccionadas):
    """Maneja la selección y deselección de opciones del menú.
    """
    for boton, opcion in botones:
        if boton.collidepoint(pos):
            if opcion not in seleccionadas:
                seleccionadas.append(opcion)
            else:
                seleccionadas.remove(opcion)

# Función para mostrar los botones en pantalla
def mostrar_botones(botones, seleccionadas, titulo, x, y, color_seleccionado):
    """Dibuja los botones y muestra el título correspondiente.
    """
    fuente = pygame.font.SysFont(None, 36)
    texto = fuente.render(titulo, True, NEGRO)
    pantalla.blit(texto, (x, y))
    for boton, opcion in botones:
        seleccionado = opcion in seleccionadas
        color_boton = color_seleccionado if seleccionado else (200, 200, 200)
        pygame.draw.rect(pantalla, color_boton, boton)
        texto_opcion = fuente.render(opcion, True, NEGRO)
        texto_rect = texto_opcion.get_rect(center=boton.center)
        pantalla.blit(texto_opcion, texto_rect)

def mostrar_seleccion_personaje():
    """Muestra el menú para seleccionar el personaje del jugador."""
    seleccion_activa = True
    fuente_titulo = pygame.font.SysFont(None, 72)
    fuente_boton = pygame.font.SysFont(None, 36)
    ancho_boton = 150
    alto_boton = 200

    # Posiciones iniciales de los botones de personajes
    espaciado = 50
    x_inicial = (ANCHO - (len(imagenes_personajes) * (ancho_boton + espaciado) - espaciado)) // 2
    y_boton = ALTO // 2 - alto_boton // 2

    botones_personajes = []

    # Crear rectángulos para cada personaje
    for idx, nombre_personaje in enumerate(imagenes_personajes.keys()):
        x_boton = x_inicial + idx * (ancho_boton + espaciado)
        boton = pygame.Rect(x_boton, y_boton, ancho_boton, alto_boton)
        botones_personajes.append((boton, nombre_personaje))

    personaje_seleccionado = None

    while seleccion_activa:
        pantalla.fill(BLANCO)  # Fondo blanco
        texto_titulo = fuente_titulo.render("Selecciona tu Personaje", True, NEGRO)
        pantalla.blit(texto_titulo, (ANCHO // 2 - texto_titulo.get_width() // 2, 50))

        # Dibujar los botones de personajes
        for boton, nombre_personaje in botones_personajes:
            pygame.draw.rect(pantalla, (200, 200, 200), boton)
            imagen_personaje = imagenes_personajes[nombre_personaje]['derecha']
            pantalla.blit(imagen_personaje, (boton.x, boton.y))
            texto_nombre = fuente_boton.render(nombre_personaje, True, NEGRO)
            pantalla.blit(texto_nombre, (boton.x + (ancho_boton // 2) - texto_nombre.get_width() // 2, boton.y + alto_boton))

        # Manejo de eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for boton, nombre_personaje in botones_personajes:
                    if boton.collidepoint(pos):
                        personaje_seleccionado = nombre_personaje
                        seleccion_activa = False

        pygame.display.flip()
        reloj.tick(30)

    return personaje_seleccionado

