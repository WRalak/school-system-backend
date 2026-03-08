from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models import Course, Teacher, Enrollment, Student

courses_bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@courses_bp.route('', methods=['GET'])
@jwt_required()
def get_courses():
    courses = Course.query.all()
    result = []
    for course in courses:
        teacher_name = f"{course.teacher.user.first_name} {course.teacher.user.last_name}" if course.teacher else None
        result.append({
            'id': course.id,
            'course_code': course.course_code,
            'name': course.name,
            'description': course.description,
            'credits': course.credits,
            'teacher': teacher_name,
            'semester': course.semester,
            'academic_year': course.academic_year,
            'enrollment_count': len(course.enrollments)
        })
    return jsonify(result), 200

@courses_bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    teacher_name = f"{course.teacher.user.first_name} {course.teacher.user.last_name}" if course.teacher else None
    
    return jsonify({
        'id': course.id,
        'course_code': course.course_code,
        'name': course.name,
        'description': course.description,
        'credits': course.credits,
        'teacher': teacher_name,
        'semester': course.semester,
        'academic_year': course.academic_year
    }), 200

@courses_bp.route('', methods=['POST'])
@jwt_required()
def create_course():
    data = request.get_json()
    
    course = Course(
        course_code=data['course_code'],
        name=data['name'],
        description=data.get('description'),
        credits=data.get('credits', 3),
        teacher_id=data.get('teacher_id'),
        semester=data.get('semester'),
        academic_year=data.get('academic_year')
    )
    
    db.session.add(course)
    db.session.commit()
    
    return jsonify({'message': 'Course created successfully', 'course_id': course.id}), 201

@courses_bp.route('/<int:course_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_student(course_id):
    data = request.get_json()
    student_id = data['student_id']
    
    # Check if already enrolled
    existing = Enrollment.query.filter_by(
        student_id=student_id, 
        course_id=course_id
    ).first()
    
    if existing:
        return jsonify({'error': 'Student already enrolled in this course'}), 400
    
    enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id
    )
    
    db.session.add(enrollment)
    db.session.commit()
    
    return jsonify({'message': 'Student enrolled successfully'}), 201

@courses_bp.route('/<int:course_id>/students', methods=['GET'])
@jwt_required()
def get_course_students(course_id):
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    students = []
    for enrollment in enrollments:
        student = enrollment.student
        students.append({
            'id': student.id,
            'student_id': student.student_id,
            'name': f"{student.user.first_name} {student.user.last_name}",
            'email': student.user.email,
            'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None,
            'status': enrollment.status
        })
    return jsonify(students), 200