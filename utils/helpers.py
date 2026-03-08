from datetime import datetime, date
import json

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def calculate_gpa(grades):
    if not grades:
        return 0.0
    
    grade_points = {
        'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0
    }
    
    total_points = 0
    total_credits = 0
    
    for grade in grades:
        if grade.grade_letter in grade_points:
            total_points += grade_points[grade.grade_letter] * grade.course.credits
            total_credits += grade.course.credits
    
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

def format_response(data=None, message=None, error=None, status_code=200):
    response = {}
    
    if data is not None:
        response['data'] = data
    if message is not None:
        response['message'] = message
    if error is not None:
        response['error'] = error
    
    return json.dumps(response, cls=JSONEncoder), status_code