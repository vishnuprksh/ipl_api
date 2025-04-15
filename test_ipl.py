import unittest
import json
import pandas as pd
import numpy as np
import ipl
from ipl import NpEncoder


class IPLFunctionsTests(unittest.TestCase):
    """Test cases for IPL module functions"""

    def setUp(self):
        """Set up test environment before each test"""
        # Load the dataset samples for testing
        # We'll use a smaller sample dataset for testing
        self.matches_sample = ipl.matches.head(50)
        self.balls_sample = ipl.balls.head(100)
        self.ball_withmatch_sample = ipl.ball_withmatch.head(100)
        self.batter_data_sample = ipl.batter_data.head(100)
        self.bowler_data_sample = ipl.bowler_data.head(100)
        
    def test_teams_played_ipl(self):
        """Test teams_played_ipl function"""
        result = ipl.teams_played_ipl()
        self.assertIsInstance(result, dict)
        self.assertIn('total_number_of_teams', result)
        self.assertIn('teams', result)
        self.assertIsInstance(result['teams'], list)
        self.assertTrue(len(result['teams']) > 0)
        # Verify specific teams exist in the result
        common_teams = ['Mumbai Indians', 'Chennai Super Kings', 'Royal Challengers Bangalore']
        for team in common_teams:
            self.assertIn(team, result['teams'])

    def test_team1_vs_team2_valid(self):
        """Test team1_vs_team2 function with valid teams"""
        team1 = 'Mumbai Indians'
        team2 = 'Chennai Super Kings'
        result = ipl.team1_vs_team2(team1, team2)
        self.assertIsInstance(result, dict)
        self.assertIn('total_matches_played', result)
        self.assertIn('team1_won', result)
        self.assertIn('team2_won', result)
        self.assertIn('no_result', result)
        
    def test_team1_vs_team2_invalid(self):
        """Test team1_vs_team2 function with invalid team"""
        team1 = 'Invalid Team'
        team2 = 'Chennai Super Kings'
        result = ipl.team1_vs_team2(team1, team2)
        self.assertEqual(result, {'response': 'Invalid team name'})

    def test_all_record_valid(self):
        """Test all_record function with valid team"""
        team = 'Chennai Super Kings'
        result = ipl.all_record(team)
        self.assertIsInstance(result, dict)
        self.assertIn('matchesplayed', result)
        self.assertIn('won', result)
        self.assertIn('loss', result)
        self.assertIn('noResult', result)
        self.assertIn('title', result)
        
    def test_all_record_invalid(self):
        """Test all_record function with invalid team"""
        team = 'Invalid Team'
        result = ipl.all_record(team)
        self.assertEqual(result, {'response': 'Invalid team name'})

    def test_team_api(self):
        """Test team_api function"""
        team = 'Chennai Super Kings'
        result = ipl.team_api(team)
        self.assertIsInstance(result, str)
        data = json.loads(result)
        self.assertIn(team, data)
        self.assertIn('overall', data[team])
        self.assertIn('against', data[team])
        
    def test_batsman_record(self):
        """Test batsman_record function"""
        # Use a common player that's likely in the dataset
        batsman = 'MS Dhoni'
        # Filter data for this batsman for testing - using 'batter' column not 'batsman'
        batsman_data = ipl.batter_data[ipl.batter_data['batter'] == batsman]
        if not batsman_data.empty:  # Only run test if player is in dataset
            result = ipl.batsman_record(batsman, batsman_data)
            self.assertIsInstance(result, dict)
            self.assertIn('innings', result)
            self.assertIn('runs', result)
            self.assertIn('avg', result)
            self.assertIn('strike_rate', result)
        
    def test_batsman_api(self):
        """Test batsman_api function"""
        batsman = 'MS Dhoni'
        result = ipl.batsman_api(batsman)
        self.assertIsInstance(result, str)
        data = json.loads(result)
        self.assertIn(batsman, data)
        self.assertIn('all', data[batsman])
        self.assertIn('against', data[batsman])
        
    def test_bowler_record(self):
        """Test bowler_record function"""
        # Use a common bowler that's likely in the dataset
        bowler = 'Harbhajan Singh'
        # Filter data for this bowler for testing
        bowler_data = ipl.bowler_data[ipl.bowler_data['bowler'] == bowler]
        if not bowler_data.empty:  # Only run test if player is in dataset
            result = ipl.bowler_record(bowler, bowler_data)
            self.assertIsInstance(result, dict)
            self.assertIn('innings', result)
            self.assertIn('wicket', result)
            self.assertIn('economy', result)
            self.assertIn('strike_rate', result)
        
    def test_bowler_api(self):
        """Test bowler_api function"""
        bowler = 'RA Jadeja'
        result = ipl.bowler_api(bowler)
        self.assertIsInstance(result, str)
        data = json.loads(result)
        self.assertIn(bowler, data)
        self.assertIn('all', data[bowler])
        self.assertIn('against', data[bowler])
        
    def test_np_encoder(self):
        """Test NpEncoder class"""
        # Create some numpy data types and test encoding
        test_data = {
            'int': np.int64(42),
            'float': np.float64(3.14),
            'array': np.array([1, 2, 3])
        }
        # This should not raise any exception
        json_data = json.dumps(test_data, cls=NpEncoder)
        decoded = json.loads(json_data)
        self.assertEqual(decoded['int'], 42)
        self.assertAlmostEqual(decoded['float'], 3.14)
        self.assertEqual(decoded['array'], [1, 2, 3])


if __name__ == '__main__':
    unittest.main()