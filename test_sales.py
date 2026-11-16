import pytest
from decimal import Decimal
from app.models.sales import Sale, PaymentStatus, SaleStatus
from app.services.sales_service import (
    create_sale_transaction, record_customer_payment, process_sale_return
)
from app.services.inventory_service import InsufficientStockError


def test_pack_sale_stock_deduction_and_totals(sample_pack_product, admin_user, db_session):
    """
    Selling 1 pack (10 pieces):
    Initial stock: 30 pieces.
    Pack price: $15.00.
    Cost: $0.80/piece -> COGS = $8.00.
    Gross profit = $15.00 - $8.00 = $7.00.
    Remaining stock = 20 pieces = 2 packs.
    """
    p = sample_pack_product
    sale = create_sale_transaction(
        items_data=[{
            'product_id': p.id,
            'unit_type': 'PACK',
            'quantity': 1
        }],
        payment_amount=Decimal('15.00'),
        payment_method='CASH',
        user_id=admin_user.id
    )

    assert sale.subtotal == Decimal('15.00')
    assert sale.total_amount == Decimal('15.00')
    assert sale.paid_amount == Decimal('15.00')
    assert sale.balance_amount == Decimal('0.00')
    assert sale.payment_status == PaymentStatus.PAID
    assert p.stock_quantity == 20
    assert p.formatted_stock == "2 packs"
    assert sale.total_cogs == Decimal('8.00')
    assert sale.gross_profit == Decimal('7.00')


def test_piece_sale_stock_deduction(sample_pack_product, admin_user):
    """
    Selling 2 loose pieces:
    Initial stock: 30 pieces.
    Piece price: $2.00.
    Total = 2 * 2.00 = $4.00.
    Stock remaining = 28 pieces = 2 packs and 8 pieces.
    """
    p = sample_pack_product
    sale = create_sale_transaction(
        items_data=[{
            'product_id': p.id,
            'unit_type': 'PIECE',
            'quantity': 2
        }],
        payment_amount=Decimal('4.00'),
        user_id=admin_user.id
    )

    assert sale.total_amount == Decimal('4.00')
    assert p.stock_quantity == 28
    assert p.formatted_stock == "2 packs and 8 pens"


def test_mixed_pack_and_piece_sale(sample_pack_product, admin_user):
    """
    Sequential test matching prompt specification:
    - Initial stock is 3 packs (30 pieces).
    - Sell 1 pack -> 20 pieces left.
    - Sell 2 loose pieces -> 18 pieces left ("1 pack and 8 pieces").
    """
    p = sample_pack_product

    # 1. Sell 1 pack
    create_sale_transaction(
        items_data=[{'product_id': p.id, 'unit_type': 'PACK', 'quantity': 1}],
        payment_amount=Decimal('15.00'),
        user_id=admin_user.id
    )
    assert p.stock_quantity == 20

    # 2. Sell 2 pieces
    create_sale_transaction(
        items_data=[{'product_id': p.id, 'unit_type': 'PIECE', 'quantity': 2}],
        payment_amount=Decimal('4.00'),
        user_id=admin_user.id
    )
    assert p.stock_quantity == 18
    assert p.formatted_stock == "1 pack and 8 pens"


def test_insufficient_stock_raises_error(sample_pack_product, admin_user):
    """
    Product has 30 pieces. Requesting 4 packs (40 pieces) must raise InsufficientStockError
    and stock must NOT become negative.
    """
    p = sample_pack_product
    with pytest.raises(InsufficientStockError) as exc_info:
        create_sale_transaction(
            items_data=[{'product_id': p.id, 'unit_type': 'PACK', 'quantity': 4}],
            user_id=admin_user.id
        )

    assert "Insufficient stock" in str(exc_info.value)
    assert p.stock_quantity == 30  # Stock unchanged


def test_discounts_and_taxes_calculated_server_side(sample_pack_product, admin_user):
    """
    Subtotal: 2 packs @ $15.00 = $30.00
    Discount: $5.00
    Taxable Base: $25.00
    Tax Rate: 10% -> Tax = $2.50
    Total: $27.50
    """
    sale = create_sale_transaction(
        items_data=[{'product_id': sample_pack_product.id, 'unit_type': 'PACK', 'quantity': 2}],
        discount_amount=Decimal('5.00'),
        tax_rate=Decimal('10.00'),
        payment_amount=Decimal('27.50'),
        user_id=admin_user.id
    )

    assert sale.subtotal == Decimal('30.00')
    assert sale.discount_amount == Decimal('5.00')
    assert sale.tax_amount == Decimal('2.50')
    assert sale.total_amount == Decimal('27.50')


def test_partial_payment_and_customer_balance(sample_pack_product, sample_customer, admin_user):
    """
    Total sale: $30.00.
    Customer pays $10.00 upfront.
    Balance due: $20.00.
    Customer balance increases by $20.00.
    """
    cust = sample_customer
    assert cust.balance == Decimal('0.00')

    sale = create_sale_transaction(
        items_data=[{'product_id': sample_pack_product.id, 'unit_type': 'PACK', 'quantity': 2}],
        customer_id=cust.id,
        payment_amount=Decimal('10.00'),
        user_id=admin_user.id
    )

    assert sale.payment_status == PaymentStatus.PARTIALLY_PAID
    assert sale.balance_amount == Decimal('20.00')
    assert cust.balance == Decimal('20.00')

    # Record follow-up payment
    record_customer_payment(
        customer_id=cust.id,
        amount=Decimal('20.00'),
        sale_id=sale.id,
        user_id=admin_user.id
    )

    assert cust.balance == Decimal('0.00')
    assert sale.balance_amount == Decimal('0.00')
    assert sale.payment_status == PaymentStatus.PAID


def test_customer_credit_limit_enforced(sample_pack_product, sample_customer, admin_user):
    """
    Customer credit limit is $500.00.
    Attempting an unpaid sale that exceeds limit must be rejected.
    """
    sample_customer.credit_limit = Decimal('50.00')
    sample_pack_product.stock_quantity = 100

    # Sale total $60.00 with $0 payment -> balance $60 > limit $50
    with pytest.raises(ValueError) as exc_info:
        create_sale_transaction(
            items_data=[{'product_id': sample_pack_product.id, 'unit_type': 'PACK', 'quantity': 4}],
            customer_id=sample_customer.id,
            payment_amount=Decimal('0.00'),
            user_id=admin_user.id
        )

    assert "Credit limit exceeded" in str(exc_info.value)


def test_sales_return_and_restocking(sample_pack_product, admin_user):
    """
    Sell 1 pack (10 pieces). Stock becomes 20 pieces.
    Process return of 1 pack:
    Stock is restocked back to 30 pieces.
    """
    p = sample_pack_product
    sale = create_sale_transaction(
        items_data=[{'product_id': p.id, 'unit_type': 'PACK', 'quantity': 1}],
        payment_amount=Decimal('15.00'),
        user_id=admin_user.id
    )
    assert p.stock_quantity == 20

    ret = process_sale_return(
        sale_id=sale.id,
        return_items_data=[{'product_id': p.id, 'quantity': 1}],
        reason='Defective packaging',
        refund_method='CASH',
        user_id=admin_user.id
    )

    assert ret.total_refund_amount == Decimal('15.00')
    assert p.stock_quantity == 30  # Stock restored!
    assert sale.status == SaleStatus.RETURNED


def test_transaction_rollback_on_failure(sample_pack_product, admin_user, db_session):
    """
    If any line in a multi-item sale fails (e.g. invalid product ID),
    the entire transaction must rollback so no items are deducted.
    """
    p = sample_pack_product
    initial_stock = p.stock_quantity
    initial_sales_count = Sale.query.count()

    with pytest.raises(ValueError):
        create_sale_transaction(
            items_data=[
                {'product_id': p.id, 'unit_type': 'PACK', 'quantity': 1},
                {'product_id': 99999, 'unit_type': 'PIECE', 'quantity': 1}  # Invalid product
            ],
            user_id=admin_user.id
        )

    # Verify atomic rollback
    assert p.stock_quantity == initial_stock
    assert Sale.query.count() == initial_sales_count
