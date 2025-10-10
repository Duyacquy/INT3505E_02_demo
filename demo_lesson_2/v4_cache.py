from flask import Flask, jsonify, request, g, make_response
from functools import wraps
import time, json, hashlib
import jwt

app = Flask(__name__)

SECRET_KEY = "DEMO_V3"
ALGORITHM = "HS256"
ACCESS_TTL = 3600

public_books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "REST in Practice", "author": "Webber et al."},
]

protected_books = [
    {"id": 1, "title": "Clean Code Pro VIP", "author": "Robert C. Martin"},
    {"id": 2, "title": "REST in Practice PREMIUM", "author": "Webber et al."},
]

#-----------------------------STATELESS------------------------------
def create_access_token(sub: str, extra: dict | None = None) -> str:
    now = int(time.time())
    payload = {
        "iss": "your-api",     
        "sub": sub,           
        "iat": now,            
        "exp": now + ACCESS_TTL,  
        **(extra or {}),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return _unauthorized("Missing Bearer token")

        token = auth.split(" ", 1)[1].strip()
        try:
            claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return _unauthorized("Token expired")
        except jwt.InvalidTokenError:
            return _unauthorized("Invalid token")

        g.current_user = claims.get("sub")
        g.claims = claims
        return f(*args, **kwargs)
    return wrapper

def _unauthorized(message="Unauthorized"):
    resp = jsonify({"error": message})
    resp.status_code = 401
    resp.headers["WWW-Authenticate"] = 'Bearer realm="api", error="invalid_token"'
    return resp

# -------------------------------CACHE------------------------------
def compute_etag(data) -> str:
    """ETag = MD5 của payload JSON (ổn cho demo)."""
    raw = json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.md5(raw).hexdigest()

def cacheable_json(data, max_age: int = 300, is_public: bool = True):
    """
    Trả JSON có ETag + Cache-Control.
    Hỗ trợ If-None-Match để trả 304 Not Modified.
    """
    etag = compute_etag(data)
    inm = request.if_none_match
    if inm and etag in inm:
        resp = make_response("", 304)
        resp.set_etag(etag)
        if is_public:
            resp.cache_control.public = True
        else:
            resp.cache_control.private = True
        resp.cache_control.max_age = max_age
        return resp

    resp = make_response(jsonify(data), 200)
    resp.set_etag(etag)
    if is_public:
        resp.cache_control.public = True
    else:
        resp.cache_control.private = True
    resp.cache_control.max_age = max_age
    return resp

@app.route("/")
def home():
    return "Đây là trang chủ"

# Public books
@app.get("/public-books")
def get_public_books():
    return cacheable_json(public_books, max_age=300, is_public=True)

# Protected (yêu cầu JWT)
@app.get("/protected-books")
@require_auth
def get_books_protected():
    return jsonify({"user": g.get("current_user"), "items": protected_books}), 200

@app.post("/auth/login")
def login():
    username = (request.get_json() or {}).get("username", "guest")
    token = create_access_token(sub=username, extra={"role": "reader"})
    return jsonify({"access_token": token, "token_type": "Bearer", "expires_in": ACCESS_TTL}), 200

if __name__ == "__main__":
    app.run(debug=True)