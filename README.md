# API Development and Documentation Final Project

## Trivia App

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a webpage to manage the trivia app and play the game, but their API experience is limited and still needs to be built out.

That's where you come in! Help them finish the trivia app so they can start holding trivia and seeing who's the most knowledgeable of the bunch. The application must:

1. Display questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer.
2. Delete questions.
3. Add questions and require that they include question and answer text.
4. Search for questions based on a text query string.
5. Play the quiz game, randomizing either all questions or within a specific category.

Completing this trivia app will give you the ability to structure plan, implement, and test an API - skills essential for enabling your future applications to communicate with others.

## Starting and Submitting the Project

[Fork](https://help.github.com/en/articles/fork-a-repo) the project repository and [clone](https://help.github.com/en/articles/cloning-a-repository) your forked repository to your machine. Work on the project locally and make sure to push all your changes to the remote repository before submitting the link to your repository in the Classroom.

## About the Stack

We started the full stack application for you. It is designed with some key functional areas:

### Backend

The [backend](./backend/README.md) directory contains a partially completed Flask and SQLAlchemy server. You will work primarily in `__init__.py` to define your endpoints and can reference models.py for DB and SQLAlchemy setup. These are the files you'd want to edit in the backend:

1. `backend/flaskr/__init__.py`
2. `backend/test_flaskr.py`

> View the [Backend README](./backend/README.md) for more details.

### Frontend

The [frontend](./frontend/README.md) directory contains a complete React frontend to consume the data from the Flask server. If you have prior experience building a frontend application, you should feel free to edit the endpoints as you see fit for the backend you design. If you do not have prior experience building a frontend application, you should read through the frontend code before starting and make notes regarding:

1. What are the end points and HTTP methods the frontend is expecting to consume?
2. How are the requests from the frontend formatted? Are they expecting certain parameters or payloads?

Pay special attention to what data the frontend is expecting from each API response to help guide how you format your API. The places where you may change the frontend behavior, and where you should be looking for the above information, are marked with `TODO`. These are the files you'd want to edit in the frontend:

1. `frontend/src/components/QuestionView.js`
2. `frontend/src/components/FormView.js`
3. `frontend/src/components/QuizView.js`

By making notes ahead of time, you will practice the core skill of being able to read and understand code and will have a simple plan to follow to build out the endpoints of your backend API.

> View the [Frontend README](./frontend/README.md) for more details.

---

## Project Setup

### Backend
1. Create the `trivia` database with `trivia.psql`
2. (Optional) Create `trivia_test` in the same way.
3. In the `backend` folder create and activate a python venv
4. Install all  dependencies with `pip install -r requirements.txt`
5. Set environment variables `FLASK_APP=flaskr` and `FLASK_ENV=development`
6. Start server: `flask run`.

### Frontend
1. In the `frontend` folder install dependencies with `npm install`
2. Start the App with `npm start`

---

## API Endpoints


### GET `/categories`
- **Description**: Returns all categories
- **Request parameters**: None
- **Response body**:

```json
{
  "success": true,
  "categories": {
    "1": "Science",
    "2": "Art"
  }
}
```


### GET `/questions?page=<integer>`
- **Description**: Returns a paginated list of questions
- **Request parameters**: `page` optional, integer, default is 1
- **Response body**:

```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "Question text",
      "answer": "Answer text",
      "difficulty": 1,
      "category": 1
    }
  ],
  "totalQuestions": 20,
  "categories": {
    "1": "Science",
    "2": "Art"
  },
  "currentCategory": null
}
```


### GET `/categories/<id>/questions`
- **Description**: Returns all questions for a given category
- **Request parameters**: `id` path parameter, integer
- **Response body**:

```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "Question text",
      "answer": "Answer text",
      "difficulty": 1,
      "category": 1
    }
  ],
  "totalQuestions": 5,
  "currentCategory": "Science"
}
```


### DELETE `/questions/<id>`
- **Description**: Deletes a question by id
- **Request parameters**: `id` path parameter, integer
- **Response body**:

```json
{
  "success": true,
  "deleted": 3
}
```

### POST `/questions` (create)
- **Description**: Creates a new question
- **Request body**:

```json
{
  "question": "New question text",
  "answer": "New answer text",
  "difficulty": 1,
  "category": 1
}
```

- **Response body**:

```json
{
  "success": true,
  "created": 21,
  "questions": [
    {
      "id": 11,
      "question": "Question text",
      "answer": "Answer text",
      "difficulty": 1,
      "category": 1
    }
  ],
  "totalQuestions": 21
}
```


### POST `/questions` (search)
- **Description**: Searches questions that contain a search term
- **Request body**:

```json
{
  "searchTerm": "title"
}
```

- **Response body**:

```json
{
  "success": true,
  "questions": [
    {
      "id": 2,
      "question": "Question with title",
      "answer": "Answer text",
      "difficulty": 2,
      "category": 2
    }
  ],
  "totalQuestions": 1,
  "currentCategory": null
}
```


### POST `/quizzes`
- **Description**: Returns a random question for the quiz that was not asked before
- **Request body**:

```json
{
  "previous_questions": [1, 2],
  "quiz_category": {
    "id": 1,
    "type": "Science"
  }
}
```

- **Response body**:

```json
{
  "success": true,
  "question": {
    "id": 3,
    "question": "Next question text",
    "answer": "Answer text",
    "difficulty": 2,
    "category": 1
  }
}
```
