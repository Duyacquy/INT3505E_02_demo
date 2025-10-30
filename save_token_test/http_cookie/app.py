from flask import Flask, request, jsonify, make_response, send_from_directory
import jwt, datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'duyacquy'

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if username == 'admin' and password == '1234':
        token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        if isinstance(token, bytes):
            token = token.decode('utf-8')

        resp = make_response(jsonify({'message': 'Đăng nhập thành công'}))
        resp.set_cookie(
            'access_token',
            token,
            httponly=True,
            samesite='Lax',
            max_age=10
        )
        return resp

    return jsonify({'message': 'Sai tài khoản hoặc mật khẩu'}), 401

@app.route('/', methods=['GET'])
def home():
    return send_from_directory('.', 'home.html')


if __name__ == "__main__":
    app.run(port=5000, debug=True)
