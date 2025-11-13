from flask import Blueprint, request, jsonify, make_response
import datetime

v1_api = Blueprint('v1_api', __name__, url_prefix='/v1')

@v1_api.route('/charge', methods=['POST'])
def charge_card():
    data = request.get_json()

    # Logic v1: xử lý trực tiếp card_number (kém an toàn)
    if 'card_number' not in data or 'amount' not in data:
        return jsonify({"error": "v1: Yêu cầu thiếu card_number hoặc amount"}), 400

    card_last_four = data['card_number'][-4:]
    amount = data['amount']
    
    print(f"Xử lý thanh toán v1 cho thẻ *...{card_last_four} với ${amount}")

    response_data = {
        "status": "success",
        "version": "v1",
        "message": f"Thanh toán ${amount} thành công (v1)."
    }

    response = make_response(jsonify(response_data), 200)

    # Giả sử ngày gỡ bỏ là 12/05/2026
    sunset_date = datetime.datetime(2026, 5, 12, 23, 59, 59, tzinfo=datetime.timezone.utc)

    response.headers['Deprecation'] = 'true'
    response.headers['Sunset'] = sunset_date.strftime('%a, %d %b %Y %H:%M:%S GMT')
    response.headers['Link'] = '<http://localhost:5000/v2/payments>; rel="alternate"; type="application/json"'
    
    return response