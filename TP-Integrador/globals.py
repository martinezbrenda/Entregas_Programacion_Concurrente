import pygame

puntaje = 0        # Puntuación del jugador
vidas = 3          # Número de vidas del jugador
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