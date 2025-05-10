from flask import Flask, request, render_template
import re
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

def extract_facebook_post_id(url):
    """
    Extracts the Facebook post ID from a given post URL, including short share links and pfbid formats.
    
    Args:
        url (str): The Facebook post URL
        
    Returns:
        str: The extracted post ID, or None if not found
    """
    # Common patterns for Facebook post URLs
    patterns = [
        r'posts/(\d+)',                     # Standard post: facebook.com/username/posts/123456789
        r'permalink\.php\?story_fbid=(\d+)', # Permalink: facebook.com/permalink.php?story_fbid=123456789
        r'fbid=(\d+)',                      # Mobile links: m.facebook.com/story.php?story_fbid=123456789
        r'/\d+/posts/(\d+)',                # Group posts: facebook.com/groups/123/posts/456789
        r'photos/\d+\.\d+\.\d+/(\d+)',      # Photo posts: facebook.com/photo?fbid=123456789
        r'share/p/([a-zA-Z0-9]+)',          # Short share link: facebook.com/share/p/1C2xJ4tocw
        r'pfbid([a-zA-Z0-9]+)'              # pfbid format: facebook.com/.../posts/pfbid...
    ]
    
    # Try regex patterns first
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            short_code = match.group(1)
            # For short share links, attempt to resolve to numeric ID
            if pattern == r'share/p/([a-zA-Z0-9]+)':
                return resolve_short_link(url, short_code)
            return short_code
    
    return None

def resolve_short_link(url, short_code):
    """
    Resolves short share links to find the numeric post ID by scraping the redirected page.
    
    Args:
        url (str): The original short URL
        short_code (str): The extracted short code
        
    Returns:
        str: The numeric post ID, or the short code if resolution fails
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            meta_tags = soup.find_all('meta', property='og:url')
            for tag in meta_tags:
                content = tag.get('content', '')
                patterns = [
                    r'posts/(\d+)',
                    r'permalink\.php\?story_fbid=(\d+)',
                    r'fbid=(\d+)',
                    r'comment_id=(\d+)'
                ]
                for pattern in patterns:
                    match = re.search(pattern, content)
                    if match:
                        return match.group(1)

            scripts = soup.find_all('script')
            for script in scripts:
                script_content = script.string
                if script_content:
                    match = re.search(r'"post_id":"(\d+)"', script_content)
                    if match:
                        return match.group(1)
            
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                match = re.search(r'fbid=(\d+)', href)
                if match:
                    return match.group(1)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    
    return short_code

@app.route('/', methods=['GET', 'POST'])
def index():
    post_id = None
    error = None
    input_url = ''
    if request.method == 'POST':
        input_url = request.form.get('url')
        if input_url:
            post_id = extract_facebook_post_id(input_url)
            if not post_id:
                error = "Could not extract Post ID from the provided URL."
        else:
            error = "Please provide a valid Facebook post URL."
    
    return render_template('index.html', post_id=post_id, error=error, input_url=input_url)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
