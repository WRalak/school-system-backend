from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Teacher, User, Course
from datetime import datetime

teachers_bp = Blueprint('teachers', __name__, url_prefix='/api/teachers')

@teachers_bp.route('', methods=['GET'])
@jwt_required()
def get_teachers():
    teachers = Teacher.query.all()
    result = []
    for teacher in teachers:
        result.append({
            'id': teacher.id,
            'employee_id': teacher.employee_id,
            'first_name': teacher.user.first_name,
            'last_name': teacher.user.last_name,
            'email': teacher.user.email,
            'qualification': teacher.qualification,
            'specialization': teacher.specialization,
            'hire_date': teacher.hire_date.isoformat() if teacher.hire_date else None,
            'course_count': len(teacher.courses)
        })
    return jsonify(result), 200

@teachers_bp.route('/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    courses = [{
        'id': course.id,
        'course_code': course.course_code,
        'name': course.name,
        'credits': course.credits,
        'semester': course.semester
    } for course in teacher.courses]
    
    return jsonify({
        'id': teacher.id,
        'employee_id': teacher.employee_id,
        'first_name': teacher.user.first_name,
        'last_name': teacher.user.last_name,
        'email': teacher.user.email,
        'qualification': teacher.qualification,
        'specialization': teacher.specialization,
        'hire_date': teacher.hire_date.isoformat() if teacher.hire_date else None,
        'courses': courses
    }), 200

@teachers_bp.route('', methods=['POST'])
@jwt_required()
def create_teacher():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'employee_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create user first
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role='teacher'
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.flush()
    
    # Create teacher profile
    teacher = Teacher(
        user_id=user.id,
        employee_id=data['employee_id'],
        qualification=data.get('qualification'),
        specialization=data.get('specialization'),
        hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date() if data.get('hire_date') else datetime.utcnow().date()
    )
    
    db.session.add(teacher)
    db.session.commit()
    
    return jsonify({'message': 'Teacher created successfully', 'teacher_id': teacher.id}), 201

@teachers_bp.route('/<int:teacher_id>', methods=['PUT'])
@jwt_required()
def update_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    data = request.get_json()
    
    # Update user fields
    if 'first_name' in data:
        teacher.user.first_name = data['first_name']
    if 'last_name' in data:
        teacher.user.last_name = data['last_name']
    if 'email' in data:
        teacher.user.email = data['email']
    
    # Update teacher fields
    if 'qualification' in data:
        teacher.qualification = data['qualification']
    if 'specialization' in data:
        teacher.specialization = data['specialization']
    if 'hire_date' in data:
        teacher.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
    
    db.session.commit()
    
    return jsonify({'message': 'Teacher updated successfully'}), 200

@teachers_bp.route('/<int:teacher_id>', methods=['DELETE'])
@jwt_required()
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    
    # Check if teacher has courses
    if teacher.courses:
        return jsonify({'error': 'Cannot delete teacher with assigned courses'}), 400
    
    user = teacher.user
    db.session.delete(teacher)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'Teacher deleted successfully'}), 200

@teachers_bp.route('/<int:teacher_id>/courses', methods=['GET'])
@jwt_required()
def get_teacher_courses(teacher_id):
    courses = Course.query.filter_by(teacher_id=teacher_id).all()
    result = []
    for course in courses:
        result.append({
            'id': course.id,
            'course_code': course.course_code,
            'name': course.name,
            'credits': course.credits,
            'semester': course.semester,
            'academic_year': course.academic_year,
            'enrollment_count': len(course.enrollments)
        })
    return jsonify(result), 200

@teachers_bp.route('/<int:teacher_id>/dashboard', methods=['GET'])
@jwt_required()
def get_teacher_dashboard(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    
    # Get courses taught by teacher
    courses = teacher.courses
    total_students = 0
    course_stats = []
    
    for course in courses:
        student_count = len(course.enrollments)
        total_students += student_count
        
        # Get recent grades for this course
        recent_grades = [{
            'student_name': f"{g.student.user.first_name} {g.student.user.last_name}",
            'assignment': g.assignment_name,
            'score': g.score,
            'percentage': g.percentage
        } for g in course.grades[-5:]]  # Last 5 grades
        
        course_stats.append({
            'course_id': course.id,
            'course_name': course.name,
            'student_count': student_count,
            'recent_grades': recent_grades
        })
    
    return jsonify({
        'teacher_name': f"{teacher.user.first_name} {teacher.user.last_name}",
        'total_courses': len(courses),
        'total_students': total_students,
        'course_stats': course_stats
    }), 200