import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/token', methods=['GET'])
def get_token():
    uid = request.args.get('uid')
    password = request.args.get('password')
    if not uid or not password:
        return jsonify({"status": "error", "message": "UID and password required"}), 400
    
    mock_token = f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.uid_{uid}.signature_mhx_vip"
    return jsonify({"status": "success", "token": mock_token})

@app.route('/sync-github', methods=['POST', 'OPTIONS'])
def sync_github():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
        return response, 200

    data = request.json or {}
    print("Received Data:", data)  # টার্মাক্সে ডাটা প্রিন্ট করে দেখার জন্য

    token = data.get("token")
    repo = data.get("repo")
    path = data.get("path")
    jwt_token = data.get("jwt_token")

    if not token or not repo or not path or not jwt_token:
        print("Error: Missing fields ->", {"token": bool(token), "repo": bool(repo), "path": bool(path), "jwt_token": bool(jwt_token)})
        resp = jsonify({"status": "error", "message": "Missing required fields in JSON request"})
        resp.headers.add("Access-Control-Allow-Origin", "*")
        return resp, 400

    api_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        get_res = requests.get(api_url, headers=headers)
        sha = None
        if get_res.status_code == 200:
            sha = get_res.json().get("sha")

        import base64
        file_content = f"token = \"{jwt_token}\"\n"
        encoded_content = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")

        payload = {
            "message": "Update JWT token via MHX Tools Hub Auto Sync",
            "content": encoded_content
        }
        if sha:
            payload["sha"] = sha

        put_res = requests.put(api_url, headers=headers, json=payload)
        
        if put_res.status_code in [200, 201]:
            resp = jsonify({"status": "success", "message": "Successfully updated on GitHub"})
            resp.headers.add("Access-Control-Allow-Origin", "*")
            return resp, 200
        else:
            err_msg = put_res.json().get("message", "GitHub API Error")
            print("GitHub API Fail:", err_msg)
            resp = jsonify({"status": "error", "message": err_msg})
            resp.headers.add("Access-Control-Allow-Origin", "*")
            return resp, 400

    except Exception as e:
        print("Server Exception:", str(e))
        resp = jsonify({"status": "error", "message": str(e)})
        resp.headers.add("Access-Control-Allow-Origin", "*")
        return resp, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
