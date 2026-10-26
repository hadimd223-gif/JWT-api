import os
import sys
import time
import json
import base64
import requests

import httpx
from flask import Flask, request, jsonify
from flask_cors import CORS
from Crypto.Cipher import AES

# ============================================================
#  SETTINGS & CONFIGURATION
# ============================================================
MAIN_KEY = base64.b64decode("WWcmdGMlREV1aDYlWmNeOA==")
MAIN_IV = base64.b64decode("Nm95WkRyMjJFM3ljaGpNJQ==")
RELEASEVERSION = "OB55"
USERAGENT = "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"
LOGIN_URL = "https://loginbp.ppmainecoonghj.com/"

# গিটহাব কনফিগারেশন (আপনার তথ্য এখানে বসাবেন)
GITHUB_TOKEN = "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN"
GITHUB_USERNAME = "YOUR_GITHUB_USERNAME"
REPO_NAME = "YOUR_REPO_NAME"
FILE_PATH = "path/to/token_file.txt"

HTTP_LIMITS = httpx.Limits(max_keepalive_connections=20, max_connections=50)
HTTP_TIMEOUT = httpx.Timeout(15.0, connect=5.0)
_http_client = httpx.Client(limits=HTTP_LIMITS, timeout=HTTP_TIMEOUT)

app = Flask(__name__)
CORS(app)

# ============================================================
#  HELPERS & CRYPTO
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
    resp = _http_client.post(url, data=payload, headers=headers)
    data = resp.json()
    return data.get("access_token", "0"), data.get("open_id", "0")

def generate_jwt_token(uid: str, password: str):
    start_time = time.time()
    token_val, open_id = get_access_token(f"uid={uid}&password={password}")
    if token_val == "0" or open_id == "0":
        raise Exception("Invalid UID or Password — access token not received")

    # সিম্পল ডেমো বা রিকোয়েস্ট বডি স্ট্রাকচার
    elapsed = time.time() - start_time
    # আপনার জেনারেটেড টোকেন স্ট্রিং এখানে তৈরি হবে
    sample_jwt = base64.b64encode(f"{uid}-{token_val}".encode()).decode()

    return {
        "access_token": token_val,
        "open_id": open_id,
        "status": "success",
        "time": f"{elapsed:.2f}s",
        "token": sample_jwt,
    }

def update_github_file(new_token: str):
    if GITHUB_TOKEN == "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN":
        return  # কনফিগার না করা থাকলে বাইপাস করবে
    api_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "vnd.github+json"
    }
    get_resp = requests.get(api_url, headers=headers)
    if get_resp.status_code != 200:
        raise Exception(f"Failed to fetch file from GitHub: {get_resp.text}")
    
    file_sha = get_resp.json().get("sha")
    encoded_content = base64.b64encode(new_token.encode("utf-8")).decode("utf-8")
    
    payload = {
        "message": "Auto-update JWT Token via Termux API",
        "content": encoded_content,
        "sha": file_sha
    }
    put_resp = requests.put(api_url, headers=headers, json=payload)
    if put_resp.status_code not in [200, 201]:
        raise Exception(f"Failed to update GitHub file: {put_resp.text}")
    return True

# ============================================================
#  ROUTES
# ============================================================
@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "running", "service": "JWT & GitHub Sync API"}), 200

@app.route("/token", methods=["GET", "POST", "OPTIONS"])
def get_jwt_token():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
        
    uid = request.args.get("uid")
    password = request.args.get("password")

    if not uid or not password:
        return jsonify({"status": "error", "error": "Both uid and password parameters are required"}), 400

    try:
        token_data = generate_jwt_token(uid, password)
        jwt_token = token_data.get("token")
        
        if jwt_token:
            try:
                update_github_file(jwt_token)
                token_data["github_sync"] = "success"
            except Exception as ge:
                token_data["github_sync"] = f"failed: {str(ge)}"
                
        return jsonify(token_data), 200
    except Exception as e:
        return jsonify({"status": "error", "error": f"Failed to generate token: {str(e)}"}), 500

@app.route('/sync-github', methods=['GET', 'POST', 'OPTIONS'])
def sync_github():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
    try:
        token_to_sync = request.args.get("token") or (request.json.get("token") if request.json else None)
        if not token_to_sync:
            return jsonify({"status": "error", "message": "Token parameter is missing"}), 400
        update_github_file(token_to_sync)
        return jsonify({"status": "success", "message": "Token updated in GitHub successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)
