from docker_profiler import main

if __name__ == "__main__":
    exit(main(
        'busybox',
        ["sh", "-c", "\'dd if=/dev/random of=/dev/stdout count=1000000 bs=512 | gzip  -c -f > /dev/null\'"]
    ))
