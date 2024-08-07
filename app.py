from flask import Flask, request, render_template, redirect, url_for
from cryptography.fernet import Fernet
import uuid

app = Flask(__name__)

# In-memory store for snippets
snippets = {}
# This key will be used for encryption and decryption
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

# Printing the key in console/terminal to check the key 
print(f"Secret Key: {KEY.decode()}")

def encrypt(text):
    return cipher.encrypt(text.encode()).decode()  #encrypts the code

def decrypt(encrypted_text, key):
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_text.encode()).decode()

@app.route('/', methods=['GET', 'POST'])    
def create_snippet():
    if request.method == 'POST':
        text = request.form['text']
        secret_key = request.form.get('secretKey', '')

        snippet_id = str(uuid.uuid4())
        if secret_key == KEY.decode():  # Check if the key matches
            encrypted_text = encrypt(text)
            snippets[snippet_id] = (encrypted_text, KEY.decode())
        else:
            snippets[snippet_id] = (text, None)  # Store plain text with no key

        snippet_url = url_for('view_snippet', snippet_id=snippet_id)
        return f'<h1>Snippet Created!</h1><p>Your shareable URL is: <a href="{snippet_url}">{snippet_url}</a></p>'

    return render_template('create_snippet.html')

@app.route('/view_snippet/<snippet_id>', methods=['GET', 'POST'])
def view_snippet(snippet_id):
    snippet = snippets.get(snippet_id)
    if not snippet:
        return 'Snippet not found', 404

    text, key = snippet

    if request.method == 'POST':
        user_key = request.form.get('key', '')
        if key and user_key == key:
            try:
                text = decrypt(text, key)
                return render_template('decrypt_snippet.html', decrypted_text=text)
            except:
                return 'Error decrypting the text', 500
        elif key:
            return 'Invalid secret key', 403

    if key:
        # Render form to enter the decryption key
        return render_template('decrypt_snippet.html')
    return f'<pre>{text}</pre>'

if __name__ == '__main__':
    app.run(debug=True)
