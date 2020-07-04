import os
from flask import Flask, request, jsonify, abort, flash
from sqlalchemy import exc
import json, sys
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
app.secret_key = 'some secret key'
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    body = request.get_json()
    title = body['title']
    recipe = body['recipe']
    old_drink = Drink.query.filter_by(title=title).one_or_none()
    if old_drink:
        flash('Drink with same title already exist')
        abort(400, 'Drink with same title already exist')

    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        formatted_drinks = [drink.long()]
        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        })
    except:
        flash('An error occur when adding new recipe')
        abort(500, 'failed to add new drink')
        print(sys.exc_info())

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, drink_id):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if not drink:
            flash('internal error: drink not found!')
            abort(404, 'internal error: drink not found!')
        if title: drink.title = title
        if recipe: drink.recipe = json.dumps(recipe)
        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        flash('An error occur when updating new recipe')
        abort(500, 'failed to update drink')
        print(sys.exc_info())

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.filter_by(id=drink_id).one_or_none()
    if not drink:
        flash('drink ID is not found.')
        abort(404, 'drink ID is not found.')

    try:
        drink.delete()
        return jsonify({
            'success': True,
            'deleted': drink_id
        })
    except:
        flash('An error occur when deleting new recipe')
        abort(500, 'failed to delete drink')
        print(sys.exc_info())

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": error.description
    }), 422

'''
Example error handling for not found
'''
@app.errorhandler(400)
def bad_request_handler(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': error.description
    }), 400

'''
Example error handling for not found
'''
@app.errorhandler(404)
def not_found_handler(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': error.description
    }), 404

'''
Example error handling for not found
'''
@app.errorhandler(500)
def internal_server_handler(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': error.description
    }), 500

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

# app.debug = True
# app.run()