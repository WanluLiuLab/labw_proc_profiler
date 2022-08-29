import os
import gc
import time

gb_bytes = bytearray(1024*1024*1024)
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_FILE = os.path.join(FILE_DIR, "tmp")

if __name__ == "__main__":
    with open(TMP_FILE, "wb") as writer:
        writer.write(gb_bytes)

    del gb_bytes
    gc.collect()
    time.sleep(5)

    with open(TMP_FILE, "rb") as reader:
        gb_bytes = reader.read()

    del gb_bytes
    gc.collect()
    time.sleep(5)

    os.remove(TMP_FILE)
