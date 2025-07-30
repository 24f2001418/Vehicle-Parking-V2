from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import db, User, Quiz, Score
from sqlalchemy import func
from datetime import datetime

admin_analytics_bp = Blueprint('admin_analytics', __name__)

@admin_analytics_bp.route('/api/admin/analytics')
@jwt_required()
def admin_analytics():
    # Leaderboard: total score, attempts, avg %
    users = User.query.filter(User.role != 'admin').all()
    leaderboard = []
    for user in users:
        scores = Score.query.filter_by(user_id=user.id).all()
        total_score = sum(s.total_score for s in scores)
        attempts = len(scores)
        avg_percent = (
            sum((s.total_score / (s.max_score or 1)) * 100 if s.max_score else s.total_score for s in scores) / attempts
            if attempts else 0
        )
        leaderboard.append({
            'id': user.id,
            'full_name': user.full_name,
            'total_score': total_score,
            'attempts': attempts,
            'avg_percent': avg_percent
        })
    leaderboard.sort(key=lambda u: u['total_score'], reverse=True)

    # User progress: for top 5 users
    user_progress = []
    for user in leaderboard[:5]:
        scores = Score.query.filter_by(user_id=user['id']).order_by(Score.attempted_at).all()
        progress = [
            {
                'date': s.attempted_at.strftime('%Y-%m-%d'),
                'score': s.total_score
            } for s in scores
        ]
        user_progress.append({
            'id': user['id'],
            'full_name': user['full_name'],
            'progress': progress
        })

    # Quiz attempts distribution
    quizzes = Quiz.query.all()
    quiz_attempts = []
    for quiz in quizzes:
        attempts = Score.query.filter_by(quiz_id=quiz.id).count()
        quiz_attempts.append({
            'quiz_title': quiz.title,
            'attempts': attempts
        })

    return jsonify({
        'leaderboard': leaderboard,
        'user_progress': user_progress,
        'quiz_attempts': quiz_attempts
    })
