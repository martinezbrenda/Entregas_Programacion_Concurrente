import java.io.IOException;

class Level4
{
  static final int LEVEL_NUMBER = 4;
  static final int SLEEP_TIME_MS = 10000;

  public static void showInfo()
  {
    ProcessHandle me = ProcessHandle.current();

    System.out.println("\t\t\t└── Nivel " + LEVEL_NUMBER + ": Padre: " + me.parent().get().pid() + ", PID: " + me.pid());
  }

  public static void main(String[] args) throws InterruptedException
  {
    Thread.sleep(SLEEP_TIME_MS);
    showInfo();
  }
}
