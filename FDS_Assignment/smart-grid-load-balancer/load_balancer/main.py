from flask import Flask, jsonify
import requests

app = Flask(__name__)

SUBSTATIONS = [
    "http://substation1:5000",
    "http://substation2:5000",
    "http://substation3:5000"
]

METRICS = [
    "http://substation1:9100",
    "http://substation2:9100",
    "http://substation3:9100"
]

@app.route("/request_charge", methods=["POST"])
def request_charge():
    best_index = None
    min_load = float('inf')

    for i, url in enumerate(METRICS):
        try:
            print(f"🔍 Checking {url}/metrics")
            resp = requests.get(f"{url}/metrics", timeout=1)
            print(resp.text)  # optional for deep debugging
            for line in resp.text.splitlines():
                if line.startswith("ev_charging_load ") and not line.startswith("#"):
                    load = float(line.split(" ")[-1])
                    print(f"📊 Substation {i+1} load = {load}")
                    if load < min_load:
                        min_load = load
                        best_index = i
        except Exception as e:
            print(f"❌ Failed to fetch metrics from {url}: {e}")

    if best_index is not None:
        try:
            post_url = f"{SUBSTATIONS[best_index]}/charge"
            print(f"🚀 Forwarding to substation: {post_url}")
            r = requests.post(post_url, timeout=2)
            return jsonify({
                "routed_to": post_url,
                "substation_response": r.json()
            }), 200
        except Exception as e:
            print(f"❌ Substation POST failed: {e}")
            return jsonify({"error": f"Substation failed: {str(e)}"}), 503
    else:
        return jsonify({"error": "No substations available"}), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)