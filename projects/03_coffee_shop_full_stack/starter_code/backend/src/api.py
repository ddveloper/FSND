import os
from flask import Flask, request, jsonify, abort, flash
from sqlalchemy import exc
import json
import sys
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
app.secret_key = 'some secret key'
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


# ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
    '''
        GET /drinks
        returns status code 200 and json {"success": True, "drinks": drinks}
            where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    '''
        GET /drinks-detail
            require the 'get:drinks-detail' permission
        returns status code 200 and json {"success": True, "drinks": drinks}
            where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    '''
        POST /drinks
            require the 'post:drinks' permission
        returns status code 200 and json {"success": True, "drinks": drink}
            where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''
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
    except Exception:
        flash('An error occur when adding new recipe')
        abort(500, 'failed to add new drink')
        print(sys.exc_info())


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, drink_id):
    '''
        PATCH /drinks/<id>
            where <id> is the existing model id
            require the 'patch:drinks' permission
            respond with a 404 error if <id> is not found
            update the corresponding row for <id>
        returns status code 200 and json {"success": True, "drinks": drink}
            where drink an array containing only the updated drink
            or appropriate status code indicating reason for failure
    '''
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if not drink:
            flash('internal error: drink not found!')
            abort(404, 'internal error: drink not found!')
        if title:
            drink.title = title
        if recipe:
            drink.recipe = json.dumps(recipe)
        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except Exception:
        flash('An error occur when updating new recipe')
        abort(500, 'failed to update drink')
        print(sys.exc_info())


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    '''
        DELETE /drinks/<drink_id>
            where <drink_id> is the existing model id
            require the 'delete:drinks' permission
            respond with a 404 error if <id> is not found
            delete the corresponding row for <id>
        returns status code 200 and json {"success": True, "delete": id}
            where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''
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
    except Exception:
        flash('An error occur when deleting new recipe')
        abort(500, 'failed to delete drink')
        print(sys.exc_info())


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    '''
    Example error handling for unprocessable entity
    '''
    return jsonify({
        "success": False,
        "error": 422,
        "message": error.description
    }), 422


@app.errorhandler(400)
def bad_request_handler(error):
    '''
    Example error handling for not found
    '''
    return jsonify({
        'success': False,
        'error': 400,
        'message': error.description
    }), 400


@app.errorhandler(404)
def not_found_handler(error):
    '''
    Example error handling for not found
    '''
    return jsonify({
        'success': False,
        'error': 404,
        'message': error.description
    }), 404


@app.errorhandler(500)
def internal_server_handler(error):
    '''
    Example error handling for not found
    '''
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
