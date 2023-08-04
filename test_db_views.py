import unittest
from app import app, db
from models import User, Location, City, State, Favorite


class FavoritesAPITestCase(unittest.TestCase):
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

    def test_adddata_route(self):
        """Test the /adddata route."""
        # Create a test user and add to the database
        user = User.signup(username='testuser', first_name='Test', last_name='User',
                           email='test@example.com', password='testpassword')
        db.session.commit()

        # Log in the user
        with self.app.session_transaction() as sess:
            sess['curr_user'] = user.id

        # Create a test city and state and add them to the database
        state = State(name='Test State')
        db.session.add(state)
        db.session.commit()
        city = City(name='Test City', state_id=state.id)
        db.session.add(city)
        db.session.commit()

        # Send a POST request to the /adddata route with JSON data
        data = {
            'state': 'Test State',
            'city': 'Test City',
            'address': '123 Test St',
            'zipcode': '12345',
            'bedrooms': 2
        }
        response = self.app.post('/adddata', json=data)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains the JSON data sent in the request
        self.assertIn(b'"state":"Test State"', response.data)
        self.assertIn(b'"city":"Test City"', response.data)
        self.assertIn(b'"address":"123 Test St"', response.data)
        self.assertIn(b'"zipcode":"12345"', response.data)
        self.assertIn(b'"bedrooms":2', response.data)

    def test_favorites_route_authenticated_user(self):
        """Test the /favorites route for an authenticated user."""
        # Create a test user and add to the database
        user = User.signup(username='testuser', first_name='Test', last_name='User',
                           email='test@example.com', password='testpassword')
        db.session.commit()

        # Log in the user
        with self.app.session_transaction() as sess:
            sess['curr_user'] = user.id

        # Send a GET request to the /favorites route
        response = self.app.get('/favorites')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains the favorites map
        # You can customize this assertion based on your actual template and data
        self.assertIn(b'Favorites Map', response.data)

    def test_favorites_route_unauthenticated_user(self):
        """Test the /favorites route for an unauthenticated user."""
        # Send a GET request to the /favorites route without logging in
        response = self.app.get('/favorites')

        # Assert that the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)
        # Assert that the response redirects to the login page
        self.assertIn('/login', response.location)

    def test_favorites_add_route(self):
        """Test the /favorites/add route."""
        # Create a test user and add to the database
        user = User.signup(username='testuser', first_name='Test', last_name='User',
                           email='test@example.com', password='testpassword')
        db.session.commit()

        # Log in the user
        with self.app.session_transaction() as sess:
            sess['curr_user'] = user.id

        # Create a test city and state and add them to the database
        state = State(name='Test State')
        db.session.add(state)
        db.session.commit()
        city = City(name='Test City', state_id=state.id)
        db.session.add(city)
        db.session.commit()

        # Create a test location and add to the database
        location = Location(
            street_address='456 Test St', zip_code='67890', city_id=city.id, bedrooms=3, user_id=user.id)
        db.session.add(location)
        db.session.commit()

        # Send a POST request to the /favorites/add route with JSON data
        data = {'average': 2000, 'address': '456 Test St'}
        response = self.app.post('/favorites/add', json=data)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        favorite = Favorite.query.filter_by(
            user_id=user.id, location_id=location.id).first()

        # Assert that the Favorite entry exists
        self.assertIsNotNone(favorite)

        # Assert that the average rent matches the expected value
        self.assertEqual(favorite.rent_average, 2000)

    def test_favorites_data_route(self):
        """Test the /favorites/data route."""
        # Create a test user and add to the database
        user = User.signup(username='testuser', first_name='Test', last_name='User',
                           email='test@example.com', password='testpassword')
        db.session.commit()

        # Log in the user
        with self.app.session_transaction() as sess:
            sess['curr_user'] = user.id

        # Create a test city and state and add them to the database
        state = State(name='Test State')
        state_2 = State(name='Test State2')
        db.session.add_all([state, state_2])
        db.session.commit()
        city = City(name='Test City', state_id=state.id)
        city_2 = City(name='Test City2', state_id=state_2.id)
        db.session.add_all([city, city_2])
        db.session.commit()
        # Create test favorites and locations and add them to the database
        location1 = Location(
            street_address='456 Test St', zip_code='67890', city_id=city.id, bedrooms=3, user_id=user.id)
        location2 = Location(
            street_address='789 Test St', zip_code='12345', city_id=city_2.id, bedrooms=2, user_id=user.id)
        db.session.add_all([location1, location2])
        db.session.commit()

        favorite1 = Favorite(
            rent_average=2000, user_id=user.id, location_id=location1.id)
        favorite2 = Favorite(
            rent_average=3000, user_id=user.id, location_id=location2.id)
        db.session.add_all([favorite1, favorite2])
        db.session.commit()

        # Send a GET request to the /favorites/data route
        response = self.app.get('/favorites/data')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains the favorite addresses and data
        # You can customize this assertion based on your actual response data
        self.assertIn(b'456 Test St 67890 Bedrooms: 3', response.data)
        self.assertIn(b'789 Test St 12345 Bedrooms: 2', response.data)


if __name__ == '__main__':
    unittest.main()
