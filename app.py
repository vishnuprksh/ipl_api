"""
This is a Flask API that provides various routes to access the IPL dataset. The API uses the 'Flask' and 'jsonify' modules for response handling and 'request' module for HTTP request handling.
"""

from flask import Flask, jsonify, request,render_template,redirect, url_for,session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import ipl
import config

app = Flask(__name__)


app.secret_key = config.SECRET_KEY
  
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)


# Home/Login Route
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    message = False
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        if user:
            session['logged_in'] = True
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            session['email'] = user['email']
            message = 'Logged in successfully !'
            return render_template('404.html', message = message)
        else:
            message = True
    return render_template('login.html', login_failed = message)


# Logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))


# Register  
@app.route('/register', methods =['GET', 'POST'])
def register():
    incomplete_form = False
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        user_name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        email_expression = regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if account:
            account_already_exist = True
            return render_template('register.html',account_already_exist=account_already_exist)
        
        elif not re.fullmatch(email_expression, email):
            invalid_email = True
            return render_template('register.html',invalid_email=invalid_email)
        elif not user_name or not password or not email:
            incomplete_form = True
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (user_name, email, password, ))
            mysql.connection.commit()
            register_success = True
            return render_template('login.html',register_success=register_success)
    elif request.method == 'POST':
        incomplete_form = True
    return render_template('register.html', incomplete_form=incomplete_form)


# Route for teams that have played IPL so far
@app.route('/api/teams-played-ipl')
def teams_played_ipl():
    """
    This function returns the list of teams that have played in the IPL so far.
    """
    response = ipl.teams_played_ipl()
    return jsonify(response)

# Route for track record of each team against each other
@app.route('/api/team1-vs-team2')
def team1_vs_team2():
    """
    This function takes two team names as parameters and returns their track record against each other.
    """
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    response = ipl.team1_vs_team2(team1, team2)
    return jsonify(response)

# Returns record of a team against all teams
@app.route('/api/record-against-all-teams')
def team_all_records():
    """
    This function takes a team name as parameter and returns its record against all the teams that it has played against.
    """
    team = request.args.get('team')
    response = ipl.all_record(team)
    return jsonify(response)

# Returns record of a team against each team
@app.route('/api/record-against-each-team')
def team_API():
    """
    This function takes a team name as parameter and returns its record against each team that it has played against.
    """
    team = request.args.get('team')
    response = ipl.team_API(team)
    return response

# Returns complete batsman record
@app.route('/api/batsman-record')
def batsman_record():
    """
    This function takes a batsman name as parameter and returns the complete batting record of the batsman.
    """
    batsman = request.args.get('batsman')
    response = ipl.batsman_API(batsman)
    return response

# Returns complete bowling record
@app.route('/api/bowling-record')
def bowling_record():
    """
    This function takes a bowler name as parameter and returns the complete bowling record of the bowler.
    """
    bowler = request.args.get('bowler')
    response = ipl.bowler_API(bowler)
    return response


# Define the 404 error handler
@app.errorhandler(404)
def page_not_found(error):
    # Render the 404 page
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
