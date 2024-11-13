import os
from flask import Flask, abort, render_template, redirect, url_for, flash


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('flask_key')


@app.route("/login",methods=['POST','GET'])
def login():
    return render_template("login.html")
print("hii")

if __name__ == "__main__":
    app.run(debug=True, port=5002)