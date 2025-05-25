from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Post UID Extractor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 40px;
            background-color: #f2f2f2;
        }
        input[type="text"] {
            width: 300px;
            padding: 10px;
            font-size: 16px;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            background-color: #007bff;
            color: white;
            border: none;
            margin-left: 10px;
            cursor: pointer;
        }
        .result {
            margin-top: 20px;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <h2>Facebook Post UID Extractor</h2>
    <form method="POST">
        <input type="text" name="post_url" placeholder="Paste Facebook Post URL here" required>
        <button type="submit">Get UID</button>
    </form>

    {% if post_uid %}
        <div class="result">
            <strong>Post UID:</strong> {{ post_uid }}
        </div>
    {% endif %}
</body>
</html>
'''

def get_post_uid(post_url):
    try:
        response = requests.post("https://kojaxd.xyz/getuid", data={"url": post_url}, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return f"Error: Status code {response.status_code}"
    except Exception as e:
        return f"Exception: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    post_uid = None
    if request.method == 'POST':
        post_url = request.form.get('post_url')
        if post_url:
            post_uid = get_post_uid(post_url)
    return render_template_string(HTML, post_uid=post_uid)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
