PROCESS_A = 'A'
PROCESS_B = 'B'
PROCESS_C = 'C'
PROCESS_D = 'D'
PROCESS_E = 'E'
PROCESS_F = 'F'
PROCESS_G = 'G'
PROCESS_H = 'H'
PROCESS_I = 'I'

TIEMPO_DE_ESPERA = 20
PROCESO_HIJO = 0
PROCESOS_ACTIVOS = 0

import os
import time

def print_process(name):
    print(f'Proceso {name} - PID: {os.getpid()}, Proceso Padre PID: {os.getppid()}')

def main():
        # Proceso principal A
        print_process(PROCESS_A)

        pid_B = os.fork()
        if pid_B == PROCESO_HIJO:
            # Proceso B
            print_process(PROCESS_B)

            pid_C = os.fork()
            if pid_C == PROCESO_HIJO:
                # Proceso C
                print_process(PROCESS_C)

                pid_E = os.fork()
                if pid_E == PROCESO_HIJO:
                    # Proceso E
                    print_process(PROCESS_E)

                    pid_H = os.fork()
                    if pid_H == PROCESO_HIJO:
                        # Proceso H
                        print_process(PROCESS_H)
                    else:
                        pid_I = os.fork()
                        if pid_I == PROCESO_HIJO:
                            # Proceso I
                            print_process(PROCESS_I)
            else:
                    pid_D = os.fork()
                    if pid_D == PROCESO_HIJO:
                        # Proceso D
                        print_process(PROCESS_D)

                        pid_F = os.fork()
                        if pid_F == PROCESO_HIJO:
                            # Proceso F
                            print_process(PROCESS_F)
                        else:
                            pid_G = os.fork()
                            if pid_G == PROCESO_HIJO:
                                # Proceso G
                                print_process(PROCESS_G)
        # Esperar a que terminen todos los procesos hijos
        time.sleep(TIEMPO_DE_ESPERA)
        while True:
            try:
                os.wait()
            except ChildProcessError:
                break


    # Esperar a que terminen todos los procesos hijos en el proceso A
        time.sleep(TIEMPO_DE_ESPERA)
        while True:
            try:
                os.wait()
            except ChildProcessError:
                break

if __name__ == '__main__':
    main()