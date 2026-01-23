from app.extensions import flask_app, db
from app.email_client import EmailClientInterface
from flask import render_template
from app.models import Blog
from app.forms import ContactForm
from dotenv import load_dotenv
import os

load_dotenv()

@flask_app.route('/')
def get_home():
    featured_posts = db.session.execute(db.select(Blog).order_by(Blog.date.desc()).limit(3)).scalars()
    return render_template('index.html', featured_posts=featured_posts)

@flask_app.route('/contact', methods=['GET', 'POST'])
def get_contact():
    form = ContactForm()

    if form.validate_on_submit():
        email = form.email.data
        name = form.name.data
        message = form.message.data

        mailer = EmailClientInterface(
            os.environ.get('EMAIL_CLIENT'),
            os.environ.get('EMAIL_ACCOUNT'),
            os.environ.get('EMAIL_API_KEY'),
            587)

        mailer.send_email(
            os.environ.get('EMAIL_ACCOUNT'),
            f"Subject:Website Contact Form Submission \n\n Sender: {name}\n Email:{email}\n Message: {message}")

        return render_template('contact.html')

    return render_template('contact.html', form=form)

@flask_app.route('/about')
def get_about():
    return render_template('about.html')

@flask_app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@flask_app.route('/kitchen-sink')
def get_design_components():
    return render_template('design-components.html')