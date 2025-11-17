import os
import json
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from openai_handler import get_intent_and_response
import jwt,datetime
from functools import wraps

load_dotenv()

SECRET_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})


clients = {}

#-------------Auth-------------------
def generate_token(user_id):
    return jwt.encode({
            "user_id":user_id,
            "exp":datetime.datetime.utcnow()+datetime.timedelta(days=1)
        },
        SECRET_KEY,
        algorithm="HS256",
    )

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception:
        return None
    
#----------------Auth Endpoints----------------
@app.route("/auth/login",methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if email == "vihan@mail.com" and password == "1234":
        token = generate_token("user_vihan")
        return jsonify({"token":token})
    
    return jsonify({"error":"Invalid Creadentials"}),401

@app.route('/',methods=['GET'])
def index():
    return jsonify({"message": "WebSocket server is running."})

# SocketIO event handlers
@socketio.on('connect', namespace='/customer')
def handel_customer_connect():
    customerId = request.sid
    clients[customerId] = {'role': 'customer'}
    print(f"server customer {customerId}")

@socketio.on('disconnect', namespace='/customer')
def handle_customer_disconnect():
    customerId = request.sid
    clients.pop(customerId, None)
    print(f"server customer disconnected {customerId}")

@socketio.on('message', namespace='/customer')
def handle_customer_message(message):
    customerId = request.sid
    print(f"Received message from customer {customerId}: {message}")

    response= get_intent_and_response(message)
    print(f"Sending response to customer {customerId}: {response}")
    socketio.emit('message', response, namespace='/customer', to=customerId)



if __name__ == '__main__':
    host = os.getenv('HOST', 'localhost')
    port = int(os.getenv('PORT', 5000))
    print(f"[server] Starting on:{port}")
    socketio.run(app, port=port)
    

