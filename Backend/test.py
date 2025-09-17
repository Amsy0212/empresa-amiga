import requests

BASE_URL = "http://localhost:2347"

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    print("/health:", r.status_code, r.json())

def test_db_ping():
    r = requests.get(f"{BASE_URL}/db-ping")
    print("/db-ping:", r.status_code, r.json())

if __name__ == "__main__":
    test_health()
    test_db_ping()

