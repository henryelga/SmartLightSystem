from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to Elga's Flask App!"

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    print(data)
    return jsonify({"status": "success", "received": data})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

