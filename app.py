from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from config import Config

# -----------------------------
# Initialize Flask app
# -----------------------------
app = Flask(__name__)
app.config.from_object(Config)

# -----------------------------
# Initialize Database
# -----------------------------
db = SQLAlchemy(app)

# -----------------------------
# Initialize Login Manager
# -----------------------------
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# -----------------------------
# Models
# -----------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'jobseeker' or 'employer'

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(100))
    location = db.Column(db.String(100))
    salary = db.Column(db.String(50))
    category = db.Column(db.String(100))
    posted_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# -----------------------------
# Login loader
# -----------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def index():
    jobs = Job.query.all()
    return render_template('index.html', jobs=jobs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']  # TODO: hash in production
        role = request.form['role']

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()  # TODO: hash passwords
        if user:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'employer':
        jobs_posted = Job.query.filter_by(posted_by=current_user.id).all()
        return render_template('dashboard.html', jobs=jobs_posted)
    else:
        all_jobs = Job.query.all()
        return render_template('dashboard.html', jobs=all_jobs)

@app.route('/post_job', methods=['GET', 'POST'])
@login_required
@app.route('/post_job', methods=['GET', 'POST'])
@login_required
def post_job():

    if current_user.role != 'employer':
        flash('Only employers can post jobs.')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':

        job = Job(
            title=request.form['title'],
            company=request.form['company'],
            description=request.form['description'],
            salary=request.form['salary'],
            location=request.form['location'],
            category=request.form['category'],
            posted_by=current_user.id
        )

        db.session.add(job)
        db.session.commit()

        flash("Job Posted Successfully")

        return redirect(url_for('jobs'))

    return render_template("post_job.html")

@app.route('/jobs')
def jobs():

    q=request.args.get("q","")
    location=request.args.get("location","")
    category=request.args.get("category","")

    jobs=Job.query

    if q:
        jobs=jobs.filter(
            (Job.title.contains(q)) |
            (Job.company.contains(q))
        )

    if location:
        jobs=jobs.filter(Job.location.contains(location))

    if category:
        jobs=jobs.filter(Job.category.contains(category))

    jobs=jobs.all()

    return render_template("jobs.html",jobs=jobs)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)

@app.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply_job(job_id):
    if current_user.role != 'jobseeker':
        flash('Only job seekers can apply.', 'danger')
        return redirect(url_for('dashboard'))

    existing = Application.query.filter_by(job_id=job_id, user_id=current_user.id).first()
    if existing:
        flash('You already applied for this job.', 'warning')
    else:
        application = Application(job_id=job_id, user_id=current_user.id)
        db.session.add(application)
        db.session.commit()
        flash('Application submitted successfully!', 'success')
    return redirect(url_for('dashboard'))

# -----------------------------
# Run the app
# -----------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # ensures the database is created
    app.run(debug=True)
