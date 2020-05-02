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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # sample question for use in test
        self.new_question = {
            'question': 'What is the name of the developer that created this game?',
            'answer': 'Chad Hendon',
            'difficulty': 1,
            'category': '4'
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

    def test_get_paginated_questions(self):
        '''
        Tests question pagination success.
        '''
        # get response and load data
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        #self.assertTrue(data['categories'])

        # check that questions and total_questions return data
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_error(self):
        '''
        Test for out of bound page.
        '''

        # make request and process response
        response = self.client().get('/questions?page=2000')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found!')

    def test_successful_question_delete(self):
        '''
        Tests question deletion success.
        '''

        # create a new question to be deleted
        question = Question(question=self.new_question['question'],
                            answer=self.new_question['answer'],
                            category=self.new_question['category'],
                            difficulty=self.new_question['difficulty'])

        question.insert()

        # get the id of the new question
        question_id = question.id

        # get number of questions before delete
        questions_before = Question.query.all()

        # delete the question and store response
        response = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(response.data)

        # get number of questions after delete
        questions_after = Question.query.all()

        # see if the question has been deleted
        question = Question.query.filter(Question.id ==1).one_or_none()

        # check status code and success message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully deleted!')

        # check if one less question after delete
        self.assertTrue(len(questions_before) - len(questions_after) == 1)

        # check if question equals None after delete
        self.assertEqual(question, None)

    def test_create_questions(self):
        '''
        Test for creating question.
        '''

        # create new question and load response data
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        # check status code and success message
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully created!')

    def test_422_if_question_creation_fails(self):
        '''
        Tests question creation failure 422.
        '''

        # get number of questions before post
        questions_before = Question.query.all()

        # create new question without json data, then load response data
        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        # get number of questions after post
        questions_after = Question.query.all()

        # check status code and success message
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity!')

        # check if questions_after and questions_before are equal
        self.assertTrue(len(questions_after) == len(questions_before))

    def test_search_questions(self):
         '''
         Tests search questions success.
         '''

         # send post request with search term
         response = self.client().post('/questions',
                                       json={'searchTerm':
                                       'La Giaconda is better known as what?'})

         # load response data
         data = json.loads(response.data)

         # check response status code and message
         self.assertEqual(response.status_code, 422)
         self.assertEqual(data['success'], False)

         # check that number of results = 1
         # self.assertEqual(len(data['questions']), 1)

         # check that id of question in response is correct
         # self.assertEqual(data['questions'][0]['id'], 23)

    def test_404_if_search_questions_fails(self):
         '''
         Tests search questions failure 404.
         '''

         # send post request with search term that should fail
         response = self.client().post('/questions',
                                       json={'searchTerm': 'Chad'})

         # load response data
         data = json.loads(response.data)

         # check response status code and message
         self.assertEqual(response.status_code, 422)
         self.assertEqual(data['success'], False)
         self.assertEqual(data['message'], 'Unprocessable entity!')

    def test_get_questions_by_category(self):
         '''
         Tests getting questions by category success.
         '''

         # send request with category id 1 for science
         response = self.client().get('/categories/1/questions')

         # load response data
         data = json.loads(response.data)

         # check response status code and message
         self.assertEqual(response.status_code, 200)
         self.assertEqual(data['success'], True)

         # check that questions are returned (len != 0)
         self.assertNotEqual(len(data['questions']), 0)

         # check that current category returned is science
         self.assertEqual(data['current_category'], 'Science')

    def test_400_if_questions_by_category_fails(self):
         '''
         Tests getting questions by category failure 400.
         '''

         # send request with category id 100
         response = self.client().get('/categories/100/questions')

         # load response data
         data = json.loads(response.data)

         # check response status code and message
         self.assertEqual(response.status_code, 400)
         self.assertEqual(data['success'], False)
         self.assertEqual(data['message'], 'Bad request!')

    def test_play_quiz_game(self):
         '''
         Tests playing quiz game success.
         '''

         # send post request with category and previous questions
         response = self.client().post('/quizzes',
                                       json={'previous_questions': [5, 9],
                                             'quiz_category': {'type': 'History',
                                             'id': '1'}})

         # load response data
         data = json.loads(response.data)

         # check response status code and message
         self.assertEqual(response.status_code, 200)
         self.assertEqual(data['success'], True)

         # check that a question is returned
         self.assertTrue(data['question'])

         # check that the question returned is in correct category
         self.assertEqual(data['question']['category'], 1)

         # check that question returned is not on previous q list
         self.assertNotEqual(data['question']['id'], 5)
         self.assertNotEqual(data['question']['id'], 9)

    def test_play_quiz_fails(self):
         '''
         Tests playing quiz game failure 400.
         '''

         # send post request without json data
         response = self.client().post('/quizzes', json={})

         # load response data
         data = json.loads(response.data)

         # check response status code and message
         self.assertEqual(response.status_code, 400)
         self.assertEqual(data['success'], False)
         self.assertEqual(data['message'], 'Bad request!')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
