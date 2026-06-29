from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from config import Config
from models import db, User, Job, Application

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please login to continue."


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -----------------------------
# Home
# -----------------------------
@app.route("/")
def index():

    q = request.args.get("q", "")
    location = request.args.get("location", "")
    category = request.args.get("category", "")

    jobs = Job.query

    if q:
        jobs = jobs.filter(
            (Job.title.contains(q)) |
            (Job.company.contains(q))
        )

    if location:
        jobs = jobs.filter(
            Job.location.contains(location)
        )

    if category:
        jobs = jobs.filter(
            Job.category.contains(category)
        )

    jobs = jobs.order_by(Job.posted_at.desc()).all()

    return render_template(
        "index.html",
        jobs=jobs
    )


# -----------------------------
# Register
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]

        email = request.form["email"]

        password = request.form["password"]

        role = request.form["role"]

        existing = User.query.filter_by(
            email=email
        ).first()

        if existing:
            flash("Email already exists")
            return redirect(url_for("register"))

        user = User(
            username=username,
            email=email,
            password=password,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration Successful")

        return redirect(url_for("login"))

    return render_template("register.html")


# -----------------------------
# Login
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:

            login_user(user)

            flash("Login Successful")

            return redirect(
                url_for("dashboard")
            )

        flash("Invalid Credentials")

    return render_template("login.html")


# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged Out Successfully")

    return redirect(url_for("index"))


# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
@login_required
def dashboard():

    if current_user.role == "employer":

        jobs = Job.query.filter_by(
            user_id=current_user.id
        ).order_by(Job.posted_at.desc()).all()

        return render_template(
            "dashboard.html",
            jobs=jobs
        )

    jobs = Job.query.order_by(
        Job.posted_at.desc()
    ).all()

    return render_template(
        "dashboard.html",
        jobs=jobs
    )


# -----------------------------
# Post Job
# -----------------------------
@app.route("/post_job", methods=["GET", "POST"])
@login_required
def post_job():

    if current_user.role != "employer":

        flash("Only employers can post jobs.")

        return redirect(url_for("dashboard"))

    if request.method == "POST":

        job = Job(

            title=request.form["title"],

            company=request.form["company"],

            category=request.form["category"],

            location=request.form["location"],

            salary=request.form["salary"],

            description=request.form["description"],

            user_id=current_user.id

        )

        db.session.add(job)

        db.session.commit()

        flash("Job Posted Successfully")

        return redirect(url_for("jobs"))

    return render_template("post_job.html")


# -----------------------------
# Jobs
# -----------------------------
@app.route("/jobs")
def jobs():

    q = request.args.get("q", "")

    location = request.args.get("location", "")

    category = request.args.get("category", "")

    jobs = Job.query

    if q:

        jobs = jobs.filter(

            (Job.title.contains(q)) |

            (Job.company.contains(q))

        )

    if location:

        jobs = jobs.filter(

            Job.location.contains(location)

        )

    if category:

        jobs = jobs.filter(

            Job.category.contains(category)

        )

    jobs = jobs.order_by(

        Job.posted_at.desc()

    ).all()

    return render_template(

        "jobs.html",

        jobs=jobs

    )


# -----------------------------
# Job Details
# -----------------------------
@app.route("/job/<int:job_id>")
def job_detail(job_id):

    job = Job.query.get_or_404(job_id)

    return render_template(

        "job_detail.html",

        job=job

    )


# -----------------------------
# Apply Job
# -----------------------------
@app.route("/apply/<int:job_id>", methods=["POST"])
@login_required
def apply(job_id):

    if current_user.role != "jobseeker":

        flash("Only Job Seekers can apply.")

        return redirect(url_for("dashboard"))

    existing = Application.query.filter_by(

        user_id=current_user.id,

        job_id=job_id

    ).first()

    if existing:

        flash("Already Applied")

        return redirect(

            url_for("job_detail", job_id=job_id)

        )

    application = Application(

        user_id=current_user.id,

        job_id=job_id

    )

    db.session.add(application)

    db.session.commit()

    flash("Application Submitted")

    return redirect(

        url_for("dashboard")

    )


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":

    with app.app_context():

        db.create_all()

    app.run(debug=True)
