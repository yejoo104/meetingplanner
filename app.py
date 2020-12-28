import sqlite3
import uuid

from flask import Flask, render_template, request, redirect, flash
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = 'eicdfwi375pfme3795e93bco3854uf'

@app.route("/", methods=["GET", "POST"])
def plannerhome():
    if request.method == "GET":
        return render_template("home.html")
    if request.method == "POST":
        # Get form data and create a has from the password as well as a unique code for the meeting
        formdata = request.form
        passwordhash = generate_password_hash(formdata["password"])
        code = str(uuid.uuid4())
        
        # Add data to the sql database
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
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            
            # if meeting does not exist, alert user
            search_command = "SELECT * FROM MEETING WHERE code=?"
            cursor.execute(search_command, (formdata["meeting_id"],))
            rows = cursor.fetchall()
            
            if len(rows) != 1:
                flash("This meeting code does not exist")
                return redirect("/join/")
            
            # meeting exists and this user is new
            passwordhash = generate_password_hash(formdata["password"])
            insert_command = "INSERT INTO REGISTRATION (email, name, password, meeting_code, admin) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(command, (formdata["email"], formdata["name"], passwordhash, formdata["meeting_id"], False))
            connection.commit()
            
            # meeting exists and user info is wrong
            
            # meeting exists and this user is returning
        return redirect("/" + formdata["meeting_id"])
            

@app.route("/<meeting_id>")
def get_meeting(meeting_id):
    return str(meeting_id)
