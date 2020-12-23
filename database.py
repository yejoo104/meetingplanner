import sqlite3

# Connect
connection = sqlite3.connect("database.db")
cursor = connection.cursor()

# Command for creating meeting table
meeting_command = """CREATE TABLE MEETING (
eventname TEXT,
email TEXT,
name TEXT,
password TEXT,
min_event INT,
max_event INT,
min_people INT,
max_people INT,
dates TEXT,
start_time TEXT,
end_time TEXT,
code TEXT);"""

cursor.execute(meeting_command)

# Commit
connection.commit()

# Close connection
connection.close()
