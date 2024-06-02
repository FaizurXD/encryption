from flask import Flask, render_template_string, request, send_file
import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

app = Flask(__name__)

# Set background image
bg_image = "bg.png"

# AES encryption
def aes_encrypt(data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    data_padded = pad(data, AES.block_size)
    return cipher.encrypt(data_padded)

# Custom encryption process
def custom_encrypt(data):
    sha256_hash = hashlib.sha256(data.encode()).digest()
    md5_hash = hashlib.md5(sha256_hash).digest()
    aes_key = hashlib.sha256(b'secretkey').digest()
    aes_encrypted_data = aes_encrypt(md5_hash, aes_key)
    return aes_encrypted_data.hex()

# HTML template with embedded CSS
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FAIZUR CUSTOM ENCRYPTION</title>
    <style>
        body {
            background-image: url('{{ bg_image }}');
            background-size: cover;
            font-family: Arial, sans-serif;
            color: #ffffff;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent background */
            border-radius: 8px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-control {
            border-radius: 5px;
        }
        .btn-primary {
            border-radius: 5px;
        }
        .response {
            margin-top: 20px;
            color: #ffffff;
        }
        .output {
            background-color: rgba(255, 255, 255, 0.7);
            color: #000000;
            padding: 10px;
            border-radius: 5px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">FAIZUR CUSTOM ENCRYPTION</h1>
        <form method="POST" action="/" enctype="multipart/form-data">
            <div class="form-group">
                <label for="plaintext">Enter your plaintext:</label>
                <input type="text" class="form-control" id="plaintext" name="plaintext" required>
            </div>
            <button type="submit" class="btn btn-primary">Encrypt</button>
        </form>
        {% if plaintext %}
        <div class="response">
            <h3>Your plaintext:</h3>
            <p>{{ plaintext }}</p>
            {% if encrypted_text %}
            <div class="output">
                <h3>Encrypted text:</h3>
                <pre>{{ encrypted_text }}</pre>
                <form method="get" action="/download">
                    <input type="hidden" name="encrypted_text" value="{{ encrypted_text }}">
                    <button type="submit" class="btn btn-primary">Download Encrypted Text</button>
                </form>
            </div>
            {% endif %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    encrypted_text = None
    plaintext = None
    if request.method == 'POST':
        plaintext = request.form['plaintext']
        encrypted_text = custom_encrypt(plaintext)
        
        # Write encrypted text to file
        with open('encrypted.txt', 'w') as f:
            f.write(encrypted_text)
        
        # Schedule deletion of the file after 30 minutes
        os.system("echo 'sleep 1800 && rm encrypted.txt' | at now")

    return render_template_string(html_template, encrypted_text=encrypted_text, plaintext=plaintext, bg_image=bg_image)

@app.route('/download', methods=['GET'])
def download():
    encrypted_text = request.args.get('encrypted_text')
    
    # Send file for download
    return send_file('encrypted.txt', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=False)
