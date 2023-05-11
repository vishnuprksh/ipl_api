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

Functions:
----------
- login(): Handles the login page route. Verifies user credentials and
    stores user details in a session upon successful login.
- logout(): Clears the user's session data and redirects them to the login page.
- register(): Handles the registration page route.
    Validates user input, checks email availability, and registers the user.
- teams_played_ipl(): Returns the list of teams that have played in the IPL.
- team1_vs_team2(): Returns the track record of two teams against each other.
- team_all_records(): Returns a team's record against all the teams it has played against.
- team_API(): Returns a team's record against each team it has played against.
- batsman_record(): Returns the complete batting record of a batsman.
- bowling_record(): Returns the complete bowling record of a bowler.
- page_not_found(error): Custom 404 error handler.

Dependencies:
-------------
The code imports several dependencies:

- Flask: A micro web framework used to develop web applications in Python.
- jsonify: A Flask function that converts Python dictionary objects to JSON format.
- request: A Flask object that represents the HTTP request sent by a client.
- render_template: A Flask function that allows the application to render HTML templates.
- redirect: A Flask function that redirects the client to a different endpoint.
- url_for: A Flask function that generates URLs for the application's endpoints.
- session: A Flask object that represents a user session,
    allowing data to be stored across requests.
- Flask-MySQLdb: A Flask extension that allows the application to interact with a MySQL database.
- MySQLdb.cursors: A Python module that provides an interface for working with
    cursors in MySQL databases.
- passlib.hash: A Python library that provides password hashing and verification functionality.
- ipl: A custom module that contains functions for processing Indian Premier League (IPL) data.
- config: A module that contains configuration settings for the application.
- utils: A module that contains utility functions used throughout the application.
"""

from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from passlib.hash import sha256_crypt
import ipl
import config
import utils

# ***************************************************************

# Create a Flask application instance
app = Flask(__name__)

# Set the secret key for the application
app.secret_key = config.SECRET_KEY

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
        else:
            status_code = 200
            error = None

        return jsonify(result=result, error=error), status_code

    wrapper.__name__ = function.__name__
    return wrapper


# ***************************************************************

# Configure the MySQL database connection settings for the application
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

# Create a MySQLdb connection object using the Flask-MySQLdb extension
mysql = MySQL(app)

# ***************************************************************

# Home/Login Route
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
@handle_exceptions
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
            # Connect to the database
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Get the user from the database
            cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
            user = cursor.fetchone()
            # Close the database connection
            cursor.close()

            # If a user is found and the password matches
            if user and sha256_crypt.verify(password, user['password']):
                # store their details in a session
                session['user_id'] = user['user_id']
                session['name'] = user['name']
                session['email'] = user['email']
                session['logged_in'] = True
                # message = 'Logged in successfully !'

                # redirect to the 404 page with a success message
                # return render_template('404.html', message=message)
                return session['name'] + "Bhai tu login hogya"
            # If no user is found, set login_failed to True to display an error message
            # on the login page
            login_failed = True

        except Exception as exc:
            raise MySQLException() from exc

    # Render the login page template with the login_failed variable set to message
    return render_template('login.html', login_failed=login_failed)


# Define a Flask route for handling logout requests
@app.route('/logout')
def logout():
    """
    This route clears the user's session data and redirects them to the login page.
    """
    # Clear the user's session data
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)

    # Redirect the user to the login page
    return redirect(url_for('login'))


# Register Route
@app.route('/register', methods=['GET', 'POST'])
@handle_exceptions
def register():
    """
    This function handles the registration page route.
    It allows users to register on the website by providing their name,
    email, and password. If the user's email is not already registered and 
    is in the correct email format, the user's details
    are stored in the database and the user is redirected to the login page 
    with a success message. If the email is already
    registered, an error message is displayed on the registration page. 
    If the email is not in the correct format or the 
    registration form is incomplete, an appropriate error message is 
    displayed on the registration page.
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
            # Encrypt the password
            hashed_password = sha256_crypt.encrypt(password)
            # Connect to the database and execute a SELECT query to check if
            # the email is already registered
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM user WHERE email = %s', (email, ))
            account = cursor.fetchone()

            # If the email is already registered, display an error message on the registration page
            if account:
                account_already_exist = True
                return render_template('register.html', account_already_exist=account_already_exist)

            # If the email is not in the correct format, display an error
            # message on the registration page
            if not utils.check_correct_email_format(email):
                invalid_email = True
                return render_template('register.html', invalid_email=invalid_email)

            # If the registration form is incomplete, display an error
            # message on the registration page
            if not user_name or not password or not email:
                incomplete_form = True

            # If the email is not already registered, is in the correct format
            # and the registration form is complete,
            # store the user's details in the database and redirect to the
            # login page with a success message
            else:
                cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s)',
                               (user_name, email, hashed_password,))
                mysql.connection.commit()
                register_success = True
                return render_template('login.html', register_success=register_success)

        except Exception as exc:
            raise MySQLException() from exc

    # If the request method is POST but the name, password
    # and email fields are not present in the request form,
    # display an error message on the registration page
    elif request.method == 'POST':
        incomplete_form = True

    # Render the registration page template with the appropriate error messages
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
        return jsonify(response)
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
        return jsonify(response)
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
        return jsonify(response)

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
        response = ipl.team_api(team)
        return response

    # Redirect to the login page if the user is not logged in
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
def page_not_found():
    """
    This function Renders the 404 page
    if the page asked does not exist.
    """
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
