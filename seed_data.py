from decimal import Decimal
from datetime import datetime, timezone, timedelta
from app.extensions import db
from app.models.user import User, Role
from app.models.settings import BusinessSettings
from app.models.inventory import Category, Product, StockMovement, MovementType
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.expense import ExpenseCategory, Expense
from app.services.sales_service import create_sale_transaction
from app.services.purchase_service import create_purchase_order, receive_goods_for_purchase


def run_seed():
    print("Seeding BizManager demonstration database...")

    # 1. Initialize Business Settings
    settings = BusinessSettings.get_settings()
    settings.business_name = "BizManager Commercial Hub"
    settings.legal_name = "BizManager Enterprise LLC"
    settings.tax_id = "US-98472910-B"
    settings.phone = "+1 (555) 019-2834"
    settings.email = "contact@bizmanager-demo.local"
    settings.address = "100 Business Parkway, Suite 400, Austin, TX 78701"
    settings.currency_symbol = "$"
    settings.tax_rate = Decimal("8.25")
    settings.invoice_prefix = "INV"
    settings.purchase_prefix = "PO"
    db.session.commit()

    # 2. Users with secure hashed passwords
    users_data = [
        ("admin", "admin@bizmanager.local", "System Administrator", Role.ADMIN, "Admin@12345"),
        ("manager", "manager@bizmanager.local", "Sarah Jenkins (Store Manager)", Role.MANAGER, "Manager@12345"),
        ("staff", "staff@bizmanager.local", "David Miller (Cashier / Staff)", Role.STAFF, "Staff@12345")
    ]

    users = {}
    for uname, email, full_name, role, pwd in users_data:
        existing = User.query.filter_by(username=uname).first()
        if not existing:
            u = User(username=uname, email=email, full_name=full_name, role=role, is_active=True)
            u.set_password(pwd)
            db.session.add(u)
            db.session.flush()
            users[uname] = u
        else:
            users[uname] = existing
    db.session.commit()

    admin_user = users["admin"]

    # 3. Product Categories
    categories = {}
    cat_names = [
        ("Beverages & Drinks", "Soft drinks, juices, mineral water, coffee & tea"),
        ("Office & Stationery", "Paper, pens, folders, and office essentials"),
        ("Electronics & Gadgets", "Cables, chargers, peripherals, and electronic accessories"),
        ("Pantry & Snacks", "Biscuits, chips, chocolates, and confectionery")
    ]
    for cname, cdesc in cat_names:
        c = Category.query.filter_by(name=cname).first()
        if not c:
            c = Category(name=cname, description=cdesc)
            db.session.add(c)
            db.session.flush()
        categories[cname] = c
    db.session.commit()

    # 4. Products demonstrating Pack and Piece stock tracking
    sample_products = [
        {
            "sku": "BEV-TEA-001",
            "barcode": "8901234567890",
            "name": "Organic Earl Grey Tea (Pack of 20 bags)",
            "category": categories["Beverages & Drinks"],
            "uom": "bags",
            "pieces_per_pack": 20,
            "pack_price": Decimal("18.00"),
            "piece_price": Decimal("1.20"),
            "purchase_cost": Decimal("0.55"),  # $0.55 per individual tea bag ($11 per pack)
            "stock_quantity": 80,  # Exactly 4 full packs
            "min_stock_level": 25
        },
        {
            "sku": "STA-PEN-002",
            "barcode": "8901234567891",
            "name": "Gel Ink Ballpoint Pens (Pack of 10)",
            "category": categories["Office & Stationery"],
            "uom": "pens",
            "pieces_per_pack": 10,
            "pack_price": Decimal("15.00"),
            "piece_price": Decimal("2.00"),
            "purchase_cost": Decimal("0.85"),  # $0.85 per pen ($8.50 per pack)
            "stock_quantity": 45,  # 4 packs and 5 pens
            "min_stock_level": 15
        },
        {
            "sku": "BEV-SODA-003",
            "barcode": "8901234567892",
            "name": "Craft Cola 330ml (Pack of 6 cans)",
            "category": categories["Beverages & Drinks"],
            "uom": "cans",
            "pieces_per_pack": 6,
            "pack_price": Decimal("7.50"),
            "piece_price": Decimal("1.75"),
            "purchase_cost": Decimal("0.80"),  # $0.80 per can
            "stock_quantity": 36,  # 6 packs
            "min_stock_level": 12
        },
        {
            "sku": "OFF-PPR-004",
            "barcode": "8901234567893",
            "name": "Premium A4 Multipurpose Copy Paper",
            "category": categories["Office & Stationery"],
            "uom": "reams",
            "pieces_per_pack": 1,
            "pack_price": Decimal("9.50"),
            "piece_price": Decimal("9.50"),
            "purchase_cost": Decimal("5.20"),
            "stock_quantity": 25,
            "min_stock_level": 10
        },
        {
            "sku": "ELE-CAB-005",
            "barcode": "8901234567894",
            "name": "Braided USB-C Fast Charging Cable (1m)",
            "category": categories["Electronics & Gadgets"],
            "uom": "pcs",
            "pieces_per_pack": 1,
            "pack_price": Decimal("14.99"),
            "piece_price": Decimal("14.99"),
            "purchase_cost": Decimal("4.50"),
            "stock_quantity": 2,  # Low stock trigger (<= 5)
            "min_stock_level": 5
        }
    ]

    products = {}
    for p_info in sample_products:
        prod = Product.query.filter_by(sku=p_info["sku"]).first()
        if not prod:
            prod = Product(
                sku=p_info["sku"],
                barcode=p_info["barcode"],
                name=p_info["name"],
                category_id=p_info["category"].id,
                uom=p_info["uom"],
                pieces_per_pack=p_info["pieces_per_pack"],
                pack_price=p_info["pack_price"],
                piece_price=p_info["piece_price"],
                purchase_cost=p_info["purchase_cost"],
                stock_quantity=p_info["stock_quantity"],
                min_stock_level=p_info["min_stock_level"],
                is_active=True
            )
            db.session.add(prod)
            db.session.flush()

            movement = StockMovement(
                product_id=prod.id,
                movement_type=MovementType.INITIAL,
                quantity=prod.stock_quantity,
                unit_cost=prod.purchase_cost,
                reference_type='Initial',
                reference_id='OPENING-BALANCE',
                notes="Initial inventory balance upon setup",
                created_by_id=admin_user.id
            )
            db.session.add(movement)
        products[p_info["sku"]] = prod
    db.session.commit()

    # 5. Customers
    cust_data = [
        ("Apex Retail Stores", "+1 (555) 234-5678", "accounts@apexretail.local", "45 Market Street, Suite 12", Decimal("1500.00")),
        ("Starlight Coffee & Co.", "+1 (555) 345-6789", "orders@starlightcafe.local", "88 Broadway Ave", Decimal("600.00")),
        ("Highland Creative Agency", "+1 (555) 456-7890", "ops@highlandagency.local", "12 Innovation Blvd", Decimal("1000.00"))
    ]
    customers = {}
    for cname, cphone, cemail, caddr, climit in cust_data:
        c = Customer.query.filter_by(name=cname).first()
        if not c:
            c = Customer(name=cname, phone=cphone, email=cemail, address=caddr, credit_limit=climit, balance=Decimal("0.00"), is_active=True)
            db.session.add(c)
            db.session.flush()
        customers[cname] = c
    db.session.commit()

    # 6. Suppliers
    supp_data = [
        ("Global Direct Imports LLC", "Global Direct Imports LLC", "+1 (555) 678-9012", "sales@globaldirect.local", "900 Harbor Blvd, Port Arthur, TX"),
        ("Metro Wholesale Distributors", "Metro Distributors Inc.", "+1 (555) 789-0123", "orders@metrowholesale.local", "1500 Logistics Way, Dallas, TX")
    ]
    suppliers = {}
    for sname, cname, sphone, semail, saddr in supp_data:
        s = Supplier.query.filter_by(name=sname).first()
        if not s:
            s = Supplier(name=sname, company_name=cname, phone=sphone, email=semail, address=saddr, balance=Decimal("0.00"), is_active=True)
            db.session.add(s)
            db.session.flush()
        suppliers[sname] = s
    db.session.commit()

    # 7. Expense Categories & Expenses
    exp_cats = ["Facility Rent", "Electricity & Utilities", "Logistics & Shipping", "Staff Welfare", "Marketing"]
    cat_objs = {}
    for ec in exp_cats:
        c = ExpenseCategory.query.filter_by(name=ec).first()
        if not c:
            c = ExpenseCategory(name=ec)
            db.session.add(c)
            db.session.flush()
        cat_objs[ec] = c
    db.session.commit()

    # Sample operating expenses
    if Expense.query.count() == 0:
        expenses_to_add = [
            (cat_objs["Facility Rent"], Decimal("1200.00"), "Monthly warehouse lease payment", "BANK_TRANSFER"),
            (cat_objs["Electricity & Utilities"], Decimal("185.50"), "Commercial power bill", "BANK_TRANSFER"),
            (cat_objs["Logistics & Shipping"], Decimal("74.20"), "Courier express dispatch", "CASH"),
            (cat_objs["Staff Welfare"], Decimal("45.00"), "Breakroom snacks and coffee supplies", "CASH")
        ]
        for ec, amt, desc, pmethod in expenses_to_add:
            exp = Expense(
                category_id=ec.id,
                expense_date=datetime.now(timezone.utc) - timedelta(days=2),
                amount=amt,
                payment_method=pmethod,
                description=desc,
                created_by_id=admin_user.id
            )
            db.session.add(exp)
        db.session.commit()

    # 8. Sample Purchase Order & Received Stock
    if suppliers and len(products) > 0:
        supplier = list(suppliers.values())[0]
        pen_prod = products["STA-PEN-002"]
        po = create_purchase_order(
            supplier_id=supplier.id,
            items_data=[{
                "product_id": pen_prod.id,
                "quantity": 20,  # 20 pens
                "unit_cost": Decimal("0.80")
            }],
            tax_amount=Decimal("1.32"),
            notes="Initial replenishment order",
            user_id=admin_user.id
        )
        receive_goods_for_purchase(po.id, user_id=admin_user.id)

    # 9. Sample Sales Invoices (Pack & Piece Sales)
    # Sale 1: Pack sale of Tea + Individual pieces of Pens
    tea_prod = products["BEV-TEA-001"]
    pen_prod = products["STA-PEN-002"]
    cust_apex = customers["Apex Retail Stores"]

    sale1 = create_sale_transaction(
        items_data=[
            {"product_id": tea_prod.id, "unit_type": "PACK", "quantity": 1},   # 1 pack of tea (20 bags) = $18.00
            {"product_id": pen_prod.id, "unit_type": "PIECE", "quantity": 2}   # 2 loose pens = $4.00
        ],
        customer_id=cust_apex.id,
        discount_amount=Decimal("2.00"),
        tax_rate=Decimal("8.25"),
        payment_amount=Decimal("21.65"),  # Paid in full
        payment_method="CARD",
        notes="Apex regular order - 1 pack tea, 2 loose pens",
        user_id=admin_user.id
    )

    print("✓ Demonstration database successfully seeded with realistic operational data!")


if __name__ == "__main__":
    from app import create_app
    app = create_app('development')
    with app.app_context():
        run_seed()
