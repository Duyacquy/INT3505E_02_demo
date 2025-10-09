# version2/app.py
from flask import Flask, request, jsonify, make_response, url_for
from datetime import datetime, timedelta, timezone
import hashlib
import jwt 

app = Flask(__name__)

def now_rfc3339():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "updatedAt": now_rfc3339()},
    {"id": 2, "title": "REST in Practice", "author": "Webber et al.", "updatedAt": now_rfc3339()},
]
next_id = 3

def respond_json(payload, status=200, etag=None, cache_seconds=60):
    resp = make_response(jsonify(payload), status)
    resp.headers["Content-Type"] = "application/json"
    resp.headers["X-Served-By"] = "books-service-v2"
    resp.headers["Vary"] = "Accept"
    resp.headers["Cache-Control"] = f"public, max-age={cache_seconds}"
    if etag:
        resp.headers["ETag"] = etag
    return resp

def not_modified_response(etag=None, cache_seconds=60):
    resp = make_response("", 304)
    resp.headers["Cache-Control"] = f"public, max-age={cache_seconds}"
    resp.headers["X-Served-By"] = "books-service-v2"
    resp.headers["Vary"] = "Accept"
    if etag:
        resp.headers["ETag"] = etag
    return resp

def collection_etag(items):
    stamp = "|".join(sorted(f"{b['id']}:{b['updatedAt']}" for b in items))
    return f'W/"{hashlib.sha256(stamp.encode()).hexdigest()[:16]}"'

def check_if_none_match(etag=None):
    inm = request.headers.get("If-None-Match")
    return bool(etag and inm and etag in inm)

JWT_SECRET = "change-me-in-prod"
JWT_ISSUER = "books-service-v2"
JWT_AUDIENCE = "books-clients"
JWT_ACCESS_TTL = timedelta(minutes=30)

def issue_jwt(subject: str, scopes=None):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "scope": " ".join(scopes or []),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + JWT_ACCESS_TTL).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt_from_request(required_scopes=None):
    auth = request.headers.get("Authorization", "")
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None, "Missing or malformed Authorization header"
    token = parts[1]
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            options={"require": ["exp", "iat"]}
        )
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError as e:
        return None, f"Invalid token: {e}"

    if required_scopes:
        have = set((payload.get("scope") or "").split())
        need = set(required_scopes)
        if not need.issubset(have):
            return None, "Insufficient scope"
    return payload, None

def require_auth(*scopes):
    payload, err = verify_jwt_from_request(required_scopes=scopes or None)
    if err:
        return respond_json({"error": "Unauthorized", "detail": err}, 401, cache_seconds=0)
    request.jwt_payload = payload  
    return None

@app.post("/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or password != "demo-password":
        return respond_json({"error": "Invalid credentials"}, 401, cache_seconds=0)

    token = issue_jwt(subject=username, scopes=["books:write"])
    return respond_json({
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": int(JWT_ACCESS_TTL.total_seconds()),
        "scope": "books:write"
    }, 200, cache_seconds=0)

@app.get("/books")
def list_books():
    try:
        page = max(1, int(request.args.get("page", "1")))
        per_page = min(50, max(1, int(request.args.get("per_page", "10"))))
    except ValueError:
        return respond_json({"error": "Invalid pagination"}, 400)

    start = (page - 1) * per_page
    end = start + per_page
    items = books[start:end]

    etag = collection_etag(books)
    if check_if_none_match(etag):
        return not_modified_response(etag)

    payload = {
        "page": page,
        "per_page": per_page,
        "total": len(books),
        "items": items,
        "_links": {
            "self": {"href": url_for("list_books", page=page, per_page=per_page, _external=True)},
            "create": {"href": url_for("create_book", _external=True), "method": "POST"},
        },
    }
    return respond_json(payload, etag=etag)

@app.post("/books")
def create_book():
    err = require_auth("books:write")
    if err:
        return err

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    if not title or not author:
        return respond_json({"error": "title and author are required"}, 400)

    global next_id
    book = {"id": next_id, "title": title, "author": author, "updatedAt": now_rfc3339()}
    next_id += 1
    books.append(book)

    resp = respond_json(book, status=201, cache_seconds=0)
    resp.headers["Location"] = url_for("list_books", _external=True)
    return resp

@app.delete("/books/<int:id>")
def delete_book(id):
    err = require_auth("books:write")
    if err:
        return err

    global books
    before = len(books)
    books = [b for b in books if b["id"] != id]
    if len(books) == before:
        return respond_json({"error": "Not Found"}, 404)
    resp = make_response("", 204)
    resp.headers["X-Served-By"] = "books-service-v2"
    return resp

if __name__ == "__main__":
    app.run(debug=True)