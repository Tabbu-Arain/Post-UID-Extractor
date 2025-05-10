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
    
    # Handle photo URLs with set=pcb. parameter specifically
    if 'photo' in url and 'set=pcb.' in url:
        match = re.search(r'set=pcb\.(\d+)', url)
        if match:
            return match.group(1)

    # Try other regex patterns
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            extracted_id = match.group(1)
            # For short share links and pfbid, attempt to resolve to numeric ID
            if pattern in [r'share/p/([a-zA-Z0-9]+)', r'pfbid([a-zA-Z0-9]+)']:
                numeric_id = resolve_to_numeric_id(url, extracted_id)
                return numeric_id if numeric_id else extracted_id
            return extracted_id
    
    return None

def resolve_to_numeric_id(url, extracted_id):
    """
    Resolves short share links and pfbid formats to a numeric post ID by scraping the redirected page.
    
    Args:
        url (str): The original URL
        extracted_id (str): The extracted ID (short code or pfbid)
        
    Returns:
        str: The numeric post ID, or None if resolution fails
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Strategy 1: Check og:url meta tag for redirected URL
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

            # Strategy 2: Look for post_id in script tags
            scripts = soup.find_all('script')
            for script in scripts:
                script_content = script.string
                if script_content:
                    # Look for numeric post_id in JSON-like data
                    match = re.search(r'"post_id":"(\d+)"', script_content)
                    if match:
                        return match.group(1)
                    # Alternative format: story_fbid
                    match = re.search(r'"story_fbid":"(\d+)"', script_content)
                    if match:
                        return match.group(1)

            # Strategy 3: Check for links with fbid in the href
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                match = re.search(r'fbid=(\d+)', href)
                if match:
                    return match.group(1)

            # Strategy 4: Check for numeric ID in meta tags with al:android:url
            android_meta = soup.find_all('meta', property='al:android:url')
            for tag in android_meta:
                content = tag.get('content', '')
                match = re.search(r'fb://post/(\d+)', content)
                if match:
                    return match.group(1)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    
    return None

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
