import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  Set up CORS. Allow '*' for origins
  '''
  CORS(app)

  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  GET requests for all available categories
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    data = Category.query.order_by(Category.id).all()
    categories = [categorie.format() for categorie in data]
    total = len(categories)

    if total == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': categories,
      'total_categories': total
    })


  '''
  GET requests for questions
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_data(request, selection)
    total = len(selection)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': total
    })

  '''
  DELETE question using a question ID.
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_data(request, selection)

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })

    except Exception:
      abort(422)

  '''
  Create a new question
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)

    if new_question is None:
      abort(422)

    try:
      question = Question(
        question=new_question,
        answer=new_answer,
        difficulty=new_difficulty,
        category=new_category
      )
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_data(request, selection)

      return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })

    except Exception:
      abort(422)

  '''
  Create a POST endpoint to get questions based on a search term.
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    search_term = request.get_json().get('search_term', '')
    selection = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
    current_questions = paginate_data(request, selection)
    total = len(selection)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': total
    })

  '''
  Create a GET endpoint to get questions based on category.
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_category_questions(category_id):
    selection = Question.query.filter(Question.category==category_id).all()
    current_questions = paginate_data(request, selection)
    total = len(selection)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': total,
      "current_category": category_id
    })


  '''
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_questions():
    quiz_category = {}
    previous_questions = []
    params = request.get_json()
    if (params != None):
      quiz_category = params.get('quiz_category', {})
      previous_questions = params.get('previous_questions', [])
    selection = Question.query.filter(
      is_valid_category(quiz_category, Question.category),
      or_(len(previous_questions)==0, is_new_question(Question.id, previous_questions))
    ).all()

    if len(selection) == 0:
      return jsonify({
      'success': True,
      'question': None
    })

    total = len(selection)
    question = selection[random.randint(0, total - 1)].format()

    return jsonify({
      'success': True,
      'question': question
    })

  def is_valid_category(quiz_category, categoryId):
    if (len(quiz_category.keys()) == 0):
      return True
    else:
      return categoryId == quiz_category['id']

  def is_new_question(id, previous_questions):
    for question in previous_questions:
      if id == question:
        return False
    return True


  '''
  Create error handlers for all expected errors
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400
      
  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "method not allowed"
      }), 405

  DATA_PER_PAGEF = 10
  def paginate_data(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * DATA_PER_PAGEF
    end = start + DATA_PER_PAGEF

    data = [item.format() for item in selection]
    current_data = data[start:end]

    return current_data
  
  return app

    