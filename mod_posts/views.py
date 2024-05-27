from flask import render_template, request, flash, session, redirect, url_for, jsonify

from . import posts
from .models import Post, Comment
from .forms import CreatePostForm, CreateCommentForm

from ..app import db
from ..mod_users import User


@posts.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('user_id'):
        flash('you are not login.')
        return render_template('users/index.html')

    form = CreateCommentForm()
    if form.validate_on_submit():
        post_id = request.form.get('post_id')
        new_comment = Comment(content=form.comment.data, post_id=post_id, user_id=session['user_id'])
        db.session.add(new_comment)
        db.session.commit()
        flash('Your comment has been added.')
        return redirect(url_for('posts.index'))

    posts = Post.query.all()
    result = []
    for post in posts:
        comments = Comment.query.filter_by(post_id=post.id).all()
        post_data = {
            'user_id': post.user_id,
            'id': post.id,
            'username': User.query.filter(User.id == post.user_id).first().username,
            'content': post.content,
            'title': post.title,
            'timestamp': post.timestamp,
            'comments': [
                {'content': comment.content, 'username': User.query.filter(User.id == comment.user_id).first().username,
                 'timestamp': comment.timestamp} for comment in comments]
        }
        result.append(post_data)
    return render_template('posts/index.html', posts=result, form=form)


@posts.route('/new/', methods=['GET', 'POST'])
def create_post():
    form = CreatePostForm(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('posts/create_post.html', form=form)

        if not session.get('user_id'):
            flash('you are not login.')
            return render_template('posts/create_post.html', form=form)

        try:
            new_post = Post()
            new_post.title = form.title.data
            new_post.content = form.content.data
            new_post.user_id = session.get('user_id')
            db.session.add(new_post)

            session['post_id'] = new_post.id
            db.session.commit()
            flash('Created Post Successfully.')
            return redirect(url_for('posts.index'))
        except:
            db.session.rollback()
            flash('Post not created!!!', 'error')
            return render_template('posts/create_post.html', form=form)

    return render_template('posts/create_post.html', form=form)


@posts.route('/posts_user/<int:id>', methods=['GET'])
def posts_user(id):
    posts = Post.query.all()
    result = []
    for post in posts:
        comments = Comment.query.filter_by(post_id=post.id).all()
        post_data = {
            'user_id': post.user_id,
            'id': post.id,
            'username': User.query.filter(User.id == post.user_id).first().username,
            'content': post.content,
            'title': post.title,
            'timestamp': post.timestamp,
            'comments': [
                {'content': comment.content, 'username': User.query.filter(User.id == comment.user_id).first().username,
                 'timestamp': comment.timestamp} for comment in comments]
        }
        result.append(post_data)
    return render_template('posts/post_user.html', posts=result)


# @posts.route('/add_comment/', methods=['GET', 'POST'])
# def add_comment():
#     posts = Post.query.all()
#     result = [{'user_id': post.user_id, 'content': post.content, 'title': post.title, 'timestamp': post.timestamp,
#                'username': User.query.filter(post.user_id == User.id).first().username} for post in posts]
#     print(posts)
#     form = CreateCommentForm(request.form)
#     if request.method == 'POST':
#         if not form.validate_on_submit():
#             return render_template('posts/create_post.html', form=form)
#
#         if not session.get('user_id') and session.get('post_id'):
#             flash('you are not login.')
#             return render_template('posts/create_post.html', form=form)
#
#         try:
#             new_comment = Comment()
#             new_comment.comment = form.comment.data
#             new_comment.user_id = session.get('user_id')
#             new_comment.post_id = session.get('post_id')
#             # new_comment.parent_id = session.get('parent_id')
#             db.session.add(new_comment)
#             db.session.commit()
#             flash("Your comment has been added to the post", "success")
#             return redirect(url_for('posts.user_posts', id=session.get('post_id')))
#         except:
#             db.session.rollback()
#             flash('Comment not submit')
#             return render_template('posts/create_post.html', form=posts)
#
#     return render_template('posts/index.html', form=result)


@posts.route('/post_comments/<int:post_id>', methods=['GET'])
def post_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).all()
    result = [{'id': comment.id, 'content': comment.content, 'user_id': comment.user_id, 'timestamp': comment.timestamp,
               'parent_id': comment.parent_id} for comment in comments]
    return jsonify(result)
