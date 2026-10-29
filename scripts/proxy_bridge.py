#!/usr/bin/env python3
# 把 127.0.0.1:7892 (HTTP 代理) 转发到 v2ray 实际监听的 127.0.0.1:8001
import socket, threading, sys

LISTEN = ('127.0.0.1', 7892)
TARGET = ('127.0.0.1', 8001)


def pipe(a, b):
    try:
        while True:
            data = a.recv(65536)
            if not data:
                break
            b.sendall(data)
    except Exception:
        pass
    finally:
        for s in (a, b):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                s.close()
            except Exception:
                pass


def handle(c):
    try:
        up = socket.create_connection(TARGET, timeout=15)
    except Exception:
        c.close()
        return
    threading.Thread(target=pipe, args=(c, up), daemon=True).start()
    threading.Thread(target=pipe, args=(up, c), daemon=True).start()


srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(LISTEN)
srv.listen(64)
sys.stderr.write('proxy bridge 7892 -> 8001 up\n')
sys.stderr.flush()
while True:
    conn, _ = srv.accept()
    threading.Thread(target=handle, args=(conn,), daemon=True).start()
