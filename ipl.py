import pandas as pd
import numpy as np
import json

# Importing Datasets
matches = pd.read_csv('datasets/ipl.csv')
balls = pd.read_csv('datasets/IPL_bowling_stats.csv')

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


ball_withmatch = balls.merge(matches, on='ID', how='inner').copy()
ball_withmatch['BowlingTeam'] = ball_withmatch.Team1 + ball_withmatch.Team2
ball_withmatch['BowlingTeam'] = ball_withmatch[['BowlingTeam', 'BattingTeam']].apply(lambda x: x.values[0].replace(x.values[1], ''), axis=1)
batter_data = ball_withmatch[np.append(balls.columns.values, ['BowlingTeam', 'Player_of_Match'])]


# Teams that have played IPL so far
def teams_played_ipl():
    
    teams = np.union1d(matches['Team1'],matches['Team2'])
    data = {
        'total_number_of_teams': teams.size,
        'teams' : list(teams)
    }
    return data

teams = np.union1d(matches['Team1'],matches['Team2'])
# Track record of each team against each other
def team1_vs_team2(team1,team2):
    if team1 in teams and team2 in teams:
        temp_df = matches[((matches['Team1'] == team1) & (matches['Team2'] == team2)) | ((matches['Team1'] == team2) & (matches['Team2'] == team1))]
        total_matches_played = temp_df.shape[0]
        team1_won = temp_df[temp_df['WinningTeam'] == team1].shape[0]
        team2_won = temp_df[temp_df['WinningTeam'] == team2].shape[0]
        no_result = total_matches_played - (team1_won + team2_won)

        data = {
            'total_matches_played' : total_matches_played,
            'team1_won':team1_won,
            'team2_won': team2_won,
            'no_result':no_result
        }
        return data
    else:
        return {'response':'Invalid team name'}

# Returns record of a team against all 
def all_record(team):
    if team in teams:
        df = matches[(matches['Team1'] == team) | (matches['Team2'] == team)].copy()
        mp = df.shape[0]
        won = df[df.WinningTeam == team].shape[0]
        no_result = df[df.WinningTeam.isnull()].shape[0]
        loss = mp - won - no_result
        no_of_title = df[(df.MatchNumber == 'Final') & (df.WinningTeam == team)].shape[0]
        return {'matchesplayed': mp,
                'won': won,
                'loss': loss,
                'noResult': no_result,
                'title': no_of_title}
    else:
        return {
            'response':'Invalid team name'
        }

# Utils: Complete team record
def team_API(team, matches=matches):
    df = matches[(matches['Team1'] == team) | (matches['Team2'] == team)].copy()
    self_record = all_record(team)
    TEAMS = matches.Team1.unique()
    against = {team2: team1_vs_team2(team, team2) for team2 in TEAMS}
    data = {team: {'overall': self_record,
                   'against': against}}
    return json.dumps(data, cls=NpEncoder,indent=4)

# Returns batsman record
def batsman_record(batsman, df):
    if df.empty:
        return np.nan
    out = df[df.player_out == batsman].shape[0]
    df = df[df['batter'] == batsman]
    inngs = df.ID.unique().shape[0]
    runs = df.batsman_run.sum()
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]
    if out:
        avg = runs / out
    else:
        avg = np.inf

    nballs = df[~(df.extra_type == 'wides')].shape[0]
    if nballs:
        strike_rate = runs / nballs * 100
    else:
        strike_rate = 0
    gb = df.groupby('ID').sum()
    fifties = gb[(gb.batsman_run >= 50) & (gb.batsman_run < 100)].shape[0]
    hundreds = gb[gb.batsman_run >= 100].shape[0]
    try:
        highest_score = gb.batsman_run.sort_values(ascending=False).head(1).values[0]
        hsindex = gb.batsman_run.sort_values(ascending=False).head(1).index[0]
        if (df[df.ID == hsindex].player_out == batsman).any():
            highest_score = str(highest_score)
        else:
            highest_score = str(highest_score) + '*'
    except:
        highest_score = gb.batsman_run.max()

    not_out = inngs - out
    mom = df[df.Player_of_Match == batsman].drop_duplicates('ID', keep='first').shape[0]
    data = {
        'innings': inngs,
        'runs': runs,
        'fours': fours,
        'sixes': sixes,
        'avg': avg,
        'strike_rate': strike_rate,
        'fifties': fifties,
        'hundreds': hundreds,
        'highest_score': highest_score,
        'not_out': not_out,
        'man_of_the_match': mom
    }
    return data

#  Utils: Complete batman record against a team
def batsman_vs_team(batsman, team, df):
    df = df[df.BowlingTeam == team].copy()
    return batsman_record(batsman, df)

# Complete batsman record
def batsman_API(batsman, balls=batter_data):
    df = balls[balls.innings.isin([1, 2])]  # Excluding Super overs
    self_record = batsman_record(batsman, df=df)
    TEAMS = matches.Team1.unique()
    against = {team: batsman_vs_team(batsman, team, df) for team in TEAMS}
    data = {
        batsman: {'all': self_record,
                  'against': against}
    }
    return json.dumps(data, cls=NpEncoder,indent=4)

bowler_data = batter_data.copy()

#  Utils: Bowler run
def bowler_run(x):
    if x[0] in ['penalty', 'legbyes', 'byes']:
        return 0
    else:
        return x[1]
bowler_data['bowler_run'] = bowler_data[['extra_type', 'total_run']].apply(bowler_run, axis=1)

#  Utils: Complete bowler wicket
def bowler_wicket(x):
    if x[0] in ['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket']:
        return x[1]
    else:
        return 0
bowler_data['isBowlerWicket'] = bowler_data[['kind', 'isWicketDelivery']].apply(bowler_wicket, axis=1)

#  Utils: Complete bowler record against all teams
def bowler_record(bowler, df):
    #if df.empty:
        #return np.nan

    df = df[df['bowler'] == bowler]
    inngs = df.ID.unique().shape[0]
    nballs = df[~(df.extra_type.isin(['wides', 'noballs']))].shape[0]
    runs = df['bowler_run'].sum()
    if nballs:
        eco = runs / nballs * 6
    else:
        eco = 0
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]

    wicket = df.isBowlerWicket.sum()
    if wicket:
        avg = runs / wicket
    else:
        avg = np.inf

    if wicket:
        strike_rate = nballs / wicket * 100
    else:
        strike_rate = np.nan

    gb = df.groupby('ID').sum()
    w3 = gb[(gb.isBowlerWicket >= 3)].shape[0]

    best_wicket = gb.sort_values(['isBowlerWicket', 'bowler_run'], ascending=[False, True])[
        ['isBowlerWicket', 'bowler_run']].head(1).values
    if best_wicket.size > 0:

        best_figure = f'{best_wicket[0][0]}/{best_wicket[0][1]}'
    else:
        best_figure = np.nan
    mom = df[df.Player_of_Match == bowler].drop_duplicates('ID', keep='first').shape[0]
    data = {
        'innings': inngs,
        'wicket': wicket,
        'economy': eco,
        'average': avg,
        'avg': avg,
        'strike_rate': strike_rate,
        'fours': fours,
        'sixes': sixes,
        'best_figure': best_figure,
        '3+W': w3,
        'man_of_the_match': mom
    }

    return data

#  Utils: Complete bowler record against a team
def bowler_vs_team(bowler, team, df):
    df = df[df.BattingTeam == team].copy()
    return bowler_record(bowler, df)

# Complete bowler record all and against
def bowler_API(bowler, balls=bowler_data):
    df = balls[balls.innings.isin([1, 2])]  # Excluding Super overs
    self_record = bowler_record(bowler, df=df)
    TEAMS = matches.Team1.unique()
    against = {team: bowler_vs_team(bowler, team, df) for team in TEAMS}
    data = {
        bowler: {'all': self_record,
                 'against': against}
    }
    return json.dumps(data, cls=NpEncoder,indent=4)