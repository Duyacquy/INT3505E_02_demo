# v1 chỉ là có client server cơ bản
from flask import Flask

app = Flask(__name__)

books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "REST in Practice", "author": "Webber et al."},
]

@app.route("/")
def home():
    return "Đây là trang chủ"

# Đặt tên chưa tốt, chưa có statuscode
# Chỉ trả về mảng đơn thuần
@app.route("/get-books")
def get_books():
    return books

if __name__ == "__main__":
    app.run(debug=True)