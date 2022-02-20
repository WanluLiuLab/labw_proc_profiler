from proc_profiler import main

if __name__ == "__main__":
    exit(main(["sh", "-c", "dd if=/dev/random of=/dev/stdout count=1000000 | gzip  -c -f > /dev/null"]))
