# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

## API References

### Getting Started
- Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `http://127.0.0.1:5000/`, which is set as a proxy in the frontend configuration.
- Authentication: This version of the application does not require authentication or API keys.

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False,
    "messages": "detailed error messages"
}
```
The API will return four error types with detailed messages when requests fail:  
 - 400: Bad Request
 - 404: Resource Not Found
 - 422: Not Processable
 - 500: Internal Server Error

### Endpoints
GET '/questions'
- General:
-- Return a list of questions, success value, total number of questions, and all category types.
-- Returns are paginated in groups of 10, include a request argument to choose page number, starting from 1.
- Sample: `curl http://127.0.0.1:5000/questions`
```
  {
    "categories":{
      "1":"Science",
      "2":"Art",
      "3":"Geography",
      "4":"History",
      "5":"Entertainment",
      "6":"Sports"
      },
    "current_category":null,
    "questions":[
      {
        "answer":"Maya Angelou",
        "category":4,
        "difficulty":2,
        "id":5,
        "question":"Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
      },{
        "answer":"Muhammad Ali",
        "category":4,
        "difficulty":1,
        "id":9,
        "question":"What boxer's original name is Cassius Clay?"
      },{
        "answer":"Apollo 13",
        "category":5,
        "difficulty":4,
        "id":2,
        "question":"What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
      },{
        "answer":"Tom Cruise",
        "category":5,
        "difficulty":4,
        "id":4,
        "question":"What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
      },{
        "answer":"Edward Scissorhands",
        "category":5,
        "difficulty":3,
        "id":6,
        "question":"What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
      },{
        "answer":"Brazil",
        "category":6,
        "difficulty":3,
        "id":10,
        "question":"Which is the only team to play in every soccer World Cup tournament?"
      },{
        "answer":"Uruguay",
        "category":6,
        "difficulty":4,
        "id":11,
        "question":"Which country won the first ever soccer World Cup in 1930?"
      },{
        "answer":"George Washington Carver",
        "category":4,
        "difficulty":2,
        "id":12,
        "question":"Who invented Peanut Butter?"
      },{
        "answer":"Lake Victoria",
        "category":3,
        "difficulty":2,
        "id":13,
        "question":"What is the largest lake in Africa?"
      },{
        "answer":"The Palace of Versailles",
        "category":3,
        "difficulty":3,
        "id":14,
        "question":"In which royal palace would you find the Hall of Mirrors?"
      }
    ],
    "success":true,
    "total_questions":19
  }
```
GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
- Sample: `curl http://127.0.0.1:5000/categories`
```
  {
    '1' : "Science",
'2' : "Art",
'3' : "Geography",
'4' : "History",
'5' : "Entertainment",
    '6' : "Sports"
  }
```
POST '/questions/search'
- Fetches a list of questions based on the search term
- Request Arguments: JSON input with "searchTerm" text
- Returns: A list of questions including searchTerm inside.
- Sample: `curl -X POST http://127.0.0.1:5000/questions/search -H "Content-Type: application/json" -d '{"searchTerm": "how"}'`
```
  {
    "questions":[
      {
        "answer":"One",
        "category":2,
        "difficulty":4,
        "id":18,
        "question":"How many paintings did Van Gogh sell in his lifetime?"
      }
    ],
    "success":true
  }
```
GET '/categories/<int:category_id>/questions'
- Fetches a list of questions based on the category ID
- Request Arguments: category_id in URL
- Returns: A list of questions under same category.
- Sample: `curl http://127.0.0.1:5000/categories/1/questions`
```
  {
    "current_category":1,
    "questions":[
      {
        "answer":"The Liver",
        "category":1,
        "difficulty":4,
        "id":20,
        "question":"What is the heaviest organ in the human body?"
      },{
        "answer":"Alexander Fleming",
        "category":1,
        "difficulty":3,
        "id":21,
        "question":"Who discovered penicillin?"
      },{
        "answer":"Blood",
        "category":1,
        "difficulty":4,
        "id":22,
        "question":"Hematology is a branch of medicine involving the study of what?"
      }
    ],
    "success":true
  }
```
POST '/questions/add'
- Add a new questions into our database
- Request Arguments: JSON input with "question", "answer", "category" and "difficulty".
- Returns: None
- Sample: `curl -X POST http://127.0.0.1:5000/questions/add -H "Content-Type: application/json" -d '{"question": "test question", "answer": "test answer", "category": 1, "difficulty": 2}'`
```
  {"new_id":28,"success":true}
```
DELETE '/questions/<int:question_id>'
- Delete a question based on question ID
- Request Arguments: "question_id" in URL
- Returns: If the operation succeeded or not.
- Sample: `curl -X DELETE http://127.0.0.1:5000/questions/28`
```
  {"deleted":28,"success":true}
```
POST '/quizzes'
- Play a quiz game
- Request Arguments: JSON input with a list of "previous_questions", current "quiz_category".
- Returns: A randomly chosen question from the database with same "quiz_category" and not in "previous_questions"
- Note: when "quiz_category" == 0 means for all categories.
- Sample: `curl -X POST http://127.0.0.1:5000/quizzes -H "Content-Type: application/json" -d '{"previous_questions": [4,6,10,9], "quiz_category": {"id": "4"}}'`
```
  {
    "question": {
      "answer":"Scarab",
      "category":4,
      "difficulty":4,
      "id":23,
      "question":"Which dung beetle was worshipped by the ancient Egyptians?"
    },
    "success":true
  }
```

## Deployment N/A
## Authors
Dawei Zhang
## Acknowledgements
The awesome team at Udacity and Coach Caryn.

```


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```