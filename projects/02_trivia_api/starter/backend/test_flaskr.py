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
        self.database_path = "postgresql://postgres:postgres@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    # test get all categories
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)

    # test get all questions
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(len(data['categories']), 6)
        self.assertIsNone(data['current_category'])

    # test delete question fail
    def test_400_for_fail_delete(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['messages'], 'question number not found')
        
    # test delete question pass
    def test_delete_question(self):
        new_question = Question(question='question to delete', 
                                answer='ans', 
                                category=2, 
                                difficulty=1)
        new_question.insert()
        new_id = new_question.get_last_id()

        res = self.client().delete('/questions/{}'.format(new_id))
        data = json.loads(res.data)
        question = Question.query.filter_by(id=new_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], new_id)
        self.assertIsNone(question)
        
    # test add question fail
    def test_400_for_fail_add(self):
        res = self.client().post('/questions/add', json={
            'question': "What boxer's original name is Cassius Clay?", 
            'answer': 'ans', 
            'category': 4, 
            'difficulty': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['messages'], 'question already exists')
        
    # test add question pass
    def test_add_question(self):
        res = self.client().post('/questions/add', json={
            'question': "new question", 
            'answer': 'ans', 
            'category': 4, 
            'difficulty': 1})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        question = Question.query.filter_by(id=int(data['new_id'])).one_or_none()
        self.assertIsNotNone(question)
        question.delete()
        
    # test query questions based on category fail
    def test_404_for_fail_query(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['messages'], 'category number not found')
        
    # test query questions based on category pass
    def test_query_questions_by_category(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 4)
        self.assertEqual(data['current_category'], 4)
        
    # test query questions based on search term empty
    def test_query_questions_by_search_empty(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'blabla'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)
        
    # test quiz bad category
    def test_400_quiz_bad_category(self):
        res = self.client().post('/quizzes', json={'previous_questions': [5,12,23,9], 'quiz_category': {'id': '1000'}})
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], False)
        self.assertEqual(data['messages'], 'category number not found')
        
    # test quiz
    def test_quiz_get_no_more(self):
        res = self.client().post('/quizzes', json={'previous_questions': [5,12,23,9], 'quiz_category': {'id': '4'}})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNone(data['question'])
        
    # test quiz
    def test_quiz_ok(self):
        res = self.client().post('/quizzes', json={'previous_questions': [4,6,10,9], 'quiz_category': {'id': '4'}})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['question'])



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

    # app = create_app()
    # #self.client = self.app.test_client
    # database_name = "trivia_test"
    # database_path = "postgresql://postgres:postgres@{}/{}".format('localhost:5432', database_name)
    # setup_db(app, database_path)

    # # binds the app to the current context
    # with app.app_context():
    #     db = SQLAlchemy()
    #     db.init_app(app)
    #     # create all tables
    #     db.create_all()
    # app.run()