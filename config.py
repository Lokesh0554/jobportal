import os

# Absolute project path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for sessions & forms (replace for production)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        f"sqlite:///{os.path.join(BASE_DIR, 'jobs.db')}"
    )

    # Disable SQLAlchemy event overhead
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Optional: pagination defaults, upload folders, etc.
    JOBS_PER_PAGE = 10
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB limit
