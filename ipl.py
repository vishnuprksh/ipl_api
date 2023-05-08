import pandas as pd
import numpy as np

ipl = pd.read_csv('datasets/ipl.csv')


# Teams that have played IPL so far
def teams_played_ipl():
    
    teams = np.union1d(ipl['Team1'],ipl['Team2'])
    response = {
        'total_number_of_teams': teams.size,
        'teams' : list(teams)
    }
    return response

# Track record of each team against each other
def team1_vs_team2(team1,team2):
    teams = np.union1d(ipl['Team1'],ipl['Team2'])
    if team1 in teams and team2 in teams:
        temp_df = ipl[((ipl['Team1'] == team1) & (ipl['Team2'] == team2)) | ((ipl['Team1'] == team2) & (ipl['Team2'] == team1))]
        total_matches_played = temp_df.shape[0]
        team1_won = temp_df[temp_df['WinningTeam'] == team1].shape[0]
        team2_won = temp_df[temp_df['WinningTeam'] == team2].shape[0]
        no_result = total_matches_played - (team1_won + team2_won)

        response = {
            'total_matches_played' : total_matches_played,
            'team1_won':team1_won,
            'team2_won': team2_won,
            'no_result':no_result
        }
        return response
    else:
        return {'response':'Invalid Team name'}
    
