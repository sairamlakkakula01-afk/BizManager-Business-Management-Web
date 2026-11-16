from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Optional, Email, Length, NumberRange
from app.models.customer import Customer
from app.models.supplier import Supplier


class CustomerForm(FlaskForm):
    name = StringField('Customer Name / Business', validators=[DataRequired(), Length(max=120)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=32)])
    email = StringField('Email Address', validators=[Optional(), Email(), Length(max=120)])
    address = TextAreaField('Billing & Shipping Address', validators=[Optional()])
    credit_limit = DecimalField('Credit Limit ($)', default=Decimal('0.00'), places=2, validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Save Customer')


class SupplierForm(FlaskForm):
    name = StringField('Contact Person / Name', validators=[DataRequired(), Length(max=120)])
    company_name = StringField('Supplier Company Name', validators=[Optional(), Length(max=120)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=32)])
    email = StringField('Email Address', validators=[Optional(), Email(), Length(max=120)])
    address = TextAreaField('Supplier Address', validators=[Optional()])
    submit = SubmitField('Save Supplier')
