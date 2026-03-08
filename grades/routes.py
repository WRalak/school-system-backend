from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models import Grade, Student, Course

grades_bp = Blueprint('grades', __name__, url_prefix='/api/grades')

@grades_bp.route('', methods=['POST'])
@jwt_required()
def create_grade():
    data = request.get_json()
    
    grade = Grade(
        student_id=data['student_id'],
        course_id=data['course_id'],
        assignment_name=data['assignment_name'],
        score=data['score'],
        max_score=data['max_score']
    )
    
    grade.calculate_percentage()
    
    db.session.add(grade)
    db.session.commit()
    
    return jsonify({'message': 'Grade recorded successfully', 'grade_id': grade.id}), 201

@grades_bp.route('/<int:grade_id>', methods=['PUT'])
@jwt_required()
def update_grade(grade_id):
    grade = Grade.query.get_or_404(grade_id)
    data = request.get_json()
    
    if 'score' in data:
        grade.score = data['score']
    if 'max_score' in data:
        grade.max_score = data['max_score']
    
    grade.calculate_percentage()
    db.session.commit()
    
    return jsonify({'message': 'Grade updated successfully'}), 200

@grades_bp.route('/course/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_grades(course_id):
    grades = Grade.query.filter_by(course_id=course_id).all()
    result = []
    for grade in grades:
        result.append({
            'id': grade.id,
            'student_name': f"{grade.student.user.first_name} {grade.student.user.last_name}",
            'student_id': grade.student.student_id,
            'assignment_name': grade.assignment_name,
            'score': grade.score,
            'max_score': grade.max_score,
            'percentage': grade.percentage,
            'grade_letter': grade.grade_letter
        })
    return jsonify(result), 200