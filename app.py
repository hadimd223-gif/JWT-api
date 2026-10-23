from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods:^(GET'))
def home():
    return jsonify({
        "status": "Online",
        "message": "Free Fire JWT Generator API is running!"
    })

@app.route('/api/get-jwt', methods=['POST'])
def get_jwt():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        uid = data.get('uid')
        access_token = data.get('access_token')

        if not uid or not access_token:
            return jsonify({"error": "Both 'uid' and 'access_token' are required fields."}), 400

        # =========================================================================
        # ফ্রী ফায়ার গেমের রিয়েল JWT টোকেন জেনারেট করার মূল লজিক বা রিকোয়েস্ট এখানে হবে।
        # সাধারণত অফিশিয়াল সার্ভার এন্ডপয়েন্টে রিকোয়েস্ট পাঠিয়ে টোকেন ফেচ করতে হয়।
        # =========================================================================
        
        # উদাহরণের জন্য রিকোয়েস্ট পাঠানোর স্ট্রাকচার:
        # payload = {"uid": uid, "token": access_token}
        # response = requests.post("FREE_FIRE_SERVER_ENDPOINT", json=payload)
        # actual_jwt = response.json().get("jwt_token")

        # আপাতত আপনার দেওয়া ইনপুট প্রসেস করে রেসপন্স পাঠানোর ফরম্যাট:
        generated_jwt = f"jwt_token_verified_for_uid_{uid}"

        return jsonify({
            "status": "success",
            "uid": uid,
            "jwt_token": generated_jwt
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
