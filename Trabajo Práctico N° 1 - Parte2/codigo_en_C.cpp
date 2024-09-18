#include <iostream>
#include <fstream>
#include <string>
#include <thread>
#include <vector>
#include <mutex>
#include <chrono>

#define INITIAL_COUNT_VALUE 0
#define FILENAME_INDEX 1
#define NUM_THREADS_INDEX 2
#define EMPTY_FILE 0
#define INITIAL_POSITION 0
#define INITIAL_THREAD_COUNT 0
#define OK 0
#define ERROR 1
#define ERROR_ARCHIVO 1

std::mutex mutex;
std::vector<int> partial_results;

// Función para contar caracteres en un rango de líneas del archivo
void count_characters(const std::vector<std::string> &lines, int ini, int stop, int partial_result_pos)
{
    int count = INITIAL_COUNT_VALUE;
    for (int i = ini; i < stop; ++i)
    {
        count += lines[i].length();
    }

    // Proteger la región crítica donde se guarda el resultado parcial
    std::lock_guard<std::mutex> guard(mutex);
    partial_results[partial_result_pos] = count;
}

// Función para abrir y cerrar el archivo
std::ifstream open_file(const std::string &filename)
{
    std::ifstream text_file(filename);
    if (!text_file.is_open())
    {
        std::cout << "No se pudo abrir el archivo.\n";
        throw std::runtime_error("Archivo no encontrado");
    }
    return text_file;
}

// Función para leer todas las líneas del archivo
std::vector<std::string> read_lines(std::ifstream &text_file)
{
    std::vector<std::string> lines;
    std::string line;
    while (std::getline(text_file, line))
    {
        if (!line.empty())
        {
            lines.push_back(line);
        }
    }
    return lines;
}

// Función para crear y lanzar los threads
void create_threads(int num_threads, const std::vector<std::string> &lines, int num_lines)
{
    std::vector<std::thread> threads;
    int lines_per_thread = num_lines / num_threads;
    int initial_position = INITIAL_POSITION;

    for (int thread_count = INITIAL_THREAD_COUNT; thread_count < num_threads; ++thread_count)
    {
        int last_position = (thread_count == num_threads - 1) ? num_lines : initial_position + lines_per_thread;
        threads.push_back(std::thread(count_characters, std::ref(lines), initial_position, last_position, thread_count));
        initial_position = last_position;
    }

    // Esperar a que terminen todos los hilos
    for (auto &t : threads)
    {
        t.join();
    }
}

// Función para sumar los resultados parciales
int sum_partial_results(int num_threads)
{
    int total_result = INITIAL_COUNT_VALUE;
    for (int i = INITIAL_THREAD_COUNT; i < num_threads; ++i)
    {
        total_result += partial_results[i];
    }
    return total_result;
}

// Función para medir el tiempo de procesamiento y mostrar el resultado
void process_and_show_results(int total_result, std::chrono::high_resolution_clock::time_point start_time)
{
    auto finish_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> processing_time = finish_time - start_time;

    std::cout << "Cantidad de caracteres del archivo: " << total_result << std::endl;
    std::cout << "Tiempo de procesamiento: " << processing_time.count() << " ms" << std::endl;
}

int main(int argc, char *argv[])
{
    std::string filename = argv[FILENAME_INDEX];
    int num_threads = std::stoi(argv[NUM_THREADS_INDEX]);

    std::ifstream text_file;
    try{
        text_file = open_file(filename);
    }catch (const std::exception &e){
        return ERROR_ARCHIVO;               }

    std::vector<std::string> lines = read_lines(text_file);
    text_file.close();

    int num_lines = lines.size();
    if (num_lines == EMPTY_FILE)
    {
        std::cout << "El archivo está vacío o no contiene líneas válidas.\n";
        return OK;
    }
    partial_results.resize(num_threads, INITIAL_COUNT_VALUE);
    auto start_time = std::chrono::high_resolution_clock::now();
    create_threads(num_threads, lines, num_lines);
    int total_result = sum_partial_results(num_threads);
    process_and_show_results(total_result, start_time);

    return OK;
}
