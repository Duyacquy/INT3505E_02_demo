from flask import Blueprint, request, jsonify
import uuid

v2_api = Blueprint('v2_api', __name__, url_prefix='/v2')

@v2_api.route('/payments', methods=['POST'])
def create_payment():
    data = request.get_json()

    # Logic v2: Chỉ xử lý payment_token (an toàn)
    if 'payment_token' not in data or 'amount' not in data:
        return jsonify({"error": "v2: Yêu cầu thiếu payment_token hoặc amount"}), 400

    token = data['payment_token']
    amount = data['amount']

    print(f"[V2 CALLED] Xử lý thanh toán v2 cho token {token} với ${amount}")
    
    # Đây là phiên bản mới, không cần header đặc biệt
    response_data = {
        "status": "success",
        "version": "v2",
        "transaction_id": f"txn_{uuid.uuid4()}",
        "message": f"Thanh toán ${amount} đã được chấp nhận (v2)."
    }

    return jsonify(response_data), 201