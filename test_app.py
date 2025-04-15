import unittest
import json
import os
from app import app, db, User
from passlib.hash import sha256_crypt
import config
from unittest.mock import patch


class IPLAPITests(unittest.TestCase):
    """Test cases for IPL API application"""

    def setUp(self):
        """Set up test environment before each test"""
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Create tables
        db.create_all()
        
        # Create a test user
        test_user = User(
            name='Test User',
            email='test@example.com',
            password=sha256_crypt.hash('testpassword')
        )
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email='test@example.com', password='testpassword'):
        """Helper method to login a user"""
        return self.app.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        """Helper method to logout a user"""
        return self.app.get('/logout', follow_redirects=True)

    # Authentication Tests
    def test_login_page(self):
        """Test that login page loads correctly"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_login_logout(self):
        """Test user login and logout functionality"""
        # Test login with correct credentials
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
        
        # Test logout
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.login(email='test@example.com', password='wrongpassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid', response.data)

    def test_register(self):
        """Test user registration"""
        response = self.app.post('/register', data=dict(
            name='New User',
            email='new@example.com',
            password='newpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify user is in database
        user = User.query.filter_by(email='new@example.com').first()
        self.assertIsNotNone(user)

    def test_invalid_email_registration(self):
        """Test registration with invalid email format"""
        response = self.app.post('/register', data=dict(
            name='Invalid Email',
            email='invalid-email',
            password='password'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid Email', response.data)

    # API Endpoint Tests - Teams
    def test_teams_played_ipl(self):
        """Test the teams_played_ipl API endpoint"""
        self.login()
        response = self.app.get('/api/teams-played-ipl')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('result', data)
        self.assertIn('teams', data['result'])
        self.assertIn('total_number_of_teams', data['result'])
        self.assertIsNone(data['error'])

    def test_team1_vs_team2(self):
        """Test the team1_vs_team2 API endpoint with valid teams"""
        self.login()
        response = self.app.get('/api/team1-vs-team2?team1=Mumbai%20Indians&team2=Chennai%20Super%20Kings')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('result', data)
        self.assertIn('total_matches_played', data['result'])
        self.assertIsNone(data['error'])

    def test_team1_vs_team2_invalid(self):
        """Test the team1_vs_team2 API endpoint with invalid team"""
        self.login()
        response = self.app.get('/api/team1-vs-team2?team1=Invalid%20Team&team2=Chennai%20Super%20Kings')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('result', data)
        self.assertEqual(data['result'], {'response': 'Invalid team name'})

    def test_record_against_all_teams(self):
        """Test the record_against_all_teams API endpoint"""
        self.login()
        response = self.app.get('/api/record-against-all-teams?team=Chennai%20Super%20Kings')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('result', data)
        self.assertIn('matchesplayed', data['result'])
        self.assertIn('won', data['result'])
        self.assertIsNone(data['error'])

    def test_record_against_each_team(self):
        """Test the record_against_each_team API endpoint"""
        self.login()
        response = self.app.get('/api/record-against-each-team?team=Chennai%20Super%20Kings')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('result', data)
        # Parse the JSON string to object
        result_data = json.loads(data['result'])
        self.assertIn('Chennai Super Kings', result_data)
        self.assertIsNone(data['error'])

    # API Endpoint Tests - Players
    def test_batsman_record(self):
        """Test the batsman_record API endpoint"""
        self.login()
        response = self.app.get('/api/batsman-record?batsman=MS%20Dhoni')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('result', data)
        # Parse the JSON string to object
        result_data = json.loads(data['result'])
        self.assertIn('MS Dhoni', result_data)
        self.assertIsNone(data['error'])

    def test_bowling_record(self):
        """Test the bowling_record API endpoint"""
        self.login()
        response = self.app.get('/api/bowling-record?bowler=RA%20Jadeja')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('result', data)
        # Parse the JSON string to object
        result_data = json.loads(data['result'])
        self.assertIn('RA Jadeja', result_data)
        self.assertIsNone(data['error'])

    # Dashboard Routes Tests
    def test_dashboard_authenticated(self):
        """Test access to dashboard when authenticated"""
        self.login()
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

    def test_dashboard_unauthenticated(self):
        """Test access to dashboard when not authenticated"""
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirects to login

    def test_teams_dashboard_authenticated(self):
        """Test access to teams dashboard when authenticated"""
        self.login()
        response = self.app.get('/teams_dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Teams', response.data)

    def test_head_to_head_authenticated(self):
        """Test access to head to head comparison when authenticated"""
        self.login()
        response = self.app.get('/head_to_head')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Head to Head', response.data)

    # Error Handling Tests
    def test_page_not_found(self):
        """Test 404 error handler"""
        response = self.app.get('/nonexistent-page')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404', response.data)

    # Exception Handling Tests
    @patch('ipl.teams_played_ipl')
    def test_exception_handler(self, mock_teams_played):
        """Test exception handling in API endpoints"""
        mock_teams_played.side_effect = Exception("Test exception")
        self.login()
        response = self.app.get('/api/teams-played-ipl')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Test exception')


if __name__ == '__main__':
    unittest.main()