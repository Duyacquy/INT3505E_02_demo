# ============ Query versioning ============
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/books', methods=['GET'])
def books_query_version():
    version = request.args.get("version", "1")

    if version == "1":
        return jsonify({"version": "v1", "data": ["Book A", "Book B"]})
    elif version == "2":
        return jsonify({"version": "v2", "data": ["Book A", "Book B", "Book C"]})
    return jsonify({"error": "Unsupported API version"}), 400

if __name__ == "__main__":
    app.run(port=5000)