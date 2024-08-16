# from vidstream import ScreenShareClient
# import threading

# server_ip = '192.168.10.119'  # Local IP or use 127.0.0.1 if local

# sender = ScreenShareClient(server_ip, 8000)

# t = threading.Thread(target=sender.start_stream)
# t.start()

# try:
#     while True:
#         pass
# except KeyboardInterrupt:
#     sender.stop_stream()