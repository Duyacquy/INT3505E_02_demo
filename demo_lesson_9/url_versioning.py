# ========== URL versioning ============
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/v1/books', methods=['GET'])
def books_v1():
    return jsonify({"version": "v1", "data": ["Book A", "Book B"]})

@app.route('/api/v2/books', methods=['GET'])
def books_v2():
    return jsonify({"version": "v2", "data": ["Book A", "Book B", "Book C"]})

if __name__ == "__main__":
    app.run(port=5000)