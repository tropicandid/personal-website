from typing import List
from datetime import date
from flask import Flask, redirect, render_template, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column, Session
from flask_login import UserMixin, login_user, LoginManager, logout_user, login_required, current_user
from sqlalchemy import Integer, String, Text, Column, ForeignKey, create_engine, Table, and_, or_
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import RegisterForm, LoginForm, BlogForm, CategoryForm, ContactForm, PortfolioEntryForm
from flask_bootstrap import Bootstrap
import os
from app.email_client import EmailClientInterface

SALT_LEN=8
def init_app():

    class Base(DeclarativeBase):
        pass

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY', 'fdjsa89fqerhfy2h989y4htgnjrfj82sdf')
    Bootstrap(app)
    ckeditor = CKEditor(app)

    # configure the SQLite database, relative to the app instance folder
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI", "sqlite:///portfolio.db")
    db = SQLAlchemy(model_class=Base)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    class Category(db.Model):
        __tablename__ = 'categories'
        id: Mapped[int] = mapped_column(primary_key=True)
        title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
        blogs: Mapped[List["Blog"]] = relationship( secondary='blog_categories', back_populates="categories_list")

    class Blog(db.Model):
        __tablename__ = 'blogs'
        id: Mapped[int] = mapped_column(primary_key=True)
        title: Mapped[str] = mapped_column(String(250), nullable=False)
        subtitle: Mapped[str] = mapped_column(String(500))
        body: Mapped[str] = mapped_column(Text)
        date: Mapped[str] = mapped_column(String(50), nullable=False)
        featured_image: Mapped[str] = mapped_column(String(500))
        author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
        author = relationship( "User", back_populates="blogs")
        categories_list: Mapped[List["Category"]] = relationship( secondary='blog_categories', back_populates="blogs")

    class PortfolioEntry(db.Model):
        __tablename__ ='portfolio_entries'
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(250), nullable=False)
        external_url: Mapped[str] = mapped_column(String(500))
        image: Mapped[str] = mapped_column(String(500))
        description: Mapped[str] = mapped_column(Text)
        tooling: Mapped[str] = mapped_column(Text)
        responsibilities: Mapped[str] = mapped_column(Text)

    class User(db.Model, UserMixin):
        __tablename__ = "users"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
        email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
        password: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
        blogs: Mapped[List["Blog"]] = relationship(back_populates="author")

    blog_categories = Table(
        'blog_categories', db.metadata,
        Column('blog_id', Integer, ForeignKey("blogs.id"), primary_key=True),
        Column('category_id', Integer, ForeignKey("categories.id"), primary_key=True)
    )

    with app.app_context():
        db.create_all()

    @app.route('/kitchen-sink')
    def get_design_components():
        return render_template('design-components.html')

    ####################### HOME #######################
    @app.route('/')
    def get_home():
        featured_posts = db.session.execute(db.select(Blog).order_by(Blog.date.desc()).limit(3)).scalars()
        return render_template('index.html', featured_posts=featured_posts)

    # TODO:
    @app.route('/edit-home')
    def edit_home():
        return render_template('index.html')

    ####################### BASIC PAGES #######################
    @app.route('/contact', methods=['GET', 'POST'])
    def get_contact():
        form = ContactForm()

        if form.validate_on_submit():
            email = form.email.data
            name = form.name.data
            message = form.message.data

            mailer = EmailClientInterface(
                "smtp.gmail.com",
                "deanna.steers@gmail.com",
                "kjtk zauz qizb lbex", #TODO: Move To OS Secret
                587)

            mailer.send_email(
                "deanna.steers@gmail.com",
                f"Subject:Website Contact Form Submission \n\n Sender: {name}\n Email:{email}\n Message: {message}")

            return render_template('contact.html')

        return render_template('contact.html', form=form)

    @app.route('/about')
    def get_about():
        return render_template('about.html')

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    ####################### BLOG #######################
    @app.route('/blog', methods=['GET'])
    def get_blogs():
        per_page = request.args.get('per_page', default=4, type=int)
        page = request.args.get('page', default=1, type=int)
        selected_categories = request.args.get('category', default='', type=str).split(',') if request.args.get('category', default='', type=str) else False
        search_term = request.args.get('s', default='', type=str)
        categories = db.session.execute( db.select(Category) ).scalars()

        query = Blog.query
        if selected_categories:
            query = query.join(Blog.categories_list).where(Category.title.in_(selected_categories))

        if search_term:
            query = query.filter(or_( Blog.title.icontains(search_term),Blog.body.icontains(search_term) ) )

        pagination = db.paginate(query.order_by(Blog.date.desc()), page=page, per_page=per_page, error_out=False)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            posts_data = [{'id': p.id, 'title': p.title, 'content': p.body[:200], 'image_url':p.featured_image} for p in pagination.items]
            return jsonify(
                {'posts': posts_data, 'has_next': pagination.has_next, 'total_pages': pagination.pages, 'next_num': pagination.next_num, 'current_page': pagination.page })
        else:
            return render_template('blog.html', pagination=pagination, categories=categories)

    # TODO:
    # 1. Get related content in sidebar dynamic
    # 2. Finish deciding upon display and content
    @app.route('/blog/<string:blog_title>')
    def get_blog_single(blog_title):
        blog_title = blog_title.replace('-', ' ')
        blog = db.session.execute(db.select(Blog).where(Blog.title == blog_title)).scalar()

        category_ids = (
            db.session.query(blog_categories.c.category_id)
            .filter(blog_categories.c.blog_id == blog.id)
            .subquery()
        )

        query = (
            Blog.query
            .join(blog_categories)
            .filter(blog_categories.c.category_id.in_(category_ids))
            .filter(Blog.id != blog.id)  # exclude the original blog
            .distinct()
            .order_by(Blog.date.desc())
        )

        related_blogs = query.limit(3).all()
        return render_template('blog/post.html', data=blog, related_blogs=related_blogs)

    @app.route('/blog/edit/<int:blog_id>', methods=['GET', 'POST'])
    @login_required
    def edit_blog(blog_id):
        if request.method == 'POST':
            with app.app_context():
                post = db.session.get(Blog, blog_id)
                post.title = request.form['title']
                post.subtitle = request.form['subtitle']
                post.body = request.form['body']
                post.featured_image = request.form['img_url']
                cats = []
                for cat in request.form.getlist('categories'):
                    cats.append( db.session.execute( db.select(Category).where(Category.id == cat) ).scalar()  )
                post.categories_list = cats
                db.session.commit()
                permalink = post.title.replace(' ', '-')
                return redirect(url_for('get_blog_single', blog_title=permalink))

        blog = db.session.execute(db.select(Blog).where(Blog.id == blog_id)).scalar()
        form = BlogForm(
            title=blog.title,
            subtitle = blog.subtitle,
            body = blog.body,
            img_url = blog.featured_image,
        )
        category_options = [(cat.id, cat.title) for cat in db.session.execute(db.select(Category)).scalars()]
        form.categories.choices = category_options
        selected_cats = []
        for cat in blog.categories_list:
            selected = db.session.execute(db.select(Category).where(Category.id == cat.id)).scalar()
            selected_cats.append(selected.id)
        form.categories.data = selected_cats
        return render_template('blog/edit.html', form=form)

    # TODO:
    # 1. Update image field so it can be an upload somewhere
    # 2. Verify all error messages are working
    @app.route('/blog/add/', methods=['GET', 'POST'])
    @login_required
    def add_blog():
        form = BlogForm()
        category_options = [(cat.id, cat.title) for cat in db.session.execute(db.select(Category)).scalars()]
        form.categories.choices = category_options

        if form.validate_on_submit():
            new_post = Blog(
                title=form.title.data,
                subtitle=form.subtitle.data,
                body=form.body.data,
                featured_image=form.img_url.data,
                # author=current_user,
                author_id=current_user.id,
                date=date.today().strftime("%B %d, %Y")
            )
            cats = []
            for cat in request.form.getlist('categories'):
                cats.append(db.session.execute(db.select(Category).where(Category.id == cat)).scalar())
            new_post.categories_list = cats

            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for("get_blogs"))

        return render_template('blog/create.html', form=form )

    ##################### CATEGORY #####################

    @app.route('/category/add/', methods=['GET', 'POST'])
    @login_required
    def add_category():
        form = CategoryForm()
        if form.validate_on_submit():
            new_category = Category(
                title=form.title.data,
            )
            db.session.add(new_category)
            db.session.commit()
            return redirect(url_for("get_blogs"))
        return render_template('category/create.html', form=form)

    @app.route('/category/edit/<int:category_id>', methods=['GET', 'POST'])
    @login_required
    def edit_category(category_id):
        if request.method == 'POST':
            with app.app_context():
                category = db.session.get(Category, category_id)
                category.title = request.form['title']
                db.session.commit()
                return redirect(url_for('get_blogs'))

        category = db.session.execute(db.select(Category).where(Category.id == category_id)).scalar()
        form = CategoryForm(
            title=category.title,
        )
        return render_template('category/edit.html', form=form)

    ####################### PORTFOLIO #######################

    @app.route('/portfolio/add', methods=['GET', 'POST'])
    @login_required
    def add_portfolio():
        form = PortfolioEntryForm()
        if form.validate_on_submit():
            new_portfolio_entry = PortfolioEntry(
                name =form.name.data,
                external_url = form.external_url.data,
                image = form.image.data,
                description = form.description.data,
                tooling = form.tooling.data,
                responsibilities = form.responsibilities.data,
            )

            db.session.add(new_portfolio_entry)
            db.session.commit()
            return redirect(url_for("get_portfolio"))
        return render_template('/portfolio/create.html', form=form)

    @app.route('/portfolio/edit/<int:portfolio_id>', methods=['GET', 'POST'])
    @login_required
    def edit_portfolio(portfolio_id):

        if request.method == 'POST':
            with app.app_context():
                entry = db.session.get(PortfolioEntry, portfolio_id)

                entry.name = request.form['name']
                entry.external_url = request.form['external_url']
                entry.image = request.form['image']
                entry.description = request.form['description']
                entry.tooling = request.form['tooling']
                entry.responsibilities = request.form['responsibilities']
                db.session.commit()

                return redirect(url_for('get_portfolio'))

        entry = db.session.execute(db.select(PortfolioEntry).where(PortfolioEntry.id == portfolio_id)).scalar()
        form = PortfolioEntryForm(
            name=entry.name,
            external_url=entry.external_url,
            image=entry.image,
            description=entry.description,
            tooling=entry.tooling,
            responsibilities=entry.responsibilities,
        )
        return render_template('/portfolio/edit.html', form=form)

    @app.route('/portfolio')
    def get_portfolio():
        entries = PortfolioEntry.query.order_by(PortfolioEntry.name).all()
        return render_template('portfolio.html', entries=entries)

    @app.route('/portfolio/entry/<int:portfolio_id>', methods=['GET'])
    def get_portfolio_entry(portfolio_id):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            entry = PortfolioEntry.query.where(PortfolioEntry.id == portfolio_id).first()
            return jsonify(
                {'name': entry.name,
                 'external_url': entry.external_url,
                 'description': entry.description,
                 'tooling': entry.tooling,
                 'responsibilities': entry.responsibilities
                 })
        return jsonify({'500 error': "Access Denied"})

    ####################### AUTH #######################
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("get_home"))

        if request.method == 'POST':
            user_exists = db.session.query(User).filter(User.email == request.form['email']).first()

            if user_exists:
                return redirect(
                    url_for("login", error="This email is already is associated with an account. Try logging in."))

            invite_code = os.environ.get('REGISTRATION_KEY', 'r3g!$tr4t!0n')
            if request.form['inviteCode'] != invite_code:
                form = RegisterForm()
                return render_template("auth/register.html", form=form,
                                       error="Invalid invitation code. Please contact your administrator if you continue to have difficulty.")

            hashed_and_encrypted = generate_password_hash(request.form['password'], method='pbkdf2:sha256',salt_length=SALT_LEN)
            new_user = User(
                name=request.form['name'],
                email=request.form['email'],
                password=hashed_and_encrypted,
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("get_home"))
        form = RegisterForm()
        return render_template("auth/register.html", form=form)

    @app.route('/login', methods=["GET", "POST"])
    def login():
        error = request.args.get('error')
        if request.method == "POST":
            form = LoginForm()
            if form.validate_on_submit():
                user = db.session.query(User).filter(User.email == request.form['email']).first()
                if not user:
                    return render_template("login.html", form=form,
                                           error="This email does not appear to have an associated account. Do you need to Register a new user?")

                if check_password_hash(user.password, request.form['password']):
                    login_user(user)
                    return redirect(url_for('get_home', name=user.name))
                else:
                    return render_template("login.html", form=form, error='Incorrect password.')
        form = LoginForm()
        return render_template("auth/login.html", form=form, error=error)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('get_home'))

    return app