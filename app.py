import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Invoice, InvoiceLine
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invoice_maker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Ensure DB and default user exist
with app.app_context():
    db.create_all()
    if not User.query.first():
        user = User(username='admin')
        user.set_password('admin')
        db.session.add(user)
        db.session.commit()

CURRENCIES = [
    ('USD', '$'),
    ('LYD', 'ل.د'),
    ('EUR', '€'),
]

# --- Authentication ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# --- Dashboard ---
@app.route('/')
@login_required
def dashboard():
    invoices = Invoice.query.order_by(Invoice.date.desc()).all()
    return render_template('dashboard.html', invoices=invoices)

# --- User Information ---

@app.route('/user_info', methods=['GET', 'POST'])
@login_required
def user_info():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.middle_name = request.form['middle_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        user.phone_number = request.form['phone_number']
        db.session.commit()
        flash('User information updated.', 'info')
        return redirect(url_for('user_info'))
    return render_template('user_info.html', user=user)

# --- Invoices ---
@app.route('/invoices')
@login_required
def invoices():
    invoices = Invoice.query.order_by(Invoice.date.desc()).all()
    return render_template('invoices.html', invoices=invoices)

@app.route('/invoices/new', methods=['GET', 'POST'])
@login_required
def new_invoice():




    if request.method == 'POST':

        currency = request.form['currency']
        line_items = []
        descriptions = request.form.getlist('description')
        quantities = request.form.getlist('quantity')
        unit_prices = request.form.getlist('unit_price')
        project_code = request.form.get('project_code') or None
        for desc, qty, price in zip(descriptions, quantities, unit_prices):
            if desc.strip():
                line_items.append({
                    'description': desc.strip(),
                    'quantity': float(qty or 0),
                    'unit_price': float(price or 0),
                })
        invoice = Invoice(date=date.today(), currency=currency, project_code=project_code)
        db.session.add(invoice)
        db.session.flush()  # Get invoice.id
        for item in line_items:
            db.session.add(InvoiceLine(
                invoice_id=invoice.id,
                description=item['description'],
                quantity=item['quantity'],
                unit_price=item['unit_price']
            ))
        db.session.commit()
        return redirect(url_for('invoice_detail', invoice_id=invoice.id))
    return render_template('invoice_form.html', currencies=CURRENCIES)

@app.route('/invoices/<int:invoice_id>')
@login_required
def invoice_detail(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    user = User.query.get(session['user_id'])
    return render_template('invoice_detail.html', invoice=invoice, user=user, currencies=CURRENCIES)

@app.route('/invoices/<int:invoice_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)

    if request.method == 'POST':

        invoice.currency = request.form['currency']
        invoice.project_code = request.form.get('project_code') or None
        # Remove old lines
        InvoiceLine.query.filter_by(invoice_id=invoice.id).delete()
        descriptions = request.form.getlist('description')
        quantities = request.form.getlist('quantity')
        unit_prices = request.form.getlist('unit_price')
        for desc, qty, price in zip(descriptions, quantities, unit_prices):
            if desc.strip():
                db.session.add(InvoiceLine(
                    invoice_id=invoice.id,
                    description=desc.strip(),
                    quantity=float(qty or 0),
                    unit_price=float(price or 0)
                ))
        db.session.commit()
        return redirect(url_for('invoice_detail', invoice_id=invoice.id))
    return render_template('invoice_form.html', invoice=invoice, currencies=CURRENCIES)

@app.route('/invoices/<int:invoice_id>/delete', methods=['POST'])
@login_required
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    InvoiceLine.query.filter_by(invoice_id=invoice.id).delete()
    db.session.delete(invoice)
    db.session.commit()
    return redirect(url_for('invoices'))

@app.route('/invoices/<int:invoice_id>/print')
@login_required
def print_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    user = User.query.get(session['user_id'])
    return render_template('invoice_print.html', invoice=invoice, user=user, currencies=CURRENCIES)

# --- Change Password ---

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if not user.check_password(current_password):
            flash('Current password is incorrect.', 'error')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'error')
        elif len(new_password) < 4:
            flash('New password must be at least 4 characters.', 'error')
        else:
            user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully.', 'info')
            return redirect(url_for('dashboard'))
    return render_template('change_password.html')

# --- Utility ---
@app.template_filter('currency_format')
def currency_format(value, currency):
    if currency == 'LYD':
        return f"{value:,.3f}"
    else:
        return f"{value:,.2f}"

if __name__ == '__main__':
    app.run(debug=True)
