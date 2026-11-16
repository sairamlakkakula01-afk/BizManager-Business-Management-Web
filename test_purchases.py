from decimal import Decimal
from app.models.purchases import PurchaseStatus, PurchasePaymentStatus
from app.services.purchase_service import (
    create_purchase_order, receive_goods_for_purchase, record_supplier_payment
)


def test_purchase_order_does_not_increase_stock_until_received(sample_pack_product, sample_supplier, admin_user):
    """
    Prompt requirement:
    'Increase stock only when goods are actually received, not merely when a purchase order is created.'
    """
    p = sample_pack_product
    s = sample_supplier
    assert p.stock_quantity == 30
    assert s.balance == Decimal('0.00')

    po = create_purchase_order(
        supplier_id=s.id,
        items_data=[{
            'product_id': p.id,
            'quantity': 20,
            'unit_cost': Decimal('1.00')
        }],
        tax_amount=Decimal('2.00'),
        user_id=admin_user.id
    )

    # 1. At ORDERED status, stock is unchanged and supplier balance is unchanged
    assert po.status == PurchaseStatus.ORDERED
    assert po.total_amount == Decimal('22.00')
    assert p.stock_quantity == 30
    assert s.balance == Decimal('0.00')

    # 2. Confirm goods received
    receive_goods_for_purchase(po.id, user_id=admin_user.id)
    assert po.status == PurchaseStatus.RECEIVED
    assert p.stock_quantity == 50  # 30 + 20
    assert s.balance == Decimal('22.00')  # Accounts payable recorded


def test_supplier_payment(sample_pack_product, sample_supplier, admin_user):
    s = sample_supplier
    po = create_purchase_order(
        supplier_id=s.id,
        items_data=[{'product_id': sample_pack_product.id, 'quantity': 10, 'unit_cost': Decimal('1.00')}],
        user_id=admin_user.id
    )
    receive_goods_for_purchase(po.id, user_id=admin_user.id)
    assert s.balance == Decimal('10.00')

    # Pay supplier
    record_supplier_payment(
        purchase_id=po.id,
        amount=Decimal('10.00'),
        user_id=admin_user.id
    )

    assert po.payment_status == PurchasePaymentStatus.PAID
    assert po.balance_amount == Decimal('0.00')
    assert s.balance == Decimal('0.00')
