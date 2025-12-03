from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import os

# Default connection values can be overridden with env secrets.
database_name = os.getenv("TRIVIA_DB_NAME", "trivia")
database_user = os.getenv("TRIVIA_DB_USER", "postgres")
database_password = os.getenv("TRIVIA_DB_PASSWORD", "password")
database_host = os.getenv("TRIVIA_DB_HOST", "localhost:5432")

database_path = os.getenv(
    "DATABASE_URL",
    f"postgresql://{database_user}:{database_password}@{database_host}/{database_name}",
)

db = SQLAlchemy()

"""
setup the database
"""
def setup_db(app, database_path=database_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

"""
Question class
"""
class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    category = Column(String, nullable=False)
    difficulty = Column(Integer, nullable=False)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }

"""
Category class
"""
class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }
