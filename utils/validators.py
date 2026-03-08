import re
from datetime import datetime

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def validate_date(date_string, format='%Y-%m-%d'):
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False

def validate_student_id(student_id):
    pattern = r'^STU\d{6}$'
    return re.match(pattern, student_id) is not None

def validate_employee_id(employee_id):
    pattern = r'^EMP\d{6}$'
    return re.match(pattern, employee_id) is not None

def validate_course_code(course_code):
    pattern = r'^[A-Z]{3}\d{3}$'
    return re.match(pattern, course_code) is not None