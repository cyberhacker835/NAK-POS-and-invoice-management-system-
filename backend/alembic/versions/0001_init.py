from alembic import op
import sqlalchemy as sa


revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255)),
        sa.Column('is_active', sa.Boolean(), default=True),
    )

    op.create_table(
        'businesses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('logo_path', sa.String(length=512)),
        sa.Column('address_line1', sa.String(length=255)),
        sa.Column('address_line2', sa.String(length=255)),
        sa.Column('contact_number1', sa.String(length=64)),
        sa.Column('contact_number2', sa.String(length=64)),
        sa.Column('trn', sa.String(length=64)),
        sa.Column('manager_signature_path', sa.String(length=512)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('business_id', sa.Integer(), sa.ForeignKey('businesses.id')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('sku', sa.String(length=128)),
        sa.Column('price_aed', sa.Numeric(12, 2), nullable=False),
        sa.Column('stock_qty', sa.Integer(), default=0),
    )

    op.create_table(
        'customers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('business_id', sa.Integer(), sa.ForeignKey('businesses.id')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('contact', sa.String(length=255)),
        sa.Column('trn', sa.String(length=64)),
    )

    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('business_id', sa.Integer(), sa.ForeignKey('businesses.id')),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id')),
        sa.Column('number', sa.String(length=64), unique=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date()),
        sa.Column('notes', sa.Text()),
        sa.Column('subtotal_aed', sa.Numeric(12, 2), default=0),
        sa.Column('vat_aed', sa.Numeric(12, 2), default=0),
        sa.Column('total_aed', sa.Numeric(12, 2), default=0),
        sa.Column('status', sa.String(length=32), default='unpaid'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        'invoice_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('invoice_id', sa.Integer(), sa.ForeignKey('invoices.id')),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id')),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('quantity', sa.Integer(), default=1),
        sa.Column('unit_price_aed', sa.Numeric(12, 2), default=0),
        sa.Column('line_total_aed', sa.Numeric(12, 2), default=0),
    )


def downgrade() -> None:
    op.drop_table('invoice_items')
    op.drop_table('invoices')
    op.drop_table('customers')
    op.drop_table('products')
    op.drop_table('businesses')
    op.drop_table('users')

