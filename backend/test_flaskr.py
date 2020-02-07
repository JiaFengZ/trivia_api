import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', 'todo', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        self.new_question = {
          "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?",
          "answer":"Apollo 13",
          "difficulty":1,
          "category": 1
        }

        self.new_bad_question = {
          "question": None,
          "answer":"Apollo 13",
          "difficulty":1,
          "category": 1
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    test GET /categories
    """
    def test_get_categories(self):
      res = self.client().get('/categories')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['total_categories'])
      self.assertTrue(len(data['categories']))

    def test_get_categories_method_not_allowed(self):
      res = self.client().post('/categories')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 405)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'method not allowed')

    """
    test GET /questions
    """
    def test_get_questions(self):
      res = self.client().get('/questions?page=1')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['total_questions'])
      self.assertTrue(len(data['questions']))

    def test_get_questions_not_valid_page(self):
      res = self.client().get('/questions?page=1000')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 404)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'resource not found')

    """
    test POST /questions
    """
    def test_create_new_question(self):
      res = self.client().post('/questions', json=self.new_question)
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['created'])
      self.assertTrue(len(data['questions']))
    
    def test_422_if_question_creation_unprocessable(self):
      res = self.client().post('/questions', json=self.new_bad_question)
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 422)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'unprocessable')

    """
    test DELETE /questions/{question_id}
    """
    def test_delete_question(self):
      res = self.client().delete('/questions/10')
      data = json.loads(res.data)

      question = Question.query.filter(Question.id == 10).one_or_none()

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertEqual(data['deleted'], 10)
      self.assertTrue(data['total_questions'])
      self.assertTrue(len(data['questions']))
      self.assertEqual(question, None)
      

    def test_422_if_question_does_not_exist(self):
      res = self.client().delete('/questions/99999')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 422)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'unprocessable')

    """
    test POST /questions/search
    """
    def test_search_questions(self):
      res = self.client().post('/questions/search', json={"search_term":"earned"})
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['total_questions'])
      self.assertTrue(len(data['questions']))

    def test_search_questions_not_found(self):
      res = self.client().post('/questions/search', json={"search_term":"earnedearnedearned"})
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 404)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'resource not found')

    """
    test GET /categories/{category_id}/questions
    """
    def test_get_questions_by_category(self):
      res = self.client().get('/categories/3/questions')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['total_questions'])
      self.assertTrue(data['current_category'])
      self.assertTrue(len(data['questions']))

    def test_get_questions_by_category_invalid_category(self):
      res = self.client().get('/categories/33333/questions')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 404)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'resource not found')

    """
    test POST /quizzes
    """
    def test_quizzes(self):
      res = self.client().post('/quizzes', json={"previous_questions":[],"quiz_category":{"type":"Art","id":"2"}})
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['question'])

    def test_quizzes_method_not_allowed(self):
      res = self.client().get('/quizzes')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 405)
      self.assertEqual(data['success'], False)
      self.assertEqual(data['message'], 'method not allowed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()