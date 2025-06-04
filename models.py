from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64), nullable=True)
    middle_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone_number = db.Column(db.String(30), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    force_password_change = db.Column(db.Boolean, default=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.force_password_change = False

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return ' '.join(filter(None, [self.first_name, self.middle_name, self.last_name]))


class CompanyInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(128), nullable=False, default='Annir Initiative by Anhi OÜ')
    address = db.Column(db.String(255), nullable=False, default='Ahtri 12, Tallinn, 10151, Estonia.')
    email = db.Column(db.String(120), nullable=False, default='Invoice@anhi.io')
    phone = db.Column(db.String(30), nullable=True)
    logo_path = db.Column(db.String(255), nullable=True)

    @staticmethod
    def get():
        info = CompanyInfo.query.first()
        if not info:
            info = CompanyInfo()
            db.session.add(info)
            db.session.commit()
        return info

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(32), unique=True, nullable=False)
    date = db.Column(db.Date, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    project_code = db.Column(db.String(120), nullable=True)
    payment_info = db.Column(db.Text, nullable=True)

class InvoiceLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    item_name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    invoice = db.relationship('Invoice', backref=db.backref('lines', lazy=True))
