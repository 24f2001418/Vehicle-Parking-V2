import os
from celery import Celery
from flask_mail import Mail, Message
from flask import Flask
from models import db, User, Quiz, Score
from datetime import datetime, timedelta

# Celery config
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery = Celery('quizmaster', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# Flask-Mail config for Mailhog
mail_settings = {
    'MAIL_SERVER': 'localhost',
    'MAIL_PORT': 1025,
    'MAIL_USE_TLS': False,
    'MAIL_USE_SSL': False,
    'MAIL_USERNAME': '',
    'MAIL_PASSWORD': '',
    'MAIL_DEFAULT_SENDER': 'noreply@quizmaster.local'
}

# Create a Flask app context for tasks
flask_app = Flask(__name__)
flask_app.config.update(mail_settings)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///quizmaster.db')
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
mail = Mail(flask_app)
db.init_app(flask_app)

@celery.task
def send_daily_quiz_reminders():
    with flask_app.app_context():
        users = User.query.all()
        for user in users:
            # Find today's quizzes for the user (customize as needed)
            quizzes = Quiz.query.all()  # Replace with user-specific logic
            if quizzes:
                msg = Message(
                    subject='QuizMaster Daily Reminder',
                    recipients=[user.email],
                    body=f"Hi {user.full_name},\nDon't forget to take your quizzes today!"
                )
                mail.send(msg)

@celery.task
def send_monthly_performance_reports():
    with flask_app.app_context():
        users = User.query.all()
        for user in users:
            # Get scores for the last month
            last_month = datetime.utcnow() - timedelta(days=30)
            scores = Score.query.filter(Score.user_id == user.id, Score.attempted_at >= last_month).all()
            total = sum(s.total_score for s in scores)
            attempts = len(scores)
            msg = Message(
                subject='QuizMaster Monthly Performance Report',
                recipients=[user.email],
                body=f"Hi {user.full_name},\nIn the last month you attempted {attempts} quizzes and scored a total of {total} points. Keep it up!"
            )
            mail.send(msg)

# Celery Beat schedule (add to your celeryconfig.py or pass to Celery)
celery.conf.beat_schedule = {
    'send-daily-quiz-reminders': {
        'task': 'tasks.send_daily_quiz_reminders',
        'schedule': 60 * 60 * 24,  # every 24 hours
    },
    'send-monthly-performance-reports': {
        'task': 'tasks.send_monthly_performance_reports',
        'schedule': 60 * 60 * 24 * 30,  # every 30 days
    },
}
celery.conf.timezone = 'UTC'
