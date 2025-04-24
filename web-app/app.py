"""Main Flask app for web app"""
# later get rid of unused modules
import os
from flask import Flask, render_template

# app setup
app = Flask(__name__)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Render login page"""
    return render_template("login.html")

@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    """Render sign up page"""
    return render_template("sign_up.html")
    
if __name__ == "__main__":
    app.run(debug=True)
