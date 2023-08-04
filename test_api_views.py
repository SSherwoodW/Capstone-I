import unittest
from app import app, db
from models import User


class APITestCase(unittest.TestCase):
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

    def test_api_geocode(self):
        """Test the /api/geocode route."""
        # Create a test user and add to the database
        user = User.signup(username='testuser', first_name='Test', last_name='User',
                           email='test@example.com', password='testpassword')
        db.session.commit()

        # Log in the user
        with self.app.session_transaction() as sess:
            sess['curr_user'] = user.id

        # Send a POST request to the /api/geocode route with JSON data
        data = {'address': '630 S Curtis Ave, Tucson, AZ, 85719'}
        response = self.app.post('/api/geocode', json=data)
        print(response.data)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains the coordinates
        self.assertIn(b'"lat":32.21399', response.data)
        self.assertIn(b'"lng":-110.95039', response.data)

    def test_api_rental_data(self):
        """Test the /api/rental-data route."""
        # Send a POST request to the /api/rental-data route with JSON data
        test_zip = 90210
        data = {'zipcode': '90210'}
        response = self.app.post('/api/rental-data', json=data)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Assert that the response is returning the applicable data
        self.assertIn(b'{"id":"90210","rentalData"', response.data)

    def test_api_rental_data_invalid_zipcode(self):
        """Test the /api/rental-data route with an invalid zipcode."""
        # Send a POST request to the /api/rental-data route with an invalid zipcode
        data = {'zipcode': 'invalid_zipcode'}
        response = self.app.post('/api/rental-data', json=data)
        print(response.data)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'error', response.data)
        # Assert that the response contains an error message (if applicable)
        # You can adjust this assertion based on the actual response data structure
        # For example, if the error message is returned as JSON, you can do something like:
        # self.assertIn(b'"error": "Invalid zipcode"', response.data)


if __name__ == '__main__':
    unittest.main()
