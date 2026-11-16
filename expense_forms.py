from decimal import Decimal
from datetime import date
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from app.models.expense import ExpenseCategory
from app.models.sales import PaymentMethod


class ExpenseCategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=256)])
    submit = SubmitField('Save Category')


class ExpenseForm(FlaskForm):
    category_id = SelectField('Expense Category', coerce=int, validators=[DataRequired()])
    expense_date = DateField('Expense Date', default=date.today, validators=[DataRequired()])
    amount = DecimalField('Amount', places=2, validators=[DataRequired(), NumberRange(min=Decimal('0.01'))])
    payment_method = SelectField('Payment Method', choices=PaymentMethod.CHOICES, default=PaymentMethod.CASH)
    description = StringField('Description / Purpose', validators=[DataRequired(), Length(max=256)])
    receipt_file = FileField('Attach Receipt / Invoice (PDF, PNG, JPG)', validators=[
        Optional(),
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 'Images and PDFs only!')
    ])
    submit = SubmitField('Record Expense')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_id.choices = [
            (cat.id, cat.name) for cat in ExpenseCategory.query.order_by(ExpenseCategory.name).all()
        ]
