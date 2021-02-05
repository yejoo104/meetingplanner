import sqlite3
import uuid
import datetime
import json

from flask import Flask, render_template, request, redirect, flash, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import generate_password_hash, check_password_hash
from algorithms import schedule, next_slot

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAYS = ["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"]

app = Flask(__name__)
app.secret_key = 'eicdfwi375pfme3795e93bco3854uf'

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["GET", "POST"])
def plannerhome():
    session.clear()
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
    session.clear()
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
                insert_command = "INSERT INTO REGISTRATION (email, name, password, meeting_code, registrant_code) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(insert_command, (formdata["email"], formdata["name"], passwordhash, formdata["meeting_id"], registrant_code))
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
        meeting_search = "SELECT dates, start_time, end_time, hours, minutes FROM MEETING WHERE code=?"
        cursor.execute(meeting_search, (meeting_id, ))
        rows = cursor.fetchall()
        meeting_slots = (rows[0][3] * 60 + rows[0][4]) // 30
        
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
        availability_search = "SELECT availability, confirmed_meeting, name FROM REGISTRATION WHERE meeting_code=? AND registrant_code=?"
        cursor.execute(availability_search, (meeting_id, registrant_id))
        rows = cursor.fetchall()
        availability = rows[0][0]
        name = rows[0][2]
        
        # Modify avilability string into array, if info exists
        availability_dict = {}
        if availability:
            availability = availability.split(",")
            for a in availability:
                a = a.split(":")
                availability_dict[a[0]] = True if a[1] == "true" else False
        
        # Modify confirmed_meeting info into confirmed slots, if there is a confirmed meeting
        meetings = []
        confirmed_meeting = rows[0][1]
        if confirmed_meeting:
            if confirmed_meeting[-2:] == "00":
                curr_slot = confirmed_meeting + confirmed_meeting[8: 8 + (len(confirmed_meeting) - 8) // 2] + "30"
            else:
                curr_slot = confirmed_meeting + str(int(confirmed_meeting[8: 8 + (len(confirmed_meeting) - 8) // 2]) + 1) + "00"
        
            for i in range(meeting_slots):
                meetings.append(curr_slot)
                curr_slot = next_slot(curr_slot)
                
        # Find info about confirmed meetings
        confirmed_search = """SELECT date, start_time, end_time, people FROM CONFIRMED WHERE meeting_code=? AND PEOPLE LIKE ?"""
        cursor.execute(confirmed_search, (meeting_id, '%' + name + '%'))
        confirmed_rows = cursor.fetchall()
        
        # return template
        return render_template("availability.html", dates_days = dates_days, start_time = start_time, end_time = end_time, meeting_id = meeting_id, registrant_id = registrant_id, availability = availability_dict, meetings = meetings, confirmed = confirmed_rows)

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
    session.clear()
    pw = request.form["password"]
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        
        # Find meeting password
        meeting_search = "SELECT password FROM MEETING WHERE code=?"
        cursor.execute(meeting_search, (meeting_id, ))
        rows = cursor.fetchall()
        
        # Redirect & flash error message if wrong password
        if not check_password_hash(rows[0][0], pw):
            session["meeting_id"] = ""
            flash("Incorrect password for the meeting")
            return redirect("/" + meeting_id + "/")
        
        else:
            session["meeting_id"] = meeting_id
            return redirect("/" + meeting_id + "/")

@app.route("/<meeting_id>/", methods=["GET", "POST"])
def get_meeting(meeting_id):
    # Meeting admin is not logged in or logged in to another meeting
    if not session or session["meeting_id"] != meeting_id:
        return render_template("admin.html", code = meeting_id, logged = False, dates_days = [], start_time = 0, end_time = 0, dict = {}, people = [], scheduled = {})

    # Meeting admin is logged in
    else:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            
            # Fetch meeting info
            meeting_search = "SELECT dates, start_time, end_time, hours, minutes FROM MEETING WHERE code=?"
            cursor.execute(meeting_search, (meeting_id, ))
            rows = cursor.fetchall()
            
            # Modify meeting info
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
            meeting_length = rows[0][3] * 60 + rows[0][4]
            
            # Fetch info about those who marked their availability
            registrant_search = "SELECT name, availability FROM registration WHERE meeting_code=?"
            cursor.execute(registrant_search, (meeting_id, ))
            registrants = cursor.fetchall()
            
            # If no registrants have marked availability, return template now :)
            if len(registrants) == 0:
                if request.method == "POST":
                    flash("There is no schedule to confirm")
                return render_template("admin.html", code = meeting_id, logged = True, dates_days = dates_days, start_time = start_time, end_time = end_time, dict = {}, people = [], scheduled = {})

            # Create a registrant_dict where keys are people's names and values are a list of available slots
            registrant_dict = {}
            for registrant in registrants:
                slots = registrant[1].split(",")
                available_slots = []
                for slot in slots:
                    stringsplit = slot.split(":")
                    if stringsplit[1] == "true":
                        available_slots.append(stringsplit[0])
                registrant_dict[registrant[0]] = available_slots
            
            # Create a dict where keys are timeslots and values are a list of available people
            dict = {}
            for date in dates_days:
                for time in range(start_time, end_time):
                    for slot in [date[2] + str(time) + "00" + str(time) + "30", date[2] + str(time) + "30" + str(time + 1) + "00"]:
                        slot_ppl = []
                        for registrant in registrant_dict:
                            if slot in registrant_dict[registrant]:
                                slot_ppl.append(registrant)
                        dict[slot] = slot_ppl
            
            # Run a schedule function to figure out the optimal schedule based on current availabilities
            for i in range(len(dates)):
                dates[i] = dates[i][-4:] + dates[i][:2] + dates[i][3:5]
            scheduled = schedule(meeting_length, dict, dates, start_time, end_time)
            
            # Modify dictionary
            for slot in scheduled:
                date_string = MONTHS[int(slot[4:6]) - 1] + " " + slot[6:8]
                slot_time = slot[8: 8 + (len(slot) - 8) // 2]
                start_string = slot_time + ":00"
                end_string = str(int(slot_time) + rows[0][3]) + ":" + format(rows[0][4], '02d')
                scheduled[slot] = (date_string, start_string, end_string, ", ".join(scheduled[slot]), scheduled[slot])
            
            # When admin confirms, delete previously confirmed meetings and add confirmed meeting info to sql
            if request.method == "POST" and "confirm" in request.form:
                if len(scheduled) == 0:
                    flash("There is no schedule to confirm")
                else:
                    delete_command = "DELETE FROM CONFIRMED WHERE meeting_code=?"
                    cursor.execute(delete_command, (meeting_id, ))
                    for slot in scheduled:
                        # add to confirmed table
                        confirmed_meeting_command = "INSERT INTO CONFIRMED(meeting_code, date, start_time, end_time, people) VALUES(?, ?, ?, ?, ?)"
                        cursor.execute(confirmed_meeting_command, (meeting_id, scheduled[slot][0], scheduled[slot][1], scheduled[slot][2], scheduled[slot][3]))
                        
                        # update registration table
                        for person in scheduled[slot][4]:
                            confirmed_command = "UPDATE REGISTRATION SET confirmed_meeting=? WHERE name=? AND meeting_code=?"
                            cursor.execute(confirmed_command, (slot, person, meeting_id))
                    flash("Schedule has been confirmed")
        
        return render_template("admin.html", code = meeting_id, logged = True, dates_days = dates_days, start_time = start_time, end_time = end_time, dict=dict, people=registrant_dict.keys(), scheduled = scheduled)
