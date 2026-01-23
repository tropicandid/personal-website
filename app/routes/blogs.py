from app.extensions import flask_app, db
from flask import redirect, render_template, url_for, request, jsonify
from sqlalchemy import or_
from flask_login import login_required, current_user
from app.models import Blog, Category, blog_categories
from app.forms import BlogForm
from datetime import date

@flask_app.route('/blog', methods=['GET'])
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
@flask_app.route('/blog/<string:blog_title>')
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

@flask_app.route('/blog/edit/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def edit_blog(blog_id):
    if request.method == 'POST':
        with flask_app.app_context():
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
@flask_app.route('/blog/add/', methods=['GET', 'POST'])
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