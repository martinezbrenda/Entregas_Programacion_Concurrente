from utils import imagenes_personajes
from globals import ALTO, ANCHO

class Jugador:
    def __init__(self, personaje='Nena 1'):
        self.ancho_jugador = 100
        self.alto_jugador = int(self.ancho_jugador * 1.5)
        self.imagen_derecha = imagenes_personajes[personaje]['derecha']
        self.imagen_izquierda = imagenes_personajes[personaje]['izquierda']

        self.x = ANCHO // 2 - self.ancho_jugador // 2
        self.y = ALTO - self.alto_jugador - 10
        self.direccion_jugador = 'derecha'

    def mover(self, direccion, velocidad, limites):
        """Mueve al jugador dentro de los límites de la pantalla."""
        if direccion == 'izquierda' and self.x - velocidad >= limites['izquierda']:
            self.x -= velocidad
            self.direccion_jugador = 'izquierda'
        elif direccion == 'derecha' and self.x + velocidad <= limites['derecha']:
            self.x += velocidad
            self.direccion_jugador = 'derecha'

    def dibujar(self, pantalla):
        """Dibuja al jugador en pantalla según la dirección."""
        imagen = self.imagen_derecha if self.direccion_jugador == 'derecha' else self.imagen_izquierda
        pantalla.blit(imagen, (self.x, self.y))
