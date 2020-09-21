from unittest import TestCase
from app import app
from models import db, User, Post, Tag, PostTag
from flask_sqlalchemy import SQLAlchemy

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_post_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()


class PostTestCase(TestCase):
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

    def test_create_post_page(self):
        """Tests that post creation form renders successfully"""
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user1.id}/posts/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                f'<h1 class="my-4">Add Post for {self.user1.first_name} {self.user1.last_name}</h1>', html)

    def test_create_post_submit(self):
        """Tests that post creation is successful"""
        with app.test_client() as client:

            d = {'title': 'Test Title', 'content': 'This is test content'}

            resp = client.post(
                f"/users/{self.user1.id}/posts/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

    def test_edit_post_submit(self):
        """Tests that post edit is successful"""
        with app.test_client() as client:

            d = {'title': 'Test Title 2',
                 'content': 'This is original test content'}

            resp = client.post(
                f"/users/{self.user1.id}/posts/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            post = Post.query.filter(Post.title == 'Test Title 2').first()

            d_edit = {'title': 'Test Title 2 Editted',
                      'content': 'This is editted test content'}

            resp = client.post(
                f"/posts/{post.id}/edit", data=d_edit, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Test Title 2 Editted', html)
            self.assertEqual(
                'Test Title 2 Editted', Post.query.filter(Post.title == 'Test Title 2 Editted').first().title)
