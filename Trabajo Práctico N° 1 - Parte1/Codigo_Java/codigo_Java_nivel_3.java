import java.io.IOException;

class Level3
{
  static final int LEVEL_NUMBER = 3;
  static final int SLEEP_TIME_MS = 10000;
  static final String FOLLOWING_LEVEL = "Level4.java";
  static final String PROCESS_C_CHILD_NUMBER = "1";
  static final String PROCESS_D_CHILD_NUMBER = "2";
  static final String PROCESS_E_CHILD_NUMBER = "1A";
  static final String PROCESS_F_CHILD_NUMBER = "1B";
  static final String PROCESS_G_CHILD_NUMBER = "2B";

  static Process children[];

  public static void showInfo()
  {
    ProcessHandle me = ProcessHandle.current();

    System.out.println("\t\t└── Nivel " + LEVEL_NUMBER + ": Padre: " + me.parent().get().pid() + ", PID: " + me.pid());
  }

  public static void createChildren() throws IOException
  {
    ProcessBuilder builder;

    children = new Process[2];

    

    builder = new ProcessBuilder("java", FOLLOWING_LEVEL);
    builder.inheritIO();
    children[0] = builder.start();

    

    builder = new ProcessBuilder("java", FOLLOWING_LEVEL);
    builder.inheritIO();
    children[1] = builder.start();
  }

  public static void waitChildren() throws InterruptedException
  {
    children[0].waitFor();
    children[1].waitFor();
  }

  public static void main(String[] args) throws IOException, InterruptedException
  {
    String numberOfChild = args[0];

    if(numberOfChild.equals(PROCESS_E_CHILD_NUMBER))
    {
      createChildren();
      waitChildren();
      showInfo();
    }
    else
    {
      showInfo();
      Thread.sleep(SLEEP_TIME_MS);
    }
  }
}
