import requests
import time

nodes = {
    'A': 'http://localhost:5000',
    'B': 'http://localhost:5001',
    'C': 'http://localhost:5002'
}

def print_all_node_states():
    for name, url in nodes.items():
        try:
            resp = requests.get(f"{url}/read")
            data = resp.json()
            print(f"Node {name} store: {data['store']}, VC: {data['vector_clock']}")
        except Exception as e:
            print(f"Node {name} unreachable: {e}")
    print("-" * 60)
    time.sleep(1)

def test_scenario():
    print("Writing x=1 to node A (5000)")
    requests.post(f"{nodes['A']}/write", json={'key': 'x', 'value': '1'})
    time.sleep(1)
    print_all_node_states()

    print("Writing y=2 to node B (5001)")
    requests.post(f"{nodes['B']}/write", json={'key': 'y', 'value': '2'})
    time.sleep(1)
    print_all_node_states()

    print("Writing z=3 to node C (5002)")
    requests.post(f"{nodes['C']}/write", json={'key': 'z', 'value': '3'})
    time.sleep(1)
    print_all_node_states()

if __name__ == '__main__':
    test_scenario()
