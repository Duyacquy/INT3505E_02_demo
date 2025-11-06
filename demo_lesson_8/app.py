from flask import Flask, request, jsonify

app = Flask(__name__)

books = [
    {"id": 1, "title": "The Hobbit", "author": "Tolkien"},
    {"id": 2, "title": "1984", "author": "Orwell"},
]

# 1. GET all books
@app.route("/books", methods=["GET"])
def get_books():
    return jsonify(books), 200

# 2. GET one book
@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    for b in books:
        if b["id"] == book_id:
            return jsonify(b), 200
    return jsonify({"error": "Book not found"}), 404

# 3. POST new book
@app.route("/books", methods=["POST"])
def add_book():
    data = request.json
    new_book = {
        "id": len(books) + 1,
        "title": data.get("title"),
        "author": data.get("author")
    }
    books.append(new_book)
    return jsonify(new_book), 201

# 4. PUT update book
@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    for b in books:
        if b["id"] == book_id:
            b.update(request.json)
            return jsonify(b), 200
    return jsonify({"error": "Book not found"}), 404

# 5. DELETE book
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    global books
    books = [b for b in books if b["id"] != book_id]
    return jsonify({"message": "Book deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)
