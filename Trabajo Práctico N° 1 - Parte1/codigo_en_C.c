#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

#define PROCESS_A 'A'
#define PROCESS_B 'B'
#define PROCESS_C 'C'
#define PROCESS_D 'D'
#define PROCESS_E 'E'
#define PROCESS_F 'F'
#define PROCESS_G 'G'
#define PROCESS_H 'H'
#define PROCESS_I 'I'
#define PROCESO_HIJO 0
#define TIEMPO_DE_ESPERA 200
#define TODOS NULL
#define PROCESOS_ACTIVOS 0
#define EJECUCION_OK 0

void print_process(char name)
{
    printf("Proceso %c - PID: %d, Proceso Padre PID: %d\n", name, getpid(), getppid());
}

int main()
{
    pid_t pid_A, pid_B, pid_C, pid_D, pid_E, pid_F, pid_G, pid_H, pid_I;
    print_process(PROCESS_A);

    pid_B = fork();
    if (pid_B == PROCESO_HIJO)
    {
        print_process(PROCESS_B);

        pid_C = fork();
        if (pid_C == PROCESO_HIJO)
        {
            
            print_process(PROCESS_C);

            pid_E = fork();
            if (pid_E == PROCESO_HIJO)
            {
                
                print_process(PROCESS_E);

                pid_H = fork();
                if (pid_H == PROCESO_HIJO)
                {
                    
                    print_process(PROCESS_H);
                }
                else
                {
                    pid_I = fork();
                    if (pid_I == PROCESO_HIJO)
                    {
                        
                        print_process(PROCESS_I);
                    }
                }
            }
        }
        else
        {
            pid_D = fork();
            if (pid_D == PROCESO_HIJO)
            {
                
                print_process(PROCESS_D);

                pid_F = fork();
                if (pid_F == PROCESO_HIJO)
                {
                    
                    print_process(PROCESS_F);
                }
                else
                {
                    pid_G = fork();
                    if (pid_G == PROCESO_HIJO)
                    {
                        
                        print_process(PROCESS_G);
                    }
                }
            }
        }
    }

    
    sleep(TIEMPO_DE_ESPERA);

    while (wait(TODOS) > PROCESOS_ACTIVOS)
        ;

    return EJECUCION_OK;
}