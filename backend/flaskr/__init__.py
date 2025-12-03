from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    """Return a page of formatted questions."""
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    """Create and configure the Flask applicaion."""
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get("SQLALCHEMY_DATABASE_URI")
        setup_db(app, database_path=database_path)

    # Enable CORS for all 
    CORS(app, resources={r"*": {"origins": "*"}})

    with app.app_context():
        db.create_all()

    @app.after_request
    def after_request(response):
        """Add CORS headers to each response."""
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type,Authorization,true",
        )
        response.headers.add(
            "Access-Control-Allow-Methods",
            "GET,POST,DELETE,OPTIONS",
        )
        return response

    @app.route("/categories", methods=["GET"])
    def retrieve_categories():
        """Return all categories."""
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        categories_dict = {
            str(category.id): category.type for category in categories
        }

        return jsonify(
            {
                "success": True,
                "categories": categories_dict,
            }
        )

    @app.route("/questions", methods=["GET"])
    def retrieve_questions():
        """Return paginated questions and category data."""
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        categories = Category.query.order_by(Category.id).all()
        categories_dict = {
            str(category.id): category.type for category in categories
        }

        total_count = len(selection)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "totalQuestions": total_count,
                "currentCategory": None,
                "total_questions": total_count,
                "current_category": None,
                "categories": categories_dict,
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        """delete a question by id."""
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        try:
            question.delete()

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                }
            )
        except Exception:
            db.session.rollback()
            abort(422)

    @app.route("/questions", methods=["POST"])
    def create_or_search_questions():
        """
        Create a new question or search questions.
        """
        body = request.get_json()

        if body is None:
            abort(400)

        search_term = body.get("searchTerm", None)

        if search_term:
            selection = (
                Question.query.filter(
                    Question.question.ilike(f"%{search_term}%")
                )
                .order_by(Question.id)
                .all()
            )

            questions = [question.format() for question in selection]
            total_count = len(selection)

            return jsonify(
                {
                    "success": True,
                    "questions": questions,
                    "totalQuestions": total_count,
                    "currentCategory": None,
                    "total_questions": total_count,
                    "current_category": None,
                }
            )

        question_text = body.get("question")
        answer_text = body.get("answer")
        category = body.get("category")
        difficulty = body.get("difficulty")

        if not question_text or not answer_text or not category or not difficulty:
            abort(400)

        try:
            question = Question(
                question=question_text,
                answer=answer_text,
                category=category,
                difficulty=difficulty,
            )
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            total_count = len(selection)

            return (
                jsonify(
                    {
                        "success": True,
                        "created": question.id,
                        "questions": current_questions,
                        "totalQuestions": total_count,
                        "total_questions": total_count,
                    }
                ),
                201,
            )
        except Exception:
            db.session.rollback()
            abort(422)

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):
        """Return questions for a category."""
        category = Category.query.get(category_id)

        if category is None:
            abort(404)

        selection = (
            Question.query.filter(Question.category == category_id)
            .order_by(Question.id)
            .all()
        )

        questions = [question.format() for question in selection]
        total_count = len(selection)

        return jsonify(
            {
                "success": True,
                "questions": questions,
                "totalQuestions": total_count,
                "currentCategory": category.type,
                "total_questions": total_count,
                "current_category": category.type,
            }
        )

    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
        """Return a random question for the quiz that was not asked before."""
        body = request.get_json()

        if body is None:
            abort(400)

        previous_questions = body.get("previous_questions", [])
        quiz_category = body.get("quiz_category", None)

        try:
            if (
                quiz_category is None
                or quiz_category == {}
                or str(quiz_category.get("id", 0)) == "0"
            ):
                questions_query = Question.query
            else:
                category_id = quiz_category.get("id")

                if isinstance(category_id, str) and category_id.isdigit():
                    category_id = int(category_id)

                questions_query = Question.query.filter(
                    Question.category == category_id
                )

            if previous_questions:
                questions = questions_query.filter(
                    ~Question.id.in_(previous_questions)
                ).all()
            else:
                questions = questions_query.all()

            if len(questions) == 0:
                return jsonify({"success": True, "question": None})

            new_question = random.choice(questions)

            return jsonify(
                {
                    "success": True,
                    "question": new_question.format(),
                }
            )
        except Exception:
            abort(422)

    @app.errorhandler(400)
    def bad_request(error):
        """Return a JSON response for 400 errors."""
        return (
            jsonify(
                {
                    "success": False,
                    "error": 400,
                    "message": "bad request",
                }
            ),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        """Return a JSON response for 404 errors."""
        return (
            jsonify(
                {
                    "success": False,
                    "error": 404,
                    "message": "resource not found",
                }
            ),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        """Return a JSON response for 422 errors."""
        return (
            jsonify(
                {
                    "success": False,
                    "error": 422,
                    "message": "unprocessable",
                }
            ),
            422,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        """Return a JSON response for 500 errors."""
        return (
            jsonify(
                {
                    "success": False,
                    "error": 500,
                    "message": "internal server error",
                }
            ),
            500,
        )

    return app