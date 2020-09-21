from unittest import TestCase
from app import app
from models import db, User, Post, Tag, PostTag
from flask_sqlalchemy import SQLAlchemy

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_tag_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()


class TagTestCase(TestCase):
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

    def test_create_tag_page(self):
        """Tests that tag creation form renders successfully"""
        with app.test_client() as client:
            resp = client.get(f"/tags/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="my-4">Create a tag</h1>', html)

    def test_create_tag_submit(self):
        """Tests that tag creation is successful"""
        with app.test_client() as client:

            d = {'tag_name': 'test-tag'}

            resp = client.post(
                "/tags/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test-tag', html)
            self.assertEqual(
                'test-tag', Tag.query.filter(Tag.name == 'test-tag').first().name)

    def test_edit_tag_submit(self):
        """Tests that tag edit is successful"""
        with app.test_client() as client:

            d = {'tag_name': 'test-tag-2'}

            resp = client.post(
                "/tags/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            tag = Tag.query.filter(Tag.name == 'test-tag-2').first()

            d_edit = {'tag_name': 'test-tag-2-editted'}

            resp = client.post(
                f"/tags/{tag.id}/edit", data=d_edit, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test-tag-2-edit', html)
            self.assertEqual(
                'test-tag-2-editted', Tag.query.filter(Tag.name == 'test-tag-2-editted').first().name)
