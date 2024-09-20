import java.io.IOException;

class Level1
{
  static final int LEVEL_NUMBER = 1;
  static final String FOLLOWING_LEVEL = "Level2.java";
  static final String PROCESS_C_CHILD_NUMBER = "1";
  static final String PROCESS_D_CHILD_NUMBER = "2";
  static final String PROCESS_E_CHILD_NUMBER = "1A";
  static final String PROCESS_F_CHILD_NUMBER = "1B";
  static final String PROCESS_G_CHILD_NUMBER = "2B";

  static Process children[];

  public static void showInfo()
  {
    ProcessHandle me = ProcessHandle.current();

    System.out.println("└── Nivel " + LEVEL_NUMBER + ": Padre: " + me.parent().get().pid() + ", PID: " + me.pid());
  }

  public static void createChildren() throws IOException, InterruptedException
  {
    ProcessBuilder builder;

    children = new Process[2];

    

    builder = new ProcessBuilder("java", FOLLOWING_LEVEL, PROCESS_C_CHILD_NUMBER);
    builder.inheritIO();
    children[0] = builder.start();

    

    builder = new ProcessBuilder("java", FOLLOWING_LEVEL, PROCESS_D_CHILD_NUMBER);
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
    createChildren();
    waitChildren();

    showInfo();
  }
}
