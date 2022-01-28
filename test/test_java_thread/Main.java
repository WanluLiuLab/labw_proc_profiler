import static java.lang.Math.sqrt;

class MyThread extends Thread {
    private final int numToSqrt;
    private final int numOfRounds;
    private final int threadID;

    public static void performSqrt(int numToSqrt, int numOfRounds) {
        double[] result = new double[numToSqrt];
        for (int round = 0; round < numOfRounds; round++) {
            for (int i = 0; i < numToSqrt; i++) {
                result[i] = sqrt(i);
            }
        }
    }
    public MyThread(int numToSqrt, int numOfRounds, int threadID) {
        this.numToSqrt = numToSqrt;
        this.numOfRounds = numOfRounds;
        this.threadID = threadID;
        System.out.printf("Thread %d allocated%n", threadID);
    }

    @Override
    public void run() {
        System.out.printf("Thread %d start%n", threadID);
        performSqrt(this.numToSqrt, this.numOfRounds);
        System.out.printf("Thread %d end%n", threadID);
    }
}

public class Main {
    public static void main(String[] args) throws InterruptedException {
        int numToSqrt = Integer.parseInt(args[0]);
        int numOfRounds = Integer.parseInt(args[1]);
        int numOfThreads = Integer.parseInt(args[2]);
        Thread[] allThreads = new Thread[numOfThreads];
        for (int i = 0; i < numOfThreads; i++) {
            allThreads[i] = new MyThread(numToSqrt, numOfRounds, i);
        }
        for (int i = 0; i < numOfThreads; i++) {
            allThreads[i].start();
        }
        for (int i = 0; i < numOfThreads; i++) {
            allThreads[i].join();
            System.out.printf("Thread %d join%n", i);
        }
    }
}
