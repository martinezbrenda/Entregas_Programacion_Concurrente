# Importamos las librerías necesarias
import pygame          # Pygame es una biblioteca para desarrollo de videojuegos en Python
import threading       # Para crear y manejar múltiples hilos
import random          # Para generar valores aleatorios
import time            # Para trabajar con funciones de tiempo
from queue import Queue  # Cola para la comunicación entre hilos

# Iniciamos Pygame
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

# Listas para almacenar las selecciones de formas buenas y malas del jugador
formas_buenas_seleccionadas = []
formas_malas_seleccionadas = []

# Diccionarios para almacenar las imágenes de las formas
imagenes_formas_buenas = {}
imagenes_formas_malas = {}

# Intentamos cargar las imágenes de las formas buenas
try:
    imagenes_formas_buenas['Pizza'] = pygame.image.load('img/81_pizza.png')
    imagenes_formas_buenas['Pancho'] = pygame.image.load('img/54_hotdog.png')
    imagenes_formas_buenas['Torta'] = pygame.image.load('img/30_chocolatecake.png')

    imagenes_formas_malas['Pizza'] = pygame.image.load('img/81_pizza.png')
    imagenes_formas_malas['Pancho'] = pygame.image.load('img/54_hotdog.png')
    imagenes_formas_malas['Torta'] = pygame.image.load('img/30_chocolatecake.png')
except pygame.error as e:
    # Si ocurre un error al cargar las imágenes, mostramos el error y salimos
    print(f"Error al cargar imágenes de las formas: {e}")
    pygame.quit()
    exit()

# Cargamos las imágenes del jugador
try:
    imagen_jugador_derecha = pygame.image.load('img/nenita_der.png').convert_alpha()
    imagen_jugador_izquierda = pygame.image.load('img/nenita_izq.png').convert_alpha()

    # Escalamos las imágenes del jugador al tamaño deseado
    ancho_jugador = 100
    alto_jugador = int(imagen_jugador_derecha.get_height() * (ancho_jugador / imagen_jugador_derecha.get_width()))

    imagen_jugador_derecha = pygame.transform.scale(imagen_jugador_derecha, (ancho_jugador, alto_jugador))
    imagen_jugador_izquierda = pygame.transform.scale(imagen_jugador_izquierda, (ancho_jugador, alto_jugador))
except pygame.error as e:
    # Si ocurre un error al cargar las imágenes del jugador, mostramos el error y salimos
    print(f"Error al cargar las imágenes del jugador: {e}")
    pygame.quit()
    exit()

# Posición inicial del jugador
x_jugador = ANCHO // 2 - ancho_jugador // 2  # Posición horizontal centrada
y_jugador = ALTO - alto_jugador - 10  # Posición vertical, cerca del borde inferior

# Dirección inicial del jugador ('izquierda' o 'derecha')
direccion_jugador = 'derecha'

# Intentamos cargar la imagen de fondo
try:
    imagen_fondo = pygame.image.load('img/background.png').convert()
    # Escalamos la imagen de fondo al tamaño de la pantalla
    imagen_fondo = pygame.transform.scale(imagen_fondo, (ANCHO, ALTO))
except pygame.error as e:
    # Si ocurre un error al cargar la imagen de fondo, mostramos el error y salimos
    print(f"Error al cargar la imagen de fondo: {e}")
    pygame.quit()
    exit()


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

# Función para mostrar el menú donde el jugador selecciona las formas buenas y malas
def mostrar_menu():
    menu_activo = True  # Variable para controlar si el menú sigue activo
    opciones = ['Pizza', 'Pancho', 'Torta']  # Opciones disponibles para seleccionar
    seleccionadas_buenas = []  # Lista para almacenar las formas buenas seleccionadas
    seleccionadas_malas = []  # Lista para almacenar las formas malas seleccionadas
    fuente = pygame.font.SysFont(None, 36)  # Fuente para el texto del menú
    ancho_boton = 200  # Ancho de los botones del menú
    alto_boton = 50  # Alto de los botones del menú

    # Calculamos la posición 'x' centrada para los botones de las formas buenas y malas
    x_centrada_buena = (ANCHO // 4) - (ancho_boton // 2)  # Mitad izquierda de la pantalla
    x_centrada_mala = (3 * ANCHO // 4) - (ancho_boton // 2)  # Mitad derecha de la pantalla

    # Definimos las posiciones y tamaños de los botones
    botones_buenas = []
    botones_malas = []
    for idx, opcion in enumerate(opciones):
        # Definimos los rectángulos de los botones de las formas buenas
        rect_buena = pygame.Rect(x_centrada_buena, 200 + idx * 60, ancho_boton, alto_boton)
        botones_buenas.append((rect_buena, opcion))

        # Definimos los rectángulos de los botones de las formas malas
        rect_mala = pygame.Rect(x_centrada_mala, 200 + idx * 60, ancho_boton, alto_boton)
        botones_malas.append((rect_mala, opcion))

    while menu_activo:
        pantalla.fill(BLANCO)  # Rellenamos la pantalla con color blanco
        texto_titulo = fuente.render("Selecciona las comidas buenas y malas", True, NEGRO)  # Texto del título del menú
        pantalla.blit(texto_titulo, (ANCHO // 2 - texto_titulo.get_width() // 2, 50))  # Mostramos el título centrado

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:  # Si el usuario cierra la ventana
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:  # Si el usuario hace clic con el ratón
                pos = pygame.mouse.get_pos()  # Obtenemos la posición del ratón
                # Verificamos si el clic fue en un botón de las formas buenas
                for boton, opcion in botones_buenas:
                    if boton.collidepoint(pos):
                        if opcion not in seleccionadas_buenas:
                            seleccionadas_buenas.append(opcion)
                        else:
                            seleccionadas_buenas.remove(opcion)
                # Verificamos si el clic fue en un botón de las formas malas
                for boton, opcion in botones_malas:
                    if boton.collidepoint(pos):
                        if opcion not in seleccionadas_malas:
                            seleccionadas_malas.append(opcion)
                        else:
                            seleccionadas_malas.remove(opcion)
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:  # Si el usuario presiona la tecla ENTER
                    menu_activo = False  # Salimos del menú

        # Mostramos los botones y opciones para las formas buenas
        texto_buenas = fuente.render("Comidas Buenas:", True, NEGRO)
        pantalla.blit(texto_buenas, (x_centrada_buena, 150))  # Texto para indicar las formas buenas
        for boton, opcion in botones_buenas:
            seleccionado = opcion in seleccionadas_buenas  # Verificamos si está seleccionada
            color_boton = (0, 200, 0) if seleccionado else (200, 200, 200)  # Color dependiendo del estado
            pygame.draw.rect(pantalla, color_boton, boton)  # Dibujamos el botón
            texto_opcion = fuente.render(opcion, True, NEGRO)
            texto_rect = texto_opcion.get_rect(center=boton.center)
            pantalla.blit(texto_opcion, texto_rect)  # Mostramos el texto de la opción en el botón

        # Mostramos los botones y opciones para las formas malas
        texto_malas = fuente.render("Comidas Malas:", True, NEGRO)
        pantalla.blit(texto_malas, (x_centrada_mala, 150))  # Texto para indicar las formas malas
        for boton, opcion in botones_malas:
            seleccionado = opcion in seleccionadas_malas  # Verificamos si está seleccionada
            color_boton = (200, 0, 0) if seleccionado else (200, 200, 200)  # Color dependiendo del estado
            pygame.draw.rect(pantalla, color_boton, boton)  # Dibujamos el botón
            texto_opcion = fuente.render(opcion, True, NEGRO)
            texto_rect = texto_opcion.get_rect(center=boton.center)
            pantalla.blit(texto_opcion, texto_rect)  # Mostramos el texto de la opción en el botón

        # Mostramos instrucciones en la parte inferior del menú
        instrucciones = [
            "Haz clic en las comidas para seleccionar/deseleccionar.",
            "Presiona ENTER para comenzar el juego."
        ]
        for idx, instruccion in enumerate(instrucciones):
            texto_instruccion = fuente.render(instruccion, True, NEGRO)
            pantalla.blit(texto_instruccion, (ANCHO // 2 - texto_instruccion.get_width() // 2, 450 + idx * 30))

        pygame.display.flip()  # Actualizamos la pantalla
        reloj.tick(30)  # Controlamos la velocidad del menú a 30 FPS

    return seleccionadas_buenas, seleccionadas_malas  # Retornamos las selecciones del jugador

# Función para generar las formas en el juego
def generar_formas():
    frecuencia_base = 1.0  # Frecuencia inicial para la aparición de nuevas formas (en segundos)
    while ejecutando:
        # Aumentamos la dificultad disminuyendo el tiempo entre las apariciones de las formas
        tiempo_juego = time.time() - tiempo_inicial
        frecuencia = max(0.2, frecuencia_base - tiempo_juego * 0.01)  # Disminuimos la frecuencia gradualmente
        nueva_forma = Forma()  # Creamos una nueva instancia de Forma

        # Verificamos si la forma está entre las seleccionadas por el jugador
        forma_nombre = nueva_forma.nombre
        if nueva_forma.tipo == 'buena':
            if forma_nombre not in formas_buenas_seleccionadas:
                continue  # No generamos formas no seleccionadas
        else:
            if forma_nombre not in formas_malas_seleccionadas:
                continue  # No generamos formas no seleccionadas

        # Añadimos la nueva forma a la cola
        with lock_formas:
            cola_formas.put(nueva_forma)
        time.sleep(frecuencia)  # Esperamos antes de generar la siguiente forma

# Función para mover las formas hacia abajo
def mover_formas():
    global puntaje, vidas
    while ejecutando:
        time.sleep(0.02)  # Controlamos la velocidad de actualización
        with lock_formas:
            formas_actualizadas = []
            while not cola_formas.empty():
                forma = cola_formas.get()
                # Aumentamos la velocidad de caída con el tiempo para incrementar la dificultad
                tiempo_juego = time.time() - tiempo_inicial
                incremento_velocidad = tiempo_juego * 0.002  # Incremento gradual de la velocidad
                forma.y += forma.velocidad + incremento_velocidad

                # Verificamos si la forma ha salido de la pantalla
                if forma.y > ALTO:
                    continue
                # Verificamos colisión con el jugador
                elif (y_jugador < forma.y + forma.tamano and
                      x_jugador < forma.x + forma.tamano and
                      x_jugador + ancho_jugador > forma.x):
                    if forma.tipo == 'buena':
                        puntaje += 1  # Aumentamos el puntaje si la forma es buena
                    else:
                        vidas -= 1  # Restamos una vida si la forma es mala
                    continue  # La forma se elimina después de la colisión

                formas_actualizadas.append(forma)  # Añadimos la forma a la lista actualizada

            # Volvemos a poner las formas actualizadas en la cola
            for forma in formas_actualizadas:
                cola_formas.put(forma)

# Función para dibujar una forma en la pantalla
def dibujar_forma(forma):
    pantalla.blit(forma.imagen, (forma.x, forma.y))  # Dibujamos la imagen en la posición de la forma

# Mostramos el menú y obtenemos las selecciones del jugador
formas_buenas_seleccionadas, formas_malas_seleccionadas = mostrar_menu()

# Validamos que el jugador haya seleccionado al menos una forma buena y una mala
if not formas_buenas_seleccionadas or not formas_malas_seleccionadas:
    print("Debe seleccionar al menos una forma buena y una forma mala.")
    pygame.quit()
    exit()

# Iniciamos los hilos para generar y mover las formas
hilo_generador = threading.Thread(target=generar_formas)
hilo_movedor = threading.Thread(target=mover_formas)
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

    # Manejo del movimiento del jugador
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] and x_jugador - velocidad_jugador >= 0:
        x_jugador -= velocidad_jugador  # Movemos al jugador a la izquierda
        direccion_jugador = 'izquierda'
    elif teclas[pygame.K_RIGHT] and x_jugador + velocidad_jugador <= ANCHO - ancho_jugador:
        x_jugador += velocidad_jugador  # Movemos al jugador a la derecha
        direccion_jugador = 'derecha'

    # Dibujamos al jugador según la dirección
    if direccion_jugador == 'derecha':
        pantalla.blit(imagen_jugador_derecha, (x_jugador, y_jugador))
    else:
        pantalla.blit(imagen_jugador_izquierda, (x_jugador, y_jugador))

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
        time.sleep(3)  # Esperamos 3 segundos antes de cerrar
        ejecutando = False
        break

    # Actualizamos la pantalla
    pygame.display.flip()

# Esperamos a que los hilos terminen antes de cerrar
hilo_generador.join()
hilo_movedor.join()

# Cerramos Pygame
pygame.quit()
