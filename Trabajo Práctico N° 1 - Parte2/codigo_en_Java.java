import java.io.IOException;
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.locks.ReentrantLock;

public class CountCharacters
{
    private static final int INITIAL_COUNT_VALUE = 0;
    private static final int FILENAME_INDEX = 0;
    private static final int NUM_THREADS_INDEX = 1;
    private static final int EMPTY_FILE = 0;
    private static final int INITIAL_POSITION = 0;
    private static final int INITIAL_THREAD_COUNT = 0;
    private static final int OK = 0;
    private static final int ERROR = 1;

    
    private static List<String> lines = new ArrayList<>();

    
    private static int partialResults[];

    
    private static final ReentrantLock mutex = new ReentrantLock();

    public static class CharacterCounterThread extends Thread
    {
      private int ini,stop,partialResultPos;

      public CharacterCounterThread(int ini, int stop, int partialResultPos)
      {
        this.ini = ini;
        this.stop = stop;
        this.partialResultPos = partialResultPos;
      }

      @Override
public void run() {
            countCharactersInRange(ini, stop, partialResultPos);
        }
    }

    private static void countCharactersInRange(int ini, int stop, int partialResultPos) {
        int count = INITIAL_COUNT_VALUE;
        for (int i = ini; i < stop; ++i) {
            count += lines.get(i).length();
        }

        mutex.lock();
        try {
            partialResults[partialResultPos] = count;
        } finally {
            mutex.unlock();
        }
    }

    private static List<String> readLinesFromFile(String filename) {
        List<String> lines = new ArrayList<>();
        try (BufferedReader fileReader = new BufferedReader(new FileReader(filename))) {
            String line;
            while ((line = fileReader.readLine()) != null) {
                if (!line.trim().isEmpty()) {
                    lines.add(line);
                }
            }
        } catch (IOException e) {
            System.out.println("No se pudo abrir el archivo.");
            System.exit(ERROR);
        }
        return lines;
    }

    private static int calculateTotalResult(int numThreads) {
        int totalResult = INITIAL_COUNT_VALUE;
        for (int i = INITIAL_THREAD_COUNT; i < numThreads; i++) {
            totalResult += partialResults[i];
        }
        return totalResult;
    }

    private static void startThreads(int numThreads, int numLines) throws InterruptedException {
        CharacterCounterThread[] threads = new CharacterCounterThread[numThreads];
        int linesPerThread = numLines / numThreads;
        int initialPosition = INITIAL_POSITION;

        for (int threadCount = INITIAL_THREAD_COUNT; threadCount < numThreads; threadCount++) {
            int lastPosition = (threadCount == numThreads - 1) ? numLines : initialPosition + linesPerThread;
            threads[threadCount] = new CharacterCounterThread(initialPosition, lastPosition, threadCount);
            threads[threadCount].start();
            initialPosition = lastPosition;
        }

        for (CharacterCounterThread thread : threads) {
            thread.join();
        }
    }

    private static void printResults(int totalResult, double processingTime) {
        System.out.println("Cantidad de caracteres del archivo: " + totalResult);
        System.out.println("Tiempo de procesamiento: " + processingTime + " ms");
    }

public static void main(String[] args) throws InterruptedException {
        String filename = args[FILENAME_INDEX];
        int numThreads = Integer.parseInt(args[NUM_THREADS_INDEX]);
        lines = readLinesFromFile(filename);
        int numLines = lines.size();
        if (numLines == EMPTY_FILE) {
            System.out.println("El archivo está vacío o no contiene líneas válidas.");
            System.exit(OK);
        }
        partialResults = new int[numThreads];
        double startTime = System.nanoTime() / 1_000_000.0;
        startThreads(numThreads, numLines);
        int totalResult = calculateTotalResult(numThreads);
        double finishTime = System.nanoTime() / 1_000_000.0;
        double processingTime = finishTime - startTime;
        printResults(totalResult, processingTime);

        System.exit(OK);
    }
}
