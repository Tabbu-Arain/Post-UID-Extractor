from flask import Flask, request, jsonify, render_template
import requests, re, os

app = Flask(__name__)
session = requests.Session()

# All endpoints to scan for EAAB tokens
FB_ENDPOINTS = [
    "https://adsmanager.facebook.com/adsmanager",
    "https://business.facebook.com/business_locations",
    "https://www.facebook.com/adsmanager/manage/",
    "https://www.facebook.com/adsmanager/reporting",
    "https://www.facebook.com/adsmanager/accounts"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cookie-login', methods=['POST'])
def cookie_login():
    cookie = request.form.get('cookie')
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': cookie
    }

    found_tokens = []

    for url in FB_ENDPOINTS:
        try:
            response = session.get(url, headers=headers, timeout=10)
            tokens = re.findall(r'EAAB\w+', response.text)
            found_tokens.extend(tokens)
        except Exception as e:
            continue  # skip failed requests

    # Remove duplicates
    found_tokens = list(set(found_tokens))

    if found_tokens:
        return jsonify({"tokens": found_tokens})
    else:
        return jsonify({"error": "No EAAB token found. Try a different cookie or account type."}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
