from flask import Flask

from v1 import v1_api
from v2 import v2_api

app = Flask(__name__)

app.register_blueprint(v1_api)
app.register_blueprint(v2_api)

@app.route('/')
def home():
    return "Payment API Server đang chạy. Thử gọi /v1/charge hoặc /v2/payments."

if __name__ == '__main__':
    app.run(debug=True, port=5000)