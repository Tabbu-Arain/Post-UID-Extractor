from flask import Flask, request, render_template
import re
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse

app = Flask(__name__)
app.config['FB_API_VERSION'] = 'v18.0'  # Current API version

def get_post_id_via_api(url, access_token):
    """Get post ID using Facebook's official Graph API"""
    try:
        api_url = f"https://graph.facebook.com/{app.config['FB_API_VERSION']}/"
        params = {
            'id': url,
            'access_token': access_token,
            'fields': 'id'
        }
        
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if 'id' in data:
            return data['id']
        return None
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            error_data = e.response.json()
            print(f"API Error: {error_data.get('error', {}).get('message')}")
        return None
    except Exception as e:
        print(f"API Request Failed: {str(e)}")
        return None

def extract_facebook_post_id(url, access_token= None):
    """
    Hybrid approach - tries API first if token provided, then falls back to scraping
    """
    # Try API first if access token is provided
    if access_token:
        api_result = get_post_id_via_api(url, access_token)
        if api_result:
            return api_result

    # Fallback to scraping if API fails or no token
    parsed = urlparse(url)
    clean_url = parsed.scheme + '://' + parsed.netloc + parsed.path

    pfbid_patterns = [
        r'/posts/(pfbid[\w]+)',
        r'/(pfbid[\w]+)$',
        r'/(pfbid[\w]+)/'
    ]
    
    for pattern in pfbid_patterns:
        match = re.search(pattern, clean_url)
        if match:
            pfbid = match.group(1)
            return resolve_pfbid(pfbid) or pfbid

    numeric_patterns = [
        r'story_fbid=(\d+)',
        r'posts/(\d+)',
        r'fbid=(\d+)',
        r'set=pcb\.(\d+)',
        r'activity/(\d+)',
        r'comment_id=(\d+)'
    ]
    
    for pattern in numeric_patterns:
        match = re.search(pattern, clean_url)
        if match:
            return match.group(1)

    return scrape_generic_url(clean_url)

# Keep resolve_pfbid(), scrape_generic_url() functions from previous version
# [Previous implementation of resolve_pfbid() and scrape_generic_url() here]

@app.route('/', methods=['GET', 'POST'])
def index():
    post_id = error = input_url = None
    api_token = None
    
    if request.method == 'POST':
        input_url = request.form.get('url', '').strip()
        api_token = request.form.get('token', '').strip()
        
        if not input_url:
            error = "Please enter a URL"
        elif 'facebook.com' not in input_url:
            error = "Please enter a valid Facebook URL"
        else:
            post_id = extract_facebook_post_id(input_url, api_token)
            if not post_id:
                error = "Could not extract Post ID. Try these solutions:"
                error += "<br>- Use a valid Facebook Access Token"
                error += "<br>- Check if the post is public"
                error += "<br>- Try again later"
    
    return render_template(
        'index.html',
        post_id=post_id,
        error=error,
        input_url=input_url,
        api_token=api_token
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
