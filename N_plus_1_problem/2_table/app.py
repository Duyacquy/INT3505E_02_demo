from flask import Flask, request, jsonify, abort, g
import random

app = Flask(__name__)

users = [{"id": i, "name": f"user_{i}"} for i in range(1, 101)]
contacts = []
cid = 1
random.seed(42)
for u in users:
    for j in range(random.randint(1, 2)):
        contacts.append({"id": cid, "user_id": u["id"], "email": f'{u["name"]}+{j}@example.com'})
        cid += 1

@app.before_request
def _reset_counter():
    g.query_count = 0

def query_users(limit: int):
    g.query_count += 1
    return users[:limit]

def query_contacts_by_user_ids(user_ids):
    g.query_count += 1
    s = set(user_ids)
    grouped = {}
    for c in contacts:
        if c["user_id"] in s:
            grouped.setdefault(c["user_id"], []).append(c)
    return grouped

@app.get("/users")
def list_users():
    limit = request.args.get("limit", default=10, type=int)
    limit = max(1, min(limit, len(users)))
    subset = query_users(limit)

    includes = {p.strip() for p in request.args.get("include", "").split(",") if p.strip()}

    if "contacts" in includes:
        user_ids = [u["id"] for u in subset]
        contact_map = query_contacts_by_user_ids(user_ids)
        data = []
        for u in subset:
            data.append({
                "id": u["id"],
                "name": u["name"],
                "contacts": contact_map.get(u["id"], [])
            })
    else:
        data = [{"id": u["id"], "name": u["name"]} for u in subset]

    return jsonify({"data": data, "meta": {"limit": limit, "queries_executed": g.query_count}})

@app.get("/users/<int:user_id>")
def get_user(user_id: int):
    for u in users:
        if u["id"] == user_id:
            return jsonify({"data": u})
    abort(404, description="user not found")

@app.get("/contacts")
def list_contacts():
    limit = request.args.get("limit", default=len(contacts), type=int)
    limit = max(1, min(limit, len(contacts)))
    return jsonify({"data": contacts[:limit]})

@app.get("/contacts/<int:contact_id>")
def get_contact(contact_id: int):
    for c in contacts:
        if c["id"] == contact_id:
            return jsonify({"data": c})
    abort(404, description="contact not found")

if __name__ == "__main__":
    app.run(port=5000, debug=True)


# 2 bảng:
# GET http://localhost:5000/users?limit=50
# GET http://localhost:5000/users?limit=50&include=contacts

# 3 bảng:
# GET http://localhost:5001/users?limit=100&include=contacts,role
# GET http://localhost:5001/users?limit=100&include=contacts,role&fields[role]=row_name&fields[contacts]=email