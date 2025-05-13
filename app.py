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

    # URLs to try to extract the EAAB token
    urls_to_try = [
        "https://business.facebook.com/content_management",
        "https://www.facebook.com/adsmanager/manage/campaigns",
        "https://www.facebook.com/adsmanager",
        "https://graph.facebook.com/me"
    ]

    for url in urls_to_try:
        try:
            print(f"Trying URL: {url}")  # Debugging log
            res = session.get(url, headers=headers, timeout=10)

            # Debugging: Log the response text to check if the EAAB token is in there
            print(res.text[:1000])  # Print the first 1000 characters of the response for debugging

            match = re.search(r'(EAAB\w+)', res.text)
            if match:
                print(f"Found EAAB Token: {match.group(1)}")  # Debugging log
                return match.group(1)

        except requests.exceptions.RequestException as e:
            print(f"Error with URL {url}: {e}")  # Error log
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
