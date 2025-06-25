from flask import Flask, jsonify
import requests

app = Flask(__name__)
LOAD_BALANCER_URL = "http://load_balancer:6000"

@app.route("/charge", methods=["POST"])
def charge():
    try:
        r = requests.post(f"{LOAD_BALANCER_URL}/request_charge", timeout=2)
        print(f"✅ Forwarded to LB. Response: {r.status_code}, {r.text}")
        return jsonify({
            "status": "forwarded",
            "details": r.json()
        }), 200
    except Exception as e:
        print(f"❌ Error in charge(): {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)
