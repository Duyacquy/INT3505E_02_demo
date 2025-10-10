from flask import Flask, jsonify

app = Flask(__name__)

books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "REST in Practice", "author": "Webber et al."},
]

@app.route("/")
def home():
    return "Đây là trang chủ"

# Đặt tên là danh từ cho endpoint kèm version
# Trả về định dạng json với status code
@app.route("/books")
def get_books():
    return jsonify(books), 200

if __name__ == "__main__":
    app.run(debug=True)