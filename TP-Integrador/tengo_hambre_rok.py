import pygame
import threading
import random
import time
from queue import Queue

pygame.init()

# Dimensiones de la pantalla
# ANCHO, ALTO = 600, 800

info_pantalla = pygame.display.Info()
ANCHO, ALTO = info_pantalla.current_w, info_pantalla.current_h
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

# Atributos del jugador
ancho_jugador = 100
alto_jugador = 20
x_jugador = ANCHO // 2 - ancho_jugador // 2
y_jugador = ALTO - alto_jugador - 10
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

# Clase para las formas
class Forma:
    def __init__(self):
        self.tipo = random.choice(['buena', 'mala'])
        self.tamano = random.randint(20, 50)
        self.color = random.choice(COLORES_FORMAS)
        self.x = random.randint(0, ANCHO - self.tamano)
        self.y = -self.tamano
        self.velocidad = random.uniform(3, 7)  # Velocidad inicial de la forma

def mostrar_menu():
    menu_activo = True
    opciones = ['Rectángulo', 'Círculo', 'Triángulo']
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
        rect_buena = pygame.Rect(x_centrada_buena, 200 + idx * 60, 200, 50)
        botones_buenas.append((rect_buena, opcion))
        # Botones para formas malas
        rect_mala = pygame.Rect(x_centrada_mala, 200 + idx * 60, 200, 50)
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
        texto_buenas = fuente.render("Formas Buenas:", True, NEGRO)
        pantalla.blit(texto_buenas, (x_centrada_buena, 150))
        for boton, opcion in botones_buenas:
            seleccionado = opcion in seleccionadas_buenas
            color_boton = (0, 200, 0) if seleccionado else (200, 200, 200)
            pygame.draw.rect(pantalla, color_boton, boton)
            texto_opcion = fuente.render(opcion, True, NEGRO)
            pantalla.blit(texto_opcion, (boton.x + 10, boton.y + 10))

        # Mostrar botones y opciones para formas malas
        texto_malas = fuente.render("Formas Malas:", True, NEGRO)
        pantalla.blit(texto_malas, (x_centrada_mala, 150))
        for boton, opcion in botones_malas:
            seleccionado = opcion in seleccionadas_malas
            color_boton = (200, 0, 0) if seleccionado else (200, 200, 200)
            pygame.draw.rect(pantalla, color_boton, boton)
            texto_opcion = fuente.render(opcion, True, NEGRO)
            pantalla.blit(texto_opcion, (boton.x + 10, boton.y + 10))

        # Instrucciones
        instrucciones = [
            "Haz clic en las formas para seleccionar/deseleccionar.",
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
        forma_nombre = obtener_nombre_forma(nueva_forma)
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
    # Dibuja la forma según su tipo y características
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
    pantalla.fill(BLANCO)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # Manejo de movimiento del jugador
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] and x_jugador - velocidad_jugador >= 0:
        x_jugador -= velocidad_jugador
    if teclas[pygame.K_RIGHT] and x_jugador + velocidad_jugador <= ANCHO - ancho_jugador:
        x_jugador += velocidad_jugador

    # Dibujar jugador
    pygame.draw.rect(pantalla, NEGRO, (x_jugador, y_jugador, ancho_jugador, alto_jugador))

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
