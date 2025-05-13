from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os  # You can use this if needed for environment variables or file paths
import re  # If you need regex functionality later

app = Flask(__name__)

def extract_eaab_token(cookie):
    # Set up Selenium options for headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run headlessly (no UI)
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    
    # Initialize the Selenium WebDriver (using Chrome in headless mode)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    # Set the Facebook URL (a page where the EAAB token might be found)
    urls_to_try = [
        "https://business.facebook.com/content_management",
        "https://www.facebook.com/adsmanager/manage/campaigns",
        "https://www.facebook.com/adsmanager",
        "https://graph.facebook.com/me"
    ]

    # Add the cookie to the browser session
    driver.get("https://www.facebook.com/")
    driver.add_cookie({"name": "cookie", "value": cookie, "domain": "facebook.com"})

    for url in urls_to_try:
        try:
            driver.get(url)
            time.sleep(5)  # Wait for the page to load fully (you may need to adjust this delay)
            
            # Retrieve the page content
            page_source = driver.page_source
            if 'EAAB' in page_source:
                # Search for the EAAB token in the page source
                start_index = page_source.find('EAAB')
                end_index = page_source.find(' ', start_index)
                token = page_source[start_index:end_index]
                driver.quit()
                return token
        except Exception as e:
            print(f"Error on {url}: {e}")

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
