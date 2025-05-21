# server.py
import socket
import threading
from datetime import datetime

class ATMServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', 2525))
        self.sock.listen(5)
        self.log_file = open("atm.log", "a")

        # 硬编码的用户信息
        self.users = {
            "admin": {"password": "admin123", "balance": 1000.0},
            "user": {"password": "123", "balance": 500.0}
        }
        print("服务器已启动，等待连接...")

    def log(self, username, service, response):
        entry = f"{datetime.now()} | {username} | {service} | {response}\n"
        self.log_file.write(entry)
        self.log_file.flush()

    def handle_client(self, conn, addr):
        try:
            username = None
            authenticated = False

            while True:
                data = conn.recv(1024).decode().strip()
                if not data:
                    break

                if data.startswith("HELO"):
                    username = data.split()[1]
                    if username in self.users:
                        conn.send(b"500 AUTH REQUIRE")
                        self.log(username, "HELO", "500 AUTH REQUIRE")
                    else:
                        conn.send(b"401 ERROR")
                        self.log(username, "HELO", "401 ERROR!")
                        break

                elif data.startswith("PASS"):
                    password = data.split()[1]
                    if username and self.users.get(username, {}).get("password") == password:
                        authenticated = True
                        conn.send(b"525 OK!")
                        self.log(username, "PASS", "525 OK!")
                    else:
                        conn.send(b"401 ERROR")
                        self.log(username, "PASS", "401 ERROR!")
                        break

                elif data == "BALA" and authenticated:
                    balance = self.users.get(username, {}).get("balance", 0.0)
                    conn.send(f"AMNT:{balance}".encode())
                    self.log(username, "BALA", f"AMNT:{balance}")

                elif data.startswith("WDRA") and authenticated:
                    try:
                        amount = float(data.split()[1])
                        if username and self.users.get(username, {}).get("balance", 0.0) >= amount:
                            self.users[username]["balance"] -= amount
                            conn.send(b"525 OK!")
                            self.log(username, "WDRA", "525 OK!")
                        else:
                            conn.send(b"401 ERROR")
                            self.log(username, "WDRA", "401 ERROR!")
                    except ValueError:
                        conn.send(b"401 ERROR")
                        self.log(username, "WDRA", "401 ERROR!")

                elif data == "BYE":
                    conn.send(b"BYE")
                    self.log(username, "BYE", "BYE")
                    break

                else:
                    conn.send(b"401 ERROR")
                    break
        finally:
            conn.close()

    def run(self):
        while True:
            conn, addr = self.sock.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    server = ATMServer()
    server.run()