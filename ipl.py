"""
IPL Data Analysis Module

This module provides functions for analyzing IPL (Indian Premier League) cricket data.
It includes various functions to retrieve team records, player records, and head-to-head statistics.

Classes:
    NpEncoder: Custom JSON encoder for handling NumPy data types.

Functions:
    teams_played_ipl: Returns information about the teams that have played in the IPL so far.
    team1_vs_team2: Returns the track record of Team 1 against Team 2 in IPL matches.
    all_record: Returns the record of a team against all other teams in IPL matches.
    team_api: Retrieves team statistics and records from the provided matches data.
    batsman_record: Computes statistics for a given batsman based on the provided
        cricket match data.
    batsman_vs_team: Retrieves the record of a batsman against a specific team.
    batsman_api: Retrieves the API data for a batsman.
    bowler_run: Calculates the number of runs conceded by a bowler for a given delivery.

Usage Example:

    # Retrieve information about the teams that have played in the IPL so far
    team_info = teams_played_ipl()
    print(json.dumps(team_info, indent=4))

    # Retrieve the track record of Team 1 against Team 2
    team1 = 'Mumbai Indians'
    team2 = 'Chennai Super Kings'
    record = team1_vs_team2(team1, team2)
    print(json.dumps(record, indent=4))

    # Retrieve the overall record of a team against all other teams
    team = 'Chennai Super Kings'
    team_record = all_record(team)
    print(json.dumps(team_record, indent=4))

    # Retrieve team statistics and records
    team = 'Chennai Super Kings'
    team_stats = team_api(team)
    print(team_stats)

    # Retrieve batsman statistics and records
    batsman_stats = batsman_api('MS Dhoni', balls)
    print(batsman_stats)
"""


import json
import pandas as pd
import numpy as np

# Importing Datasets
matches = pd.read_csv('datasets/ipl.csv')
balls = pd.read_csv('datasets/IPL_bowling_stats.csv')


class NpEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that extends the functionality of the
    default JSONEncoder to handle NumPy data types.

    This class is designed to be used as an encoder when converting NumPy objects to JSON format.

    The encoder handles the following NumPy types:
    - np.integer: Converted to int.
    - np.floating: Converted to float.
    - np.ndarray: Converted to a Python list.

    All other types are handled by the default JSONEncoder.

    Usage example:
    ```
    import json
    import numpy as np

    # Create an instance of the NpEncoder
    encoder = NpEncoder()

    # Convert a NumPy object to JSON using the custom encoder
    data = np.array([1, 2, 3])
    json_data = json.dumps(data, cls=encoder)
    ```

    Reference: https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.number
    """

    def default(self, o):
        """
        Override the default method of JSONEncoder to handle additional NumPy data types.

        Args:
            obj: The object to encode.

        Returns:
            The encoded object.

        Raises:
            TypeError: If the object type is not supported by the encoder.
        """
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super(NpEncoder, self).default(o)


ball_withmatch = balls.merge(matches, on='ID', how='inner').copy()
ball_withmatch['BowlingTeam'] = ball_withmatch.Team1 + ball_withmatch.Team2
ball_withmatch['BowlingTeam'] = ball_withmatch[['BowlingTeam', 'BattingTeam']].apply(
    lambda x: x.values[0].replace(x.values[1], ''), axis=1)
batter_data = ball_withmatch[np.append(
    balls.columns.values, ['BowlingTeam', 'Player_of_Match'])]


# Teams that have played IPL so far
def teams_played_ipl():
    """
    Returns information about the teams that have played in the IPL so far.

    Returns:
        dict: Dictionary containing the total number of teams and a list of team names.
    """
    total_teams = np.union1d(matches['Team1'], matches['Team2'])
    data = {
        'total_number_of_teams': total_teams.size,
        'teams': list(total_teams)
    }
    return data


teams = np.union1d(matches['Team1'], matches['Team2'])
# Track record of each team against each other


def team1_vs_team2(team1, team2):
    """
    Returns the track record of Team 1 against Team 2 in IPL matches.

    Args:
        team1 (str): Name of Team 1.
        team2 (str): Name of Team 2.

    Returns:
        dict: Dictionary containing the total matches played, number of wins for Team 1,
              number of wins for Team 2, and the number of matches with no result.
    """
    if team1 in teams and team2 in teams:
        temp_df = matches[((matches['Team1'] == team1) & (matches['Team2'] == team2))
                          | ((matches['Team1'] == team2) & (matches['Team2'] == team1))]
        total_matches_played = temp_df.shape[0]
        team1_won = temp_df[temp_df['WinningTeam'] == team1].shape[0]
        team2_won = temp_df[temp_df['WinningTeam'] == team2].shape[0]
        no_result = total_matches_played - (team1_won + team2_won)

        data = {
            'total_matches_played': total_matches_played,
            'team1_won': team1_won,
            'team2_won': team2_won,
            'no_result': no_result
        }
        return data
    return {'response': 'Invalid team name'}

# Returns record of a team against all other teams


def all_record(team):
    """
    Returns the record of a team against all other teams in IPL matches.

    Args:
        team (str): Name of the team.

    Returns:
        dict: Dictionary containing the number of matches played, number of wins, number of losses,
              number of matches with no result, and number of titles won by the team.
    """
    if team in teams:
        df_matches = matches[(matches['Team1'] == team) | (
            matches['Team2'] == team)].copy()
        match_played = df_matches.shape[0]
        won = df_matches[df_matches.WinningTeam == team].shape[0]
        no_result = df_matches[df_matches.WinningTeam.isnull()].shape[0]
        loss = match_played - won - no_result
        no_of_title = df_matches[(df_matches.MatchNumber == 'Final') &
                                 (df_matches.WinningTeam == team)].shape[0]
        return {'matchesplayed': match_played,
                'won': won,
                'loss': loss,
                'noResult': no_result,
                'title': no_of_title}

    return {
        'response': 'Invalid team name'
    }

# Utils: Complete team record


def team_api(team, match=matches):
    """
    Retrieves team statistics and records from the provided matches data.

    This function generates team statistics and records based on the matches data.
     It calculates the overall record
    for the given team, as well as the head-to-head records against all other teams.

    Args:
        team (str): The name of the team for which statistics are to be generated.
        matches (DataFrame): The matches data containing information
        about the matches (default: matches).

    Returns:
        str: A JSON string containing the team statistics and records.

    Raises:
        None.

    Example:
        ```
        import json

        # Retrieve team statistics for "TeamA"
        team_stats = team_API("TeamA")

        # Print the JSON string
        print(team_stats)
        ```

    Note:
        - The matches data should be provided as a DataFrame.
        - The matches DataFrame should contain columns 'Team1' and 'Team2' representing
            the team names.

    """
    match[(match['Team1'] == team) | (match['Team2'] == team)].copy()
    self_record = all_record(team)
    unique_teams = match.Team1.unique()
    against = {team2: team1_vs_team2(team, team2) for team2 in unique_teams}
    data = {team: {'overall': self_record,
                   'against': against}}
    return json.dumps(data, cls=NpEncoder, indent=4)


# Returns batsman record
def batsman_record(batsman, data_frame):
    """
    Compute statistics for a given batsman based on the provided dataframe of cricket matches.

    Args:
        batsman: A string with the name of the batsman to compute statistics for.
        df: A pandas DataFrame with columns 
            'ID', 'batsman', 'player_out', 'batsman_run', 'non_boundary', and 'extra_type',
            containing the records of all batsmen in all cricket matches.

    Returns:
        A dictionary with the following keys:
        - 'out': An integer with the number of times the batsman got out.
        - 'innings': An integer with the number of innings the batsman played.
        - 'runs': An integer with the total runs scored by the batsman.
        - 'fours': An integer with the number of fours scored by the batsman.
        - 'sixes': An integer with the number of sixes scored by the batsman.
        - 'average': A float with the batting average of the batsman 
            (runs/out), or infinity if out=0.
        - 'strike_rate': A float with the batting strike
            rate of the batsman (runs/balls*100), or 0 if balls=0.
        - 'fifties': An integer with the number of half-centuries scored by the batsman.
        - 'hundreds': An integer with the number of centuries scored by the batsman.
        - 'highest_score': A string with the highest score of the batsman in a
            single innings, followed by a '*' if
          the batsman was not out in that innings, or the highest score
          if the player was out in every innings.
    """
    if data_frame.empty:
        return pd.NaT

    # Get the number of innings played.
    inngs = data_frame.ID.unique().shape[0]

    # Get the number of runs scored.
    runs = data_frame.batsman_run.sum()

    # Get the number of fours and sixes hit.
    fours = data_frame[(data_frame.batsman_run == 4) & (
        data_frame.non_boundary == 0)].shape[0]
    sixes = data_frame[(data_frame.batsman_run == 6) & (
        data_frame.non_boundary == 0)].shape[0]

    # Get the batting average.
    if inngs:
        avg = runs / inngs
    else:
        avg = pd.NaT

    # Get the strike rate.
    if inngs:
        strike_rate = runs / inngs * 100
    else:
        strike_rate = pd.NaT

    # Get the number of half-centuries and centuries scored.
    fifties = data_frame[(data_frame.batsman_run >= 50) &
                         (data_frame.batsman_run < 100)].shape[0]
    hundreds = data_frame[data_frame.batsman_run >= 100].shape[0]

    # Get the highest score.
    highest_score = data_frame.batsman_run.sort_values(
        ascending=False).head(1).values[0]

    # Get the number of times the batsman was not out.
    not_out = inngs - data_frame[data_frame.player_out == batsman].shape[0]

    # Get the number of times the batsman was awarded the Man of the Match.
    mom = data_frame[data_frame.Player_of_Match ==
                     batsman].drop_duplicates('ID', keep='first').shape[0]

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
def batsman_vs_team(batsman, team, input_df):
    """
    Retrieves the record of a batsman against a specific team.

    This function calculates and returns the record of a batsman against
        a specific team based on the provided DataFrame.
    It filters the DataFrame based on the bowling team and then calls the
        'batsman_record' function to calculate the
    batsman's record against the given team.

    Args:
        batsman (str): The name of the batsman for whom the record is to be retrieved.
        team (str): The name of the team against which the batsman's record is to be calculated.
        df (DataFrame): The DataFrame containing the match data.

    Returns:
        float: The record of the batsman against the specified team.

    Raises:
        None.

    Example:
        ```
        # Create a DataFrame containing match data
        match_data = ...

        # Retrieve the record of batsman 'John' against 'TeamA'
        record = batsman_vs_team('John', 'TeamA', match_data)

        # Print the record
        print(record)
        ```

    Note:
        - The DataFrame should contain a column named 'BowlingTeam' representing the bowling team.
        - The 'batsman_record' function is used to calculate the
            batsman's record against the specified team.

    """
    input_df = input_df[input_df.BowlingTeam == team].copy()
    return batsman_record(batsman, input_df)


# Complete batsman record
def batsman_api(batsman, total_balls=batter_data):
    """
    Retrieves the API data for a batsman.

    This function calculates and returns the API data for a batsman
        based on the provided DataFrame containing ball data.
    It retrieves the batsman's record, as well as the record against
        each team, using the 'batsman_record' and 'batsman_vs_team'
        functions, respectively.

    Args:
        batsman (str): The name of the batsman for whom the API data is to be retrieved.
        balls (DataFrame): The DataFrame containing the ball data.

    Returns:
        str: The API data for the batsman, serialized as a JSON string.

    Raises:
        None.

    Example:
        ```
        # Create a DataFrame containing ball data
        ball_data = ...

        # Retrieve the API data for batsman 'John'
        api_data = batsman_api('John', balls=ball_data)

        # Print the API data
        print(api_data)
        ```

    Note:
        - The DataFrame should contain a column named 'innings'
            representing the innings of each ball.
        - The 'batsman_record' and 'batsman_vs_team' functions are used
            to calculate the batsman's record and the record against each team, respectively.

    """
    # Get the batsman's record.
    ball_df = total_balls[total_balls.innings.isin([1, 2])]  # Excluding Super overs
    self_record = batsman_record(batsman, data_frame=ball_df)

    # Get the batsman's record against each team.
    team_unique = matches.Team1.unique()
    against = {team: batsman_vs_team(batsman, team, ball_df)
               for team in team_unique}

    # Return the JSON object.
    data = {
        batsman: {'all': self_record,
                  'against': against}
    }
    return json.dumps(data, cls=NpEncoder, indent=4)


bowler_data = batter_data.copy()

#  Utils: Bowler run


def bowler_run(tup_x):
    """
    Calculates the number of runs conceded by a bowler for a given delivery.

    Parameters:
        tup_x (tuple): A tuple containing the type of delivery and
            the total runs scored off that delivery.

    Returns:
        int: The number of runs conceded by the bowler.s
        Returns 0 if the delivery type is 'penalty', 'legbyes', or 'byes'.

    Example:
        bowler_run(('wides', 1))  # Returns 1
        bowler_run(('byes', 2))  # Returns 0
    """
    if tup_x.iloc[0] in ['penalty', 'legbyes', 'byes']:
        return 0
    return tup_x.iloc[1]


bowler_data['bowler_run'] = bowler_data[[
    'extra_type', 'total_run']].apply(bowler_run, axis=1)

#  Utils: Complete bowler wicket


def bowler_wicket(tup_x):
    """
    Determines whether a bowler has taken a wicket on a given delivery.

    Parameters:
        x (tuple): A tuple containing the type of dismissal and a binary indicator
        (1 for wicket, 0 for no wicket).

    Returns:
        int: The wicket count (1 if the delivery resulted in a wicket, 0 otherwise).

    Example:
        bowler_wicket(('caught', 1))  # Returns 1
        bowler_wicket(('run out', 0))  # Returns 0
    """
    if tup_x.iloc[0] in ['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket']:
        return tup_x.iloc[1]
    return 0


bowler_data['isBowlerWicket'] = bowler_data[[
    'kind', 'isWicketDelivery']].apply(bowler_wicket, axis=1)

#  Utils: Complete bowler record against all teams


def bowler_record(bowler, match_df):
    """
    Args:
        - bowler_name (str): Name of the bowler for whom the statistics are to be calculated.
        - match_df (pd.DataFrame): Dataframe containing the cricket match data.

    Returns:
        - A dictionary containing the following bowling statistics of the bowler:
        - innings (int): Number of innings bowled by the bowler.
        - wicket (int): Total number of wickets taken by the bowler.
        - economy (float): Bowling economy rate of the bowler.
        - average (float): Bowling average of the bowler.
        - strike_rate (float): Bowling strike rate of the bowler.
        - fours (int): Total number of fours conceded by the bowler.
        - sixes (int): Total number of sixes conceded by the bowler.
        - best_figure (str): Best bowling figure of the bowler in terms
            of wickets taken and runs conceded.
        - 3+W (int): Total number of matches in which the bowler took 3 or more wickets.
        - man_of_the_match (int): Total number of times the bowler
            was awarded the Man of the Match award.
    """

    match_df = match_df[match_df['bowler'] == bowler]
    inngs = match_df.ID.unique().shape[0]
    nballs = match_df[~(match_df.extra_type.isin(['wides', 'noballs']))].shape[0]
    runs = match_df['bowler_run'].sum()
    if nballs:
        eco = runs / nballs * 6
    else:
        eco = 0
    fours = match_df[(match_df.batsman_run == 4) & (match_df.non_boundary == 0)].shape[0]
    sixes = match_df[(match_df.batsman_run == 6) & (match_df.non_boundary == 0)].shape[0]

    wicket = match_df.isBowlerWicket.sum()
    if wicket:
        avg = runs / wicket
    else:
        avg = np.inf

    if wicket:
        strike_rate = nballs / wicket * 100
    else:
        strike_rate = np.nan

    group_by_df = match_df.groupby('ID').sum()
    three_wicket_plus = group_by_df[(group_by_df.isBowlerWicket >= 3)].shape[0]

    best_wicket = (group_by_df.sort_values(['isBowlerWicket', 'bowler_run'],
                    ascending=[False, True])[['isBowlerWicket', 'bowler_run']].head(1).values)
    if best_wicket.size > 0:

        best_figure = f'{best_wicket[0][0]}/{best_wicket[0][1]}'
    else:
        best_figure = np.nan
    mom = match_df[match_df.Player_of_Match == bowler].drop_duplicates(
        'ID', keep='first').shape[0]
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
        '3+W': three_wicket_plus,
        'man_of_the_match': mom
    }

    return data


#  Utils: Complete bowler record against a team
def bowler_vs_team(bowler, team, data_frame):
    """
    Calculates the performance statistics for a given bowler against
    a specific team based on the provided DataFrame.

    Parameters:
        bowler (str): Name of the bowler.
        team (str): Name of the team.
        df (pd.DataFrame): DataFrame containing the match data.

    Returns:
        dict: A dictionary containing the performance statistics of
        the bowler against the team.

    Example:
        df = pd.DataFrame(...)  # DataFrame with match data
        bowler_stats = bowler_vs_team('Bowler Name', 'Team Name', df)
        print(bowler_stats)

    """

    # Filter the DataFrame for matches where the specified team was batting
    team_df = data_frame[data_frame['BattingTeam'] == team].copy()

    # Calculate the performance statistics for the specified bowler against the team
    bowler_stats = bowler_record(bowler, team_df)

    return bowler_stats


# Complete bowler record all and against
def bowler_api(bowler, total_balls=bowler_data):
    """
    Generates an API response containing the performance statistics of a bowler.

    Parameters:
        bowler (str): Name of the bowler.
        balls (pd.DataFrame): DataFrame containing the ball-by-ball data. Defaults to `bowler_data`.

    Returns:
        str: JSON-formatted API response containing the performance statistics of the bowler.

    Example:
        response = bowler_API('Bowler Name', total_balls=bowler_data)
        print(response)

    """

    # Filter the DataFrame to exclude super overs
    data_frame = total_balls[total_balls['innings'].isin([1, 2])]

    # Retrieve the performance statistics of the bowler against all teams
    self_record = bowler_record(bowler, match_df=data_frame)

    # Get the unique teams from the matches data
    unique_teams = matches['Team1'].unique()

    # Calculate the performance statistics of the bowler against each team
    against = {team: bowler_vs_team(bowler, team, data_frame) for team in unique_teams}

    # Create the response data in the required format
    data = {
        bowler: {
            'all': self_record,
            'against': against
        }
    }

    # Convert the data to JSON format
    response = json.dumps(data, cls=NpEncoder, indent=4)

    return response
