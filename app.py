"""
The Flask application provides routes for user authentication, registration, and IPL statistics API.

Routes:
-------
- '/' or '/login': Handles the login page route. Allow users to log in using their email & password.
- '/logout': Clears the user's session data and redirects them to the login page.
- '/register': Handles the registration page route. Allows users to register
    by providing their name, email, and password.
- '/api/teams-played-ipl': Returns the list of teams that have played in the IPL.
- '/api/team1-vs-team2': Takes two team names as parameters and returns their
    track record against each other.
- '/api/record-against-all-teams': Takes a team name as a parameter and returns
    its record against all teams.
- '/api/record-against-each-team': Takes a team name as a parameter
    and returns its record against each team.
- '/api/batsman-record': Takes a batsman name as a parameter and returns
    the complete batting record of the batsman.
- '/api/bowling-record': Takes a bowler name as a parameter and
    returns the complete bowling record of the bowler.
"""

from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
import ipl
import config
import utils
import os
import json

# ***************************************************************

# Create a Flask application instance
app = Flask(__name__)

# Set the secret key for the application
app.secret_key = config.SECRET_KEY

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config.SQLITE_DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy instance
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Create the database tables
with app.app_context():
    # Check if the database file exists
    if not os.path.exists(config.SQLITE_DB_PATH):
        db.create_all()

# ***************************************************************

# Exception Classes


class MySQLException(Exception):
    """
    Handles MySQL Exception
    """


class KeyException(Exception):
    """
    Handles Key Exception
    """


class TypeException(Exception):
    """
    Handles Type Exception
    """


class AttributeException(Exception):
    """
    Handles Attribute Exception
    """


class ValueErrorException(Exception):
    """
    Handles Value Error Exception
    """


class MissingBackendError(Exception):
    """
    Handles Missing Backend Error
    """


# Exception handling routes
@app.errorhandler(MySQLException)
def handle_mysql_exception(error):
    """
    Error handler for handling MySQL exceptions.

    Args:
        error: The MySQLException object representing the error.

    Returns:
        A JSON response with the error message and a status code of 500 (Internal Server Error).
    """
    return jsonify(error=str(error)), 500


@app.errorhandler(KeyException)
def handle_key_exception(error):
    """
    Error handler for handling Key exceptions.

    Args:
        error: The KeyException object representing the error.

    Returns:
        A JSON response with the error message and a status code of 400 (Bad Request).
    """
    return jsonify(error=str(error)), 400


@app.errorhandler(TypeException)
def handle_type_exception(error):
    """
    Error handler for handling Type exceptions.

    Args:
        error: The TypeException object representing the error.

    Returns:
        A JSON response with the error message and a status code of 400 (Bad Request).
    """
    return jsonify(error=str(error)), 400


@app.errorhandler(AttributeException)
def handle_attribute_exception(error):
    """
    Error handler for handling Attribute exceptions.

    Args:
        error: The AttributeException object representing the error.

    Returns:
        A JSON response with the error message and a status code of 400 (Bad Request).
    """
    return jsonify(error=str(error)), 400


@app.errorhandler(ValueErrorException)
def handle_value_error_exception(error):
    """
    Error handler for handling Value Error exceptions.

    Args:
        error: The ValueErrorException object representing the error.

    Returns:
        A JSON response with the error message and a status code of 400 (Bad Request).
    """
    return jsonify(error=str(error)), 400


@app.errorhandler(MissingBackendError)
def handle_missing_backend_error(error):
    """
    Error handler for handling Missing Backend errors.

    Args:
        error: The MissingBackendError object representing the error.

    Returns:
        A JSON response with the error message and a status code of 500 (Internal Server Error).
    """
    return jsonify(error=str(error)), 500


def handle_exceptions(function):
    """
    Decorator function for handling exceptions.

    This decorator wraps the given function with exception handling logic.
    It catches specific exceptions and returns
    a JSON response with the corresponding error message and status code.

    Args:
        function: The function to be decorated.

    Returns:
        The decorated function that handles exceptions.

    Raises:
        None.
    """
    def wrapper(*args, **kwargs):
        result = None  # Initialize result to avoid UnboundLocalError
        error = None   # Initialize error to avoid UnboundLocalError
        status_code = 200
        
        try:
            result = function(*args, **kwargs)
        except MySQLException as exception:
            status_code = 500
            error = str(exception)
        except (KeyException, TypeException, AttributeException, ValueErrorException) as exception:
            status_code = 400
            error = str(exception)
        except MissingBackendError as exception:
            status_code = 500
            error = str(exception)
        except Exception as exception:
            status_code = 500
            error = str(exception)

        return jsonify(result=result, error=error), status_code

    wrapper.__name__ = function.__name__
    return wrapper


# ***************************************************************

# Home/Login Route
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    - This function handles the login page route. It allows users to log in to the website
    using their email and password.
    - If the user's email and password are found in the database, their details are
    stored in a session and they are 
    redirected to the 404 page with a success message.
    - If the user's email and password are not found in the database,
    an error message is displayed on the login page.
    """
    login_failed = False

    # Check if the request method is POST and if the email and password
    # fields are present in the request form
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        try:
            # Get the user from the database
            user = User.query.filter_by(email=email).first()

            # If a user is found and the password matches
            if user and sha256_crypt.verify(password, user.password):
                # store their details in a session
                session['user_id'] = user.id
                session['name'] = user.name
                session['email'] = user.email
                session['logged_in'] = True

                # Redirect to dashboard after successful login
                return redirect(url_for('dashboard'))
            # If no user is found, set login_failed to True to display an error message
            login_failed = True

        except Exception as exc:
            login_failed = True
            print(f"Login error: {str(exc)}")

    # Render the login page template with the login_failed variable set to message
    return render_template('login.html', login_failed=login_failed)


# Define a Flask route for handling logout requests
@app.route('/logout')
def logout():
    """
    This route clears the user's session data and redirects them to the login page.
    """
    # Clear the user's session data
    session.clear()

    # Redirect the user to the login page
    return redirect(url_for('login'))


# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    This function handles the registration page route.
    It allows users to register on the website by providing their name,
    email, and password.
    """
    incomplete_form = False
    # Check if the request method is POST and if the name, password and
    # email fields are present in the request form
    if (request.method == 'POST' and
        'name' in request.form and
        'password' in request.form and
        'email' in request.form):

        user_name = request.form['name']
        password = request.form['password']
        email = request.form['email']

        try:
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            
            # If the email is already registered, display an error message on the registration page
            if existing_user:
                account_already_exist = True
                return render_template('register.html', account_already_exist=account_already_exist)

            # If the email is not in the correct format, display an error message
            if not utils.check_correct_email_format(email):
                invalid_email = True
                return render_template('register.html', invalid_email=invalid_email)

            # If the registration form is incomplete, display an error message
            if not user_name or not password or not email:
                incomplete_form = True
                return render_template('register.html', incomplete_form=incomplete_form)

            # Hash the password
            hashed_password = sha256_crypt.hash(password)
            
            # Create a new user
            new_user = User(name=user_name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            
            # Registration successful
            register_success = True
            return render_template('login.html', register_success=register_success)

        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error=str(e))

    # If the request method is POST but the form is incomplete
    elif request.method == 'POST':
        incomplete_form = True

    # Render the registration page template
    return render_template('register.html', incomplete_form=incomplete_form)


# Route for teams that have played IPL so far
@app.route('/api/teams-played-ipl')
@handle_exceptions
def teams_played_ipl():
    """
    This function returns the list of teams that have played in the IPL so far.
    """
    # Check if the user is logged in
    if 'user_id' in session:
        response = ipl.teams_played_ipl()
        return response
    # Redirect to the login page if the user is not logged in
    return redirect(url_for('login'))


# Route for track record of each team against each other
@app.route('/api/team1-vs-team2')
@handle_exceptions
def team1_vs_team2():
    """
    This function takes two team names as parameters
    and returns their track record against each other.
    """
    # Check if the user is logged in
    if 'user_id' in session:
        team1 = request.args.get('team1')
        team2 = request.args.get('team2')
        response = ipl.team1_vs_team2(team1, team2)
        return response
    # Redirect to the login page if the user is not logged in
    return redirect(url_for('login'))

# Returns record of a team against all teams
@app.route('/api/record-against-all-teams')
@handle_exceptions
def team_all_records():
    """
    This function takes a team name as parameter and returns
    its record against all the teams that it has played against.
    """
    # Check if the user is logged in
    if 'user_id' in session:
        team = request.args.get('team')
        response = ipl.all_record(team)
        return response
    # Redirect to the login page if the user is not logged in
    return redirect(url_for('login'))


# Returns record of a team against each team
@app.route('/api/record-against-each-team')
@handle_exceptions
def team_api():
    """
    This function takes a team name as parameter and returns
    its record against each team that it has played against.
    """
    if 'user_id' in session:
        team = request.args.get('team')
        json_response = ipl.team_api(team)
        # Parse the JSON string to a Python dictionary before returning
        parsed_response = json.loads(json_response)
        return parsed_response
    # Redirect to login page if user is not logged in
    return redirect(url_for('login'))

# Returns complete batsman record
@app.route('/api/batsman-record')
@handle_exceptions
def batsman_record():
    """
    This function takes a batsman name as parameter and
    returns the complete batting record of the batsman.
    """
    if 'user_id' in session:
        batsman = request.args.get('batsman')
        response = ipl.batsman_api(batsman)
        return response
    # Redirect to the login page if the user is not logged in
    return redirect(url_for('login'))


# Returns complete bowling record
@app.route('/api/bowling-record')
@handle_exceptions
def bowling_record():
    """
    This function takes a bowler name as parameter and
    returns the complete bowling record of the bowler.
    """
    if 'user_id' in session:
        bowler = request.args.get('bowler')
        response = ipl.bowler_api(bowler)
        return response
    # Redirect to the login page if the user is not logged in
    return redirect(url_for('login'))


# Define the 404 error handler
@app.errorhandler(404)
def page_not_found(error):
    """
    This function Renders the 404 page
    if the page asked does not exist.
    """
    return render_template('404.html',error=error), 404


# Dashboard routes
@app.route('/dashboard')
def dashboard():
    """
    This function renders the main dashboard page.
    It's accessible only to logged-in users.
    """
    # Check if user is logged in
    if 'user_id' in session:
        return render_template('dashboard.html')
    # Redirect to login page if user is not logged in
    return redirect(url_for('login'))


@app.route('/teams_dashboard')
def teams_dashboard():
    """
    This function renders the teams statistics dashboard.
    It's accessible only to logged-in users.
    """
    # Check if user is logged in
    if 'user_id' in session:
        teams = ipl.teams_played_ipl()
        return render_template('teams_dashboard.html', teams=teams)
    # Redirect to login page if user is not logged in
    return redirect(url_for('login'))


@app.route('/players_dashboard')
def players_dashboard():
    """
    This function renders the players statistics dashboard.
    It's accessible only to logged-in users.
    """
    # Check if user is logged in
    if 'user_id' in session:
        return render_template('players_dashboard.html')
    # Redirect to login page if user is not logged in
    return redirect(url_for('login'))


@app.route('/head_to_head')
def head_to_head():
    """
    This function renders the head to head comparison page for teams.
    It's accessible only to logged-in users.
    """
    # Check if user is logged in
    if 'user_id' in session:
        teams = ipl.teams_played_ipl()
        return render_template('head_to_head.html', teams=teams)
    # Redirect to login page if user is not logged in
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
