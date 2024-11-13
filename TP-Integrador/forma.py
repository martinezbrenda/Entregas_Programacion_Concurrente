import pygame
import random
from utils import pantalla, imagenes_formas_buenas, imagenes_formas_malas, ANCHO

# Clase que representa una forma que cae (puede ser buena o mala)
class Forma:
    def __init__(self, formas_buenas_seleccionadas):
        self.tamano = random.randint(40, 80)  # Tamaño aleatorio de la forma
        self.nombre = random.choice(['Pizza', 'Pancho', 'Torta'])  # Nombre de la forma
        self.x = random.randint(0, ANCHO - self.tamano)  # Posición horizontal aleatoria
        self.y = -self.tamano  # Posición inicial (fuera de la pantalla, para caer desde arriba)
        self.velocidad = random.uniform(3, 7)  # Velocidad de caída

        # Tipo de la forma (buena o mala)
        if self.nombre in formas_buenas_seleccionadas:
            self.tipo = 'buena'
        else:
            self.tipo = 'mala'

        # Asignamos la imagen correspondiente según el tipo (buena o mala)
        if self.tipo == 'buena':
            self.imagen = imagenes_formas_buenas[self.nombre]
        else:
            self.imagen = imagenes_formas_malas[self.nombre]
        
        # Redimensionamos la imagen al tamaño de la forma
        self.imagen = pygame.transform.scale(self.imagen, (self.tamano, self.tamano))

    def mover(self, incremento_velocidad, alto_pantalla):
        """Mueve la forma hacia abajo. Retorna True si sale de la pantalla."""
        self.y += self.velocidad + incremento_velocidad
        return self.y > alto_pantalla

    def colisiona_con(self, jugador):
        """Verifica si la forma colisiona con el jugador."""
        return (
            jugador.y < self.y + self.tamano and
            jugador.x < self.x + self.tamano and
            jugador.x + jugador.ancho_jugador > self.x
        )

# Función para dibujar una forma en la pantalla
def dibujar_forma(forma):
    pantalla.blit(forma.imagen, (forma.x, forma.y))  # Dibujamos la imagen en la posición de la forma
