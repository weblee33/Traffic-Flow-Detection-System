import time
import subprocess

while True:
    subprocess.run(["python", "detector/detect_demo.py"])
    time.sleep(30)  # 每 30 秒執行一次
