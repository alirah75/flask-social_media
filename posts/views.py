from flask import render_template, request, flash, session, redirect, url_for, jsonify

from . import posts
from .models import Post, Comment
from .forms import CreatePostForm, CreateCommentForm, CommentReplyForm

from ..app import db
from ..users import User


@posts.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('user_id'):
        flash('you are not login.')
        return redirect(url_for('users.login'))

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
    return render_template('posts/index.html', posts=result, form=form, current_user=True)


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


@posts.route('/posts_user/<int:post_id>', methods=['GET', 'POST'])
def posts_user(post_id):
    if not session.get('user_id'):
        flash('You are not logged in.')
        return redirect(url_for('users.login'))

    comment_form = CreateCommentForm()
    reply_form = CommentReplyForm()

    if comment_form.validate_on_submit() and 'parent_comment_id' not in request.form:
        new_comment = Comment(content=comment_form.comment.data, user_id=session['user_id'], post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Your comment has been posted.')
        return redirect(url_for('posts.posts_user', id=post_id))

    if reply_form.validate_on_submit() and 'parent_comment_id' in request.form:
        # Replying to a comment
        reply_content = reply_form.reply.data
        parent_comment_id = request.form.get('parent_comment_id')
        new_reply = Comment(content=reply_content, user_id=session['user_id'], post_id=post_id, parent_id=parent_comment_id)
        db.session.add(new_reply)
        db.session.commit()
        flash('Your reply has been posted.')
        return redirect(url_for('posts.posts_user', post_id=post_id))

    posts = Post.query.filter(Post.user_id == post_id).all()
    result = []
    for post in posts:
        post_data = {
            'user_id': post.user_id,
            'id': post.id,
            'username': User.query.filter(User.id == post.user_id).first().username,
            'content': post.content,
            'title': post.title,
            'timestamp': post.timestamp,
            'comments': get_comments_with_replies(post.id)
        }
        result.append(post_data)
    return render_template('posts/post_user.html', posts=result, comment_form=comment_form,
                           reply_form=reply_form, current_user=True)


def get_comments_with_replies(post_id):
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None).all()
    comment_tree = []
    for comment in comments:
        comment_data = {
            'content': comment.content,
            'username': User.query.filter(User.id == comment.user_id).first().username,
            'timestamp': comment.timestamp,
            'id': comment.id,
            'replies': get_replies(post_id, comment.id)
        }
        comment_tree.append(comment_data)
    return comment_tree


def get_replies(post_id, comment_id):
    replies = Comment.query.filter_by(post_id=post_id, parent_id=comment_id).all()
    print(replies)
    reply_list = []
    for reply in replies:
        reply_data = {
            'content': reply.content,
            'username': User.query.filter(User.id == reply.user_id).first().username,
            'user_id': reply.user_id,
            'timestamp': reply.timestamp,
            'id': reply.id,
            'replies': get_replies(post_id, reply.id)
        }
        reply_list.append(reply_data)
    return reply_list
