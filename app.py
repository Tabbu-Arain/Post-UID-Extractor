from flask import Flask, request, jsonify
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

app = Flask(__name__)

def extract_post_number(fb_url):
    """Extracts numeric post number from Facebook URL"""
    url_pattern = r'(?:posts|permalink\.php\?story_fbid=)(\d+)'
    match = re.search(url_pattern, fb_url)
    if match:
        return match.group(1)
    
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        
        service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(fb_url)
        time.sleep(5)
        
        # Meta tag approach
        meta_tags = driver.find_elements(By.TAG_NAME, 'meta')
        for tag in meta_tags:
            if 'post_id' in tag.get_attribute('property'):
                content = tag.get_attribute('content')
                post_id_match = re.search(r'(\d+)', content)
                if post_id_match:
                    return post_id_match.group(1)
        
        # Timestamp link approach
        try:
            timestamp_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/posts/"]'))
            )
            href = timestamp_link.get_attribute('href')
            post_id_match = re.search(r'/posts/(\d+)', href)
            if post_id_match:
                return post_id_match.group(1)
        except:
            pass
        
    except Exception as e:
        print(f"Scraping error: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass
    return None

@app.route('/')
def home():
    return app.send_static_file('../frontend/index.html')

@app.route('/extract', methods=['POST'])
def extract():
    data = request.get_json()
    fb_url = data.get('url', '')
    
    if not fb_url:
        return jsonify({'error': 'URL is required'}), 400
    
    post_number = extract_post_number(fb_url)
    
    if post_number:
        return jsonify({'post_number': post_number})
    else:
        return jsonify({'error': 'Could not extract post number'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
