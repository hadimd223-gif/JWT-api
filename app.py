from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "Online",
        "author": "Mahi",
        "message": "Free Fire JWT Generator API is running successfully!"
    })

@app.route('/api/get-jwt', methods=['POST'])
def get_jwt():
    try:
        # ক্লায়েন্ট থেকে JSON ডাটা গ্রহণ করা
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        uid = data.get('uid')
        access_token = data.get('access_token')

        # ইউআইডি এবং এক্সেস টোকেন চেক করা
        if not uid or not access_token:
            return jsonify({"error": "Both 'uid' and 'access_token' are required fields."}), 400

        # --- ফ্রি ফায়ার সার্ভার রিকোয়েস্ট বা প্রসেসিং লজিক ---
        # সাধারণত এখানে গেমের অফিশিয়াল বা প্রোটোবাফ (Protobuf) এন্ডপয়েন্টে রিকোয়েস্ট পাঠিয়ে টোকেন রিট্রাইভ করতে হয়।
        # নিচে একটি ডেমো রেসপন্স স্ট্রাকচার দেওয়া হলো:
        
        # simulated_jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." (আপনার আসল প্রসেসিং কোড এখানে বসবে)
        
        simulated_jwt_token = f"sample_jwt_token_for_uid_{uid}"

        return jsonify({
            "status": "success",
            "uid": uid,
            "jwt_token": simulated_jwt_token
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
