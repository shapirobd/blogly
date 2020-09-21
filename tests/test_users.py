from unittest import TestCase
from app import app
from models import db, User, Post, Tag, PostTag
from flask_sqlalchemy import SQLAlchemy

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_user_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()


class UserTestCase(TestCase):
    """Tests for views for Users."""

    def setUp(self):
        """Add sample user."""

        # User.query.delete()

        user1 = User(first_name="Bob", last_name="Evans",
                     image_url="https://static.tvtropes.org/pmwiki/pub/images/AverageMan1.jpg")
        user2 = User(first_name="Ashley", last_name="Smith")
        user3 = User(first_name="Jordan", last_name="Brooks",
                     image_url="https://static.tvtropes.org/pmwiki/pub/images/AverageMan1.jpg")
        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.commit()

        self.user1_id = user1.id
        self.user2_id = user2.id
        self.user3_id = user3.id
        self.user1 = user1
        self.user2 = user2
        self.user3 = user3

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_list_users(self):
        """Tests that user list renders successfully"""
        with app.test_client() as client:
            resp = client.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('Bob Evans', html)
            self.assertIn('Ashley Smith', html)
            self.assertIn('Jordan Brooks', html)

    def test_user_details(self):
        """Tests that user details are successfully created"""
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user2.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('<h1>Ashley Smith</h1>', html)

            self.assertIn(
                'https://plumepoetry.com/wp-content/uploads/2019/12/default-profile.png', html)

    def test_edit_user(self):
        """Tests that user edit form is successfully rendered"""
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user1.id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('<h1 class="my-4">Edit a User</h1>', html)

            self.assertIn('Bob', html)
            self.assertIn('Evans', html)
            self.assertIn(
                'https://static.tvtropes.org/pmwiki/pub/images/AverageMan1.jpg', html)

    def test_edit_user_submit(self):
        """Tests that user edit is submitted successfully"""
        with app.test_client() as client:

            d = {'first_name': 'Jordie', 'last_name': 'Brink',
                 'image_url': 'https://static.tvtropes.org/pmwiki/pub/images/AverageMan1.jpg'}

            resp = client.post(
                f"/users/{self.user3.id}/edit", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            db.session.add(self.user3)
            db.session.commit()

            self.assertEqual(resp.status_code, 200)

            self.assertEqual(self.user3.first_name, 'Jordie')
            self.assertEqual(self.user3.last_name, 'Brink')
            self.assertIn(self.user3.first_name, html)
            self.assertIn(self.user3.last_name, html)

    def test_create_user(self):
        """Tests that user creation form is successfully rendered"""
        with app.test_client() as client:
            resp = client.get(f"/users/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="my-4">Create a User</h1>', html)

    def test_create_user_submit(self):
        """Tests that user creation is submitted successfully"""
        with app.test_client() as client:

            d = {'first_name': 'Haley', 'last_name': 'Peterson', 'image_url': ''}

            resp = client.post(
                f"/users/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            user4 = User.query.filter(User.first_name == 'Haley').first()

            self.assertEqual(resp.status_code, 200)

            self.assertIn(user4.first_name, html)
            self.assertIn(user4.last_name, html)
            self.assertEquals(
                user4.image_url, 'https://plumepoetry.com/wp-content/uploads/2019/12/default-profile.png')
