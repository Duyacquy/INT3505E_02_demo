from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from soa_lib.extensions import db
from ..models import Book
from .auth import login_required

api_bp = Blueprint("api", __name__)

def parse_pagination():
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    try:
        page_size = min(int(request.args.get("page_size", 10)), 100)
    except ValueError:
        page_size = 10
    return page, page_size

@api_bp.get("/books")
@login_required
def list_books():
    q = Book.query
    search = request.args.get("search")
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Book.title.ilike(like), Book.author.ilike(like), Book.isbn.ilike(like)))
    page, page_size = parse_pagination()
    total = q.count()
    items = q.order_by(Book.id.desc()).offset((page-1)*page_size).limit(page_size).all()
    data = [serialize_book(b) for b in items]
    return jsonify({"data": data, "page": page, "page_size": page_size, "total": total}), 200

@api_bp.post("/books")
@login_required
def create_book():
    payload = request.get_json(silent=True) or {}
    for r in ["title", "author"]:
        if not payload.get(r):
            return jsonify({"error": f"'{r}' là bắt buộc"}), 400
    b = Book(
        title=payload["title"],
        author=payload["author"],
        isbn=payload.get("isbn"),
        published_year=payload.get("published_year"),
        quantity_total=payload.get("quantity_total", 1),
        quantity_available=payload.get("quantity_available", payload.get("quantity_total", 1)),
    )
    db.session.add(b)
    db.session.commit()
    return jsonify(serialize_book(b)), 201

@api_bp.get("/books/<int:book_id>")
@login_required
def get_book(book_id: int):
    b = Book.query.get_or_404(book_id)
    return jsonify(serialize_book(b)), 200

@api_bp.put("/books/<int:book_id>")
@login_required
def update_book(book_id: int):
    b = Book.query.get_or_404(book_id)
    payload = request.get_json(silent=True) or {}
    for field in ["title", "author", "isbn", "published_year", "quantity_total", "quantity_available"]:
        if field in payload:
            setattr(b, field, payload[field])
    db.session.commit()
    return jsonify(serialize_book(b)), 200

@api_bp.delete("/books/<int:book_id>")
@login_required
def delete_book(book_id: int):
    b = Book.query.get_or_404(book_id)
    db.session.delete(b)
    db.session.commit()
    return jsonify({"status": "deleted"}), 204

def serialize_book(b: Book):
    return {
        "id": b.id,
        "title": b.title,
        "author": b.author,
        "isbn": b.isbn,
        "published_year": b.published_year,
        "quantity_total": b.quantity_total,
        "quantity_available": b.quantity_available,
        "created_at": b.created_at.isoformat() if b.created_at else None,
        "updated_at": b.updated_at.isoformat() if b.updated_at else None,
    }