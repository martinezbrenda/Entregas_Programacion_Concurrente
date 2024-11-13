import pygame
import threading    
import time
from queue import Queue

# Definimos las dimensiones de la pantalla del juego
ANCHO, ALTO = 800, 600  # Ajusta el tamaño de la pantalla
pantalla = pygame.display.set_mode((ANCHO, ALTO))  # Creamos la pantalla del juego
pygame.display.set_caption("Atrapa las Comidas")  # Título de la ventana

# Definimos colores usando formato RGB
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# Velocidad de movimiento del jugador
velocidad_jugador = 10

reloj = pygame.time.Clock()  # Reloj para controlar los FPS del juego

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

# Cargar imágenes de personajes disponibles
imagenes_personajes = {
    'Nena 1': {
        'derecha': cargar_imagen('img/nenita1_der.png', (100, 150)),
        'izquierda': cargar_imagen('img/nenita1_iz.png', (100, 150))
    },
    'Nena 2': {
        'derecha': cargar_imagen('img/aros-der.png', (100, 150)),
        'izquierda': cargar_imagen('img/aros-iz.png', (100, 150))
    },
    'Nene 1': {
        'derecha': cargar_imagen('img/nene1-der.png', (100, 150)),
        'izquierda': cargar_imagen('img/nene1-iz.png', (100, 150))
    },
    'Nene 2': {
        'derecha': cargar_imagen('img/will-der.png', (100, 150)),
        'izquierda': cargar_imagen('img/will-iz.png', (100, 150))
    },
}

# Cargar imagen de fondo
imagen_fondo = cargar_imagen('img/day2.png', (ANCHO, ALTO))