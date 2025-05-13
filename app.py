from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
import os
import re

app = Flask(__name__)

def extract_eaab_token(cookie):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-software-rasterizer')

    # Render-specific Chromium path
    chrome_path = shutil.which("chromium-browser") or shutil.which("chromium")
    driver_path = shutil.which("chromedriver")

    if not chrome_path or not driver_path:
        return "Chromium or Chromedriver not found. Make sure they are installed on the server."

    chrome_options.binary_location = chrome_path

    # Initialize the driver
    driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)

    urls_to_try = [
        "https://business.facebook.com/content_management",
        "https://www.facebook.com/adsmanager/manage/campaigns",
        "https://www.facebook.com/adsmanager",
        "https://graph.facebook.com/me"
    ]

    try:
        driver.get("https://www.facebook.com/")
        driver.add_cookie({"name": "cookie", "value": cookie, "domain": ".facebook.com"})

        for url in urls_to_try:
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                page_source = driver.page_source
                if 'EAAB' in page_source:
                    match = re.search(r'EAAB\w+', page_source)
                    if match:
                        driver.quit()
                        return match.group(0)
            except Exception as e:
                print(f"Error visiting {url}: {e}")
    except Exception as outer:
        print(f"Browser error: {outer}")
    finally:
        driver.quit()

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
