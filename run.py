from flask import Flask
from config import verification_bp

app = Flask(__name__)

# Register the blueprint
# We keep the url_prefix so your routes remain '/liveness/popup', etc.
app.register_blueprint(verification_bp, url_prefix='/liveness')

if __name__ == '__main__':
    print("--- Starting Verification Service on Port 5001 ---")
    app.run(debug=True, port=5001)  # port=5001 isolates this from your Main App (which is on 5000)sub