from datetime import datetime
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, student, parent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False)
    teacher_profile = db.relationship('Teacher', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    enrollment_date = db.Column(db.Date, default=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    attendance = db.relationship('Attendance', backref='student', lazy=True)
    grades = db.relationship('Grade', backref='student', lazy=True)

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    qualification = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    hire_date = db.Column(db.Date, default=datetime.utcnow)
    
    # Relationships
    courses = db.relationship('Course', backref='teacher', lazy=True)

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, default=3)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    semester = db.Column(db.String(20))
    academic_year = db.Column(db.String(20))
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    attendance = db.relationship('Attendance', backref='course', lazy=True)
    grades = db.relationship('Grade', backref='course', lazy=True)

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    enrollment_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, completed, dropped
    
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='unique_enrollment'),)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present, absent, late, excused
    remarks = db.Column(db.String(200))
    
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', 'date', name='unique_attendance'),)

class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    assignment_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False)
    percentage = db.Column(db.Float)
    grade_letter = db.Column(db.String(2))
    date_recorded = db.Column(db.Date, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', 'assignment_name', name='unique_grade'),)
    
    def calculate_percentage(self):
        if self.max_score > 0:
            self.percentage = (self.score / self.max_score) * 100
            self.assign_letter_grade()
    
    def assign_letter_grade(self):
        if self.percentage >= 90:
            self.grade_letter = 'A'
        elif self.percentage >= 80:
            self.grade_letter = 'B'
        elif self.percentage >= 70:
            self.grade_letter = 'C'
        elif self.percentage >= 60:
            self.grade_letter = 'D'
        else:
            self.grade_letter = 'F'