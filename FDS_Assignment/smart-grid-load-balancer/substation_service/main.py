from flask import Flask, jsonify
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST, start_http_server
import threading
import time
import random

app = Flask(__name__)

# Prometheus metric
load_gauge = Gauge("ev_charging_load", "Current charging load")
current_load = 0

@app.route("/charge", methods=["POST"])
def charge():
    global current_load
    current_load += 1
    load_gauge.set(current_load)

    def simulate_charging():
        time.sleep(random.randint(2, 5))
        global current_load
        current_load -= 1
        load_gauge.set(current_load)

    threading.Thread(target=simulate_charging).start()

    return jsonify({"status": "charging started"}), 200

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    start_http_server(9100)            # Metrics on 9100
    app.run(host="0.0.0.0", port=5000) # Flask on 5000
