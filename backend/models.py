from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    email     = db.Column(db.String(120), unique=True, nullable=False)
    password  = db.Column(db.String(200), nullable=False)   # store the HASH!
    qualification = db.Column(db.String(120), )  
    dob       = db.Column(db.Date, ) 
    role      = db.Column(db.String(20), default='user', nullable=False) 
    is_active   = db.Column(db.Boolean, default=True) # 'admin' | 'user'

    scores = db.relationship('Score', backref='user', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "qualification": self.qualification,
            "dob": self.dob.isoformat() if self.dob else None,
            "role": self.role,
        }


class Subject(db.Model):
    __tablename__ = 'subject'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    chapters = db.relationship(
        'Chapter',
        backref='subject',
        cascade='all, delete-orphan',
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }


class Chapter(db.Model):
    __tablename__ = 'chapter'

    id          = db.Column(db.Integer, primary_key=True)
    subject_id  = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    quizzes = db.relationship(
        'Quiz',
        backref='chapter',
        cascade='all, delete-orphan',
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "subject_id": self.subject_id,
            "name": self.name,
            "description": self.description,
        }

class Quiz(db.Model):
    __tablename__ = 'quiz'

    id            = db.Column(db.Integer, primary_key=True)
    chapter_id    = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete='CASCADE'), nullable=False)
    title         = db.Column(db.String(150))
    start_time    = db.Column(db.DateTime, nullable=False)  # NEW
    end_time      = db.Column(db.DateTime, nullable=False)  # NEW
    time_duration = db.Column(db.String(8))  # format HH:MM
    remarks       = db.Column(db.Text)

    questions = db.relationship(
        'Question',
        backref='quiz',
        cascade='all, delete-orphan',
        lazy=True
    )
    scores = db.relationship(
        'Score',
        backref='quiz',
        cascade='all, delete-orphan',
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "chapter_id": self.chapter_id,
            "title": self.title,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "time_duration": self.time_duration,
            "remarks": self.remarks,
        }

    def is_active(self):
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time


class Question(db.Model):
    __tablename__ = 'question'

    id                 = db.Column(db.Integer, primary_key=True)
    quiz_id            = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1            = db.Column(db.String(250))
    option2            = db.Column(db.String(250))
    option3            = db.Column(db.String(250))
    option4            = db.Column(db.String(250))
    correct_option     = db.Column(db.Integer)  

    def to_dict(self):
        return {
            "id": self.id,
            "quiz_id": self.quiz_id,
            "question_statement": self.question_statement,
            "option1": self.option1,
            "option2": self.option2,
            "option3": self.option3,
            "option4": self.option4,
            "correct_option": self.correct_option,
        }

class Score(db.Model):
    __tablename__ = 'score'

    id        = db.Column(db.Integer, primary_key=True)
    quiz_id   = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_score  = db.Column(db.Integer, nullable=False)
    remarks      = db.Column(db.String(255))

    def to_dict(self):
        return {
            "id": self.id,
            "quiz_id": self.quiz_id,
            "user_id": self.user_id,
            "attempted_at": self.attempted_at.isoformat(),
            "total_score": self.total_score,
            "remarks": self.remarks,
        }
