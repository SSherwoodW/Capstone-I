from app import app
import os
from unittest import TestCase
from sqlalchemy import exc

from models import User, Location, State, City, connect_db, db

os.environ['DATABASE_URL'] = "postgresql:///movein-test"

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserModelTestCase(TestCase):
    """Test user and locations models."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "Test", "Case",
                         "email1@email.com", "password")
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2", "Test2", "Case2",
                         "email2@email.com", "password")
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            first_name="Scott",
            last_name="Waller",
            password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()

        # User should have no location
        self.assertEqual(u.location, None)

    ####
    #
    # Location tests
    #
    ####

    def test_location_models(self):
        state1 = State(name="Teststate")
        sid1 = 111
        state1.id = sid1
        db.session.add(state1)
        db.session.commit()

        city1 = City(name="Testcity", state_id=sid1)
        cid1 = 222
        city1.id = cid1
        city1.state_id = state1.id

        db.session.add(city1)
        db.session.commit()

        l1 = Location(street_address="111 Test Ave", zip_code=12345,
                      city_id=city1.id, bedrooms=1, user_id=self.u1.id)
        lid1 = 1
        l1.id = lid1
        db.session.add(l1)
        db.session.commit()

        city1 = City.query.get(cid1)
        state1 = State.query.get(sid1)
        l1 = Location.query.get(lid1)

        self.city1 = city1
        self.state1 = state1
        self.l1 = l1

        # Test that table relationships work properly
        self.assertEqual(self.l1.city_id, 222)
        self.assertEqual(self.city1.state_id, 111)
        self.assertEqual(self.l1.user_id, 1111)

    ####
    #
    # Signup Tests
    #
    ####
    def test_valid_signup(self):
        u_test = User.signup(
            "testtesttest", "test", "case", "testtest@test.com", "password")
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertEqual(u_test.email, "testtest@test.com")
        self.assertNotEqual(u_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test", "case",
                              "test@test.com", "password")
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", "test", "case", None, "password")
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "test", "case",
                        "email@email.com", "")

        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "test", "case",
                        "email@email.com", None)

    ####
    #
    # Authentication Tests
    #
    ####
    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))
