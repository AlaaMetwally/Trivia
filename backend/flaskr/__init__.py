import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10



def get_pagination(request, questions, num_of_questions):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * num_of_questions
  end = start + num_of_questions

  questions = [question.format() for question in questions]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers',
                           'Content-Type, Authorization')
      response.headers.add('Access-Control-Allow-Methods',
                           'GET, POST, PATCH, DELETE, OPTIONS')
      return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def categories():
      categories = Category.query.order_by(Category.id).all()
      categories_json = {}
      for category in categories:
          categories_json[category.id] = category.type
      return jsonify({
          'success': True,
          'categories': categories_json
      }),200

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def questions():
      questions = Question.query.order_by(Question.id).all()
      categories = Category.query.order_by(Category.id).all()
      total_questions = len(questions)

      questions = get_pagination(
        request, questions,
        QUESTIONS_PER_PAGE)

      categories_json = {}
      for category in categories:
          categories_json[category.id] = category.type
      return jsonify({
          'success': True,
          'questions': questions,
          'categories' : categories_json,
          'total_questions':total_questions
      }),200


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
        question = Question.query.get(id)
        question.delete()

        return jsonify({
            'success': True,
            'message': "Question has been deleted successfully"
        }),200 


  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
      data = request.get_json()
      question = data.get('question', '')
      answer = data.get('answer', '')
      difficulty = data.get('difficulty', '')
      category = data.get('category', '')

     
      question = Question(
            question=question,
            answer=answer,
            difficulty=difficulty,
            category=category)

      question.insert()
      return jsonify({
            'success': True,
             'message': 'Question has been created successfully!'
        }), 200
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
      data = request.get_json()
      search_term = data.get('searchTerm', '')
      questions = Question.query.filter(Question.question.ilike('%{search_term}%')).all()
      paginated_questions = get_pagination(
              request, questions,
              QUESTIONS_PER_PAGE)

      return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(Question.query.all())
       }), 200

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_questions_category(id):

      category = Category.query.filter_by(id=id).one_or_none()
      questions = Question.query.filter_by(category=str(id)).all()

      current_questions = get_pagination(
          request, questions,
          QUESTIONS_PER_PAGE)

      return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(questions),
          'current_category': category.type
      })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def quiz_question():
      data = request.get_json()
      previous_questions = data.get('previous_questions')
      quiz_category = data.get('quiz_category')

      if (quiz_category['id'] == 0):
          questions = Question.query.all()
      else:
          questions = Question.query.filter_by(
              category=quiz_category['id']).all()

      next_question = questions[random.randint(0, len(questions)-1)]
      found = True

      while found:
          if next_question.id in previous_questions:
              next_question = questions[random.randint(0, len(questions)-1)]
          else:
              found = False

      return jsonify({
          'success': True,
          'question': next_question.format(),
      }), 200

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          'success': False,
          'error': 404,
          'message': "Not Found"
      }), 404

  @app.errorhandler(422)
  def un_processable_entitiy(error):
      return jsonify({
          'success': False,
          'error': 422,
          'message': "un processable entitiy"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          'success': False,
          'error': 400,
          'message': "bad request"
      }), 400

  @app.errorhandler(500)
  def internal_error(error):
      return jsonify({
          'success': False,
          'error': 500,
          'message': "internal server error"
      }), 500

  return app

    
