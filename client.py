# client.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import socket
import threading

class NetworkManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.socket = None
            cls._instance.connect()
        return cls._instance

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('192.168.138.161', 2525))
        except Exception as e:
            messagebox.showerror("连接错误", f"无法连接服务器: {str(e)}")

    def send(self, msg):
        self.socket.sendall(f"{msg}\n".encode())

    def receive(self):
        return self.socket.recv(1024).decode().strip()

    def close(self):
        self.socket.close()

class CardInsertionFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ATM")
        self.geometry("400x240")

        ttk.Label(self, text="欢迎使用银行系统", font=('Arial', 14)).pack(pady=10)
        ttk.Label(self, text="请输入用户名:").pack()
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack(pady=5)

        ttk.Button(self, text="确定", command=self.on_submit).pack(pady=10)

    def on_submit(self):
        username = self.username_entry.get()
        if not username:
            messagebox.showerror("错误", "用户名不能为空")
            return
        NetworkManager().send(f"HELO {username}")
        response = NetworkManager().receive()
        if response.startswith("500 AUTH REQUIRE"):
            self.destroy()
            LoginFrame()
        else:
            messagebox.showerror("错误", "无效用户名")
            self.username_entry.delete(0, tk.END)

class LoginFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ATM")
        self.geometry("400x240")

        ttk.Label(self, text="请输入密码:", font=('Arial', 12)).pack(pady=10)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack()

        ttk.Button(self, text="登录", command=self.on_login).pack(pady=10)

    def on_login(self):
        password = self.password_entry.get()
        NetworkManager().send(f"PASS {password}")
        response = NetworkManager().receive()
        if response.startswith("525 OK!"):
            self.destroy()
            ServiceFrame()
        else:
            messagebox.showerror("错误", "密码错误")
            self.password_entry.delete(0, tk.END)

class ServiceFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ATM服务")
        self.geometry("400x300")

        self.balance_label = ttk.Label(self, text="", font=('Arial', 12))
        self.balance_label.pack(pady=10)

        ttk.Button(self, text="查询余额", command=self.check_balance).pack(pady=5)
        ttk.Button(self, text="取款", command=self.withdraw).pack(pady=5)
        ttk.Button(self, text="退出", command=self.quit).pack(pady=5)

    def check_balance(self):
        NetworkManager().send("BALA")
        response = NetworkManager().receive()
        if response.startswith("AMNT:"):
            balance = response.split(":")[1]
            self.balance_label.config(text=f"当前余额: {balance}")
        else:
            messagebox.showerror("错误", "查询余额失败")

    def withdraw(self):
        amount = simpledialog.askinteger("取款", "请输入取款金额:")
        if amount is not None:
            NetworkManager().send(f"WDRA {amount}")
            response = NetworkManager().receive()
            if response.startswith("525 OK!"):
                self.balance_label.config(text=f"取款成功! 当前余额: {self.get_balance()}")
                messagebox.showinfo("成功", "取款成功")
            else:
                messagebox.showerror("错误", "余额不足或取款失败")

    def get_balance(self):
        NetworkManager().send("BALA")
        response = NetworkManager().receive()
        if response.startswith("AMNT:"):
            return response.split(":")[1]
        return "查询失败"

    def quit(self):
        NetworkManager().send("BYE")
        NetworkManager().close()
        self.destroy()

if __name__ == "__main__":
    app = CardInsertionFrame()
    app.mainloop()