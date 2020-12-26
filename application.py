from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def plannerhome():
    if request.method == "GET":
        return render_template("home.html")
    if request.method == "POST":
        formdata = request.form
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            command = "INSERT INTO MEETING (eventname, email, name, password, min_event, max_event, min_people, max_people, dates, start_time, end_time, code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(command, (formdata["eventname"], formdata["email"], formdata["name"], formdata["password"], formdata["min_event"], formdata["max_event"], formdata["min_people"], formdata["max_people"], formdata["dates"], formdata["start_time"], formdata["end_time"], "fddjkf"))
        
            connection.commit()
            connection.close
        return redirect("/")

@app.route("/<meeting_id>")
def get_meeting(meeting_id):
    return str(meeting_id)
