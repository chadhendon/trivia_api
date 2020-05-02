import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


# utility for paginating questions
def paginate_questions(request, selection):

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Set up CORS. Allow ALL '*' for origins.
    CORS(app, resources={'/': {'origins': '*'}})

    # Use the after_request decorator to set Access control
    @app.after_request
    def after_request(response):
        '''
        Sets access control.
        '''
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization, True')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS')

        return response

    # Handles Get request for all '*' categories
    # or status code 500 for server error
    @app.route('/categories')
    def get_all_categories():

        try:
            categories = Category.query.all()
            # Format categories to match front-end
            categories_dict = {}
            for category in categories:
                categories_dict[category.id] = category.type

            # return successful response
            return jsonify({
                'success': True,
                'categories': categories_dict
                }), 200

        except Exception:
            abort(500)

    @app.route('/questions')
    def get_questions():
        '''
        Endpoint to handle GET request for questions,
        including pagination every 10 questions.
        '''

        # get paginated questions and categories
        selection = Question.query.all()
        total_questions = len(selection)

        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        current_questions = paginate_questions(request, selection)

        # return 404 if there are no questions for the page numbers
        if (len(current_questions) == 0):
            abort(404)

        # return values if there are no errors
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories_dict
            }), 200

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        '''
        Endpoint deletes a specific question by the id
        given as a url parameter.
        '''

        try:
            # get the question by id
            question = Question.query.get(id)
            question.delete()

            return jsonify({
                'success': True,
                'message': "Question successfully deleted!"
                }), 200
        except IndexError:
            # abort if problem deleting question
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        '''
        Endpoint handles POST requests for
        creating new questions. Status code 422 is
        returned if any of the json data is empty.
        '''

        # Get json data from request
        data = request.get_json()

        # Load json data
        question = data.get('question', '')
        answer = data.get('answer', '')
        difficulty = data.get('difficulty', '')
        category = data.get('category', '')

        # validate to ensure no data is empty
        if ((question == '') or (answer == '')
           or (difficulty == '') or (category == '')):
            abort(422)

        try:
            # Create a new question instance
            question = Question(question=question, answer=answer,
                                difficulty=difficulty, category=category)

            # save question
            question.insert()

            # return success message
            return jsonify({
                'success': True,
                'message': 'Question successfully created!'
                }), 201

        except IndexError:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def search_questions():
        '''
        Endpoint handles POST requests for
        creating searching questions. Status code
        422 is returned if any of the json data is
        empty.
        '''

        data = reques.get_json()
        search_term = data.get('searchTerm', '')

        # Return 422 status code if empty search term is sent
        if search_term == '':
            abort(422)

        try:
            # query the database using search term
            selection = Question.query.filter(Question.question.ilike
                                              (f'%{search_term}%')).all()

            # 404 if no results found
            if len(questions) == 0:
                abort(404)

            paginated = paginate_questions(request, selection)

            # return results
            return jsonify({
                'success': True,
                'questions': paginated,
                'total_questions': len(Question.query.all())
                }), 200

        except IndexError:
            abort(404)

    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        '''
        Endpoint to get questions by category.
        '''

        # Get the category by id.
        category = Category.query.filter_by(id=id).one_or_none()

        # abort 400 for bad request if category is not found
        if (category is None):
            abort(400)

        selection = Question.query.filter_by(category=id).all()

        # paginate the selection
        paginated = paginate_questions(request, selection)

        # return the results
        return jsonify({
            'success': True,
            'questions': paginated,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
            }), 200

    @app.route('/quizzes', methods=['POST'])
    def get_random_quiz_question():
        '''
        Endpoint to handles POST requests for playing quiz.
        '''
        # process the request data and get the values
        data = request.get_json()
        previous_questions = data.get('previous_questions')
        quiz_category = data.get('quiz_category')

        # abort 400 if quiz_category of previous_questions is empty
        if ((quiz_category is None) or (previous_questions is None)):
            abort(400)

        # Load questions all questions if "ALL" is selected
        if (quiz_category['id'] == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(
             category=quiz_category['id']).all()

        # defines a random question generator method
        def get_random_question():
            return questions[random.randint(0, len(questions)-1)]

        # get random question for the next question
        next_question = get_random_question()

        # defines boolean used to check that the question
        # is not a previous question
        found = True

        while found:
            if next_question.id in previous_questions:
                next_question = get_random_question()
            else:
                found = False

        return jsonify({
            'success': True,
            'question': next_question.format(),
            }), 200

    # Error handler for Bad request (400)
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request!'
            }), 400

    # Error handler for resource not found (404)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found!'
            }), 404

    # Error handler for unprocesable entity (422)
    @app.errorhandler(422)
    def unprocesable_entity(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity!'
            }), 422

    return app
