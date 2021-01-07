import sqlite3
import uuid
import datetime
import json

from flask import Flask, render_template, request, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAYS = ["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"]

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
            meeting_search_command = "SELECT * FROM MEETING WHERE code=?"
            cursor.execute(meeting_search_command, (formdata["meeting_id"],))
            rows = cursor.fetchall()
            
            if len(rows) != 1:
                flash("This meeting code does not exist")
                return redirect("/join/")
            
            # Search user email
            email_search_command = "SELECT name, password, registrant_code FROM REGISTRATION WHERE meeting_code=? AND email=?"
            cursor.execute(email_search_command, (formdata["meeting_id"], formdata["email"],))
            rows = cursor.fetchall()
            
            # meeting exists and this user is new
            if len(rows) == 0:
                registrant_code = str(uuid.uuid4())
                passwordhash = generate_password_hash(formdata["password"])
                insert_command = "INSERT INTO REGISTRATION (email, name, password, meeting_code, registrant_code, admin) VALUES (?, ?, ?, ?, ?, ?)"
                cursor.execute(insert_command, (formdata["email"], formdata["name"], passwordhash, formdata["meeting_id"], registrant_code, False))
                connection.commit()
                return redirect("/" + formdata["meeting_id"] + "/" + registrant_code)
            
            # meeting exists and user info is wrong
            if rows[0][0] != formdata["name"]:
                flash("Incorrect name")
                return redirect("/join/" + meeting_id)
            if not check_password_hash(rows[0][1], formdata["password"]):
                flash("Incorrect password")
                return redirect("/join/" + meeting_id)
            
            # meeting exists and this user is returning
            return redirect("/" + formdata["meeting_id"] + "/" + rows[0][2])
            
@app.route("/<meeting_id>/<registrant_id>")
def get_availability(meeting_id, registrant_id):
    with sqlite3.connect("database.db") as connection:
        # Fetch this particular meeting info
        cursor = connection.cursor()
        meeting_search = "SELECT dates, start_time, end_time FROM MEETING WHERE code=?"
        cursor.execute(meeting_search, (meeting_id, ))
        rows = cursor.fetchall()
        
        # Modify selected info
        dates = rows[0][0].split(",")
        dates_days = []
        for date in dates:
            date = date.split("/")
            month = MONTHS[int(date[0]) - 1]
            day = date[1]
            weekday = WEEKDAYS[datetime.datetime(int(date[2]), int(date[0]), int(date[1])).weekday()]
            dates_days.append((month + " " + day, weekday, date[2] + date[0] + date[1]))
        
        start_time = int(rows[0][1])
        end_time = int(rows[0][2])
        
        # Fetch availability info
        availability_search = "SELECT availability FROM REGISTRATION WHERE meeting_code=? AND registrant_code=?"
        cursor.execute(availability_search, (meeting_id, registrant_id))
        rows = cursor.fetchall()
        availability = rows[0][0]
        
        # Modify avilability string into array
        availability = availability.split(",")
        availability_dict = {}
        for a in availability:
            a = a.split(":")
            availability_dict[a[0]] = True if a[1] == "true" else False
        
        # return template
        return render_template("availability.html", dates_days = dates_days, start_time = start_time, end_time = end_time, meeting_id = meeting_id, registrant_id = registrant_id, availability = availability_dict)

@app.route("/request/<meeting_id>/<registrant_id>", methods=["POST"])
def update(meeting_id, registrant_id):
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        
        # Find meeting
        meeting_search = "SELECT dates, start_time, end_time FROM MEETING WHERE code=?"
        cursor.execute(meeting_search, (meeting_id, ))
        rows = cursor.fetchall()
        
        # Turn availability into string
        availability = ""
        dates = rows[0][0].split(",")
        dates = [date[6:] + date[:6].replace("/", "") for date in dates]
        start_time = int(rows[0][1])
        end_time = int(rows[0][2])
        for date in dates:
            for i in range(start_time, end_time):
                slot1 = date + str(i) + "00" + str(i) + "30"
                slot2 = date + str(i) + "30" + str(i + 1) + "00"
                availability = availability + slot1 + ":" + request.form[slot1] + "," + slot2 + ":" + request.form[slot2] + ","
        
        # Add availability string to database
        add_availability = "UPDATE REGISTRATION SET availability=? WHERE meeting_code=? AND registrant_code=?"
        cursor.execute(add_availability, (availability[:-1], meeting_id, registrant_id))
    
    return json.dumps([""])

@app.route("/login/<meeting_id>", methods=["POST"])
def login(meeting_id):
    pw = request.form["password"]
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        
        # Find meeting password
        meeting_search = "SELECT password FROM MEETING WHERE code=?"
        cursor.execute(meeting_search, (meeting_id, ))
        rows = cursor.fetchall()
        
        # Redirect & flash error message if wrong password
        if not check_password_hash(rows[0][0], pw):
            flash("Incorrect password for the meeting")
            return redirect("/" + meeting_id + "/")
        
        else:
            return redirect("/" + meeting_id + "/logged")

@app.route("/<meeting_id>/")
def get_meeting_login(meeting_id):
    return render_template("admin.html", code = meeting_id, logged = False)

@app.route("/<meeting_id>/logged")
def get_meeting_info(meeting_id):
    return render_template("admin.html", code = meeting_id, logged = True)
