"""Main Flask app for web app"""

from flask import Flask

# app setup
app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True)
