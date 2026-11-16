from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from app.models.customer import Customer
from app.models.sales import PaymentMethod


class CustomerPaymentForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Payment Amount', places=2, validators=[DataRequired(), NumberRange(min=Decimal('0.01'), message="Amount must be greater than zero.")])
    payment_method = SelectField('Payment Method', choices=PaymentMethod.CHOICES, default=PaymentMethod.CASH)
    reference_no = StringField('Reference / Cheque / Transaction #', validators=[Optional()])
    notes = TextAreaField('Payment Notes', validators=[Optional()])
    submit = SubmitField('Record Payment')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer_id.choices = [
            (c.id, f"{c.name} (Balance: ${c.balance:,.2f})")
            for c in Customer.query.filter_by(is_active=True).order_by(Customer.name).all()
        ]


class SaleReturnForm(FlaskForm):
    reason = StringField('Reason for Return', validators=[DataRequired()])
    refund_method = SelectField('Refund Method', choices=PaymentMethod.CHOICES, default=PaymentMethod.CASH)
    submit = SubmitField('Process Return & Restock')
