from flask import Flask, request, render_template_string
import requests
import re
import os

app = Flask(_name_)

def extract_uid_from_facebook_url(fb_url):
    try:
        response = requests.get(fb_url, allow_redirects=True, timeout=10)
        final_url = response.url

        # Match /posts/<post_id>, /permalink/<post_id>, or /videos/<video_id>
        match = re.search(r"/(?:posts|permalink|videos)/(\d+)", final_url)
        if match:
            return match.group(1), final_url
        else:
            return None, final_url
    except Exception as e:
        return str(e), None

@app.route('/', methods=['GET', 'POST'])
def index():
    uid = None
    error = None
    real_url = None
    if request.method == 'POST':
        fb_url = request.form.get('fb_url')
        uid, real_url = extract_uid_from_facebook_url(fb_url)
        if not uid:
            error = "UID extract nahi ho paaya. URL galat hai ya redirect nahi ho raha."
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Facebook Post UID Extractor</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 30px; background: #f8f8f8; }
            form { margin-bottom: 20px; }
            input[type="text"] { width: 60%; padding: 10px; }
            button { padding: 10px 20px; }
            .result { background: #fff; padding: 15px; border-radius: 5px; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <h2>Facebook Post UID Extractor</h2>
        <form method="post">
            <label>Facebook Post URL:</label><br><br>
            <input type="text" name="fb_url" placeholder="https://www.facebook.com/share/p/..." required>
            <button type="submit">Extract UID</button>
        </form>

        {% if uid %}
        <div class="result">
            <p><strong>Redirected URL:</strong> {{ real_url }}</p>
            <p><strong>Post UID:</strong> {{ uid }}</p>
        </div>
        {% elif error %}
        <p class="error">{{ error }}</p>
        {% endif %}
    </body>
    </html>
    """, uid=uid, error=error, real_url=real_url)

if _name_ == '_main_':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
