import subprocess
import time

def ping_host(address):
    try:
        start = time.time()

        result = subprocess.run(
            ["ping", "-n", "1", address],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        end = time.time()
        latency = (end - start) * 1000

        if result.returncode == 0:
            return "UP", latency, None
        else:
            return "DOWN", None, result.stderr

    except Exception as e:
        return "DOWN", None, str(e)