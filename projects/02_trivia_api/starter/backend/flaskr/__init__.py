import os
from flask import Flask, request, abort, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  @app.route('/categories', methods=['GET'])
  def get_categories():
    # return all categories
    categories = Category.query.all()
    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories}
    })

  @app.route('/questions', methods=['GET'])
  def get_questions():
    # return paginated questions list
    page = request.args.get('page', 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = Question.query.all()
    formatted_questions = [question.format() for question in questions]
    categories = Category.query.all()
    return jsonify({
      'success': True,
      'questions': formatted_questions[start:end],
      'total_questions': len(questions),
      'current_category': None,
      'categories': {category.id: category.type for category in categories}
    })

  @app.route('/questions/search', methods=['POST'])
  def search_questions():    
    # return questions list based on search term
    body = request.get_json()
    search_term = body.get('searchTerm', None)
    questions = Question.query.filter(Question.question.ilike(r'%{}%'.format(search_term))).all()
    formatted_questions = [question.format() for question in questions]
    return jsonify({
      'success': True,
      'questions': formatted_questions
    })

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    # return questions list having category id == input id
    categories = Category.query.all()
    if category_id not in [category.id for category in categories]:
      abort(400, 'category number not found')

    questions = Question.query.filter_by(category=category_id).all()
    formatted_questions = [question.format() for question in questions]
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'current_category': category_id
    })

  @app.route('/questions/add', methods=['POST'])
  def add_question():
    # add a new question into database
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    old_question = Question.query.filter_by(question=new_question) \
                    .filter_by(category=new_category).one_or_none()
    if old_question is not None:
      abort(400, 'question already exists')

    try:
      question = Question(question=new_question, answer=new_answer, 
                    category=new_category, difficulty=new_difficulty)
      question.insert()
      new_id = question.get_last_id()
      return jsonify({
        'success': True,
        'new_id': new_id
      })
    except:
      flash('An error occur when adding new question')
      abort(500, 'failed to add new question')
      print(sys.exc_info())

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question_by_id(question_id):
    # delete question based on input question id (same as id in DB)
    question = Question.query.filter_by(id=question_id).first()
    if question is None:
      abort(400, 'question number not found')

    try:
      question.delete()
      return jsonify({
        'success': True,
        'deleted': question_id
      })
    except:
      flash('An error occur when deleting question {}'.format(question_id))
      abort(500, 'failed to delete question {}'.format(question_id))
      print(sys.exc_info())

  @app.route('/quizzes', methods=['POST'])
  def quiz():    
    # return questions based on quiz status from frontend
    body = request.get_json()
    previous_questions = body.get('previous_questions', [])
    quiz_category = body.get('quiz_category', None)
    categories = Category.query.all()
    quiz_category_id = int(quiz_category['id'])
    if quiz_category_id != 0 and quiz_category_id not in [category.id for category in categories]:
      abort(400, 'category number not found')

    questions = Question.query.all() if quiz_category_id == 0 else Question.query.filter_by(category=quiz_category['id']).all()
    filtered_questions = []
    for question in questions:
      if question.id not in previous_questions:
        filtered_questions.append(question)
    random_question = None if len(filtered_questions) == 0 else random.choice(filtered_questions).format()
    #print(random_question)
    return jsonify({
      'success': True,
      'question': random_question
    })

  @app.errorhandler(400)
  def bad_request_error(error):
    return jsonify({
      'success': False,
      'messages': error.description
    }), 400

  @app.errorhandler(404)
  def not_found_error(error):
    return jsonify({
      'success': False,
      'messages': error.description
    }), 404

  @app.errorhandler(422)
  def unprocessable_entity_error(error):
    return jsonify({
      'success': False,
      'messages': error.description
    }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      'success': False,
      'messages': error.description
    }), 500
  
  return app

    