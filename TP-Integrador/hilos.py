import threading
import time
import random
import globals
from queue import Queue
from forma import Forma
from globals import ALTO

class GeneradorFormas:
    def __init__(self, cola, lock, tiempo_inicial, stop_event, formas_buenas_seleccionadas, frecuencia_base=1.0):
        self.cola = cola
        self.lock = lock
        self.frecuencia_base = frecuencia_base
        self.tiempo_inicial = tiempo_inicial
        self.stop_event = stop_event
        self.formas_buenas_seleccionadas = formas_buenas_seleccionadas

    def generar_formas(self):
        while not self.stop_event.is_set():
            tiempo_juego = time.time() - self.tiempo_inicial
            frecuencia = max(0.2, self.frecuencia_base - tiempo_juego * 0.01)
            nueva_forma = Forma(self.formas_buenas_seleccionadas)

            with self.lock:
                self.cola.put(nueva_forma)
            self.stop_event.wait(frecuencia)

class MovimientoFormas:
    def __init__(self, cola, lock, jugador, reloj, tiempo_inicial, stop_event):
        self.cola = cola
        self.lock = lock
        self.jugador = jugador
        self.reloj = reloj
        self.tiempo_inicial = tiempo_inicial
        self.stop_event = stop_event

    def mover_formas(self):
        while not self.stop_event.is_set():
            self.reloj.tick(50)
            with self.lock:
                formas_actualizadas = []
                while not self.cola.empty():
                    forma = self.cola.get()
                    tiempo_juego = time.time() - self.tiempo_inicial
                    incremento_velocidad = tiempo_juego * 0.002
                    forma.y += forma.velocidad + incremento_velocidad

                    if forma.y > ALTO:
                        continue
                    elif (self.jugador.y < forma.y + forma.tamano and
                          self.jugador.x < forma.x + forma.tamano and
                          self.jugador.x + self.jugador.ancho_jugador > forma.x):
                        if forma.tipo == 'buena':
                            globals.puntaje += 1
                        else:
                            globals.vidas -= 1
                        continue

                    formas_actualizadas.append(forma)

                for forma in formas_actualizadas:
                    self.cola.put(forma)

