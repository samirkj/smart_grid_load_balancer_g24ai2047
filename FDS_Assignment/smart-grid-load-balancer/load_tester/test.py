import requests
import time

substations = [
    "http://localhost:9101/metrics",  # substation1
    "http://localhost:9102/metrics",  # substation2
    "http://localhost:9103/metrics"   # substation3
]

def get_load(url):
    try:
        resp = requests.get(url, timeout=1)
        for line in resp.text.splitlines():
            if line.startswith("ev_charging_load "):
                return float(line.split(" ")[-1])
    except Exception as e:
        print(f"Failed to get metrics from {url}: {e}")
    return None

for i in range(100):
    # Step 1: Get current load from all substations
    loads = [get_load(url) for url in substations]
    print(f"[{i}] Substation Loads → [S1: {loads[0]}, S2: {loads[1]}, S3: {loads[2]}]")

    # Step 2: Send a charge request via the load balancer
    try:
        r = requests.post("http://localhost:7000/charge", timeout=3)
        data = r.json()
        print(f"[{i}] Routed to: {data['details']['routed_to']}")
    except Exception as e:
        print(f"[{i}] ERROR during charge request: {e}")

    time.sleep(0.6)  # short pause between requests
