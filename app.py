from flask import Flask, render_template_string, request
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import hashlib

app = Flask(__name__)

# Encryption logic from fse.py
def load_sbox(filename):
    with open(filename, 'r') as file:
        lines = file.read().split()
        return lines

def fse512_substitution(data, sbox):
    hex_data = data.hex()
    return ''.join(sbox[int(hex_data[i:i+2], 16) % len(sbox)] for i in range(0, len(hex_data), 2))

def aes_encrypt(data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    data_padded = pad(data, AES.block_size)
    return cipher.encrypt(data_padded)

def encrypt(data, sbox):
    sha256_hash = hashlib.sha256(data.encode()).digest()
    md5_hash = hashlib.md5(sha256_hash).digest()
    aes_key = hashlib.sha256(b'secretkey').digest()
    aes_encrypted_data = aes_encrypt(md5_hash, aes_key)
    extended_data = (aes_encrypted_data * (512 // len(aes_encrypted_data) + 1))[:512]
    encrypted_data = fse512_substitution(extended_data, sbox)
    return encrypted_data[:512].ljust(512, '0')

# HTML template with embedded CSS
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Custom Encryption</title>
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #343a40;
            font-family: Arial, sans-serif;
            color: #ffffff;
        }
        .container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background-color: #495057;
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
        }
        .output {
            background-color: #D1FFBD;
            color: #000000;
            padding: 10px;
            border-radius: 5px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Custom Encryption</h1>
        <form method="POST" action="/">
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
                <p>{{ encrypted_text }}</p>
            </div>
            {% endif %}
        </div>
        {% endif %}
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    encrypted_text = None
    plaintext = None
    if request.method == 'POST':
        plaintext = request.form['plaintext']
        sbox = load_sbox('sbox.txt')  # Ensure 'sbox.txt' is in the same directory
        encrypted_text = encrypt(plaintext, sbox)
    return render_template_string(html_template, encrypted_text=encrypted_text, plaintext=plaintext)

if __name__ == '__main__':
    app.run(debug=True)
