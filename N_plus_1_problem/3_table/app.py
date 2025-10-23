from flask import Flask, request, jsonify, abort, g
import random

app = Flask(__name__)

roles = [
    {"id": 1, "row_name": "admin"},
    {"id": 2, "row_name": "manager"},
    {"id": 3, "row_name": "viewer"},
]
role_by_id = {r["id"]: r for r in roles}

random.seed(7)
users = [{"id": i, "name": f"user_{i}", "role_id": random.choice([1,2,3])}
         for i in range(1, 101)]

contacts = []
cid = 1
for u in users:
    for j in range(random.randint(1, 3)):
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

def query_roles_by_ids(role_ids):
    g.query_count += 1
    s = set(role_ids)
    return {r["id"]: r for r in roles if r["id"] in s}

@app.get("/users")
def list_users():
    limit = request.args.get("limit", default=10, type=int)
    limit = max(1, min(limit, len(users)))
    subset = query_users(limit)

    includes = {p.strip() for p in request.args.get("include", "").split(",") if p.strip()}
    fields = {k[7:-1]: {x.strip() for x in v.split(",") if x.strip()}
              for k, v in request.args.items() if k.startswith("fields[") and k.endswith("]")}

    contact_map = {}
    if "contacts" in includes:
        contact_map = query_contacts_by_user_ids([u["id"] for u in subset])

    role_map = {}
    if "role" in includes:
        role_map = query_roles_by_ids([u["role_id"] for u in subset])

    data = []
    for u in subset:
        item = {"id": u["id"], "name": u["name"], "role_id": u["role_id"]}
        if "contacts" in includes:
            cs = contact_map.get(u["id"], [])
            if fields.get("contacts") == {"email"}:
                item["contacts"] = [{"email": c["email"]} for c in cs]
            else:
                item["contacts"] = cs
        if "role" in includes:
            r = role_map.get(u["role_id"])
            if r:
                item["role"] = {"id": r["id"], "row_name": r["row_name"]}
                if fields.get("role"):
                    item["role"] = {k: v for k, v in item["role"].items() if k in fields["role"]}
            else:
                item["role"] = None
        data.append(item)

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

@app.get("/roles")
def list_roles():
    limit = request.args.get("limit", default=len(roles), type=int)
    limit = max(1, min(limit, len(roles)))
    return jsonify({"data": roles[:limit]})

@app.errorhandler(404)
def _not_found(err):
    return jsonify({"error": {"code": 404, "message": err.description}}), 404

if __name__ == "__main__":
    app.run(port=5001, debug=True)