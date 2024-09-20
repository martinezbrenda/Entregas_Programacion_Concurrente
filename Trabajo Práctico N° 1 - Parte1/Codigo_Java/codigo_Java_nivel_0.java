import java.io.IOException;

public class Level0
{
  static final int LEVEL_NUMBER = 0;
  static final String FOLLOWING_LEVEL = "Level1.java";

  static Process children[];

  public static void showInfo()
  {
    ProcessHandle me = ProcessHandle.current();

    System.out.println("Nivel " + LEVEL_NUMBER + ": Proceso Raíz, PID: " + me.pid());
  }

  public static void createChildren() throws IOException
  {
    ProcessBuilder builder;

    children = new Process[1];

    

    builder = new ProcessBuilder("java", FOLLOWING_LEVEL);
    builder.inheritIO();
    children[0] = builder.start();
  }

  public static void waitChildren() throws InterruptedException
  {
    children[0].waitFor();
  }

  public static void main(String[] args) throws IOException, InterruptedException
  {
    createChildren();
    waitChildren();

    showInfo();
  }
}
