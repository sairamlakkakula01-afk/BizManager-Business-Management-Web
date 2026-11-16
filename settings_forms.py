from decimal import Decimal
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange


class BusinessSettingsForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired(), Length(max=120)])
    legal_name = StringField('Legal Registered Name', validators=[Optional(), Length(max=120)])
    tax_id = StringField('Tax ID / GST / VAT Number', validators=[Optional(), Length(max=64)])
    phone = StringField('Business Phone', validators=[Optional(), Length(max=32)])
    email = StringField('Business Email', validators=[Optional(), Length(max=120)])
    address = TextAreaField('Physical Address', validators=[Optional()])
    currency_symbol = StringField('Currency Symbol (e.g. $, ₹, £, €)', default='$', validators=[DataRequired(), Length(max=8)])
    tax_rate = DecimalField('Default Tax Rate (%)', default=Decimal('0.00'), places=2, validators=[Optional(), NumberRange(min=0, max=100)])
    invoice_prefix = StringField('Sales Invoice Prefix', default='INV', validators=[DataRequired(), Length(max=16)])
    purchase_prefix = StringField('Purchase Order Prefix', default='PO', validators=[DataRequired(), Length(max=16)])
    logo = FileField('Business Logo', validators=[
        Optional(),
        FileAllowed(['png', 'jpg', 'jpeg', 'svg', 'webp'], 'Images only!')
    ])
    submit = SubmitField('Save Settings')
