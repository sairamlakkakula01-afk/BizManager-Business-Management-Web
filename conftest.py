import pytest
from decimal import Decimal
from app import create_app
from app.extensions import db as _db
from app.models.user import User, Role
from app.models.settings import BusinessSettings
from app.models.inventory import Category, Product, StockMovement, MovementType
from app.models.customer import Customer
from app.models.supplier import Supplier


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db_session(app):
    with app.app_context():
        _db.create_all()
        # Initialize default settings
        BusinessSettings.get_settings()
        yield _db.session
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app, db_session):
    return app.test_client()


@pytest.fixture
def admin_user(db_session):
    user = User(
        username='admin',
        email='admin@bizmanager.test',
        full_name='Admin User',
        role=Role.ADMIN,
        is_active=True
    )
    user.set_password('AdminSecure123!')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def manager_user(db_session):
    user = User(
        username='manager',
        email='manager@bizmanager.test',
        full_name='Manager User',
        role=Role.MANAGER,
        is_active=True
    )
    user.set_password('ManagerSecure123!')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def staff_user(db_session):
    user = User(
        username='staff',
        email='staff@bizmanager.test',
        full_name='Staff User',
        role=Role.STAFF,
        is_active=True
    )
    user.set_password('StaffSecure123!')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_pack_product(db_session, admin_user):
    """
    Standard test product:
    - 1 pack = 10 pieces
    - Initial stock = 3 packs = 30 pieces
    - Piece price: $2.00
    - Pack price: $15.00
    - Purchase cost: $0.80 per piece
    """
    cat = Category(name='Stationery')
    db_session.add(cat)
    db_session.flush()

    product = Product(
        sku='PEN-PACK-01',
        name='Ballpoint Pens (Pack of 10)',
        category_id=cat.id,
        uom='pens',
        pieces_per_pack=10,
        piece_price=Decimal('2.00'),
        pack_price=Decimal('15.00'),
        purchase_cost=Decimal('0.80'),
        stock_quantity=30,  # 3 full packs
        min_stock_level=5,
        is_active=True
    )
    db_session.add(product)
    db_session.flush()

    m = StockMovement(
        product_id=product.id,
        movement_type=MovementType.INITIAL,
        quantity=30,
        unit_cost=Decimal('0.80'),
        reference_type='Initial',
        reference_id='INIT',
        created_by_id=admin_user.id
    )
    db_session.add(m)
    db_session.commit()
    return product


@pytest.fixture
def sample_customer(db_session):
    customer = Customer(
        name='Acme Enterprises',
        phone='+1 555-0100',
        email='billing@acme.test',
        credit_limit=Decimal('500.00'),
        balance=Decimal('0.00'),
        is_active=True
    )
    db_session.add(customer)
    db_session.commit()
    return customer


@pytest.fixture
def sample_supplier(db_session):
    supplier = Supplier(
        name='Apex Wholesalers',
        company_name='Apex Wholesalers LLC',
        phone='+1 555-0200',
        email='sales@apex.test',
        balance=Decimal('0.00'),
        is_active=True
    )
    db_session.add(supplier)
    db_session.commit()
    return supplier
