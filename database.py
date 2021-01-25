import sqlite3

# Connect
connection = sqlite3.connect("database.db")
cursor = connection.cursor()

# Command for creating meeting table
meeting_command = """CREATE TABLE MEETING (
eventname TEXT NOT NULL,
email TEXT NOT NULL,
name TEXT,
password TEXT NOT NULL,
min_event INT,
max_event INT,
min_people INT,
max_people INT,
dates TEXT NOT NULL,
start_time TEXT NOT NULL,
end_time TEXT NOT NULL,
hours INT NOT NULL,
minutes INT NOT NULL,
code TEXT NOT NULL,
PRIMARY KEY(code));"""

cursor.execute(meeting_command)

# Command for creating registration table
registration_command = """CREATE TABLE REGISTRATION (
email TEXT NOT NULL,
name TEXT NOT NULL,
password TEXT NOT NULL,
availability TEXT,
meeting_code TEXT NOT NULL,
registrant_code TEXT NOT NULL,
confirmed_meeting TEXT);"""

cursor.execute(registration_command)

# Commit
connection.commit()

# Close connection
connection.close()
