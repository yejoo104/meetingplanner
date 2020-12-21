from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def plannerhome():
    return render_template("home.html")
