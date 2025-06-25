import os
import json
import requests
from flask import Flask, request

app = Flask(__name__)

# Node configuration
NODE_NAME = os.environ.get("NODE_NAME")  # A, B, or C
NODE_PORT = int(os.environ.get("NODE_PORT"))

ALL_NODES = {
    'A': 'node1:5000',
    'B': 'node2:5001',
    'C': 'node3:5002'
}
OTHER_NODES = {k: v for k, v in ALL_NODES.items() if k != NODE_NAME}

vector_clock = {k: 0 for k in ALL_NODES}
store = {}
buffer = []

def broadcast_write(key, value):
    payload = {
        'type': 'write',
        'key': key,
        'value': value,
        'vector_clock': vector_clock.copy(),
        'sender': NODE_NAME
    }
    print(f"[{NODE_NAME}] Broadcasting write {key}={value}, VC={vector_clock}")
    for name, address in OTHER_NODES.items():
        try:
            res = requests.post(f"http://{address}/receive", json=payload, timeout=3)
            print(f"[{NODE_NAME}] Sent to {name} at {address}, status={res.status_code}")
        except Exception as e:
            print(f"[{NODE_NAME}] Failed to send to {name}: {e}")

def is_causally_ready(received_vc, sender):
    for node in received_vc:
        if node == sender:
            if received_vc[node] != vector_clock[node] + 1:
                return False
        else:
            if received_vc[node] > vector_clock[node]:
                return False
    return True

def apply_write(key, value, received_vc, sender):
    store[key] = value
    for node in vector_clock:
        vector_clock[node] = max(vector_clock[node], received_vc.get(node, 0))
    print(f"[{NODE_NAME}] Applied {key}={value}, VC={vector_clock}")

@app.route('/write', methods=['POST'])
def write():
    data = request.get_json()
    key = data['key']
    value = data['value']

    print(f"[{NODE_NAME}] Local write {key}={value}")
    store[key] = value
    vector_clock[NODE_NAME] += 1
    print(f"[{NODE_NAME}] Updated VC: {vector_clock}")
    
    try:
        broadcast_write(key, value)
    except Exception as e:
        print(f"[{NODE_NAME}] ERROR in broadcast: {e}")
    
    return {'status': 'write propagated'}


@app.route('/receive', methods=['POST'])
def receive():
    data = request.get_json()
    print(f"[{NODE_NAME}] Received write from {data['sender']} with key={data['key']} VC={data['vector_clock']}")
    if data['type'] == 'write':
        if is_causally_ready(data['vector_clock'], data['sender']):
            apply_write(data['key'], data['value'], data['vector_clock'], data['sender'])
            check_buffer()
        else:
            print(f"[{NODE_NAME}] Buffered write due to unmet causal dependency")
            buffer.append(data)
    return 'OK'

def check_buffer():
    global buffer
    delivered = []
    for msg in buffer:
        if is_causally_ready(msg['vector_clock'], msg['sender']):
            apply_write(msg['key'], msg['value'], msg['vector_clock'], msg['sender'])
            delivered.append(msg)
    for msg in delivered:
        buffer.remove(msg)

@app.route('/read', methods=['GET'])
def read():
    return {
        'store': store,
        'vector_clock': vector_clock
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=NODE_PORT)
