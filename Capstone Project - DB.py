import sqlite3
import json
import xml.etree.ElementTree as ET

try:
    conn = sqlite3.connect("HyperionDev.db")
except sqlite3.Error:
    print("Please store your database as HyperionDev.db")
    quit()

cur = conn.cursor()

# Load SQL queries from create_database.sql file
with open("create_database", "r") as sql_file:
    sql_queries = sql_file.read()

# Execute SQL queries
try:
    cur.executescript(sql_queries)
except sqlite3.Error as e:
    print(f"Error executing SQL queries: {e}")
    quit()

def usage_is_incorrect(input, num_args):
    if len(input) != num_args + 1:
        print(f"The {input[0]} command requires {num_args} arguments.")
        return True
    return False

def store_data_as_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

def store_data_as_xml(data, filename):
    root = ET.Element("data")
    for row in data:
        entry = ET.SubElement(root, "entry")
        for key, value in row.items():
            field = ET.SubElement(entry, key)
            field.text = str(value)
    
    tree = ET.ElementTree(root)
    tree.write(filename)

def offer_to_store(data):
    while True:
        print("Would you like to store this result?")
        choice = input("Y/[N]? : ").strip().lower()

        if choice == "y":
            filename = input("Specify filename. Must end in .xml or .json: ")
            ext = filename.split(".")[-1]
            if ext == 'xml':
                store_data_as_xml(data, filename)
            elif ext == 'json':
                store_data_as_json(data, filename)
            else:
                print("Invalid file extension. Please use .xml or .json")

        elif choice == 'n':
            break

        else:
            print("Invalid choice")

usage = '''
What would you like to do?

d - demo
vs <student_id>            - view subjects taken by a student
la <firstname> <surname>   - lookup address for a given firstname and surname
lr <student_id>            - list reviews for a given student_id
lc <teacher_id>            - list all courses taken by teacher_id
lnc                        - list all students who haven't completed their course
lf                         - list all students who have completed their course and achieved 30 or below
e                          - exit this program

Type your option here: '''

print("Welcome to the data querying app!")

while True:
    print()
    # Get input from the user
    user_input = input(usage).split(" ")
    print()

    # Parse user input into command and args
    command = user_input[0]
    if len(user_input) > 1:
        args = user_input[1:]

    if command == 'd':
        data = cur.execute("SELECT * FROM Student").fetchall()
        for _, firstname, surname, _, _ in data:
            print(f"{firstname} {surname}")

    elif command == 'vs':
        if usage_is_incorrect(user_input, 1):
            continue
        student_id = args[0]
        data = cur.execute(f"SELECT Course.course_name FROM StudentCourse JOIN Course ON StudentCourse.course_code = Course.course_code WHERE StudentCourse.student_id = '{student_id}' AND StudentCourse.is_complete = 1").fetchall()
        offer_to_store(data)

    elif command == 'la':
        if usage_is_incorrect(user_input, 2):
            continue
        firstname, surname = args[0], args[1]
        data = cur.execute(f"SELECT street, city FROM Address JOIN Student ON Address.address_id = Student.address_id WHERE Student.first_name = '{firstname}' AND Student.last_name = '{surname}'").fetchall()
        offer_to_store(data)

    elif command == 'lr':
        if usage_is_incorrect(user_input, 1):
            continue
        student_id = args[0]
        data = cur.execute(f"SELECT completeness, efficiency, style, documentation, review_text FROM Review WHERE student_id = '{student_id}'").fetchall()
        offer_to_store(data)

    elif command == 'lc':
        if usage_is_incorrect(user_input, 1):
            continue
        teacher_id = args[0]
        data = cur.execute(f"SELECT course_name FROM Course WHERE teacher_id = '{teacher_id}'").fetchall()
        offer_to_store(data)

    elif command == 'lnc':
        data = cur.execute("SELECT Student.student_id, Student.first_name, Student.last_name, Student.email, Course.course_name FROM Student LEFT JOIN StudentCourse ON Student.student_id = StudentCourse.student_id LEFT JOIN Course ON StudentCourse.course_code = Course.course_code WHERE StudentCourse.is_complete IS NULL").fetchall()
        offer_to_store(data)

    elif command == 'lf':
        data = cur.execute("SELECT Student.student_id, Student.first_name, Student.last_name, Student.email, Course.course_name, StudentCourse.mark FROM StudentCourse JOIN Student ON StudentCourse.student_id = Student.student_id JOIN Course ON StudentCourse.course_code = Course.course_code WHERE StudentCourse.is_complete = 1 AND (StudentCourse.mark IS NULL OR StudentCourse.mark <= 30)").fetchall()
        offer_to_store(data)

    elif command == 'e':
        print("Program exited successfully!")
        break

    else:
        print(f"Incorrect command: '{command}'")