from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Student, User, Enrollment, Course, Grade, Attendance
from datetime import datetime

students_bp = Blueprint('students', __name__, url_prefix='/api/students')

@students_bp.route('', methods=['GET'])
@jwt_required()
def get_students():
    students = Student.query.all()
    result = []
    for student in students:
        result.append({
            'id': student.id,
            'student_id': student.student_id,
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
            'email': student.user.email,
            'phone': student.phone,
            'enrollment_date': student.enrollment_date.isoformat() if student.enrollment_date else None
        })
    return jsonify(result), 200

@students_bp.route('/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    student = Student.query.get_or_404(student_id)
    return jsonify({
        'id': student.id,
        'student_id': student.student_id,
        'first_name': student.user.first_name,
        'last_name': student.user.last_name,
        'email': student.user.email,
        'date_of_birth': student.date_of_birth.isoformat() if student.date_of_birth else None,
        'address': student.address,
        'phone': student.phone,
        'enrollment_date': student.enrollment_date.isoformat() if student.enrollment_date else None
    }), 200

@students_bp.route('', methods=['POST'])
@jwt_required()
def create_student():
    data = request.get_json()
    
    # Create user first
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role='student'
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.flush()
    
    # Create student profile
    student = Student(
        user_id=user.id,
        student_id=data['student_id'],
        date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
        address=data.get('address'),
        phone=data.get('phone')
    )
    
    db.session.add(student)
    db.session.commit()
    
    return jsonify({'message': 'Student created successfully', 'student_id': student.id}), 201

@students_bp.route('/<int:student_id>/courses', methods=['GET'])
@jwt_required()
def get_student_courses(student_id):
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    courses = []
    for enrollment in enrollments:
        course = enrollment.course
        courses.append({
            'id': course.id,
            'course_code': course.course_code,
            'name': course.name,
            'credits': course.credits,
            'teacher': f"{course.teacher.user.first_name} {course.teacher.user.last_name}" if course.teacher else None,
            'status': enrollment.status
        })
    return jsonify(courses), 200

@students_bp.route('/<int:student_id>/grades', methods=['GET'])
@jwt_required()
def get_student_grades(student_id):
    grades = Grade.query.filter_by(student_id=student_id).all()
    result = []
    for grade in grades:
        result.append({
            'id': grade.id,
            'course': grade.course.name,
            'assignment_name': grade.assignment_name,
            'score': grade.score,
            'max_score': grade.max_score,
            'percentage': grade.percentage,
            'grade_letter': grade.grade_letter,
            'date_recorded': grade.date_recorded.isoformat() if grade.date_recorded else None
        })
    return jsonify(result), 200