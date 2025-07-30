import csv
import os
from io import StringIO
from celery import Celery
from flask_mail import Message, Mail
from flask import Flask
from models import db, User, Quiz, Score
from datetime import datetime

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery = Celery('quizmaster', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

mail_settings = {
    'MAIL_SERVER': 'localhost',
    'MAIL_PORT': 1025,
    'MAIL_USE_TLS': False,
    'MAIL_USE_SSL': False,
    'MAIL_USERNAME': '',
    'MAIL_PASSWORD': '',
    'MAIL_DEFAULT_SENDER': 'noreply@quizmaster.local'
}

flask_app = Flask(__name__)
flask_app.config.update(mail_settings)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///quizmaster.db')
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
mail = Mail(flask_app)
db.init_app(flask_app)

@celery.task
def export_user_quiz_history_csv(user_id, user_email):
    """Export a user's quiz history as CSV and email it to them."""
    with flask_app.app_context():
        scores = Score.query.filter_by(user_id=user_id).all()
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Quiz Title', 'Score', 'Attempted At'])
        for score in scores:
            quiz = Quiz.query.get(score.quiz_id)
            writer.writerow([
                quiz.title if quiz else 'Unknown',
                score.total_score,
                score.attempted_at.strftime('%Y-%m-%d %H:%M')
            ])
        output.seek(0)
        msg = Message(
            subject='Your Quiz History Export',
            recipients=[user_email],
            body='Attached is your quiz history in CSV format.'
        )
        msg.attach('quiz_history.csv', 'text/csv', output.read())
        mail.send(msg)

@celery.task
def export_admin_user_performance_csv(admin_email):
    """Export all users' performance as CSV and email to admin."""
    with flask_app.app_context():
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['User', 'Email', 'Quiz', 'Score', 'Attempted At'])
        scores = Score.query.all()
        for score in scores:
            user = User.query.get(score.user_id)
            quiz = Quiz.query.get(score.quiz_id)
            writer.writerow([
                user.full_name if user else 'Unknown',
                user.email if user else 'Unknown',
                quiz.title if quiz else 'Unknown',
                score.total_score,
                score.attempted_at.strftime('%Y-%m-%d %H:%M')
            ])
        output.seek(0)
        msg = Message(
            subject='All User Performance Export',
            recipients=[admin_email],
            body='Attached is the user performance data in CSV format.'
        )
        msg.attach('user_performance.csv', 'text/csv', output.read())
        mail.send(msg)
