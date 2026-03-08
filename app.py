from flask import Flask, jsonify
from extensions import db, migrate, jwt, cors, login_manager
from config import Config
import os

# Import blueprints
from auth.routes import auth_bp
from students.routes import students_bp
from teachers.routes import teachers_bp
from courses.routes import courses_bp
from grades.routes import grades_bp
from attendance.routes import attendance_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Print database URI for debugging
    print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Database file will be created at: {os.path.abspath('school.db')}")
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])
    login_manager.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(attendance_bp)
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'School system API is running'}), 200
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        print("Database tables created/verified")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)