import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from werkzeug.security import generate_password_hash

from models import db, User         

from controllers import (
    LoginResource, RegisterResource,
    SubjectListResource, SubjectResource,
    ChapterListResource, ChapterResource,
    QuizListResource, QuizResource,
    QuestionListResource, QuestionResource,
    UserListResource,
    ScoreListResource, AttemptQuizResource,
    UserAdminResource, UserActivationResource,
    QuizAllResource,
)


app = Flask(__name__)

# Core config
app.config['SQLALCHEMY_DATABASE_URI']  = os.getenv('DATABASE_URL', 'sqlite:///quizmaster.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-me')

# Init extensions
db.init_app(app)
jwt = JWTManager(app)
api = Api(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})   # dev‑friendly CORS

# ──────────────────────────────────────────────────────────────────── #
#  Routes                                                             #
# Auth
api.add_resource(RegisterResource, "/api/auth/register")
api.add_resource(LoginResource,    "/api/auth/login")

# Subjects & nested CRUD
api.add_resource(SubjectListResource, "/api/subjects")
api.add_resource(SubjectResource,     "/api/subjects/<int:subject_id>")
api.add_resource(ChapterListResource, "/api/subjects/<int:subject_id>/chapters")
api.add_resource(ChapterResource,     "/api/chapters/<int:chapter_id>")
api.add_resource(QuizListResource,    "/api/chapters/<int:chapter_id>/quizzes")
api.add_resource(QuizResource,        "/api/quizzes/<int:quiz_id>")
api.add_resource(QuestionListResource,"/api/quizzes/<int:quiz_id>/questions")
api.add_resource(QuestionResource,    "/api/questions/<int:question_id>")

# Attempt & scores
api.add_resource(AttemptQuizResource, "/api/quizzes/<int:quiz_id>/attempt")
api.add_resource(ScoreListResource,   "/api/scores")

# Admin users
api.add_resource(UserListResource,      "/api/users")                       # list all
api.add_resource(UserAdminResource,     "/api/users/<int:user_id>")         # get / delete
api.add_resource(UserActivationResource,
                "/api/users/<int:user_id>/<string:action>") 

api.add_resource(QuizAllResource,     "/api/quizzesall")           # GET (admin)

def seed_admin():
    admin = User.query.filter_by(email='admin@mad2.com').first()
    if not admin:
        admin = User(
            email='admin@mad2.com',
            full_name='Admin',
            password=generate_password_hash('12345678'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin created — email: admin@mad2.com  |  password: 12345678')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_admin()
    app.run(debug=True)
