from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, HiddenField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired


class CreatePostForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    content = TextAreaField(validators=[DataRequired()])


class CreateCommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[DataRequired()])


class CommentReplyForm(FlaskForm):
    reply = TextAreaField('Reply', validators=[DataRequired()])
