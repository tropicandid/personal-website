from app.extensions import flask_app, db
from flask import redirect, render_template, url_for, request
from flask_login import login_required
from app.models import Category
from app.forms import CategoryForm

@flask_app.route('/category/add/', methods=['GET', 'POST'])
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


@flask_app.route('/category/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    if request.method == 'POST':
        with flask_app.app_context():
            category = db.session.get(Category, category_id)
            category.title = request.form['title']
            db.session.commit()
            return redirect(url_for('get_blogs'))

    category = db.session.execute(db.select(Category).where(Category.id == category_id)).scalar()
    form = CategoryForm(
        title=category.title,
    )
    return render_template('category/edit.html', form=form)