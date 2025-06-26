from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# HTML template for the frontend
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FB POST & PROFILE UID</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --dark-bg1: #000000;
            --dark-bg2: #1a1a1a;
            --dark-bg3: #2d2d2d;
            --dark-bg4: #4a0000;
            --dark-bg5: #1c1c1c;
            --primary: #8b0000;
            --secondary: #4a0000;
        }

        body {
            margin: 0;
            padding: 0;
            min-height: 100vh;
            background: linear-gradient(135deg, var(--dark-bg1), var(--dark-bg2));
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .container {
            max-width: 400px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin: 50px auto;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            position: relative;
            z-index: 1;
        }

        .form-control {
            background-color: var(--dark-bg3);
            border-color: var(--dark-bg4);
            color: #fff;
            padding: 15px;
            transition: all 0.3s ease;
        }

        .form-control:focus {
            background-color: var(--dark-bg2);
            box-shadow: 0 0 0 3px rgba(139, 0, 0, 0.3);
        }

        h1 {
            font-size: 1.5em;
            color: #8b0000;
            text-shadow: 0 0 20px #8b0000, 0 0 30px #8b0000;
        }

        .btn-primary {
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border: none;
            transition: transform 0.3s ease, background-position 0.3s ease;
            padding: 12px 30px;
            border-radius: 25px;
            box-shadow: 0 4px 15px rgba(139, 0, 0, 0.3);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            background-position: 100% 0;
            box-shadow: 0 6px 20px rgba(139, 0, 0, 0.5);
        }

        .copy-btn {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .copy-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(139, 0, 0, 0.3);
        }

        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            position: relative;
            overflow: hidden;
        }

        .success {
            background-color: rgba(212, 237, 218, 0.2);
            color: lime;
            text-shadow: 0 0 20px lime, 0 0 30px lime;
        }

        .error {
            background-color: rgba(248, 215, 218, 0.2);
            color: red;
            text-shadow: 0 0 20px red, 0 0 30px red;
        }

       .footer {
    margin-top: 20px;
    text-align: center;
    font-size: 1.2em;
    color: #8b0000;
    text-shadow: 0 0 20px #8b0000, 0 0 30px #8b0000;
}
    </style>
</head>

<body>
    <div class="container">
        <h1 class="text-center mb-4">GET FB POST AND PROFILE UID</h1>
        <form action="/" method="post">
            <div class="mb-3">
                <label for="facebookLink" class="form-label" , style="color:#8b0000;text-shadow: 0 0 20px #8b0000, 0 0 30px #8b0000;">PASTE FB POST OR PROFILE LINK:</label>
                <input type="text" class="form-control" id="facebookLink" name="facebookLink" placeholder="e.g: https://www.facebook.com/HASNA1N.AL1" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">GET UID</button>
        </form>

        {% if result %}
        <div class="result {{ result_class }}">
            <span>{{ result }}</span>
            <button class="copy-btn float-end mt-2" style="background: linear-gradient(90deg, var(--primary), var(--secondary)); color: white;">
                Copy UID
            </button>
        </div>
        {% endif %}
        <div class="footer">
            &copy; 2025 Coded by Tabbu Arain.
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const copyButtons = document.querySelectorAll('.copy-btn');

            copyButtons.forEach(button => {
                button.addEventListener('click', async function(e) {
                    const resultSpan = this.previousElementSibling;
                    const text = resultSpan.textContent.trim();

                    try {
                        await navigator.clipboard.writeText(text);

                        // Show success feedback
                        const originalText = this.textContent;
                        this.textContent = 'Copied!';
                        setTimeout(() => {
                            this.textContent = originalText;
                        }, 1500);
                    } catch (err) {
                        console.error('Failed to copy:', err);
                    }
                });
            });
        });
    </script>
</body>

</html>
'''

@app.route('/', methods=['GET', 'POST'])
def get_facebook_id():
    result = None
    result_class = None

    if request.method == 'POST':
        facebook_link = request.form.get('facebookLink')
        base_url = "https://koja.web-server.xyz"

        try:
            # Make GET request to the koja.web-server.xyz API
            response = requests.get(f"{base_url}/api/get_id", params={"link": facebook_link}, timeout=10)

            if response.status_code == 200:
                # Extract ID from JSON response
                fb_id = response.json().get("id")
                if fb_id:
                    result = f"{fb_id}"
                    result_class = "success"
                else:
                    result = "Error: No ID found in response."
                    result_class = "error"
            else:
                # Extract error message from JSON response
                error_msg = response.json().get("error", "Unknown error occurred")
                result = f"Error: {error_msg}"
                result_class = "error"
        except requests.RequestException as e:
            # Handle network or request errors
            result = f"Error: Failed to connect to the API - {str(e)}"
            result_class = "error"
        except ValueError:
            # Handle JSON decode errors
            result = "Error: Invalid response from the API"
            result_class = "error"

    # Render the template with result if available
    return render_template_string(INDEX_HTML, result=result, result_class=result_class)

if __name__ == '__main__':
    app.run()
