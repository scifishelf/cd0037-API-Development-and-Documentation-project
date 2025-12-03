import unittest
import os

from flaskr import create_app
from models import db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """The trivia test case class."""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_user = "postgres"
        self.database_password = "password"
        self.database_host = "localhost:5432"

        # Allow overriding default test database with env secrets
        self.database_path = os.getenv(
            "TEST_DATABASE_URL",
            f"postgresql://{self.database_user}:"
            f"{self.database_password}@{self.database_host}/"
            f"{self.database_name}",
        )

        # Create app with test configuration
        self.app = create_app(
            {
                "SQLALCHEMY_DATABASE_URI": self.database_path,
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "TESTING": True,
            }
        )
        self.client = self.app.test_client()

        self.new_question = {
            "question": "New sample question",
            "answer": "New sample answer",
            "difficulty": 1,
            "category": 1,
        }

    def tearDown(self):
        """Executed after each test."""
        with self.app.app_context():
            db.session.remove()

    # ------------------------------------------------------------
    # Categories test
    def test_get_categories_success(self):
        """Test fetching all categories."""
        response = self.client.get("/categories")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("categories", data)
        self.assertGreaterEqual(len(data["categories"]), 2)

    # ------------------------------------------------------------
    # Questions list and pagination test
    def test_get_paginated_questions_success(self):
        """Test fetching paginated questions."""
        response = self.client.get("/questions?page=1")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("questions", data)
        self.assertIn("totalQuestions", data)
        self.assertIn("categories", data)
        self.assertIsNone(data["currentCategory"])
        self.assertGreater(len(data["questions"]), 0)

    def test_get_paginated_questions_page_not_found(self):
        """Test requesting a page that does not exist."""
        response = self.client.get("/questions?page=1000")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], 404)

    # ------------------------------------------------------------
    # Delete question test
    def test_delete_question_success(self):
        """Test deleting an existing question."""
        # Create a question to delete
        with self.app.app_context():
            question = Question(
                question="Question to delete",
                answer="Answer",
                category=1,
                difficulty=1,
            )
            question.insert()
            question_id = question.id

        response = self.client.delete(f"/questions/{question_id}")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["deleted"], question_id)

        with self.app.app_context():
            deleted_question = Question.query.get(question_id)
            self.assertIsNone(deleted_question)

    def test_delete_question_not_found(self):
        """Test deleting a non existing question."""
        response = self.client.delete("/questions/9999")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], 404)

    # ------------------------------------------------------------
    # Create question test
    def test_create_question_success(self):
        """Test creating a new question."""
        response = self.client.post("/questions", json=self.new_question)
        data = response.get_json()

        self.assertIn(response.status_code, (200, 201))
        self.assertTrue(data["success"])
        self.assertIn("created", data)
        self.assertIn("totalQuestions", data)

    def test_create_question_bad_request(self):
        """Test creating a question with missing fields."""
        invalid_question = {
            "question": "Incomplete question",
            "answer": "No category and difficulty",
        }

        response = self.client.post("/questions", json=invalid_question)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], 400)

    # ------------------------------------------------------------
    # Search question test
    def test_search_questions_success(self):
        """Test searching for questions with results."""
        response = self.client.post(
            "/questions", json={"searchTerm": "Tom"}
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertGreater(data["totalQuestions"], 0)

    def test_search_questions_no_results(self):
        """Test searching for questions with no results."""
        response = self.client.post(
            "/questions", json={"searchTerm": "no-such-question-term"}
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["totalQuestions"], 0)

    # ------------------------------------------------------------
    # Questions by category test
    def test_get_questions_by_category_success(self):
        """Test fetching questions by category."""
        response = self.client.get("/categories/1/questions")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertGreater(data["totalQuestions"], 0)
        self.assertEqual(data["currentCategory"], "Science")

    def test_get_questions_by_category_not_found(self):
        """Test fetching questions for a non existing category."""
        response = self.client.get("/categories/9999/questions")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], 404)

    # ------------------------------------------------------------
    # Play quiz test

    def test_play_quiz_success(self):
        """Test playing quiz and receiving a question."""
        quiz_payload = {
            "previous_questions": [],
            "quiz_category": {"id": 1, "type": "Science"},
        }

        response = self.client.post("/quizzes", json=quiz_payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["question"])
        self.assertEqual(data["question"]["category"], 1)

    def test_play_quiz_no_more_questions(self):
        """Test playing quiz when no questions are left."""
        # All known questions in Science category
        with self.app.app_context():
            science_questions = Question.query.filter(
                Question.category == 1
            ).all()
            previous_ids = [q.id for q in science_questions]

        quiz_payload = {
            "previous_questions": previous_ids,
            "quiz_category": {"id": 1, "type": "Science"},
        }

        response = self.client.post("/quizzes", json=quiz_payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsNone(data["question"])

    # ------------------------------------------------------------
    # Error handlers test
    def test_404_for_invalid_route(self):
        """Test 404 response for non existing route."""
        response = self.client.get("/does-not-exist")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], 404)


if __name__ == "__main__":
    unittest.main()
