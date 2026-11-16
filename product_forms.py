from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, ValidationError
from app.models.inventory import Product, Category


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=256)])
    submit = SubmitField('Save Category')

    def __init__(self, original_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, field):
        if not self.original_name or field.data.strip().lower() != self.original_name.lower():
            if Category.query.filter(Category.name.ilike(field.data.strip())).first():
                raise ValidationError('Category name already exists.')


class ProductForm(FlaskForm):
    sku = StringField('SKU / Code', validators=[DataRequired(), Length(max=64)])
    barcode = StringField('Barcode / UPC', validators=[Optional(), Length(max=64)])
    name = StringField('Product Name', validators=[DataRequired(), Length(max=120)])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional()])
    uom = StringField('Unit of Measure (Base Unit)', default='pcs', validators=[DataRequired(), Length(max=32)])

    # Pack & Piece fields
    pieces_per_pack = IntegerField('Pieces Per Pack', default=1, validators=[DataRequired(), NumberRange(min=1, message="Must be at least 1 piece per pack.")])
    piece_price = DecimalField('Piece Selling Price', default=Decimal('0.00'), places=2, validators=[DataRequired(), NumberRange(min=0)])
    pack_price = DecimalField('Pack Selling Price', default=Decimal('0.00'), places=2, validators=[Optional(), NumberRange(min=0)])
    
    # Cost & Stock
    purchase_cost = DecimalField('Purchase Cost (per base piece)', default=Decimal('0.00'), places=2, validators=[DataRequired(), NumberRange(min=0)])
    opening_stock = IntegerField('Initial Stock (in pieces)', default=0, validators=[DataRequired(), NumberRange(min=0)])
    min_stock_level = IntegerField('Minimum Stock Alert Level (in pieces)', default=5, validators=[DataRequired(), NumberRange(min=0)])
    
    submit = SubmitField('Save Product')

    def __init__(self, original_product=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_product = original_product
        self.category_id.choices = [(0, '-- Select Category --')] + [
            (c.id, c.name) for c in Category.query.order_by(Category.name).all()
        ]

    def validate_sku(self, field):
        sku_clean = field.data.strip()
        if not self.original_product or sku_clean != self.original_product.sku:
            if Product.query.filter_by(sku=sku_clean).first():
                raise ValidationError('A product with this SKU already exists.')

    def validate_barcode(self, field):
        if field.data and field.data.strip():
            barcode_clean = field.data.strip()
            if not self.original_product or barcode_clean != self.original_product.barcode:
                if Product.query.filter_by(barcode=barcode_clean).first():
                    raise ValidationError('A product with this barcode already exists.')


class StockAdjustmentForm(FlaskForm):
    new_quantity = IntegerField('New Physical Stock (Total Base Pieces)', validators=[DataRequired(), NumberRange(min=0)])
    reason = SelectField('Reason for Adjustment', choices=[
        ('Damaged / Broken', 'Damaged / Broken'),
        ('Inventory Reconciliation', 'Inventory Reconciliation / Audit'),
        ('Expired Stock', 'Expired Stock'),
        ('Internal Usage', 'Internal Business Usage'),
        ('Returned to Vendor', 'Returned to Vendor (Manual)'),
        ('Correction of Counting Error', 'Correction of Counting Error'),
        ('Other', 'Other')
    ], default='Inventory Reconciliation')
    notes = TextAreaField('Detailed Notes / Audit Justification', validators=[Optional()])
    submit = SubmitField('Apply Adjustment')
