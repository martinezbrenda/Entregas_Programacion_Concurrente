import pygame
import threading
import random
import time
from queue import Queue

pygame.init()

# Dimensiones de la pantalla (ajustadas para ser más pequeñas que la pantalla completa)
ANCHO, ALTO = 800, 600  # Puedes cambiar estos valores a las dimensiones que prefieras
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Atrapa las Comidas")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# Atributos del jugador


velocidad_jugador = 10

# Variables del juego
ejecutando = True
puntaje = 0
vidas = 3
reloj = pygame.time.Clock()
tiempo_inicial = time.time()

# Cola y lock para comunicación entre hilos
cola_formas = Queue()
lock_formas = threading.Lock()

# Opciones seleccionadas por el jugador
formas_buenas_seleccionadas = []
formas_malas_seleccionadas = []

# Cargar imágenes de los sprites con manejo de excepciones
imagenes_formas_buenas = {}
imagenes_formas_malas = {}

try:
    imagenes_formas_buenas['Pizza'] = pygame.image.load('81_pizza.png')
    imagenes_formas_buenas['Pancho'] = pygame.image.load('54_hotdog.png')
    imagenes_formas_buenas['Torta'] = pygame.image.load('30_chocolatecake.png')

    imagenes_formas_malas['Pizza'] = pygame.image.load('81_pizza.png')
    imagenes_formas_malas['Pancho'] = pygame.image.load('54_hotdog.png')
    imagenes_formas_malas['Torta'] = pygame.image.load('30_chocolatecake.png')
except pygame.error as e:
    print(f"Error al cargar imágenes de las formas: {e}")
    pygame.quit()
    exit()

# Cargar imágenes del jugador
try:
    imagen_jugador_derecha = pygame.image.load('nenita_der.png').convert_alpha()
    imagen_jugador_izquierda = pygame.image.load('nenita_izq.png').convert_alpha()

    # Escalar las imágenes al tamaño deseado
    ancho_jugador = 100  # Puedes ajustar este valor
    alto_jugador = int(imagen_jugador_derecha.get_height() * (ancho_jugador / imagen_jugador_derecha.get_width()))

    imagen_jugador_derecha = pygame.transform.scale(imagen_jugador_derecha, (ancho_jugador, alto_jugador))
    imagen_jugador_izquierda = pygame.transform.scale(imagen_jugador_izquierda, (ancho_jugador, alto_jugador))
except pygame.error as e:
    print(f"Error al cargar las imágenes del jugador: {e}")
    pygame.quit()
    exit()

x_jugador = ANCHO // 2 - ancho_jugador // 2
y_jugador = ALTO - alto_jugador - 10

# Dirección actual del jugador: 'izquierda' o 'derecha'
direccion_jugador = 'derecha'

# Cargar la imagen de fondo
try:
    imagen_fondo = pygame.image.load('background.png').convert()
    # Escalar la imagen al tamaño de la pantalla
    imagen_fondo = pygame.transform.scale(imagen_fondo, (ANCHO, ALTO))
except pygame.error as e:
    print(f"Error al cargar la imagen de fondo: {e}")
    pygame.quit()
    exit()


# Clase para las formas
class Forma:
    def __init__(self):
        self.tipo = random.choice(['buena', 'mala'])
        self.tamano = random.randint(40, 80)
        self.nombre = random.choice(['Pizza', 'Pancho', 'Torta'])
        self.x = random.randint(0, ANCHO - self.tamano)
        self.y = -self.tamano
        self.velocidad = random.uniform(3, 7)

        # Asignar la imagen correspondiente
        if self.tipo == 'buena':
            self.imagen = imagenes_formas_buenas[self.nombre]
        else:
            self.imagen = imagenes_formas_malas[self.nombre]
        
        # Redimensionar la imagen al tamaño de la forma
        self.imagen = pygame.transform.scale(self.imagen, (self.tamano, self.tamano))

def mostrar_menu():
    menu_activo = True
    opciones = ['Pizza', 'Pancho', 'Torta']
    seleccionadas_buenas = []
    seleccionadas_malas = []
    fuente = pygame.font.SysFont(None, 36)
    ancho_boton = 200  # Ancho de los botones
    alto_boton = 50    # Alto de los botones

    # Calcular la posición 'x' centrada para cada mitad de la pantalla
    x_centrada_buena = (ANCHO // 4) - (ancho_boton // 2)  # Centrada en la mitad izquierda
    x_centrada_mala = (3 * ANCHO // 4) - (ancho_boton // 2)  # Centrada en la mitad derecha

    # Definir posiciones y tamaños de los botones
    botones_buenas = []
    botones_malas = []
    for idx, opcion in enumerate(opciones):
        # Botones para formas buenas
        rect_buena = pygame.Rect(x_centrada_buena, 200 + idx * 60, ancho_boton, alto_boton)
        botones_buenas.append((rect_buena, opcion))
        # Botones para formas malas
        rect_mala = pygame.Rect(x_centrada_mala, 200 + idx * 60, ancho_boton, alto_boton)
        botones_malas.append((rect_mala, opcion))

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
                for boton, opcion in botones_buenas:
                    if boton.collidepoint(pos):
                        if opcion not in seleccionadas_buenas:
                            seleccionadas_buenas.append(opcion)
                        else:
                            seleccionadas_buenas.remove(opcion)
                # Verificar clic en botones de formas malas
                for boton, opcion in botones_malas:
                    if boton.collidepoint(pos):
                        if opcion not in seleccionadas_malas:
                            seleccionadas_malas.append(opcion)
                        else:
                            seleccionadas_malas.remove(opcion)
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    menu_activo = False

        # Mostrar botones y opciones para formas buenas
        texto_buenas = fuente.render("Comidas Buenas:", True, NEGRO)
        pantalla.blit(texto_buenas, (x_centrada_buena, 150))
        for boton, opcion in botones_buenas:
            seleccionado = opcion in seleccionadas_buenas
            color_boton = (0, 200, 0) if seleccionado else (200, 200, 200)
            pygame.draw.rect(pantalla, color_boton, boton)
            texto_opcion = fuente.render(opcion, True, NEGRO)
            texto_rect = texto_opcion.get_rect(center=boton.center)
            pantalla.blit(texto_opcion, texto_rect)

        # Mostrar botones y opciones para formas malas
        texto_malas = fuente.render("Comidas Malas:", True, NEGRO)
        pantalla.blit(texto_malas, (x_centrada_mala, 150))
        for boton, opcion in botones_malas:
            seleccionado = opcion in seleccionadas_malas
            color_boton = (200, 0, 0) if seleccionado else (200, 200, 200)
            pygame.draw.rect(pantalla, color_boton, boton)
            texto_opcion = fuente.render(opcion, True, NEGRO)
            texto_rect = texto_opcion.get_rect(center=boton.center)
            pantalla.blit(texto_opcion, texto_rect)

        # Instrucciones
        instrucciones = [
            "Haz clic en las comidas para seleccionar/deseleccionar.",
            "Presiona ENTER para comenzar el juego."
        ]
        for idx, instruccion in enumerate(instrucciones):
            texto_instruccion = fuente.render(instruccion, True, NEGRO)
            pantalla.blit(texto_instruccion, (ANCHO // 2 - texto_instruccion.get_width() // 2, 450 + idx * 30))

        pygame.display.flip()
        reloj.tick(30)

    return seleccionadas_buenas, seleccionadas_malas

def generar_formas():
    frecuencia_base = 1.0  # Frecuencia inicial de aparición (en segundos)
    while ejecutando:
        # Aumentar la dificultad disminuyendo el tiempo entre apariciones
        tiempo_juego = time.time() - tiempo_inicial
        frecuencia = max(0.2, frecuencia_base - tiempo_juego * 0.01)
        nueva_forma = Forma()

        # Verificar si la forma está entre las seleccionadas
        forma_nombre = nueva_forma.nombre
        if nueva_forma.tipo == 'buena':
            if forma_nombre not in formas_buenas_seleccionadas:
                continue  # No generar formas no seleccionadas
        else:
            if forma_nombre not in formas_malas_seleccionadas:
                continue  # No generar formas no seleccionadas

        with lock_formas:
            cola_formas.put(nueva_forma)
        time.sleep(frecuencia)

def obtener_nombre_forma(forma):
    # Determina el nombre de la forma según sus características
    if forma.tamano >= 40:
        return 'Rectángulo'
    elif forma.tamano >= 30:
        return 'Círculo'
    else:
        return 'Triángulo'

def mover_formas():
    global puntaje, vidas
    while ejecutando:
        time.sleep(0.02)  # Controla la velocidad de actualización
        with lock_formas:
            formas_actualizadas = []
            while not cola_formas.empty():
                forma = cola_formas.get()
                # Aumentar la velocidad de caída con el tiempo para incrementar la dificultad
                tiempo_juego = time.time() - tiempo_inicial
                incremento_velocidad = tiempo_juego * 0.002  # Incremento gradual
                forma.y += forma.velocidad + incremento_velocidad
                # Verifica si la forma ha salido de la pantalla
                if forma.y > ALTO:
                    continue
                # Verifica colisión con el jugador
                elif (y_jugador < forma.y + forma.tamano and
                      x_jugador < forma.x + forma.tamano and
                      x_jugador + ancho_jugador > forma.x):
                    if forma.tipo == 'buena':
                        puntaje += 1
                    else:
                        vidas -= 1
                    continue  # La forma se elimina después de la colisión
                formas_actualizadas.append(forma)
            # Vuelve a poner las formas actualizadas en la cola
            for forma in formas_actualizadas:
                cola_formas.put(forma)

def dibujar_forma(forma):
    pantalla.blit(forma.imagen, (forma.x, forma.y))

# Mostrar el menú y obtener las selecciones del jugador
formas_buenas_seleccionadas, formas_malas_seleccionadas = mostrar_menu()

# Validar que al menos haya una forma buena y una mala seleccionada
if not formas_buenas_seleccionadas or not formas_malas_seleccionadas:
    print("Debe seleccionar al menos una forma buena y una forma mala.")
    pygame.quit()
    exit()

# Iniciar hilos
hilo_generador = threading.Thread(target=generar_formas)
hilo_movedor = threading.Thread(target=mover_formas)
hilo_generador.start()
hilo_movedor.start()

# Bucle principal del juego
while ejecutando:
    reloj.tick(60)  # 60 FPS
    pantalla.blit(imagen_fondo, (0, 0))

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # Manejo de movimiento del jugador
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] and x_jugador - velocidad_jugador >= 0:
        x_jugador -= velocidad_jugador
        direccion_jugador = 'izquierda'
    elif teclas[pygame.K_RIGHT] and x_jugador + velocidad_jugador <= ANCHO - ancho_jugador:
        x_jugador += velocidad_jugador
        direccion_jugador = 'derecha'


    # Dibujar jugador según la dirección
    if direccion_jugador == 'derecha':
        pantalla.blit(imagen_jugador_derecha, (x_jugador, y_jugador))
    else:
        pantalla.blit(imagen_jugador_izquierda, (x_jugador, y_jugador))


    # Dibujar formas
    with lock_formas:
        formas_a_dibujar = list(cola_formas.queue)
    for forma in formas_a_dibujar:
        dibujar_forma(forma)

    # Mostrar puntaje y vidas
    fuente = pygame.font.SysFont(None, 36)
    texto_puntaje = fuente.render(f"Puntaje: {puntaje}", True, NEGRO)
    texto_vidas = fuente.render(f"Vidas: {vidas}", True, NEGRO)
    pantalla.blit(texto_puntaje, (10, 10))
    pantalla.blit(texto_vidas, (10, 50))

    # Verificar si el jugador ha perdido todas las vidas
    if vidas <= 0:
        fuente_game_over = pygame.font.SysFont(None, 72)
        texto_game_over = fuente_game_over.render("¡Juego Terminado!", True, NEGRO)
        pantalla.blit(texto_game_over, (ANCHO // 2 - texto_game_over.get_width() // 2, ALTO // 2))
        pygame.display.flip()
        time.sleep(3)
        ejecutando = False
        break

    # Actualizar pantalla
    pygame.display.flip()

# Esperar a que los hilos terminen antes de cerrar
hilo_generador.join()
hilo_movedor.join()

pygame.quit()
