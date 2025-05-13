from flask import Flask, render_template, request
import requests
import re
import os

app = Flask(__name__)

def extract_eaab_token(cookie):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Referer': 'https://www.facebook.com/',
        'Cookie': cookie
    }

    urls_to_try = [
        "https://business.facebook.com/content_management",
        "https://www.facebook.com/adsmanager/manage/campaigns",
        "https://www.facebook.com/adsmanager",
        "https://graph.facebook.com/me"
    ]

    for url in urls_to_try:
        try:
            res = session.get(url, headers=headers, timeout=10)
            match = re.search(r'(EAAB\w+)', res.text)
            if match:
                return match.group(1)
        except requests.exceptions.RequestException:
            continue

    return None

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/cookie-login', methods=['POST'])
def cookie_login():
    cookie = request.form.get('cookie')
    if not cookie:
        return "❌ Cookie is required.", 400

    token = extract_eaab_token(cookie)
    if token:
        return f"<p style='color: #00ff88; font-size:18px;'>✅ Token Found:</p><textarea rows='3' style='width:100%;'>{token}</textarea>"
    else:
        return "<p style='color: #ff0033;'>❌ EAAB Token not found. Please check your cookie.</p>"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
