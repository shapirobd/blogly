"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'mynameisbrian1339'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

# *****************
# ** USER ROUTES **
# *****************


@app.route('/')
def redirect_show_users():

    return redirect("/users")


@app.route('/users', methods=['GET', 'POST'])
def show_users():

    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('/users/users.html', users=users)


@app.route('/users/new', methods=['GET'])
def show_create_user_form():

    return render_template('/users/create_user.html')


@app.route('/users/new', methods=['POST'])
def create_user():

    new_user = User(first_name=request.form['first_name'],
                    last_name=request.form['last_name'],
                    image_url=request.form['image_url'] or None)

    db.session.add(new_user)
    db.session.commit()

    return redirect('/users')


@app.route('/users/<int:user_id>', methods=['GET', 'POST'])
def show_user_info(user_id):

    user = User.query.get(user_id)
    posts = Post.query.filter(Post.user_id == user_id).all()
    return render_template('/users/user_info.html', user=user, posts=posts)


@app.route('/users/<int:user_id>/edit')
def edit_user_form(user_id):

    user = User.query.get(user_id)
    return render_template('/users/edit_user.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=['POST'])
def proccess_edit_user(user_id):

    user = User.query.get(user_id)

    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()

    return redirect('/users')


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):

    User.query.filter(User.id == user_id).delete()
    db.session.commit()

    return redirect('/users')

# *****************
# ** POST ROUTES **
# *****************


"""Show form to add a post for that user."""


@app.route('/users/<int:user_id>/posts/new')
def show_create_post_form(user_id):
    user = User.query.get(user_id)
    tags = Tag.query.all()

    return render_template('/posts/create_post.html', user=user, tags=tags)


"""Handle add form add post and redirect to the user detail page."""


@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def create_post(user_id):
    new_post = Post(
        title=request.form['title'], content=request.form['content'], user_id=user_id)

    tags = Tag.query.all()

    db.session.add(new_post)
    db.session.commit()

    for tag in tags:

        if request.form.get(f'{tag.name}'):

            new_postTag = PostTag(tag_id=tag.id, post_id=new_post.id)

            db.session.add(new_postTag)
            db.session.commit()

    return redirect(f'/users/{user_id}')


"""Show a post - Show buttons to edit and delete the post."""


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    post = Post.query.get(post_id)
    user = User.query.get(post.user_id)
    postTags = PostTag.query.filter(PostTag.post_id == post_id).all()
    tags = [Tag.query.get(postTag.tag_id)
            for postTag in postTags if postTag.post_id == post.id]

    return render_template('/posts/post_info.html', post=post, user=user, tags=tags)


# """Show form to edit a post, and to cancel(back to user page)."""


@app.route('/posts/<int:post_id>/edit')
def show_edit_post_form(post_id):
    post = Post.query.get(post_id)
    tags = Tag.query.all()

    post_tags = PostTag.query.filter(PostTag.post_id == post.id).all()

    checked_tags = [Tag.query.get(post_tag.tag_id) for post_tag in post_tags]

    return render_template('/posts/edit_post.html', post=post, tags=tags, checked_tags=checked_tags)


# """Handle editing of a post. Redirect back to the post view."""

@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def proccess_edit_post(post_id):
    post = Post.query.get(post_id)

    post.title = request.form['title']
    post.content = request.form['content']

    PostTag.query.filter(PostTag.post_id == post_id).delete()

    tags = Tag.query.all()

    db.session.add(post)
    db.session.commit()

    for tag in tags:

        if request.form.get(f'{tag.name}'):

            new_postTag = PostTag(tag_id=tag.id, post_id=post.id)

            db.session.add(new_postTag)
            db.session.commit()

    return redirect(f'/posts/{post_id}')


# """Delete the post."""
@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):
    post = Post.query.filter(id == post_id).first()
    user_id = post.user_id

    Post.query.filter(Post.id == post_id).delete()

    db.session.commit()

    return redirect(f'/users/{user_id}')


# ****************
# ** TAG ROUTES **
# ****************

# """Lists all tags, with links to the tag detail page."""
@app.route('/tags', methods=['GET', 'POST'])
def show_tags():
    tags = Tag.query.all()
    return render_template('tags/list_tags.html', tags=tags)


# """Show detail about a tag. Have links to edit form and to delete."""
@app.route('/tags/<int:tag_id>')
def tag_details(tag_id):
    tag = Tag.query.get(tag_id)

    post_tags = PostTag.query.filter(tag_id == tag_id).all()
    posts = [post_tag.post for post_tag in post_tags]

    return render_template('/tags/show_tag.html', posts=posts, tag=tag)


# # """Shows a form to add a new tag."""
@app.route('/tags/new')
def show_create_tag_form():
    return render_template(f'/tags/create_tag.html')

# """Process add form, adds tag, and redirect to tag list."""


@app.route('/tags/new', methods=['POST'])
def create_tag():
    new_tag = Tag(
        name=request.form['tag_name'])

    db.session.add(new_tag)
    db.session.commit()

    return redirect('/tags')


# # """Show edit form for a tag."""
@app.route('/tags/<int:tag_id>/edit')
def show_edit_tag_form(tag_id):
    tag = Tag.query.get(tag_id)
    return render_template('tags/edit_tag.html', tag=tag)


# # """Process edit form, edit tag, and redirects to the tags list."""
@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def edit_tag(tag_id):
    tag = Tag.query.get(tag_id)

    tag.name = request.form['tag_name']

    db.session.add(tag)
    db.session.commit()

    return redirect('/tags')


# # """Delete a tag."""
@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tag(tag_id):
    Tag.query.filter(Tag.id == tag_id).delete()
    db.session.commit()

    return redirect('/tags')
