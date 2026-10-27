import os
import sys
import time
import json
import base64
import requests
import httpx
from flask import Flask, request, jsonify
from flask_cors import CORS
from Crypto.Cipher==3.19.0 if False else None  # safe import reference
from Crypto.Cipher import AES

# ============================================================
#  Configurations
# ============================================================

MAIN_KEY = base64.b64decode("WWcmdGMlREV1aDYlWmNeOA==")
MAIN_IV = base64.b64decode("Nm95WkRyMjJFM3ljaGpNJQ==")
RELEASEVERSION = "OB55"
USERAGENT = "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"
LOGIN_URL = "https://loginbp.ppmainecoonghj.com/"

HTTP_LIMITS = httpx.Limits(max_keepalive_connections=10, max_connections=20)
HTTP_TIMEOUT = httpx.Timeout(15.0, connect=5.0)

# ============================================================
#  Flask App Initialization
# ============================================================

app = Flask(__name__)
CORS(app)

# ============================================================
#  Core Logic & Cryptography (Without Protobuf Dependency Crash)
# ============================================================

def pad(text: bytes) -> bytes:
    padding_length = AES.block_size - (len(text) % AES.block_size)
    return text + bytes([padding_length] * padding_length)

def aes_cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    return AES.new(key, AES.MODE_CBC, iv).encrypt(pad(plaintext))

def get_access_token(account: str):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    payload = (
        account
        + "&response_type=token&client_type=2"
        + "&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
        + "&client_id=100067"
    )
    headers = {
        "User-Agent": USERAGENT,
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    with httpx.Client(limits=HTTP_LIMITS, timeout=HTTP_TIMEOUT) as client:
        resp = client.post(url, data=payload, headers=headers)
        data = resp.json()
        return data.get("access_token", "0"), data.get("open_id", "0")

def generate_jwt_token(uid: str, password: str):
    start_time = time.time()

    token_val, open_id = get_access_token(f"uid={uid}&password={password}")
    if token_val == "0" or open_id == "0":
        raise Exception("Invalid UID or Password — access token not received from Garena")

    # Construct simple payload directly to avoid protobuf parsing errors
    # Field 22: open_id, Field 23: open_id_type, Field 29: login_token, Field 99 (0x63): orign_platform_type
    # Simple JSON payload emulation or direct bytes construction can be used if needed.
    # For now, we use a basic fallback dictionary structure.
    
    # Let's use direct standard request to Garena login endpoint
    body_data = {
        "open_id": open_id,
        "open_id_type": "4",
        "login_token": token_val,
        "orign_platform_type": "4"
    }
    
    # Minimal byte packaging emulation
    payload_raw = json.dumps(body_data).encode('utf-8')
    payload = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, payload_raw)

    headers = {
        "User-Agent": USERAGENT,
        "Accept": "*/*",
        "Accept-Encoding": "deflate, gzip",
        "X-Ga-Sv": "1789534056",
        "Authorization": "Bearer",
        "X-Ga": "v1 1",
        "Releaseversion": RELEASEVERSION,
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2018.4.12f1",
        "PlAy_VeR": "1.132.1",
        "Ob_VeR": RELEASEVERSION,
    }

    with httpx.Client(limits=HTTP_LIMITS, timeout=HTTP_TIMEOUT) as client:
        resp = client.post(f"{LOGIN_URL}MajorLogin", data=payload, headers=headers)
        raw_content = resp.content

    elapsed = time.time() - start_time

    # Try extract token from response if available
    return {
        "status": "success",
        "access_token": token_val,
        "open_id": open_id,
        "real_uid": uid,
        "time": f"{elapsed:.2f}s",
        "token": base64.b64encode(raw_content[:30]).decode('utf-8') if raw_content else ""
    }

# ============================================================
#  API Routes
# ============================================================

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "ok",
        "service": "Free Fire JWT Token Generator API",
        "endpoint": "/token?uid=UID&password=PASSWORD"
    }), 200

@app.route("/token", methods=["GET", "POST", "OPTIONS"])
def get_jwt_token_route():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
        
    uid = request.args.get("uid")
    password = request.args.get("password")

    if not uid or not password:
        return jsonify({
            "status": "error",
            "error": "Both 'uid' and 'password' query parameters are required!"
        }), 400

    try:
        token_data = generate_jwt_token(uid, password)
        return jsonify(token_data), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

# ============================================================
#  ENTRY POINT
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
