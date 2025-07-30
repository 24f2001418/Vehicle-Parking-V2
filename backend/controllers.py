# controllers.py
from datetime import datetime
from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token, get_jwt, get_jwt_identity,
    jwt_required, verify_jwt_in_request
)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import re
from sqlalchemy.orm import joinedload
from models import db, User, Subject, Chapter, Quiz, Question, Score

# Import caching/rate-limiting decorators
from utils_cache import make_cache_key, rate_limit

# ─────────────────────────────────────────────────────────────────── #
#  Helpers                                                            #
# ------------------------------------------------------------------- #
def is_admin():
    identity = get_jwt_identity()
    user = User.query.filter_by(email=identity).first()
    return bool(user and user.role == 'admin')


# ─────────────────────────────────────────────────────────────────── #
#  Authentication                                                     #
# ------------------------------------------------------------------- #
class RegisterResource(Resource):
    def post(self):
        data = request.get_json() or {}
        full_name = data.get("full_name")
        email     = data.get("email")
        password  = data.get("password")

        if not all([full_name, email, password]):
            return {"msg": "Missing required fields"}, 400

        if User.query.filter_by(email=email.lower()).first():
            return {"msg": "User already exists"}, 409

        user = User(
            full_name=full_name,
            email=email.lower(),
            password=generate_password_hash(password),
            role="user",
            qualification=data.get("qualification"),
            dob=datetime.fromisoformat(data["dob"]).date() if data.get("dob") else None,
        )
        db.session.add(user); db.session.commit()

        token = create_access_token(
            identity=user.email,            # ← email as identity
            additional_claims={"role": user.role}
        )

        return {
            "msg":  "Registration successful",
            "token": token,
            "user": user.to_dict(),
        }, 201


class LoginResource(Resource):
    def post(self):
        data = request.get_json() or {}
        email, password = data.get("email"), data.get("password")

        if not (email and password):
            return {"msg": "Missing credentials"}, 400

        user = User.query.filter_by(email=email.lower()).first()
        if not user or not check_password_hash(user.password, password):
            return {"msg": "Invalid credentials"}, 401

        token = create_access_token(
            identity=user.email,
            additional_claims={"role": user.role}
        )
        return {
            "msg":   "Logged in",
            "token": token,
            "user":  user.to_dict(),
        }, 200


# ─────────────────────────────────────────────────────────────────── #
#  Subject CRUD                                                       #
# ------------------------------------------------------------------- #
class SubjectListResource(Resource):
    @jwt_required(optional=True)
    def get(self):
        return {"subjects": [s.to_dict() for s in Subject.query.all()]}

    @jwt_required()
    def post(self):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        data = request.get_json() or {}
        if not data.get("name"):
            return {"msg": "Missing field 'name'"}, 400
        subj = Subject(name=data["name"], description=data.get("description"))
        db.session.add(subj); db.session.commit()
        return {"msg": "Subject created", "subject": subj.to_dict()}, 201


class SubjectResource(Resource):
    @jwt_required(optional=True)
    def get(self, subject_id):
        s = Subject.query.get_or_404(subject_id)
        return {"subject": s.to_dict()}

    @jwt_required()
    def put(self, subject_id):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        subj = Subject.query.get_or_404(subject_id)
        data = request.get_json() or {}
        subj.name        = data.get("name", subj.name)
        subj.description = data.get("description", subj.description)
        db.session.commit()
        return {"msg": "Subject updated", "subject": subj.to_dict()}

    @jwt_required()
    def delete(self, subject_id):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        subj = Subject.query.get_or_404(subject_id)
        if subj.chapters:
            for chapter in subj.chapters:
                for quiz in chapter.quizzes:
                    for score in quiz.scores:
                        db.session.delete(score)
                    db.session.delete(quiz)     
                db.session.delete(chapter)
        db.session.delete(subj)
        db.session.commit()
        return {"msg": "Subject deleted"}


# ─────────────────────────────────────────────────────────────────── #
#  Chapter CRUD (under a subject)                                     #
# ------------------------------------------------------------------- #
class ChapterListResource(Resource):
    @jwt_required(optional=True)
    def get(self, subject_id):
        subj = Subject.query.get_or_404(subject_id)
        return {"chapters": [c.to_dict() for c in subj.chapters]}

    @jwt_required()
    def post(self, subject_id):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        data = request.get_json() or {}
        if not data.get("name"):
            return {"msg": "Missing field 'name'"}, 400
        chap = Chapter(
            subject_id=subject_id,
            name=data["name"],
            description=data.get("description")
        )
        db.session.add(chap); db.session.commit()
        return {"msg": "Chapter created", "chapter": chap.to_dict()}, 201


class ChapterResource(Resource):
    @jwt_required(optional=True)
    def get(self, chapter_id):
        chap = Chapter.query.get_or_404(chapter_id)
        return {"chapter": chap.to_dict()}

    @jwt_required()
    def put(self, chapter_id):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        chap = Chapter.query.get_or_404(chapter_id)
        data = request.get_json() or {}
        chap.name        = data.get("name", chap.name)
        chap.description = data.get("description", chap.description)
        db.session.commit()
        return {"msg": "Chapter updated", "chapter": chap.to_dict()}

    @jwt_required()
    def delete(self, chapter_id):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        chap = Chapter.query.get_or_404(chapter_id)
        for quiz in chap.quizzes:
            for score in quiz.scores:
                db.session.delete(score)
            db.session.delete(quiz)
        db.session.delete(chap)
        db.session.commit()
        return {"msg": "Chapter deleted"}


# ─────────────────────────────────────────────────────────────────── #
#  Quiz CRUD (under a chapter)                                        #
# ------------------------------------------------------------------- #
class QuizListResource(Resource):
    @jwt_required(optional=True)
    def get(self, chapter_id):
        ch = Chapter.query.get_or_404(chapter_id)
        return {"quizzes": [q.to_dict() for q in ch.quizzes]}

    @jwt_required()
    def post(self, chapter_id):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403

        data = request.get_json() or {}

        quiz = Quiz(
            chapter_id=chapter_id,
            title=data.get("title"),
            start_time=datetime.strptime(data.get("start_time"), "%Y-%m-%dT%H:%M") if data.get("start_time") else None,
            end_time=datetime.strptime(data.get("end_time"), "%Y-%m-%dT%H:%M") if data.get("end_time") else None,
            time_duration=data.get("time_duration"),
            remarks=data.get("remarks"),
        )
        db.session.add(quiz)
        db.session.commit()
        return {"msg": "Quiz created", "quiz": quiz.to_dict()}, 201


class QuizResource(Resource):
    @jwt_required(optional=True)
    def get(self, quiz_id):
        q = Quiz.query.get_or_404(quiz_id)
        return {"quiz": q.to_dict()}

    @jwt_required()
    def put(self, quiz_id):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        q = Quiz.query.get_or_404(quiz_id)
        data = request.get_json() or {}
        q.title = data.get("title", q.title)
        # Robust ISO datetime parsing for start_time
        def parse_dt(val):
            if not val:
                return None
            if isinstance(val, str):
                for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
                    try:
                        return datetime.strptime(val, fmt)
                    except Exception:
                        continue
                raise ValueError("Invalid datetime format. Use YYYY-MM-DDTHH:MM[:SS]")
            return val

        if "start_time" in data:
            try:
                q.start_time = parse_dt(data["start_time"])
            except Exception as e:
                return {"msg": str(e)}, 400
        if "end_time" in data:
            try:
                q.end_time = parse_dt(data["end_time"])
            except Exception as e:
                return {"msg": str(e)}, 400
        q.time_duration = data.get("time_duration", q.time_duration)
        q.remarks = data.get("remarks", q.remarks)
        db.session.commit()
        return {"msg": "Quiz updated", "quiz": q.to_dict()}
class QuestionListResource(Resource):
    @jwt_required(optional=True)
    def get(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        return {"questions": [q.to_dict() for q in quiz.questions]}

    @jwt_required()
    def post(self, quiz_id):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        data = request.get_json() or {}
        if not data.get("question_statement"):
            return {"msg": "question_statement is required"}, 400
        if not 1 <= data.get("correct_option", 0) <= 4:
            return {"msg": "correct_option must be between 1 and 4"}, 400

        qs = Question(
            quiz_id=quiz_id,
            question_statement=data["question_statement"],
            option1=data.get("option1"),
            option2=data.get("option2"),
            option3=data.get("option3"),
            option4=data.get("option4"),
            correct_option=data.get("correct_option"),
        )
        db.session.add(qs); db.session.commit()
        return {"msg": "Question created", "question": qs.to_dict()}, 201


class QuestionResource(Resource):
    @jwt_required(optional=True)
    def get(self, question_id):
        qs = Question.query.get_or_404(question_id)
        return {"question": qs.to_dict()}

    @jwt_required()
    def put(self, question_id):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        qs = Question.query.get_or_404(question_id)
        d = request.get_json() or {}
        qs.question_statement = d.get("question_statement", qs.question_statement)
        qs.option1, qs.option2, qs.option3, qs.option4 = (
            d.get("option1", qs.option1),
            d.get("option2", qs.option2),
            d.get("option3", qs.option3),
            d.get("option4", qs.option4),
        )
        qs.correct_option = d.get("correct_option", qs.correct_option)
        db.session.commit()
        return {"msg": "Question updated", "question": qs.to_dict()}

    @jwt_required()
    def delete(self, question_id):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        qs = Question.query.get_or_404(question_id)
        db.session.delete(qs); db.session.commit()
        return {"msg": "Question deleted"}


# ─────────────────────────────────────────────────────────────────── #
#  Quiz Attempt + Score history                                       #
# ------------------------------------------------------------------- #
class AttemptQuizResource(Resource):
    @jwt_required()
    def post(self, quiz_id):
        user_email = get_jwt_identity()
        user = User.query.filter_by(email=user_email).first_or_404()

        quiz = Quiz.query.get_or_404(quiz_id)

        # TIME VALIDATION: only allow attempt if within allowed window
        now = datetime.utcnow()

        if quiz.start_time and now < quiz.start_time:
            return {"msg": "Quiz has not started yet."}, 403

        if quiz.end_time and now > quiz.end_time:
            return {"msg": "Quiz has expired."}, 403

        # SCORE CALCULATION
        answers = request.get_json().get("answers", {})
        if not answers:
            return {"msg": "Answers required"}, 400

        total = 0
        for q in quiz.questions:
            chosen = answers.get(str(q.id)) or answers.get(q.id)
            if chosen and int(chosen) == q.correct_option:
                total += 1

        score = Score(
            quiz_id=quiz_id,
            user_id=user.id,
            total_score=total,
            attempted_at=now,
            max_score=len(quiz.questions),
        )
        db.session.add(score)
        db.session.commit()

        return {"msg": "Quiz submitted", "total_score": total}, 201


class ScoreListResource(Resource):
    @jwt_required()
    def get(self):
        user_email = get_jwt_identity()
        user = User.query.filter_by(email=user_email).first_or_404()

        scores = (
            Score.query.options(joinedload(Score.quiz))
            .filter_by(user_id=user.id)
            .order_by(Score.attempted_at.desc())
            .all()
        )

        result = []
        for s in scores:
            result.append({
                "id": s.id,
                "total_score": s.total_score,
                "attempted_at": s.attempted_at.isoformat(),
                "quiz_id": s.quiz.id if s.quiz else None,
                "quiz_title": s.quiz.title if s.quiz else None,
                "max_score": len(s.quiz.questions) if s.quiz and s.quiz.questions else 1
            })

        return {"scores": result}, 200


# ─────────────────────────────────────────────────────────────────── #
#  Admin: list all users                                              #
# ------------------------------------------------------------------- #
class UserListResource(Resource):
    @jwt_required()
    def get(self):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        return {"users": [u.to_dict() for u in User.query.all()]}, 200

class UserAdminResource(Resource):
    """ Admin-only single‑user operations """
    @jwt_required()
    def get(self, user_id):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        user = User.query.get_or_404(user_id)
        return {"user": user.to_dict()}

    @jwt_required()
    def delete(self, user_id):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        user = User.query.get_or_404(user_id)
        # also delete their scores:
        Score.query.filter_by(user_id=user.id).delete()
        db.session.delete(user); db.session.commit()
        return {"msg": "User deleted"}, 200


class UserActivationResource(Resource):
    """PUT → activate / deactivate"""
    @jwt_required()
    def put(self, user_id, action):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        user = User.query.get_or_404(user_id)

        if action not in ("activate", "deactivate"):
            return {"msg": "Invalid action"}, 400

        user.is_active = (action == "activate")
        db.session.commit()
        state = "activated" if user.is_active else "deactivated"
        return {"msg": f"User {state}", "user": user.to_dict()}

class QuizAllResource(Resource):
    @jwt_required()
    def get(self):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403

        quizzes = Quiz.query.all()
        return {"quizzes": [q.to_dict() for q in quizzes]}, 200

def search_by_query(model, field, query):
    return db.session.query(model).filter(field.ilike(f"%{query}%")).all()


# ─────────────────────────────────────────────────────────────────── #
#  User Search: Find quizzes and subjects by keyword (not admin)     #
# ------------------------------------------------------------------- 

class UserSearchQuizzesSubjectsAPI(Resource):
    @jwt_required(optional=True)
    @rate_limit(limit=20, period=60)
    @make_cache_key('usersearch', timeout=60)
    def get(self):
        q = request.args.get("q", "").strip()
        if not q or len(q) < 2:
            return {"msg": "Query too short", "quizzes": [], "subjects": []}, 400
        quizzes = search_by_query(Quiz, Quiz.title, q)
        subjects = search_by_query(Subject, Subject.name, q)
        return {
            "quizzes": [{"id": quiz.id, "title": quiz.title, "chapter_id": quiz.chapter_id} for quiz in quizzes],
            "subjects": [{"id": subj.id, "name": subj.name} for subj in subjects]
        }


# ─────────────────────────────────────────────────────────────────── #
#  Search Chapters API (admin only)                                  #
# ------------------------------------------------------------------- #
class SearchChaptersAPI(Resource):
    @jwt_required()
    @rate_limit(limit=10, period=60)
    @make_cache_key('searchchapters', timeout=60)
    def get(self):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        q = request.args.get("q", "").strip()
        if not q or len(q) < 2:
            return {"msg": "Query too short", "chapters": []}, 400
        chapters = search_by_query(Chapter, Chapter.name, q)
        return {"chapters": [{"id": c.id, "name": c.name, "subject_id": c.subject_id} for c in chapters]}


class SearchUsersAPI(Resource):
    @jwt_required()
    @rate_limit(limit=10, period=60)
    @make_cache_key('searchusers', timeout=60)
    def get(self):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        q = request.args.get("q", "").strip()
        if not q or len(q) < 2:
            return {"msg": "Query too short", "users": []}, 400
        users = search_by_query(User, User.full_name, q)
        return {"users": [{"id": u.id, "name": u.full_name, "email": u.email} for u in users]}


class SearchSubjectsAPI(Resource):
    @jwt_required()
    @rate_limit(limit=10, period=60)
    @make_cache_key('searchsubjects', timeout=60)
    def get(self):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        q = request.args.get("q", "").strip()
        if not q or len(q) < 2:
            return {"msg": "Query too short", "subjects": []}, 400
        subjects = search_by_query(Subject, Subject.name, q)
        return {"subjects": [{"id": s.id, "name": s.name} for s in subjects]}


class SearchQuizzesAPI(Resource):
    @jwt_required()
    @rate_limit(limit=10, period=60)
    @make_cache_key('searchquizzes', timeout=60)
    def get(self):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        q = request.args.get("q", "").strip()
        if not q or len(q) < 2:
            return {"msg": "Query too short", "quizzes": []}, 400
        quizzes = search_by_query(Quiz, Quiz.title, q)
        return {"quizzes": [{"id": qz.id, "title": qz.title, "chapter_id": qz.chapter_id} for qz in quizzes]}


class SearchQuestionsAPI(Resource):
    @jwt_required()
    @rate_limit(limit=10, period=60)
    @make_cache_key('searchquestions', timeout=60)
    def get(self):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        q = request.args.get("q", "").strip()
        if not q or len(q) < 2:
            return {"msg": "Query too short", "questions": []}, 400
        questions = search_by_query(Question, Question.question_statement, q)
        return {"questions": [{"id": qs.id, "text": qs.question_statement, "quiz_id": qs.quiz_id} for qs in questions]}

# Export search API classes for app.py
__all__ = [
    'SearchUsersAPI',
    'SearchSubjectsAPI',
    'SearchQuizzesAPI',
    'SearchQuestionsAPI',
    'SearchChaptersAPI',
    'UserSearchQuizzesSubjectsAPI',
]