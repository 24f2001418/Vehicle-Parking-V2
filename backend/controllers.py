from datetime import datetime
from flask import request, jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token, get_jwt, get_jwt_identity, jwt_required
)
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, User, Subject, Chapter, Quiz, Question, Score

def is_admin():
    identity = get_jwt()
    if identity.get("role") != "admin":
        return jsonify({"msg": "Admin privileges required"}), 403

class LoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email",    required=True, help="Email required")
        parser.add_argument("password", required=True, help="Password required")
        args = parser.parse_args()

        user = User.query.filter_by(email=args.email.lower()).first()
        if not user or not check_password_hash(user.password, args.password):
            return {"msg": "Invalid credentials"}, 401
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"role": user.role, "email": user.email}
        )

        return {
            "msg": "Logged in",
            "access_token": access_token,
            "user": user.to_dict(),     
            "role": user.role,
        }, 200

class RegisterResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("full_name",    required=True)
        parser.add_argument("email",        required=True)
        parser.add_argument("password",     required=True)
        parser.add_argument("qualification")
        parser.add_argument("dob")  
        args = parser.parse_args()

        if User.query.filter_by(email=args.email.lower()).first():
            return {"msg": "User already exists"}, 409

        hashed_pw = generate_password_hash(args.password)  # PBKDF2‑sha256 default

        user = User(
            full_name=args.full_name,
            email=args.email.lower(),
            password=hashed_pw,
            qualification=args.qualification,
            dob=datetime.fromisoformat(args.dob).date() if args.dob else None,
            role="user",
        )
        db.session.add(user); db.session.commit()

        access_token = create_access_token(
            identity=user.id,
            additional_claims={"role": "user", "email": user.email}
        )

        return {
            "msg": "Registration successful",
            "access_token": access_token,
            "user": user.to_dict(),
            "role": "user",
        }, 201

class SubjectResource(Resource):
    @jwt_required(optional=True)
    def get(self, subject_id=None):
        if subject_id:
            s = Subject.query.get_or_404(subject_id)
            return {"subject": s.to_dict()}
        return {"subjects": [s.to_dict() for s in Subject.query.all()]}

    @jwt_required()
    def post(self):
        if not is_admin():
            return {"msg": "Not authorized"}, 401

        data = request.get_json()
        if not data.get("name"):
            return {"msg": "Missing field 'name'"}, 400

        subj = Subject(name=data["name"], description=data.get("description"))
        db.session.add(subj)
        db.session.commit()
        return {"msg": "Subject created", "subject": subj.to_dict()}, 201

    @jwt_required()
    def put(self, subject_id):
        if not is_admin():
            return {"msg": "Not authorized"}, 401
        subj = Subject.query.get_or_404(subject_id)

        data = request.get_json()
        subj.name        = data.get("name", subj.name)
        subj.description = data.get("description", subj.description)
        db.session.commit()
        return {"msg": "Subject updated", "subject": subj.to_dict()}, 200

    @jwt_required()
    def delete(self, subject_id):
        if not is_admin():
            return {"msg": "Not authorized"}, 401
        subj = Subject.query.get_or_404(subject_id)
        # Optional safety: block delete if chapters exist
        if subj.chapters:
            return {"msg": "Subject has chapters; delete them first."}, 400
        db.session.delete(subj)
        db.session.commit()
        return {"msg": "Subject deleted"}, 200

#  CHAPTERS (CRUD)
#  Routes →  /api/subjects/<int:subject_id>/chapters  &  /api/chapters/<id>
class ChapterListResource(Resource):
    @jwt_required(optional=True)
    def get(self, subject_id):
        subj = Subject.query.get_or_404(subject_id)
        return {"chapters": [c.to_dict() for c in subj.chapters]}

    @jwt_required()
    def post(self, subject_id):
        if not is_admin():
            return {"msg": "Not authorized"}, 401
        data = request.get_json()
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
            return {"msg": "Not authorized"}, 401
        chap = Chapter.query.get_or_404(chapter_id)
        data = request.get_json()
        chap.name        = data.get("name", chap.name)
        chap.description = data.get("description", chap.description)
        db.session.commit()
        return {"msg": "Chapter updated", "chapter": chap.to_dict()}

    @jwt_required()
    def delete(self, chapter_id):
        if not is_admin():
            return {"msg": "Not authorized"}, 401
        chap = Chapter.query.get_or_404(chapter_id)
        if chap.quizzes:
            return {"msg": "Chapter has quizzes; delete them first."}, 400
        db.session.delete(chap); db.session.commit()
        return {"msg": "Chapter deleted"}

#  QUIZZES (CRUD) – inside a chapter
#  Routes →  /api/chapters/<int:chapter_id>/quizzes & /api/quizzes/<id>
class QuizListResource(Resource):
    @jwt_required(optional=True)
    def get(self, chapter_id):
        ch = Chapter.query.get_or_404(chapter_id)
        return {"quizzes": [q.to_dict() for q in ch.quizzes]}

    @jwt_required()
    def post(self, chapter_id):
        if not is_admin():
            return {"msg": "Not authorized"}, 401
        data = request.get_json()
        quiz = Quiz(
            chapter_id=chapter_id,
            title=data.get("title"),
            date_of_quiz=data.get("date_of_quiz"),
            time_duration=data.get("time_duration"),
            remarks=data.get("remarks")
        )
        db.session.add(quiz); db.session.commit()
        return {"msg": "Quiz created", "quiz": quiz.to_dict()}, 201

class QuizResource(Resource):
    @jwt_required(optional=True)
    def get(self, quiz_id):
        q = Quiz.query.get_or_404(quiz_id)
        return {"quiz": q.to_dict()}

    @jwt_required()
    def put(self, quiz_id):
        if not is_admin():
            return {"msg": "Not authorized"}, 401
        q = Quiz.query.get_or_404(quiz_id)
        d = request.get_json()
        q.title         = d.get("title", q.title)
        q.date_of_quiz  = d.get("date_of_quiz", q.date_of_quiz)
        q.time_duration = d.get("time_duration", q.time_duration)
        q.remarks       = d.get("remarks", q.remarks)
        db.session.commit()
        return {"msg": "Quiz updated", "quiz": q.to_dict()}

    @jwt_required()
    def delete(self, quiz_id):
        if not is_admin():
            return {"msg": "Not authorized"}, 401
        q = Quiz.query.get_or_404(quiz_id)
        if q.questions:
            return {"msg": "Quiz has questions; delete them first."}, 400
        db.session.delete(q); db.session.commit()
        return {"msg": "Quiz deleted"}

#  QUESTIONS (CRUD) – inside a quiz
#  Routes → /api/quizzes/<int:quiz_id>/questions  &  /api/questions/<id>
class QuestionListResource(Resource):
    @jwt_required(optional=True)
    def get(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        return {"questions": [q.to_dict() for q in quiz.questions]}

    @jwt_required()
    def post(self, quiz_id):
        if not is_admin():
            return {"msg": "Not authorized"}, 401
        data = request.get_json()
        # Basic validation
        if not data.get("question_statement"):
            return {"msg": "question_statement is required"}, 400
        qs = Question(
            quiz_id=quiz_id,
            question_statement=data["question_statement"],
            option1=data.get("option1"),
            option2=data.get("option2"),
            option3=data.get("option3"),
            option4=data.get("option4"),
            correct_option=data.get("correct_option")
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
            return {"msg": "Not authorized"}, 401
        qs = Question.query.get_or_404(question_id)
        d  = request.get_json()
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
            return {"msg": "Not authorized"}, 401
        qs = Question.query.get_or_404(question_id)
        db.session.delete(qs); db.session.commit()
        return {"msg": "Question deleted"}

#  USER QUIZ ATTEMPT  (submit answers)  &  SCORE HISTORY
class AttemptQuizResource(Resource):
    @jwt_required()
    def post(self, quiz_id):
        user_id = get_jwt_identity()
        quiz = Quiz.query.get_or_404(quiz_id)

        # Expect answers as {question_id: chosen_option_int}
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
            user_id=user_id,
            total_score=total,
            attempted_at=datetime.utcnow(),
        )
        db.session.add(score); db.session.commit()
        return {"msg": "Quiz submitted", "total_score": total}, 201

class ScoreListResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        scores = Score.query.filter_by(user_id=user_id).order_by(
            Score.attempted_at.desc()
        )
        return {"scores": [s.to_dict() for s in scores]}, 200
    
class UserListResource(Resource):
    @jwt_required()
    def get(self):
        if not is_admin():
            return {"msg": "Admin privileges required"}, 403
        users = User.query.all()
        return {"users": [u.to_dict() for u in users]}, 200