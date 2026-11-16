from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from app.models.supplier import Supplier
from app.models.sales import PaymentMethod


class SupplierPaymentForm(FlaskForm):
    amount = DecimalField('Payment Amount', places=2, validators=[DataRequired(), NumberRange(min=Decimal('0.01'))])
    payment_method = SelectField('Payment Method', choices=PaymentMethod.CHOICES, default='BANK_TRANSFER')
    reference_no = StringField('Transaction / Transfer #', validators=[Optional()])
    notes = TextAreaField('Payment Notes', validators=[Optional()])
    submit = SubmitField('Record Supplier Payment')
