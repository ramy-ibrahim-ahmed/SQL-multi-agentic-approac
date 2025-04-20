import sqlite3
from datetime import datetime

conn = sqlite3.connect("lms.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

tables = ["grades", "enrollments", "courses", "teachers", "students", "departments"]
for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table};")

cursor.execute(
    """
    CREATE TABLE departments (
        department_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );
"""
)

cursor.execute(
    """
    CREATE TABLE teachers (
        teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department_id INTEGER,
        FOREIGN KEY(department_id) REFERENCES departments(department_id)
    );
"""
)

cursor.execute(
    """
    CREATE TABLE courses (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department_id INTEGER,
        teacher_id INTEGER,
        FOREIGN KEY(department_id) REFERENCES departments(department_id),
        FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id)
    );
"""
)

cursor.execute(
    """
    CREATE TABLE students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department_id INTEGER,
        FOREIGN KEY(department_id) REFERENCES departments(department_id)
    );
"""
)

cursor.execute(
    """
    CREATE TABLE enrollments (
        enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        enrollment_date TEXT,
        FOREIGN KEY(student_id) REFERENCES students(student_id),
        FOREIGN KEY(course_id) REFERENCES courses(course_id)
    );
"""
)

cursor.execute(
    """
    CREATE TABLE grades (
        grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
        enrollment_id INTEGER,
        grade TEXT,
        grade_date TEXT,
        FOREIGN KEY(enrollment_id) REFERENCES enrollments(enrollment_id)
    );
"""
)

departments = [
    ("Computer Science",),
    ("Mathematics",),
    ("History",),
    ("Physics",),
    ("Literature",),
]
cursor.executemany("INSERT INTO departments (name) VALUES (?);", departments)

teachers = [
    ("Alice Johnson", 1),
    ("Bob Smith", 2),
    ("Charlie Davis", 3),
    ("Diana Evans", 4),
    ("Ethan Wright", 5),
    ("Fiona Lee", 1),
]
cursor.executemany(
    "INSERT INTO teachers (name, department_id) VALUES (?, ?);", teachers
)

courses = [
    ("Introduction to Programming", 1, 1),
    ("Data Structures", 1, 6),
    ("Calculus I", 2, 2),
    ("World History", 3, 3),
    ("Classical Mechanics", 4, 4),
    ("Modern Poetry", 5, 5),
    ("Algorithms", 1, 1),
    ("Linear Algebra", 2, 2),
]
cursor.executemany(
    "INSERT INTO courses (name, department_id, teacher_id) VALUES (?, ?, ?);", courses
)

students = [
    ("John Doe", 1),
    ("Jane Roe", 2),
    ("Mark Spencer", 1),
    ("Lucy Gray", 3),
    ("Sam Brown", 4),
    ("Nina Patel", 5),
    ("Paul Adams", 2),
    ("Laura Wilson", 1),
    ("James King", 4),
    ("Olivia Green", 3),
]
cursor.executemany(
    "INSERT INTO students (name, department_id) VALUES (?, ?);", students
)

today = datetime.now().strftime("%Y-%m-%d")
enrollments = [
    (1, 1, today),
    (2, 3, today),
    (3, 2, today),
    (4, 4, today),
    (5, 5, today),
    (6, 6, today),
    (7, 7, today),
    (8, 8, today),
    (9, 1, today),
    (10, 2, today),
    (1, 7, today),
    (3, 8, today),
]
cursor.executemany(
    "INSERT INTO enrollments (student_id, course_id, enrollment_date) VALUES (?, ?, ?);",
    enrollments,
)

grades = [
    (1, "A", today),
    (2, "B+", today),
    (3, "A-", today),
    (4, "B", today),
    (5, "C+", today),
    (6, "A", today),
    (7, "B-", today),
    (8, "A+", today),
    (9, "B+", today),
    (10, "A", today),
    (11, "C", today),
    (12, "B", today),
]
cursor.executemany(
    "INSERT INTO grades (enrollment_id, grade, grade_date) VALUES (?, ?, ?);", grades
)

conn.commit()
conn.close()

print("Dummy LMS SQLite database 'lms.db' created and populated with sample data.")
