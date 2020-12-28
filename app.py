import sqlite3
import uuid

from flask import Flask, render_template, request, redirect
from werkzeug.security import generate_password_hash

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def plannerhome():
    if request.method == "GET":
        return render_template("home.html")
    if request.method == "POST":
        formdata = request.form
        passwordhash = generate_password_hash(formdata["password"])
        code = str(uuid.uuid4())
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            command = "INSERT INTO MEETING (eventname, email, name, password, min_event, max_event, min_people, max_people, dates, start_time, end_time, hours, minutes, code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(command, (formdata["eventname"], formdata["email"], formdata["name"], passwordhash, formdata["min_event"], formdata["max_event"], formdata["min_people"], formdata["max_people"], formdata["dates"], formdata["start_time"], formdata["end_time"], formdata["hours"], formdata["minutes"], code))
        
            connection.commit()
        return redirect("/" + code)

@app.route("/join/", defaults={'meeting_id': ''}, methods=["GET", "POST"])
@app.route("/join/<meeting_id>", methods=["GET", "POST"])
def join(meeting_id):
    if request.method == "GET":
        if meeting_id == "":
            return render_template("join.html")
        else:
            return render_template("join.html", meeting_code = meeting_id)
    if request.method == "POST":
        formdata = request.form
        passwordhash = generate_password_hash(formdata["password"])
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            command = "INSERT INTO REGISTRATION (email, name, password, meeting_code, admin) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(command, (formdata["email"], formdata["name"], passwordhash, formdata["meeting_id"], False))
            connection.commit()
        return redirect("/" + formdata["meeting_id"])
            

@app.route("/<meeting_id>")
def get_meeting(meeting_id):
    return str(meeting_id)
