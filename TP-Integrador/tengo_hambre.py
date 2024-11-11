import pygame
import threading
import random
import time
from queue import Queue

pygame.init()

# Definimos las dimensiones de la pantalla del juego
ANCHO, ALTO = 800, 600  # Ajusta el tamaño de la pantalla
pantalla = pygame.display.set_mode((ANCHO, ALTO))  # Creamos la pantalla del juego
pygame.display.set_caption("Atrapa las Comidas")  # Título de la ventana

# Definimos colores usando formato RGB
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# Velocidad de movimiento del jugador
velocidad_jugador = 10

# Variables del estado del juego
ejecutando = True  # Controla si el juego sigue ejecutándose

puntaje = 0        # Puntuación del jugador
vidas = 3          # Número de vidas del jugador
reloj = pygame.time.Clock()  # Reloj para controlar los FPS del juego
tiempo_inicial = time.time()  # Tiempo en el que inicia el juego

# Cola y lock (bloqueo) para manejar la comunicación entre hilos
cola_formas = Queue()           # Cola para las formas
lock_formas = threading.Lock()  # Lock para evitar problemas de acceso concurrente a la cola

# Evento para controlar la detención de hilos
stop_event = threading.Event()

# Listas para almacenar las selecciones de formas buenas y malas del jugador
formas_buenas_seleccionadas = []
formas_malas_seleccionadas = []

# Diccionarios para almacenar las imágenes de las formas
imagenes_formas_buenas = {}
imagenes_formas_malas = {}

# Función para cargar imágenes con manejo de errores
def cargar_imagen(ruta, escala=None):
    try:
        imagen = pygame.image.load(ruta).convert_alpha()
        if escala:
            imagen = pygame.transform.scale(imagen, escala)
        return imagen
    except pygame.error as e:
        print(f"Error al cargar la imagen '{ruta}': {e}")
        pygame.quit()
        exit()

# Cargar imágenes de las formas buenas y malas
imagenes_formas_buenas = {
    'Pizza': cargar_imagen('img/81_pizza.png'),
    'Pancho': cargar_imagen('img/54_hotdog.png'),
    'Torta': cargar_imagen('img/30_chocolatecake.png')
}

imagenes_formas_malas = {
    'Pizza': cargar_imagen('img/81_pizza.png'),
    'Pancho': cargar_imagen('img/54_hotdog.png'),
    'Torta': cargar_imagen('img/30_chocolatecake.png')
}

# Cargar imagen de fondo
imagen_fondo = cargar_imagen('img/background.png', (ANCHO, ALTO))

class Jugador:
    def __init__(self):
        self.ancho_jugador = 100
        self.alto_jugador = int(self.ancho_jugador * 1.5)
        self.imagen_derecha = cargar_imagen('img/nenita_der.png', (self.ancho_jugador, self.alto_jugador))
        self.imagen_izquierda = cargar_imagen('img/nenita_izq.png', (self.ancho_jugador, self.alto_jugador))

        self.x = ANCHO // 2 - self.ancho_jugador // 2
        self.y = ALTO - self.alto_jugador - 10
        self.direccion_jugador = 'derecha'

jugador = Jugador()

# Clase que representa una forma que cae (puede ser buena o mala)
class Forma:
    def __init__(self):
        self.tipo = random.choice(['buena', 'mala'])  # Tipo de la forma (buena o mala)
        self.tamano = random.randint(40, 80)  # Tamaño aleatorio de la forma
        self.nombre = random.choice(['Pizza', 'Pancho', 'Torta'])  # Nombre de la forma
        self.x = random.randint(0, ANCHO - self.tamano)  # Posición horizontal aleatoria
        self.y = -self.tamano  # Posición inicial (fuera de la pantalla, para caer desde arriba)
        self.velocidad = random.uniform(3, 7)  # Velocidad de caída

        # Asignamos la imagen correspondiente según el tipo (buena o mala)
        if self.tipo == 'buena':
            self.imagen = imagenes_formas_buenas[self.nombre]
        else:
            self.imagen = imagenes_formas_malas[self.nombre]
        
        # Redimensionamos la imagen al tamaño de la forma
        self.imagen = pygame.transform.scale(self.imagen, (self.tamano, self.tamano))

# Función para mostrar la pantalla de portada
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

class GeneradorFormas:
    def __init__(self, cola, lock, frecuencia_base=1.0):
        self.cola = cola
        self.lock = lock
        self.frecuencia_base = frecuencia_base

    def generar_formas(self):
        while not stop_event.is_set():
            tiempo_juego = time.time() - tiempo_inicial
            frecuencia = max(0.2, self.frecuencia_base - tiempo_juego * 0.01)
            nueva_forma = Forma()

            if nueva_forma.tipo == 'buena' and nueva_forma.nombre not in formas_buenas_seleccionadas:
                continue
            elif nueva_forma.tipo == 'mala' and nueva_forma.nombre not in formas_malas_seleccionadas:
                continue

            with self.lock:
                self.cola.put(nueva_forma)
            stop_event.wait(frecuencia)

class MovimientoFormas:
    def __init__(self, cola, lock, jugador, reloj):
        self.cola = cola
        self.lock = lock
        self.jugador = jugador
        self.reloj = reloj

    def mover_formas(self):
        global puntaje, vidas
        while not stop_event.is_set():
            self.reloj.tick(50)
            with self.lock:
                formas_actualizadas = []
                while not self.cola.empty():
                    forma = self.cola.get()
                    tiempo_juego = time.time() - tiempo_inicial
                    incremento_velocidad = tiempo_juego * 0.002
                    forma.y += forma.velocidad + incremento_velocidad

                    if forma.y > ALTO:
                        continue
                    elif (self.jugador.y < forma.y + forma.tamano and
                          self.jugador.x < forma.x + forma.tamano and
                          self.jugador.x + self.jugador.ancho_jugador > forma.x):
                        if forma.tipo == 'buena':
                            puntaje += 1
                        else:
                            vidas -= 1
                        continue

                    formas_actualizadas.append(forma)

                for forma in formas_actualizadas:
                    self.cola.put(forma)

# Función para dibujar una forma en la pantalla
def dibujar_forma(forma):
    pantalla.blit(forma.imagen, (forma.x, forma.y))  # Dibujamos la imagen en la posición de la forma

# Mostrar la portada antes de continuar al menú de opciones
mostrar_portada()

# Mostramos el menú y obtenemos las selecciones del jugador
formas_buenas_seleccionadas, formas_malas_seleccionadas = mostrar_menu()

# Crear instancias del generador y del movimiento de formas
generador_formas = GeneradorFormas(cola_formas, lock_formas)
movimiento_formas = MovimientoFormas(cola_formas, lock_formas, jugador, reloj)

# Iniciar los hilos para generar y mover las formas
hilo_generador = threading.Thread(target=generador_formas.generar_formas)
hilo_movedor = threading.Thread(target=movimiento_formas.mover_formas)
hilo_generador.start()
hilo_movedor.start()

# Bucle principal del juego
while ejecutando:
    reloj.tick(60)  # Controlamos el juego a 60 FPS
    pantalla.blit(imagen_fondo, (0, 0))  # Dibujamos la imagen de fondo

    # Manejamos los eventos del juego
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:  # Si el jugador cierra la ventana
            ejecutando = False
            stop_event.set()

    # Manejo del movimiento del jugador
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] and jugador.x - velocidad_jugador >= 0:
        jugador.x -= velocidad_jugador  # Movemos al jugador a la izquierda
        jugador.direccion_jugador = 'izquierda'
    elif teclas[pygame.K_RIGHT] and jugador.x + velocidad_jugador <= ANCHO - jugador.ancho_jugador:
        jugador.x += velocidad_jugador  # Movemos al jugador a la derecha
        jugador.direccion_jugador = 'derecha'

    # Dibujamos al jugador según la dirección
    if jugador.direccion_jugador == 'derecha':
        pantalla.blit(jugador.imagen_derecha, (jugador.x, jugador.y))
    else:
        pantalla.blit(jugador.imagen_izquierda, (jugador.x, jugador.y))

    # Dibujamos las formas
    with lock_formas:
        formas_a_dibujar = list(cola_formas.queue)
    for forma in formas_a_dibujar:
        dibujar_forma(forma)

    # Mostramos el puntaje y las vidas
    fuente = pygame.font.SysFont(None, 36)
    texto_puntaje = fuente.render(f"Puntaje: {puntaje}", True, NEGRO)
    texto_vidas = fuente.render(f"Vidas: {vidas}", True, NEGRO)
    pantalla.blit(texto_puntaje, (10, 10))
    pantalla.blit(texto_vidas, (10, 50))

    # Verificamos si el jugador ha perdido todas las vidas
    if vidas <= 0:
        fuente_game_over = pygame.font.SysFont(None, 72)
        texto_game_over = fuente_game_over.render("¡Juego Terminado!", True, NEGRO)
        pantalla.blit(texto_game_over, (ANCHO // 2 - texto_game_over.get_width() // 2, ALTO // 2))
        pygame.display.flip()
        time.sleep(3)
        ejecutando = False
        break

    # Actualizamos la pantalla
    pygame.display.flip()

# Esperar a que los hilos terminen antes de cerrar
stop_event.set()
hilo_generador.join()
hilo_movedor.join()

# Mostrar la pantalla de fin del juego
accion = mostrar_pantalla_fin()
if accion == "salir":
    pygame.quit()
    exit(0)
elif accion == "volver":
    mostrar_menu()

# Cerramos Pygame
pygame.quit()