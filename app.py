import os
import json
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_required, current_user
from backend.db_models import db, User, Student, Faculty, Course, Subject, Attendance, SystemLog, ModelInfo
from backend.db_manager import init_db, log_system_event
from backend.auth import auth_bp
from backend.routes_api import api_bp

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SECRET_KEY'] = 'ai_attendance_secret_key_1910'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, "database", "attendance.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure database directory exists
os.makedirs(os.path.join(app.root_path, "database"), exist_ok=True)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize DB & Seeder
init_db(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp, url_prefix='/api')


# ==========================================
# PAGE ROUTING CONTROLLERS
# ==========================================

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'faculty':
            return redirect(url_for('faculty_dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('auth.login'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash("Access Denied: Admin privileges required.", "danger")
        return redirect(url_for('index'))
        
    # Gather Metrics
    total_students = Student.query.count()
    total_faculty = Faculty.query.count()
    active_classes = Subject.query.count()
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Today's attendance percentage calculation
    # Number of students present today
    students_present_today = Attendance.query.filter_by(date=today_str).filter(Attendance.status.in_(["Present", "Late"])).count()
    
    # Attendance percentage
    attendance_pct = 0.0
    if total_students > 0:
        attendance_pct = round((students_present_today / total_students) * 100, 1)
        
    # Recent Attendance
    recent_attendance = db.session.query(
        Attendance.date,
        Attendance.time,
        Attendance.status,
        Attendance.confidence,
        Student.name.label('student_name'),
        Student.roll_number,
        Subject.name.label('subject_name')
    ).join(Student, Attendance.student_id == Student.id)\
     .join(Subject, Attendance.subject_id == Subject.id)\
     .order_by(Attendance.created_at.desc())\
     .limit(7).all()
     
    # Training status or latest trained model
    latest_model = ModelInfo.query.order_by(ModelInfo.trained_at.desc()).first()
    
    return render_template(
        'dashboard_admin.html',
        total_students=total_students,
        total_faculty=total_faculty,
        today_attendance=students_present_today,
        attendance_percentage=attendance_pct,
        recent_attendance=recent_attendance,
        active_classes=active_classes,
        latest_model=latest_model
    )


@app.route('/faculty/dashboard')
@login_required
def faculty_dashboard():
    if current_user.role != 'faculty':
        flash("Access Denied: Faculty privileges required.", "danger")
        return redirect(url_for('index'))
        
    faculty = current_user.faculty_profile
    if not faculty:
        flash("Faculty profile not set up.", "danger")
        return redirect(url_for('auth.login'))
        
    # Faculty's assigned subjects
    subjects = Subject.query.filter_by(faculty_id=faculty.id).all()
    
    # Students registered in subjects' courses
    course_ids = [sub.course_id for sub in subjects]
    students = Student.query.filter(Student.course_id.in_(course_ids)).all() if course_ids else []
    
    # Today's attendance counts for faculty classes
    today_str = datetime.now().strftime("%Y-%m-%d")
    faculty_subject_ids = [sub.id for sub in subjects]
    
    today_records = Attendance.query.filter(
        Attendance.subject_id.in_(faculty_subject_ids),
        Attendance.date == today_str
    ).all() if faculty_subject_ids else []
    
    today_present = sum(1 for r in today_records if r.status in ["Present", "Late"])
    
    return render_template(
        'dashboard_faculty.html',
        faculty=faculty,
        subjects=subjects,
        students=students,
        today_present=today_present,
        today_total=len(today_records)
    )


@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash("Access Denied: Student privileges required.", "danger")
        return redirect(url_for('index'))
        
    student = current_user.student_profile
    if not student:
        flash("Student profile not set up.", "danger")
        return redirect(url_for('auth.login'))
        
    # Course and subjects
    course = student.course
    subjects = Subject.query.filter_by(course_id=course.id).all() if course else []
    
    # Attendance percentage for student (all subjects)
    total_classes = Attendance.query.filter_by(student_id=student.id).count()
    present_classes = Attendance.query.filter_by(student_id=student.id).filter(Attendance.status.in_(["Present", "Late"])).count()
    
    att_percentage = 0.0
    if total_classes > 0:
        att_percentage = round((present_classes / total_classes) * 100, 1)
        
    # Attendance history
    history = db.session.query(
        Attendance.date,
        Attendance.time,
        Attendance.status,
        Attendance.confidence,
        Attendance.method,
        Subject.name.label('subject_name'),
        Subject.code.label('subject_code')
    ).join(Subject, Attendance.subject_id == Subject.id)\
     .filter(Attendance.student_id == student.id)\
     .order_by(Attendance.date.desc(), Attendance.time.desc())\
     .limit(15).all()
     
    # Subject-wise attendance breakdown
    subject_stats = []
    for sub in subjects:
        sub_total = Attendance.query.filter_by(student_id=student.id, subject_id=sub.id).count()
        sub_present = Attendance.query.filter_by(student_id=student.id, subject_id=sub.id).filter(Attendance.status.in_(["Present", "Late"])).count()
        sub_pct = round((sub_present / sub_total * 100), 1) if sub_total > 0 else 100.0
        
        subject_stats.append({
            "name": sub.name,
            "code": sub.code,
            "total": sub_total,
            "present": sub_present,
            "percentage": sub_pct
        })
        
    return render_template(
        'dashboard_student.html',
        student=student,
        attendance_percentage=att_percentage,
        history=history,
        subject_stats=subject_stats
    )


# ==========================================
# ADMINISTRATIVE PAGE MANAGEMENT
# ==========================================

@app.route('/admin/students')
@login_required
def student_mgmt():
    if current_user.role != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('index'))
    courses = Course.query.all()
    return render_template('student_mgmt.html', courses=courses)


@app.route('/admin/faculty')
@login_required
def faculty_mgmt():
    if current_user.role != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('index'))
    faculties = Faculty.query.all()
    departments = ["Computer Science", "Information Technology", "Electrical Engineering", "Mechanical Engineering", "Mathematics"]
    return render_template('faculty_mgmt.html', faculties=faculties, departments=departments)


@app.route('/admin/courses', methods=['GET', 'POST'])
@login_required
def course_mgmt():
    if current_user.role != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_course':
            name = request.form.get('name')
            code = request.form.get('code')
            if Course.query.filter_by(code=code).first():
                flash(f"Course code '{code}' already exists.", "danger")
            else:
                c = Course(name=name, code=code)
                db.session.add(c)
                db.session.commit()
                flash("Course added successfully!", "success")
        elif action == 'add_subject':
            name = request.form.get('name')
            code = request.form.get('code')
            course_id = request.form.get('course_id')
            faculty_id = request.form.get('faculty_id')
            if Subject.query.filter_by(code=code).first():
                flash(f"Subject code '{code}' already exists.", "danger")
            else:
                s = Subject(name=name, code=code, course_id=course_id, faculty_id=faculty_id if faculty_id else None)
                db.session.add(s)
                db.session.commit()
                flash("Subject added successfully!", "success")
        return redirect(url_for('course_mgmt'))
        
    courses = Course.query.all()
    subjects = Subject.query.all()
    faculties = Faculty.query.all()
    return render_template('course_mgmt.html', courses=courses, subjects=subjects, faculties=faculties)


@app.route('/admin/dataset')
@login_required
def dataset_mgmt():
    if current_user.role != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('index'))
    students = Student.query.all()
    return render_template('dataset_mgmt.html', students=students)


@app.route('/admin/train')
@login_required
def model_training():
    if current_user.role != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('index'))
        
    models = ModelInfo.query.order_by(ModelInfo.trained_at.desc()).all()
    
    # Check if plots exist, to show them in the UI
    models_dir = os.path.join(app.root_path, "static", "images", "plots")
    os.makedirs(models_dir, exist_ok=True)
    
    # Copy plots from models/ to static/images/plots/ so Flask can serve them dynamically!
    src_dir = os.path.abspath(os.path.join(app.root_path, "..", "models"))
    plots = ["training_curves.png", "confusion_matrix.png", "roc_curve.png"]
    for plot in plots:
        src = os.path.join(src_dir, plot)
        dst = os.path.join(models_dir, plot)
        if os.path.exists(src):
            try:
                import shutil
                shutil.copy2(src, dst)
            except Exception as e:
                print(f"Error copying plot {plot}: {e}")
                
    return render_template('model_training.html', models=models)


@app.route('/attendance')
@login_required
def attendance_view():
    courses = Course.query.all()
    subjects = Subject.query.all()
    
    # Filter variables
    date_filter = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    subject_filter = request.args.get('subject_id')
    course_filter = request.args.get('course_id')
    
    # Query building
    query = db.session.query(
        Attendance.id,
        Attendance.date,
        Attendance.time,
        Attendance.status,
        Attendance.confidence,
        Attendance.method,
        Attendance.student_id,
        Attendance.subject_id,
        Student.name.label('student_name'),
        Student.roll_number,
        Course.name.label('course_name'),
        Subject.name.label('subject_name')
    ).join(Student, Attendance.student_id == Student.id)\
     .join(Course, Student.course_id == Course.id)\
     .join(Subject, Attendance.subject_id == Subject.id)
     
    if date_filter:
        query = query.filter(Attendance.date == date_filter)
    if subject_filter:
        query = query.filter(Attendance.subject_id == subject_filter)
    if course_filter:
        query = query.filter(Student.course_id == course_filter)
        
    records = query.order_by(Attendance.date.desc(), Attendance.time.desc()).all()
    
    return render_template(
        'attendance_view.html',
        records=records,
        courses=courses,
        subjects=subjects,
        selected_date=date_filter,
        selected_subject=subject_filter,
        selected_course=course_filter
    )


@app.route('/recognize')
@login_required
def live_recognition():
    # Only faculty and admins can initiate camera recognition sessions
    if current_user.role not in ['admin', 'faculty']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('index'))
        
    subjects = Subject.query.all()
    return render_template('live_recognition.html', subjects=subjects)


@app.route('/profile')
@login_required
def profile():
    student = current_user.student_profile if current_user.role == 'student' else None
    faculty = current_user.faculty_profile if current_user.role == 'faculty' else None
    
    # Generate QR Code details for Student ID
    qr_data = None
    if student:
        # Save Student info to a string which will be parsed into QR
        qr_info = {
            "name": student.name,
            "roll": student.roll_number,
            "course": student.course.name if student.course else "Unassigned",
            "email": current_user.email
        }
        qr_data = json.dumps(qr_info)
        
    # Get system logs if admin
    logs = None
    if current_user.role == 'admin':
        logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(50).all()
        
    return render_template('profile.html', student=student, faculty=faculty, qr_data=qr_data, logs=logs)


# Photo update request handler (Mock)
@app.route('/profile/update-photo', methods=['POST'])
@login_required
def update_photo_request():
    if current_user.role != 'student':
        flash("Unauthorized.", "danger")
        return redirect(url_for('profile'))
        
    flash("Your photo update request has been submitted to the administrator for review.", "success")
    log_system_event("Info", f"Student '{current_user.student_profile.name}' submitted a photo update request.")
    return redirect(url_for('profile'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
