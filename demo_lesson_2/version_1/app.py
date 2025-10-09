# version1/app.py
from flask import Flask, redirect, request, make_response
from datetime import datetime
import uuid, json

app = Flask(__name__)

books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "updatedAt": datetime.utcnow().isoformat() + "Z"},
    {"id": 2, "title": "REST in Practice", "author": "Webber et al.", "updatedAt": datetime.utcnow().isoformat() + "Z"},
]

server_sessions = {}
next_id = 3

def get_or_create_session(resp=None):
    sid = request.cookies.get("sid")

    if not sid or sid not in server_sessions:
        sid = str(uuid.uuid4())
        print(sid)
        server_sessions[sid] = {}
        if resp:
            resp.set_cookie("sid", sid, httponly=True)
    return sid

# Đặt tên API chưa tốt
@app.get('/getAllBooks')
def get_all_books():
    # Trả về html khiến frontend và backend lẫn lộn
    html = f"<h1>Books</h1><pre>{json.dumps(books, indent=2)}</pre>"
    resp = make_response(html, 200)
    get_or_create_session(resp) 
    return resp

# Đặt tên API chưa tốt
@app.post("/addBook")
def add_book():
    sid = get_or_create_session()
    # Dùng session server-side để "login" giả lập
    if "user" not in server_sessions[sid]:
        server_sessions[sid]["user"] = "student"

    data = request.get_json(silent=True) or request.form
    title = data.get("title")
    author = data.get("author")
    if not title or not author:
        return "Missing fields", 400

    global next_id
    book = {"id": next_id, "title": title, "author": author, "updatedAt": datetime.utcnow().isoformat() + "Z"}
    next_id += 1
    books.append(book)
    return f"Added book with id={book['id']}"

@app.route("/deleteBook", methods=["GET", "POST"])
def delete_book():
    sid = get_or_create_session()
    if "user" not in server_sessions[sid]:
        server_sessions[sid]["user"] = "student"

    bid = request.args.get("id")
    if not bid:
        data = request.get_json(silent=True) or request.form or {}
        bid = data.get("id")
    try:
        bid = int(bid)
    except (TypeError, ValueError):
        return "Invalid or missing id", 400

    global books
    before = len(books)
    books = [b for b in books if b["id"] != bid]
    if len(books) == before:
        return f"Book id={bid} not found", 404
    
    next_id -= 1
    return f"Deleted book with id={bid}"

if __name__ == "__main__":
    app.run(debug=True)

    