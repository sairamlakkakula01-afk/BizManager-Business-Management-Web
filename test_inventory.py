import pytest
from decimal import Decimal
from app.models.inventory import Product, MovementType
from app.services.inventory_service import (
    adjust_stock, update_weighted_average_cost, InsufficientStockError
)


def test_pack_and_piece_conversions_and_display(sample_pack_product):
    """
    Direct test of the user specification:
    - 1 pack contains 10 pieces.
    - Initial stock is 3 packs = 30 pieces.
    - Display remaining stock as 3 packs.
    """
    p = sample_pack_product
    assert p.stock_quantity == 30
    assert p.pieces_per_pack == 10
    assert p.packs_count == 3
    assert p.remaining_pieces_count == 0
    assert p.formatted_stock == "3 packs"

    # Simulate selling 1 pack (10 pieces)
    p.stock_quantity -= 10
    assert p.stock_quantity == 20
    assert p.packs_count == 2
    assert p.remaining_pieces_count == 0
    assert p.formatted_stock == "2 packs"

    # Simulate selling 2 individual pieces
    p.stock_quantity -= 2
    assert p.stock_quantity == 18
    assert p.packs_count == 1
    assert p.remaining_pieces_count == 8
    assert p.formatted_stock == "1 pack and 8 pens"

    # Simulate stock falling below 1 pack (e.g. 5 pieces left)
    p.stock_quantity = 5
    assert p.packs_count == 0
    assert p.remaining_pieces_count == 5
    assert p.formatted_stock == "5 pens"


def test_inventory_valuation_weighted_average_cost(sample_pack_product):
    """
    Valuation = base pieces * weighted-average cost
    Initial: 30 pieces @ $0.80 = $24.00
    """
    p = sample_pack_product
    assert p.stock_valuation == Decimal('24.00')

    # Receiving 20 new pieces @ $1.00 each:
    # WAC = (30 * 0.80 + 20 * 1.00) / (30 + 20) = (24 + 20) / 50 = 44 / 50 = $0.88
    new_cost = update_weighted_average_cost(p, incoming_qty=20, incoming_unit_cost=Decimal('1.00'))
    assert new_cost == Decimal('0.88')
    p.stock_quantity += 20
    assert p.stock_valuation == Decimal('50') * Decimal('0.88')  # $44.00


def test_stock_adjustment(sample_pack_product, admin_user, db_session):
    p = sample_pack_product
    assert p.stock_quantity == 30

    # Adjust stock to 25 due to damage
    adj = adjust_stock(
        product=p,
        new_quantity=25,
        reason='Damaged / Broken',
        notes='5 pens damaged in shipping',
        user_id=admin_user.id
    )
    db_session.commit()

    assert p.stock_quantity == 25
    assert adj.quantity_before == 30
    assert adj.quantity_after == 25
    assert adj.difference == -5
    assert adj.reason == 'Damaged / Broken'


def test_negative_stock_adjustment_rejected(sample_pack_product, admin_user):
    with pytest.raises(ValueError):
        adjust_stock(
            product=sample_pack_product,
            new_quantity=-5,
            reason='Error',
            user_id=admin_user.id
        )
