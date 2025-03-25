from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, URL, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class VideoUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=100)])
    url = StringField('Video URL', validators=[DataRequired(), URL()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    submit = SubmitField('Upload Video')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=100)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=10, max=5000)])
    submit = SubmitField('Create Post')

class CommentForm(FlaskForm):
    comment_text = TextAreaField('Comment', validators=[DataRequired(), Length(min=1, max=500)])
    video_id = HiddenField('Video ID', validators=[DataRequired()])
    submit = SubmitField('Post Comment')
