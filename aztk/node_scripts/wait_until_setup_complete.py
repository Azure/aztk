import time
import os


while not os.path.exists('/tmp/setup_complete'):
    time.sleep(1)

print("SETUP FINSIHED")
os.remove('/tmp/setup_complete')
