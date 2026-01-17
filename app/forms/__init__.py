from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField

class BlogForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    categories = SelectMultipleField("Categories", coerce=int)
    submit = SubmitField("Submit Post")

class PortfolioEntryForm(FlaskForm):
    name = StringField("Entry Title", validators=[DataRequired()])
    external_url = StringField("External URL", validators=[URL()])
    image = StringField("Blog Image URL")
    description = CKEditorField("Entry Description")
    tooling = CKEditorField("Entry Tech Stack & Tools")
    responsibilities = CKEditorField("My Roles & Responsibilities")
    submit = SubmitField("Submit Portfolio Entry")

class RegisterForm(FlaskForm):
    inviteCode = StringField("Invite Code", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    name = StringField("User Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class CategoryForm(FlaskForm):
    title = StringField("Category Label", validators=[DataRequired()])
    submit = SubmitField("submit")

class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send Message")