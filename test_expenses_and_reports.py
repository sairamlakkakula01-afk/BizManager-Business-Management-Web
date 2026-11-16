from datetime import datetime, timezone, timedelta
from decimal import Decimal
from app.models.expense import ExpenseCategory, Expense
from app.services.sales_service import create_sale_transaction
from app.services.report_service import get_profit_and_loss, get_cash_flow_summary, get_dashboard_metrics


def test_expense_and_profit_loss_calculations(sample_pack_product, admin_user, db_session):
    """
    Test income statement logic:
    Sale: 1 pack = $15.00
    COGS: 10 pieces * $0.80 = $8.00
    Gross Profit: $15.00 - $8.00 = $7.00
    Expense: Rent = $3.00
    Net Profit: $7.00 - $3.00 = $4.00
    """
    p = sample_pack_product
    cat = ExpenseCategory(name='Rent')
    db_session.add(cat)
    db_session.flush()

    exp = Expense(
        category_id=cat.id,
        amount=Decimal('3.00'),
        payment_method='BANK_TRANSFER',
        description='Shop rent installment',
        created_by_id=admin_user.id
    )
    db_session.add(exp)

    # Sale
    create_sale_transaction(
        items_data=[{'product_id': p.id, 'unit_type': 'PACK', 'quantity': 1}],
        payment_amount=Decimal('15.00'),
        user_id=admin_user.id
    )

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=1)
    end = now + timedelta(days=1)

    pnl = get_profit_and_loss(start, end)
    assert pnl['gross_sales'] == Decimal('15.00')
    assert pnl['cogs'] == Decimal('8.00')
    assert pnl['gross_profit'] == Decimal('7.00')
    assert pnl['total_expenses'] == Decimal('3.00')
    assert pnl['net_profit'] == Decimal('4.00')


def test_cash_flow_summary(sample_pack_product, admin_user, db_session):
    """
    Cash inflow: Customer pays $15.00 cash for invoice.
    Cash outflow: $5.00 electricity expense.
    Net Cash Flow: $15.00 - $5.00 = +$10.00.
    """
    p = sample_pack_product
    cat = ExpenseCategory(name='Utilities')
    db_session.add(cat)
    db_session.flush()

    exp = Expense(
        category_id=cat.id,
        amount=Decimal('5.00'),
        payment_method='CASH',
        description='Power bill',
        created_by_id=admin_user.id
    )
    db_session.add(exp)

    create_sale_transaction(
        items_data=[{'product_id': p.id, 'unit_type': 'PACK', 'quantity': 1}],
        payment_amount=Decimal('15.00'),
        payment_method='CASH',
        user_id=admin_user.id
    )

    now = datetime.now(timezone.utc)
    cf = get_cash_flow_summary(now - timedelta(days=1), now + timedelta(days=1))
    assert cf['total_inflows'] == Decimal('15.00')
    assert cf['expense_outflows'] == Decimal('5.00')
    assert cf['net_cash_flow'] == Decimal('10.00')
