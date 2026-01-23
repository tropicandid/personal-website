from app.extensions import flask_app, db
from flask import redirect, render_template, url_for, request, jsonify
from flask_login import login_required
from app.models import PortfolioEntry
from app.forms import PortfolioEntryForm

@flask_app.route('/portfolio/add', methods=['GET', 'POST'])
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

@flask_app.route('/portfolio/edit/<int:portfolio_id>', methods=['GET', 'POST'])
@login_required
def edit_portfolio(portfolio_id):

    if request.method == 'POST':
        with flask_app.app_context():
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

@flask_app.route('/portfolio')
def get_portfolio():
    entries = PortfolioEntry.query.order_by(PortfolioEntry.name).all()
    return render_template('portfolio.html', entries=entries)

@flask_app.route('/portfolio/entry/<int:portfolio_id>', methods=['GET'])
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