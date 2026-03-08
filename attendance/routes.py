from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models import Attendance, Student, Course
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

@attendance_bp.route('', methods=['POST'])
@jwt_required()
def mark_attendance():
    data = request.get_json()
    
    # Check if attendance already marked for this student/course/date
    existing = Attendance.query.filter_by(
        student_id=data['student_id'],
        course_id=data['course_id'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date()
    ).first()
    
    if existing:
        existing.status = data['status']
        existing.remarks = data.get('remarks')
    else:
        attendance = Attendance(
            student_id=data['student_id'],
            course_id=data['course_id'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            status=data['status'],
            remarks=data.get('remarks')
        )
        db.session.add(attendance)
    
    db.session.commit()
    
    return jsonify({'message': 'Attendance marked successfully'}), 201

@attendance_bp.route('/course/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_attendance(course_id):
    date_str = request.args.get('date')
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        attendance = Attendance.query.filter_by(course_id=course_id, date=date).all()
    else:
        attendance = Attendance.query.filter_by(course_id=course_id).all()
    
    result = []
    for record in attendance:
        result.append({
            'id': record.id,
            'student_name': f"{record.student.user.first_name} {record.student.user.last_name}",
            'student_id': record.student.student_id,
            'date': record.date.isoformat(),
            'status': record.status,
            'remarks': record.remarks
        })
    
    return jsonify(result), 200

@attendance_bp.route('/student/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_attendance(student_id):
    attendance = Attendance.query.filter_by(student_id=student_id).all()
    result = []
    for record in attendance:
        result.append({
            'id': record.id,
            'course': record.course.name,
            'date': record.date.isoformat(),
            'status': record.status,
            'remarks': record.remarks
        })
    return jsonify(result), 200