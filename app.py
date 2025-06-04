import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Invoice, InvoiceLine, CompanyInfo
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
        user = User(username='admin', is_admin=True, force_password_change=False)
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
            if not user.is_active:
                flash('Your account is deactivated.', 'error')
                return render_template('login.html')
            session['user_id'] = user.id
            if user.force_password_change:
                return redirect(url_for('force_change_password'))
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

@app.route('/force_change_password', methods=['GET', 'POST'])
@login_required
def force_change_password():
    user = User.query.get(session['user_id'])
    if not user.force_password_change:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
        elif len(new_password) < 4:
            flash('Password must be at least 4 characters.', 'error')
        else:
            user.set_password(new_password)
            user.force_password_change = False
            db.session.commit()
            flash('Password updated. Please log in again.', 'info')
            session.clear()
            return redirect(url_for('login'))
    return render_template('force_change_password.html')

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

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# --- Admin: User Management ---
@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@admin_required
def admin_add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = bool(request.form.get('is_admin'))
        user = User(username=username, is_admin=is_admin, is_active=True, force_password_change=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('User added.', 'info')
        return redirect(url_for('admin_users'))
    return render_template('admin_add_user.html')

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.middle_name = request.form['middle_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        user.phone_number = request.form['phone_number']
        user.is_admin = bool(request.form.get('is_admin'))
        user.is_active = bool(request.form.get('is_active'))
        db.session.commit()
        flash('User updated.', 'info')
        return redirect(url_for('admin_users'))
    return render_template('admin_edit_user.html', user=user)

@app.route('/admin/users/<int:user_id>/reset_password', methods=['POST'])
@admin_required
def admin_reset_password(user_id):
    user = User.query.get_or_404(user_id)
    new_password = request.form['new_password']
    user.set_password(new_password)
    user.force_password_change = True
    db.session.commit()
    flash('Password reset. User must change on next login.', 'info')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'info')
    return redirect(url_for('admin_users'))

# --- Admin: Company Info/Logo Management ---
@app.route('/admin/company', methods=['GET', 'POST'])
@admin_required
def admin_company():
    from models import CompanyInfo
    info = CompanyInfo.get()
    if request.method == 'POST':
        info.company_name = request.form['company_name']
        info.address = request.form['address']
        info.email = request.form['email']
        info.phone = request.form['phone']
        # Handle logo upload
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo and logo.filename:
                logo_path = os.path.join('static', 'uploads', logo.filename)
                os.makedirs(os.path.dirname(logo_path), exist_ok=True)
                logo.save(logo_path)
                info.logo_path = logo_path
        db.session.commit()
        flash('Company info updated.', 'info')
        return redirect(url_for('admin_company'))
    return render_template('admin_company.html', info=info)

# --- Dashboard ---
@app.route('/')
@login_required
def dashboard():
    invoices = Invoice.query.order_by(Invoice.date.desc()).all()
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', invoices=invoices, user=user)

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
    user = User.query.get(session['user_id'])
    user_info_incomplete = not all([
        user.first_name, user.last_name, user.email, user.phone_number
    ])
    if request.method == 'POST':
        if user_info_incomplete:
            flash('Please complete your user information before creating an invoice.', 'error')
            return render_template('invoice_form.html', currencies=CURRENCIES, user_info_incomplete=True)
        # Get fields
        currency = request.form['currency']
        project_code = request.form.get('project_code') or None
        date_str = request.form['date']
        from datetime import datetime
        try:
            invoice_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            invoice_date = date.today()
        payment_info = request.form.get('payment_info')
        item_names = request.form.getlist('item_name')
        descriptions = request.form.getlist('description')
        quantities = request.form.getlist('quantity')
        unit_prices = request.form.getlist('unit_price')
        line_items = []
        for name, desc, qty, price in zip(item_names, descriptions, quantities, unit_prices):
            if name.strip():
                line_items.append({
                    'item_name': name.strip(),
                    'description': desc.strip(),
                    'quantity': float(qty or 0),
                    'unit_price': float(price or 0),
                })
        # Generate invoice number
        import random, string
        yyyymm = invoice_date.strftime('%Y%m')
        initials = (user.first_name[0] if user.first_name else '') + (user.last_name[0] if user.last_name else '')
        initials = initials.upper()
        def gen_ref():
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        # Ensure uniqueness
        for _ in range(10):
            ref = gen_ref()
            invoice_number = f"{yyyymm}-{initials}-{ref}"
            if not Invoice.query.filter_by(invoice_number=invoice_number).first():
                break
        else:
            flash('Could not generate unique invoice number. Try again.', 'error')
            return render_template('invoice_form.html', currencies=CURRENCIES, user_info_incomplete=False)
        # Save invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            date=invoice_date,
            currency=currency,
            project_code=project_code,
            payment_info=payment_info
        )
        db.session.add(invoice)
        db.session.flush()  # Get invoice.id
        for item in line_items:
            db.session.add(InvoiceLine(
                invoice_id=invoice.id,
                item_name=item['item_name'],
                description=item['description'],
                quantity=item['quantity'],
                unit_price=item['unit_price']
            ))
        db.session.commit()
        return redirect(url_for('invoice_detail', invoice_id=invoice.id))
    return render_template('invoice_form.html', currencies=CURRENCIES, user_info_incomplete=user_info_incomplete)


@app.route('/invoices/<int:invoice_id>')
@login_required
def invoice_detail(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    user = User.query.get(session['user_id'])
    info = CompanyInfo.query.first() or CompanyInfo()  # Get or create default company info
    return render_template('invoice_detail.html', invoice=invoice, user=user, info=info, currencies=CURRENCIES)

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
    info = CompanyInfo.query.first() or CompanyInfo()  # Get or create default company info
    return render_template('invoice_print.html', invoice=invoice, user=user, info=info, currencies=CURRENCIES)

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
