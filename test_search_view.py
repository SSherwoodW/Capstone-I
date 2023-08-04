# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_search_views.py

import unittest
from app import app, db
from models import User


class SearchViewTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()

    def test_search_view_authenticated_user(self):
        """Test if the search view is accessible for an authenticated user."""
        # Create a test user and add to the database
        user = User.signup(username='testuser', first_name='Test', last_name='User',
                           email='test@example.com', password='testpassword')
        db.session.commit()

        # Log in the user
        with self.app.session_transaction() as sess:
            sess['curr_user'] = user.id

        # Send a GET request to the /search route
        response = self.app.get('/search')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains the search form
        self.assertIn(b'<form', response.data)
        self.assertIn(
            b'<input class="form-control" id="address" name="address"', response.data)
        self.assertIn(b'form="address-lookup-form"', response.data)

    def test_search_view_unauthenticated_user(self):
        """Test if the search view redirects to login for an unauthenticated user."""
        # Send a GET request to the /search route without logging in
        response = self.app.get('/search')

        # Assert that the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)
        # Assert that the response redirects to the login page
        self.assertIn('/login', response.location)

    def test_search_view_no_user(self):
        """Test if the search view shows a flash message for unauthenticated access."""
        # Send a GET request to the /search route without logging in
        response = self.app.get('/search', follow_redirects=True)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains a flash message
        self.assertIn(b'Access unauthorized. Please log in.', response.data)
        # Assert that the response contains the login link
        self.assertIn(
            b'<button class="btn btn-primary btn-block btn-lg">Log in</button>', response.data)


if __name__ == '__main__':
    unittest.main()
