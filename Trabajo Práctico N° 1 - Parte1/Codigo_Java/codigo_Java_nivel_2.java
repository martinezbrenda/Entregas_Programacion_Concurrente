import java.io.IOException;

class Level2
{
  static final int LEVEL_NUMBER = 2;
  static final String FOLLOWING_LEVEL = "Level3.java";
  static final String PROCESS_C_CHILD_NUMBER = "1";
  static final String PROCESS_D_CHILD_NUMBER = "2";
  static final String PROCESS_E_CHILD_NUMBER = "1A";
  static final String PROCESS_F_CHILD_NUMBER = "1B";
  static final String PROCESS_G_CHILD_NUMBER = "2B";

  static Process children[];

  public static void showInfo()
  {
    ProcessHandle me = ProcessHandle.current();
    System.out.println("\t└── Nivel " + LEVEL_NUMBER + ": Padre: " + me.parent().get().pid() + ", PID: " + me.pid());
  }

  public static void createChildren(String numberOfChild) throws IOException
  {
    ProcessBuilder builder;

    if(numberOfChild.equals(PROCESS_C_CHILD_NUMBER))
    {
      children = new Process[1];

      

      builder = new ProcessBuilder("java", FOLLOWING_LEVEL, PROCESS_E_CHILD_NUMBER);
      builder.inheritIO();
      children[0] = builder.start();
    }
    else
    {
      children = new Process[2];

      

      builder = new ProcessBuilder("java", FOLLOWING_LEVEL, PROCESS_F_CHILD_NUMBER);
      builder.inheritIO();
      children[0] = builder.start();

      

      builder = new ProcessBuilder("java", FOLLOWING_LEVEL, PROCESS_G_CHILD_NUMBER);
      builder.inheritIO();
      children[1] = builder.start();
    }
  }

  public static void waitChildren(String numberOfChild) throws InterruptedException
  {
    if(numberOfChild.equals(PROCESS_C_CHILD_NUMBER))
    {
      children[0].waitFor();
    }
    else
    {
      children[0].waitFor();
      children[1].waitFor();
    }
  }

  public static void main(String[] args) throws IOException, InterruptedException
  {
    String numberOfChild = args[0];

    createChildren(numberOfChild);
    waitChildren(numberOfChild);

    showInfo();
  }
}
