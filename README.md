# BizManager — Complete Business Management Web Application

BizManager is a production-ready, full-stack business management web application built with Python and Flask. It provides small and medium-sized enterprises (SMEs) with daily operational control over inventory, sales billing, purchase orders, customer receivables, supplier payables, operating expenses, and financial profitability reports.

---

## 1. Architecture & Technology Stack

- **Backend Framework**: **Python 3.13+** with **Flask** using the Application Factory pattern (`create_app`) and modular Blueprints.
- **ORM & Database**: **SQLAlchemy 2.0+** and **Flask-SQLAlchemy 3.1+**. Defaults to **SQLite** for development with a migration path to **PostgreSQL**.
- **Database Migrations**: **Flask-Migrate** (Alembic) for schema versioning and database updates.
- **Form Security & Validation**: **Flask-WTF** and **WTForms** providing server-side data validation and CSRF (Cross-Site Request Forgery) protection.
- **Authentication & Authorization**: **Flask-Login** for session handling with role-based decorators (`ADMIN`, `MANAGER`, `STAFF`) and Werkzeug password hashing.
- **Brute-Force Protection**: **Flask-Limiter** rate limiting on authentication endpoints (e.g. max 15 login attempts per minute).
- **Financial & Inventory Accuracy**: Decimal representation (`Numeric(12, 2)`) avoids floating-point drift. Perpetual **Moving Weighted-Average Costing (WAC)** accurately tracks Cost of Goods Sold (COGS), Gross Profit, and Balance Sheet Valuation.
- **Pack & Piece Functionality**: Complete multi-unit stock tracking. Physical stock is maintained in base units (pieces) while permitting sales and inventory display in full packs and loose pieces.
- **Invoicing & PDF Generation**: Native HTML print stylesheet (`@media print`) and **ReportLab** PDF generation for downloadable invoices.
- **Interactive Visualizations**: **Chart.js** for 7-day sales and gross profit trend curves.
- **Automated Testing**: **Pytest** with 23 automated tests covering atomic transactions, permissions, pack/piece conversions, and financial logic.

---

## 2. Directory Layout

```text
bizmanager/
├── app/
│   ├── __init__.py           # Application Factory (create_app), Jinja filters, error handlers
│   ├── config.py             # Development, Testing, and Production configurations
│   ├── extensions.py         # Extensions initialization (db, login_manager, migrate, csrf, limiter)
│   ├── models/               # Normalized SQLAlchemy Database Models
│   │   ├── __init__.py       # Model exports
│   │   ├── user.py           # User, Role, AuditLog
│   │   ├── settings.py       # BusinessSettings (singleton profile & defaults)
│   │   ├── inventory.py      # Category, Product, StockMovement, StockAdjustment
│   │   ├── customer.py       # Customer (credit limits, accounts receivable)
│   │   ├── supplier.py       # Supplier (accounts payable)
│   │   ├── sales.py          # Sale, SaleItem, Payment, SaleReturn, SaleReturnItem
│   │   ├── purchases.py      # Purchase, PurchaseItem, PurchasePayment, PurchaseReturn
│   │   └── expense.py        # ExpenseCategory, Expense
│   ├── services/             # Clean Business Logic Layer
│   │   ├── audit_service.py     # System action logging
│   │   ├── inventory_service.py # Pack/piece breakdown, WAC costing, stock deductions/returns
│   │   ├── sales_service.py     # Atomic sales invoices, payment balance, returns
│   │   ├── purchase_service.py  # Purchase orders, physical goods receiving, supplier payments
│   │   └── report_service.py    # Live dashboard metrics, P&L, Cash Flow, trends
│   ├── routes/               # Flask Blueprints
│   │   ├── utils.py          # @role_required decorator
│   │   ├── auth.py           # Authentication, profile, user management
│   │   ├── dashboard.py      # Live operational dashboard & Chart.js API
│   │   ├── products.py       # Inventory catalog, adjustments, movements
│   │   ├── sales.py          # POS checkout, invoices, PDF downloads, returns
│   │   ├── purchases.py      # Supplier orders, receiving, payments
│   │   ├── customers.py      # Customer ledger, payment collections
│   │   ├── suppliers.py      # Supplier ledger, disbursements
│   │   ├── expenses.py       # Operating expenses, receipt uploads
│   │   ├── reports.py        # Sales, Inventory Valuation, P&L, Cash Flow, CSV exports
│   │   └── settings.py       # Business profile, prefixes, logo, audit panel
│   ├── forms/                # Flask-WTF Forms with validation
│   ├── static/
│   │   ├── css/style.css     # Accessible, responsive CSS stylesheet
│   │   └── js/
│   │       ├── main.js       # Sidebar toggle, alert dismissal, confirmation dialogs
│   │       ├── pos.js        # Dynamic billing engine (Pack/Piece calculation)
│   │       └── charts.js     # Chart.js visualization
│   └── templates/            # Jinja2 Templates (Dashboard, POS, Reports, etc.)
├── instance/                 # SQLite database and uploaded receipts/logos
├── migrations/               # Alembic database version control
├── scripts/
│   ├── backup_db.py          # Transactional SQLite backup and restore CLI
│   └── seed_data.py          # Realistic demonstration data generator
├── tests/                    # 23 Pytest automated test cases
├── requirements.txt          # Python dependencies
├── pytest.ini                # Pytest configuration
├── .env.example              # Environment variables template
├── .gitignore
├── run.py                    # Application launcher and management CLI
└── README.md
```

---

## 3. Installation & Startup Commands

### On macOS / Linux

1. **Clone or navigate to the project directory**:
   ```bash
   cd /Users/sairam/website
   ```

2. **Create and activate a Python virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database schema and apply migrations**:
   ```bash
   flask --app run.py db upgrade
   ```

5. **Create your initial administrator account** (Safe prompt with hidden password input):
   ```bash
   flask --app run.py create-admin
   ```
   *(Prompts for Username, Email, Full Name, and Password)*

6. *(Optional)* **Populate sample business demonstration data**:
   ```bash
   flask --app run.py seed-demo
   ```
   *Demo accounts created:*
   - **Admin**: `admin` / `Admin@12345`
   - **Manager**: `manager` / `Manager@12345`
   - **Staff**: `staff` / `Staff@12345`

7. **Run the local development server**:
   ```bash
   python run.py
   ```
   Access the application at `http://127.0.0.1:5000`.

---

### On Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app run.py db upgrade
flask --app run.py create-admin
python run.py
```

---

## 4. User Roles and Security Permissions

BizManager enforces role-based authorization at the server level via the `@role_required` decorator:

| Feature / Section | Owner / Admin | Manager | Staff |
| :--- | :---: | :---: | :---: |
| **Sales Invoices & POS** | Full Access | Full Access | Full Access |
| **View Catalog & Stock** | Full Access | Full Access | Full Access |
| **Add / Edit Products** | Full Access | Full Access | Read-Only |
| **Manual Stock Adjustments**| Full Access | Full Access | Restricted |
| **Purchases & Receiving** | Full Access | Full Access | Read-Only |
| **Customer Ledger & Collections**| Full Access | Full Access | Full Access |
| **Operating Expenses** | Full Access | Full Access | Full Access |
| **Financial Reports & P&L** | Full Access | Full Access | Restricted |
| **Business Settings & Logo** | Full Access | Restricted | Restricted |
| **User Accounts & Activation**| Full Access | Restricted | Restricted |
| **Security Audit Logs** | Full Access | Restricted | Restricted |

---

## 5. Module Usage Guide

### 5.1 Dashboard
- **Live Metrics**: Shows Today's Sales, Period Revenue, COGS, Gross Profit, Net Operating Profit, Operating Expenses, Goods Purchased, Customer Receivables, and Supplier Payables.
- **Chart.js Trends**: 7-day line chart contrasting Sales Revenue with Gross Profit.
- **Stock Alert Card**: Highlights items whose stock in pieces is at or below the minimum threshold.
- **Date Filters**: Filter metrics by any start and end date.

### 5.2 Products & Pack-and-Piece Inventory
- **Single Unit vs. Pack Configuration**: Set `pieces_per_pack`. If `pieces_per_pack = 10`, stock is stored in base pieces and automatically formatted as `"X packs and Y pieces"`.
- **Separate Pack & Piece Prices**: Sell at either the wholesale pack price or retail individual piece price.
- **Weighted-Average Cost (WAC)**: Dynamically updates whenever goods are received on purchase orders:
  $$\text{New Cost} = \frac{(\text{Current Stock} \times \text{Current Cost}) + (\text{Incoming Qty} \times \text{Incoming Cost})}{\text{Current Stock} + \text{Incoming Qty}}$$
- **Stock Adjustment**: Perform manual physical reconciliations or damage write-offs with mandatory audit reason logging.
- **Stock Movement Log**: Perpetual audit trail tracking every unit received, sold, returned, or adjusted.

### 5.3 Sales & Billing (POS)
- **Pack & Piece Selection**: Choose whether to sell by pack or individual piece. The system calculates base pieces and validates stock availability before checkout.
- **Dynamic Calculation**: Subtotals, customer discounts, and sales taxes are calculated server-side.
- **Customer Account vs. Walk-In**: Supports walk-in customers or registered accounts with credit limits.
- **Payment Methods**: Cash, Credit/Debit Card, Bank Transfer, UPI, Cheque.
- **Print & PDF Invoices**: Generate a clean A4 printout or downloadable PDF invoice using ReportLab.
- **Sales Returns**: Select individual lines and quantities to return; items are automatically restocked into warehouse inventory and refunds/balances adjusted.

### 5.4 Purchases & Supplier Management
- **Two-Step Receiving**: Creating a purchase order (status `ORDERED`) records the order without touching inventory. Stock increases **only** when goods are confirmed as `RECEIVED`.
- **Accounts Payable**: Supplier balances automatically increase upon goods receipt and decrease when disbursements are recorded.

### 5.5 Customers & Receivables
- Track customer contact information, lifetime purchases, and credit limits.
- Record debt collections against outstanding balances.

### 5.6 Expenses & Cash Flow
- Log operating expenses by category (Rent, Utilities, Shipping, Marketing, Payroll).
- Secure receipt upload with filename hashing.
- Distinguishes cash inflows, outflows, and net cash flow.

### 5.7 Reports & Analytics
- **Sales Report**: Filterable date ranges with CSV export.
- **Inventory Valuation Report**: Balance sheet valuation of inventory with CSV export.
- **Profit & Loss Statement (P&L)**:
  - Gross Profit = Net Revenue (Gross Sales - Discounts) - COGS
  - Gross Margin % = (Gross Profit / Net Revenue) * 100
  - Net Profit = Gross Profit - Operating Expenses
  - Net Margin % = (Net Profit / Net Revenue) * 100
- **Cash Flow Statement**: Net Cash Generated = Customer Inflows - (Supplier Outflows + Operating Expenses).

---

## 6. Automated Testing Report

BizManager includes 23 automated tests executed with **Pytest**:

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.1, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/sairam/website
configfile: pytest.ini
testpaths: tests
plugins: flask-1.3.0
collected 23 items

tests/test_auth.py::test_login_success PASSED                            [  4%]
tests/test_auth.py::test_login_invalid_password PASSED                   [  8%]
tests/test_auth.py::test_login_deactivated_account PASSED                [ 13%]
tests/test_auth.py::test_logout PASSED                                   [ 17%]
tests/test_auth.py::test_role_permissions_admin_vs_staff PASSED          [ 21%]
tests/test_auth.py::test_unauthenticated_redirect PASSED                 [ 26%]
tests/test_expenses_and_reports.py::test_expense_and_profit_loss_calculations PASSED [ 30%]
tests/test_expenses_and_reports.py::test_cash_flow_summary PASSED        [ 34%]
tests/test_inventory.py::test_pack_and_piece_conversions_and_display PASSED [ 39%]
tests/test_inventory.py::test_inventory_valuation_weighted_average_cost PASSED [ 43%]
tests/test_inventory.py::test_stock_adjustment PASSED                    [ 47%]
tests/test_inventory.py::test_negative_stock_adjustment_rejected PASSED  [ 52%]
tests/test_purchases.py::test_purchase_order_does_not_increase_stock_until_received PASSED [ 56%]
tests/test_purchases.py::test_supplier_payment PASSED                    [ 60%]
tests/test_sales.py::test_pack_sale_stock_deduction_and_totals PASSED    [ 65%]
tests/test_sales.py::test_piece_sale_stock_deduction PASSED              [ 69%]
tests/test_sales.py::test_mixed_pack_and_piece_sale PASSED               [ 73%]
tests/test_sales.py::test_insufficient_stock_raises_error PASSED         [ 78%]
tests/test_sales.py::test_discounts_and_taxes_calculated_server_side PASSED [ 82%]
tests/test_sales.py::test_partial_payment_and_customer_balance PASSED    [ 86%]
tests/test_sales.py::test_customer_credit_limit_enforced PASSED          [ 91%]
tests/test_sales.py::test_sales_return_and_restocking PASSED             [ 95%]
tests/test_sales.py::test_transaction_rollback_on_failure PASSED         [100%]

============================== 23 passed in 1.94s ==============================
```

To run the test suite at any time:
```bash
pytest
```

---

## 7. Sample Step-by-Step Workflow

1. **Create Product**: Navigate to **Products & Stock** → **+ Add Product**. Enter SKU `SNK-CHIP-01`, Name `Artisan Potato Chips (Box of 12 bags)`, Base UOM `bags`, `Pieces Per Pack = 12`, `Piece Price = $2.00`, `Pack Price = $20.00`, `Purchase Cost = $0.90`, `Opening Stock = 24` (2 packs).
2. **Purchase Stock**: Go to **Purchases** → **+ Create Purchase Order**. Select supplier and order 24 bags @ $0.80/bag. Notice stock stays at 24 bags.
3. **Receive Goods**: Open the Purchase Order and click **Confirm Goods Received**. Stock increases to 48 bags (4 packs). The moving average cost recalculates automatically.
4. **Complete a Sale**: Go to **POS / New Sale**. Select the product, choose `PACK`, quantity `1` ($20.00). Add a second line with `PIECE`, quantity `2` ($4.00). Subtotal is $24.00. Enter $24.00 in Amount Paid and click **Complete & Generate Invoice**. Remaining stock is now `2 packs and 10 bags` (34 bags).
5. **View Financial Report**: Navigate to **Reports & P&L** → **Profit & Loss Statement**. View Net Sales Revenue, Cost of Goods Sold, and Gross Profit calculated from real database transactions.

---

## 8. Database Backup & Restore Utility

BizManager includes a transactional database backup script utilizing SQLite's online backup API:

- **Create a Backup**:
  ```bash
  python scripts/backup_db.py backup
  ```
  *(Creates a timestamped snapshot in `instance/backups/bizmanager_backup_YYYYMMDD_HHMMSS.sqlite3`)*

- **List Existing Backups**:
  ```bash
  python scripts/backup_db.py list
  ```

- **Restore Database**:
  ```bash
  python scripts/backup_db.py restore instance/backups/bizmanager_backup_20261027_151556.sqlite3
  ```
  *(Automatically creates a safety backup of your current database before overwriting)*

---

## 9. Production Deployment & Security Checklist

Before deploying BizManager to a live internet server or processing real financial records:

- [ ] **Set a Strong Secret Key**: Generate a 64-character secret key via `python -c "import secrets; print(secrets.token_hex(32))"` and set `SECRET_KEY` in `.env`.
- [ ] **Switch to PostgreSQL**: For concurrent multi-user production, set `DATABASE_URL=postgresql://user:password@host:5432/dbname`.
- [ ] **Use a Production WSGI Server**: Run behind **Gunicorn** or **uWSGI** with an **Nginx** reverse proxy (e.g. `gunicorn -w 4 -b 127.0.0.1:8000 run:app`).
- [ ] **Enable HTTPS / SSL**: Configure TLS certificates (e.g. via Let's Encrypt / Certbot) and ensure `SESSION_COOKIE_SECURE = True`.
- [ ] **Persistent Rate Limiting**: Configure `RATELIMIT_STORAGE_URI=redis://localhost:6379/0` in production.
- [ ] **Automate Daily Backups**: Schedule a daily cron job for `python scripts/backup_db.py backup` with off-site cloud replication (e.g., S3 or Google Cloud Storage).
- [ ] **File Storage**: For distributed deployments, configure cloud object storage (e.g., AWS S3 or Google Cloud Storage) for user receipt uploads.
