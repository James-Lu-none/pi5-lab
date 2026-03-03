from flask import Flask, jsonify, request
import socket, struct, time

app = Flask(__name__)

PVE_MAC = "0a:e0:af:c2:13:65"
PVE_BROADCAST = "10.0.0.255"
PVE_PORT = 9
PVE_IP = "10.0.0.101"
PVE_HTTP_PORT = 8006

def send_magic_packet(mac, broadcast=PVE_BROADCAST, port=PVE_PORT):
    mac_bytes = bytes.fromhex(mac.replace(":", "").replace("-", ""))
    packet = b"\xff" * 6 + mac_bytes * 16
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(packet, (broadcast, port))

@app.route("/api/wol", methods=["POST"])
def api_wol():
    send_magic_packet(PVE_MAC)
    return jsonify({"status": "ok", "message": "Magic packet sent"})

@app.route("/api/status", methods=["GET"])
def api_status():
    start = time.monotonic()
    online = False
    try:
        with socket.create_connection((PVE_IP, PVE_HTTP_PORT), timeout=2):
            online = True
    except OSError:
        online = False
    latency_ms = int((time.monotonic() - start) * 1000)
    return jsonify({"online": online, "latency_ms": latency_ms})
