"""
This is a Flask API that provides various routes to access the IPL dataset. The API uses the 'Flask' and 'jsonify' modules for response handling and 'request' module for HTTP request handling.
"""

from flask import Flask, jsonify, request
import ipl

app = Flask(__name__)

# Home Route
@app.route('/')
def index():
    """
    This function returns a string as a response to the default route.
    """
    return "API development on IPL Dataset"

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

if __name__ == '__main__':
    app.run(debug=True)
