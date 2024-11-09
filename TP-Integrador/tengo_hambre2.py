import pygame
import threading
import random
import time
from queue import Queue

pygame.init()

# Dimensiones de la pantalla
ANCHO, ALTO = 600, 800
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Atrapa las Formas")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
COLORES_FORMAS = [
    (255, 0, 0),    # Rojo
    (0, 255, 0),    # Verde
    (0, 0, 255),    # Azul
    (255, 255, 0),  # Amarillo
    (255, 165, 0),  # Naranja
    (128, 0, 128)   # Púrpura
]


# Variables del juego
ejecutando = True
reloj = pygame.time.Clock()
tiempo_inicial = time.time()

# Cola y lock para comunicación entre hilos
cola_formas = Queue()
lock_formas = threading.Lock()

# Opciones seleccionadas por el jugador
formas_buenas_seleccionadas = []
formas_malas_seleccionadas = []

# Clase Forma
class Forma:
    def __init__(self):
        self.tipo = random.choice(['buena', 'mala'])
        self.tamano = random.randint(20, 50)
        self.color = random.choice(COLORES_FORMAS)
        self.x = random.randint(0, ANCHO - self.tamano)
        self.y = -self.tamano
        self.velocidad = random.uniform(3, 7)

def set_player():
    global x_jugador, y_jugador, ancho_jugador, alto_jugador, velocidad_jugador
    ancho_jugador = 100
    alto_jugador = 20
    x_jugador = ANCHO // 2 - ancho_jugador // 2
    y_jugador = ALTO - alto_jugador - 10
    velocidad_jugador = 20

def set_game_variables():
    global puntaje, vidas
    puntaje = 0
    vidas = 3

def set_shapes():
    global formas_buenas_seleccionadas, formas_malas_seleccionadas
    opciones_buenas = ['Rectángulo', 'Círculo', 'Triángulo']
    opciones_malas = ['Rectángulo', 'Círculo', 'Triángulo']
    formas_buenas_seleccionadas = opciones_buenas
    formas_malas_seleccionadas = opciones_malas

def mostrar_menu():
    menu_activo = True
    opciones = ['Rectángulo', 'Círculo', 'Triángulo']
    seleccionadas_buenas = []
    seleccionadas_malas = []
    fuente = pygame.font.SysFont(None, 36)
    botones_buenas = []
    botones_malas = []
    
    for idx, opcion in enumerate(opciones):
        rect_buena = pygame.Rect(70, 200 + idx * 60, 200, 50)
        botones_buenas.append((rect_buena, opcion))
        rect_mala = pygame.Rect(330, 200 + idx * 60, 200, 50)
        botones_malas.append((rect_mala, opcion))

    while menu_activo:
        pantalla.fill(BLANCO)
        texto_titulo = fuente.render("Selecciona las formas buenas y malas", True, NEGRO)
        pantalla.blit(texto_titulo, (ANCHO // 2 - texto_titulo.get_width() // 2, 50))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for boton, opcion in botones_buenas:
                    if boton.collidepoint(pos):
                        if opcion not in seleccionadas_buenas:
                            seleccionadas_buenas.append(opcion)
                        else:
                            seleccionadas_buenas.remove(opcion)
                for boton, opcion in botones_malas:
                    if boton.collidepoint(pos):
                        if opcion not in seleccionadas_malas:
                            seleccionadas_malas.append(opcion)
                        else:
                            seleccionadas_malas.remove(opcion)
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    menu_activo = False

        texto_buenas = fuente.render("Formas Buenas:", True, NEGRO)
        pantalla.blit(texto_buenas, (70, 150))
        for boton, opcion in botones_buenas:
            seleccionado = opcion in seleccionadas_buenas
            color_boton = (0, 200, 0) if seleccionado else (200, 200, 200)
            pygame.draw.rect(pantalla, color_boton, boton)
            texto_opcion = fuente.render(opcion, True, NEGRO)
            pantalla.blit(texto_opcion, (boton.x + 10, boton.y + 10))

        texto_malas = fuente.render("Formas Malas:", True, NEGRO)
        pantalla.blit(texto_malas, (330, 150))
        for boton, opcion in botones_malas:
            seleccionado = opcion in seleccionadas_malas
            color_boton = (200, 0, 0) if seleccionado else (200, 200, 200)
            pygame.draw.rect(pantalla, color_boton, boton)
            texto_opcion = fuente.render(opcion, True, NEGRO)
            pantalla.blit(texto_opcion, (boton.x + 10, boton.y + 10))

        instrucciones = [
            "Haz clic en las formas para seleccionar/deseleccionar.",
            "Presiona ENTER para comenzar el juego."
        ]
        for idx, instruccion in enumerate(instrucciones):
            texto_instruccion = fuente.render(instruccion, True, NEGRO)
            pantalla.blit(texto_instruccion, (50, 450 + idx * 30))

        pygame.display.flip()
        reloj.tick(30)

    return seleccionadas_buenas, seleccionadas_malas

def generar_formas():
    frecuencia_base = 1.0
    while ejecutando:
        tiempo_juego = time.time() - tiempo_inicial
        frecuencia = max(0.2, frecuencia_base - tiempo_juego * 0.01)
        nueva_forma = Forma()
        forma_nombre = obtener_nombre_forma(nueva_forma)
        if nueva_forma.tipo == 'buena':
            if forma_nombre not in formas_buenas_seleccionadas:
                continue
        else:
            if forma_nombre not in formas_malas_seleccionadas:
                continue
        with lock_formas:
            cola_formas.put(nueva_forma)
        time.sleep(frecuencia)

def obtener_nombre_forma(forma):
    if forma.tamano >= 40:
        return 'Rectángulo'
    elif forma.tamano >= 30:
        return 'Círculo'
    else:
        return 'Triángulo'

def mover_formas():
    global puntaje, vidas
    while ejecutando:
        time.sleep(0.02)
        with lock_formas:
            formas_actualizadas = []
            while not cola_formas.empty():
                forma = cola_formas.get()
                tiempo_juego = time.time() - tiempo_inicial
                incremento_velocidad = tiempo_juego * 0.002
                forma.y += forma.velocidad + incremento_velocidad
                if forma.y > ALTO:
                    continue
                elif (y_jugador < forma.y + forma.tamano and
                      x_jugador < forma.x + forma.tamano and
                      x_jugador + ancho_jugador > forma.x):
                    if forma.tipo == 'buena':
                        puntaje += 1
                    else:
                        vidas -= 1
                    continue
                formas_actualizadas.append(forma)
            for forma in formas_actualizadas:
                cola_formas.put(forma)

def dibujar_forma(forma):
    forma_nombre = obtener_nombre_forma(forma)
    if forma_nombre == 'Rectángulo':
        pygame.draw.rect(pantalla, forma.color, (forma.x, forma.y, forma.tamano, forma.tamano))
    elif forma_nombre == 'Círculo':
        pygame.draw.circle(pantalla, forma.color, (int(forma.x + forma.tamano / 2), int(forma.y + forma.tamano / 2)), forma.tamano // 2)
    elif forma_nombre == 'Triángulo':
        puntos = [
            (forma.x + forma.tamano / 2, forma.y),
            (forma.x, forma.y + forma.tamano),
            (forma.x + forma.tamano, forma.y + forma.tamano)
        ]
        pygame.draw.polygon(pantalla, forma.color, puntos)

# Iniciar juego
set_player()
set_game_variables()
set_shapes()

# Mostrar el menú y obtener las selecciones del jugador
formas_buenas_seleccionadas, formas_malas_seleccionadas = mostrar_menu()

# Validar que al menos haya una forma seleccionada en cada categoría
if not formas_buenas_seleccionadas or not formas_malas_seleccionadas:
    print("Debe seleccionar al menos una forma buena y una mala.")
    pygame.quit()
    exit()

# Crear y ejecutar hilos para generar y mover formas
hilo_formas = threading.Thread(target=generar_formas, daemon=True)
hilo_mover_formas = threading.Thread(target=mover_formas, daemon=True)
hilo_formas.start()
hilo_mover_formas.start()

# Bucle principal
# Bucle principal
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_LEFT:
                x_jugador -= velocidad_jugador
            if evento.key == pygame.K_RIGHT:
                x_jugador += velocidad_jugador

    # Limitar la posición del jugador para que no salga de la pantalla
    if x_jugador < 0:
        x_jugador = 0
    elif x_jugador > ANCHO - ancho_jugador:
        x_jugador = ANCHO - ancho_jugador

    pantalla.fill(BLANCO)

    # Dibujar al jugador como un rectángulo
    pygame.draw.rect(pantalla, (0, 0, 0), (x_jugador, y_jugador, ancho_jugador, alto_jugador))

    # Mostrar puntaje y vidas
    fuente = pygame.font.SysFont(None, 36)
    texto_puntaje = fuente.render(f"Puntaje: {puntaje}", True, NEGRO)
    pantalla.blit(texto_puntaje, (10, 10))
    texto_vidas = fuente.render(f"Vidas: {vidas}", True, NEGRO)
    pantalla.blit(texto_vidas, (ANCHO - 120, 10))

    # Dibujar las formas
    with lock_formas:
        for forma in list(cola_formas.queue):
            dibujar_forma(forma)

    # Comprobar si el jugador ha perdido
    if vidas <= 0:
        ejecutando = False
        print("¡Perdiste! Fin del juego.")
        break

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
