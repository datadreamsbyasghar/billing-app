import requests

BASE_URL = "http://127.0.0.1:8000"

# -----------------------------
# 0. Login with your registered user
# -----------------------------
login_payload = {
    "username": "admin2",   # change to "staff1" or "user1" depending on test
    "password": "Admin@12345"
}
resp = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
print("Login:", resp.status_code, resp.json())

if resp.status_code == 200:
    data = resp.json()
    token = data["access_token"]
    role = data["role"]
    headers = {"Authorization": f"Bearer {token}"}

    print(f"\n✅ Logged in successfully as role: {role}\n")

    if role == "admin":
      print("=== ADMIN PORTAL TESTS ===")

      # Register a new staff user
      register_payload = {
          "username": "staff3",
          "password": "Staff@12345",
          "role": "staff"
      }
      resp = requests.post(f"{BASE_URL}/auth/register", json=register_payload, headers=headers)
      print("Register Staff:", resp.status_code, resp.json())

      # Add a product
      product_payload = {"name": "Marker", "price": 30, "stock": 50}
      resp = requests.post(f"{BASE_URL}/products/add", json=product_payload, headers=headers)
      print("Add Product:", resp.status_code, resp.json())

      # List products
      resp = requests.get(f"{BASE_URL}/products/list", headers=headers)
      print("List Products:", resp.status_code, resp.json())

      # Update product price
      update_price_payload = {"product_id": 1, "new_price": 55}
      resp = requests.post(f"{BASE_URL}/products/update_price", json=update_price_payload, headers=headers)
      print("Update Price:", resp.status_code, resp.json())

      # Update product stock
      update_stock_payload = {"product_id": 1, "new_stock": 120}
      resp = requests.post(f"{BASE_URL}/products/update_stock", json=update_stock_payload, headers=headers)
      print("Update Stock:", resp.status_code, resp.json())

      # Analytics summary
      resp = requests.get(f"{BASE_URL}/analytics/summary", headers=headers)
      print("Analytics Summary:", resp.status_code, resp.json())

      # Export monthly CSV
      resp = requests.get(f"{BASE_URL}/export/monthly_csv?year=2025&month=12", headers=headers)
      print("Export CSV:", resp.status_code, resp.text[:200], "...")
    # -----------------------------
    # User Portal Tests
    # -----------------------------
    if role == "user":
        print("=== USER PORTAL TESTS ===")

        # 1. List products (read-only)
        resp = requests.get(f"{BASE_URL}/products/list", headers=headers)
        print("List Products:", resp.status_code, resp.json())

        # 2. List bills (read-only)
        resp = requests.get(f"{BASE_URL}/bills/list", headers=headers)
        print("List Bills:", resp.status_code, resp.json())

        # 3. View a bill detail (read-only)
        resp = requests.get(f"{BASE_URL}/bills/1", headers=headers)
        print("Bill Details:", resp.status_code, resp.json())

        # 4. View client list (read-only)
        resp = requests.get(f"{BASE_URL}/clients/list", headers=headers)
        print("Client List:", resp.status_code, resp.json())

else:
    print("❌ Login failed, cannot test protected routes.")