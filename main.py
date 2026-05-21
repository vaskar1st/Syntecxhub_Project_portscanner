import socket
import threading
from queue import Queue

# ================= INPUT =================
target = input("Enter target (IP/domain): ")

try:
    target_ip = socket.gethostbyname(target)
except socket.gaierror:
    print("Invalid host.")
    exit()

start_port = int(input("Start Port: "))
end_port = int(input("End Port: "))

print(f"\nScanning {target} ({target_ip}) from port {start_port} to {end_port}\n")

# ================= SETTINGS =================
THREADS = 50
TIMEOUT = 1
LOG_FILE = "results.txt"

# ================= GLOBALS =================
queue = Queue()
lock = threading.Lock()
open_ports = []   # ⭐ NEW

# ================= LOG FUNCTION =================
def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

# ================= SCAN FUNCTION =================
def scan(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)

        result = s.connect_ex((target_ip, port))

        if result == 0:
            msg = f"[OPEN] Port {port}"
            open_ports.append(port)   # ⭐ NEW
        elif result == 1:
            msg = f"[CLOSED] Port {port}"
        else:
            msg = f"[TIMEOUT] Port {port}"

        with lock:
            print(msg)
            log(msg)

        s.close()

    except Exception as e:
        with lock:
            print(f"[ERROR] Port {port}: {e}")

# ================= WORKER =================
def worker():
    while not queue.empty():
        port = queue.get()
        scan(port)
        queue.task_done()

# ================= ADD PORTS =================
for port in range(start_port, end_port + 1):
    queue.put(port)

# ================= START THREADS =================
for _ in range(THREADS):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

queue.join()

# ================= FINAL OUTPUT =================
print("\n[+] Scan Completed.")
print(f"[+] Results saved in {LOG_FILE}")

print("\n[+] Open Ports Found:")
print(open_ports)
