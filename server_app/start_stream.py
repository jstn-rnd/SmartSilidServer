from vidstream import ScreenShareClient
import threading

server_ip = 'your_server_ip'  # Local IP or use 127.0.0.1 if local

sender = ScreenShareClient(server_ip, 9999)

t = threading.Thread(target=sender.start_stream)
t.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    sender.stop_stream()