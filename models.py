from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)

    jobs = db.relationship(
        "Job",
        backref="employer",
        lazy=True,
        cascade="all, delete"
    )

    applications = db.relationship(
        "Application",
        backref="applicant",
        lazy=True,
        cascade="all, delete"
    )


class Job(db.Model):

    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)

    company = db.Column(db.String(150), nullable=False)

    category = db.Column(db.String(100), nullable=False)

    location = db.Column(db.String(150), nullable=False)

    salary = db.Column(db.String(80))

    description = db.Column(db.Text, nullable=False)

    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    applications = db.relationship(
        "Application",
        backref="job",
        lazy=True,
        cascade="all, delete"
    )


class Application(db.Model):

    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    cover_letter = db.Column(db.Text)

    applied_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("jobs.id"),
        nullable=False
    )
