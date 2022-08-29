import time

if __name__ == "__main__":
    lb = 1 * 1024 * 1024 * 1024
    a = bytearray(lb)
    a[lb - 1] = 5
    time.sleep(10)
    del a
