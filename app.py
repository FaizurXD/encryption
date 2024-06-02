from flask import Flask, render_template, request, send_file
from faizurEncrypt import encrypt
from datetime import datetime, timedelta
import pytz
import os
import sched
import time

app = Flask(__name__)
scheduler = sched.scheduler(time.time, time.sleep)

html_template = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Encryptor</title>
    <!-- Bootstrap CSS -->
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <style>
        body {
            background-image: url("bg.png");
            background-size: cover;
            font-family: Arial, sans-serif;
        }

        .container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background-color: rgba(255, 255, 255, 0.7); /* semi-transparent white */
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

        .download-btn {
            margin-top: 10px;
        }
    </style>
</head>

<body>
    <div class="container">
        <h1 class="mb-4">Encryptor</h1>
        <form method="POST" action="/">
            <div class="form-group">
                <label for="input_text">Enter your plaintext:</label>
                <input type="text" class="form-control" id="input_text" name="input_text" required>
            </div>
            <button type="submit" class="btn btn-primary">Encrypt</button>
        </form>
        {% if input_text %}
        <div class="response">
            <h3>Your plaintext:</h3>
            <p>{{ input_text }}</p>
            {% if output %}
            <div class="output">
                <h3>Encrypted text:</h3>
                <p>{{ output }}</p>
                <form action="/download" method="GET" class="download-btn">
                    <input type="hidden" name="encrypted_text" value="{{ output }}">
                    <button type="submit" class="btn btn-success">Download Encrypted Text</button>
                </form>
            </div>
            {% endif %}
        </div>
        {% endif %}
    </div>

    <!-- Bootstrap JS and dependencies -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>

</html>
"""

def get_timestamp():
    ist = pytz.timezone('Asia/Kolkata')  # Indian Standard Time
    now = datetime.now(ist)
    return now.strftime("%Y-%m-%d_%H-%M-%S")

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    else:
        print(f"File does not exist: {file_path}")

def schedule_file_deletion(file_path):
    deletion_time = datetime.now() + timedelta(minutes=10)
    deletion_timestamp = deletion_time.timestamp()
    scheduler.enterabs(deletion_timestamp, 1, delete_file, (file_path,))

@app.route('/', methods=['GET', 'POST'])
def home():
    input_text = None
    output = None

    if request.method == 'POST':
        input_text = request.form['input_text']
        output = encrypt(input_text)

        file_name = f"encrypted-{get_timestamp()}.txt"
        file_path = os.path.join(app.root_path, file_name)
        with open(file_path, "w") as text_file:
            text_file.write(output)

        schedule_file_deletion(file_path)

    return render_template_string(html_template, input_text=input_text, output=output)

@app.route('/download')
def download_file():
    file_name = f"encrypted-{get_timestamp()}.txt"
    file_path = os.path.join(app.root_path, file_name)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=False)
    scheduler.run()
