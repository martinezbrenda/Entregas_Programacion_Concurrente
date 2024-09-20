import threading
import time
import sys

INITIAL_COUNT_VALUE = 0
FILENAME_INDEX = 1
NUM_THREADS_INDEX = 2
EMPTY_FILE = 0
INITIAL_POSITION = 0
INITIAL_THREAD_COUNT = 0
OK = 0
ERROR = 1


lines = []


partial_results = []


mutex = threading.Lock()

def open_file(filename):
    try:
        text_file = open(filename, 'r')
        return text_file
    except FileNotFoundError:
        print("No se pudo abrir el archivo.")
        sys.exit(ERROR)

def read_lines(text_file):
    global lines
    for line in text_file:
        line = line.strip()
        if line:
            lines.append(line)
    text_file.close()

def initialize_partial_results(num_threads):
    global partial_results
    partial_results = [INITIAL_COUNT_VALUE] * num_threads

def count_characters(ini, stop, partial_result_pos):
    count = INITIAL_COUNT_VALUE
    for i in range(ini, stop):
        count += len(lines[i])

    
    with mutex:
        partial_results[partial_result_pos] = count

def create_threads(num_threads, num_lines):
    threads = []
    lines_per_thread = num_lines // num_threads
    initial_position = INITIAL_POSITION

    for thread_count in range(num_threads):
        last_position = num_lines if thread_count == num_threads - 1 else initial_position + lines_per_thread
        thread = threading.Thread(target=count_characters, args=(initial_position, last_position, thread_count))
        threads.append(thread)
        thread.start()
        initial_position = last_position

    
    for thread in threads:
        thread.join()
def sum_partial_results(num_threads):
    total_result = INITIAL_COUNT_VALUE
    for i in range(num_threads):
        total_result += partial_results[i]
    return total_result

def measure_time(start_time):
    finish_time = time.time()
    processing_time = (finish_time - start_time) * 1000
    return processing_time

def main():
    filename = sys.argv[FILENAME_INDEX]
    num_threads = int(sys.argv[NUM_THREADS_INDEX])
    text_file = open_file(filename)
    read_lines(text_file)
    num_lines = len(lines)
    if num_lines == EMPTY_FILE:
        print("El archivo está vacío o no contiene líneas válidas.")
        return OK

    initialize_partial_results(num_threads)
    start_time = time.time()
    create_threads(num_threads, num_lines)
    total_result = sum_partial_results(num_threads)
    processing_time = measure_time(start_time)
    print("Cantidad de caracteres del archivo:", total_result)
    print("Tiempo de procesamiento:", processing_time, "ms")
    return OK

if __name__ == '__main__':
    main()
