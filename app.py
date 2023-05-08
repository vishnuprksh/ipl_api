from flask import Flask,jsonify,request
import ipl

app = Flask(__name__)

# Home Route
@app.route('/')
def index():
    return "API development on IPL Dataset"


# Route for teams that have played IPL so far
@app.route('/api/teams_played_ipl')
def teams_played_ipl():
    response = ipl.teams_played_ipl()
    return jsonify(response)


# Route for track record of each team against each other
@app.route('/api/team1_vs_team2')
def team1_vs_team2():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    response = ipl.team1_vs_team2(team1,team2)
    return jsonify(response)


app.run(debug=True) 