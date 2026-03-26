"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-26 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("phone", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("CUSTOMER", "SALES_REP", "ADMIN", name="userrole"),
            nullable=False,
            server_default="CUSTOMER",
        ),
        sa.Column("address_cuba", sa.String(500), nullable=True),
        sa.Column("province_cuba", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_phone", "users", ["phone"])

    # Orders
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("sales_rep_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "SUBMITTED", "ESTIMATED", "AWAITING_DEPOSIT", "DEPOSIT_RECEIVED",
                "PRICE_VERIFICATION", "PURCHASING", "SHIPPED_TO_MIAMI",
                "RECEIVED_IN_MIAMI", "IN_TRANSIT_TO_CUBA", "RECEIVED_IN_CUBA",
                "CATEGORIZING", "FINAL_INVOICE_SENT", "COMPLETED", "CANCELLED",
                name="orderstatus",
            ),
            nullable=False,
            server_default="SUBMITTED",
        ),
        sa.Column("service_fee_pct", sa.Float(), nullable=False, server_default="15.0"),
        sa.Column("subtotal_estimate", sa.Float(), nullable=True),
        sa.Column("service_fee_amount", sa.Float(), nullable=True),
        sa.Column("total_estimate", sa.Float(), nullable=True),
        sa.Column("deposit_amount", sa.Float(), nullable=True),
        sa.Column("final_total", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("customer_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_orders_customer_id", "orders", ["customer_id"])
    op.create_index("ix_orders_status", "orders", ["status"])

    # Order Items
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("product_url", sa.String(2000), nullable=False),
        sa.Column("product_name", sa.String(500), nullable=True),
        sa.Column("product_image_url", sa.String(2000), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("estimated_price", sa.Float(), nullable=True),
        sa.Column("actual_price", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("variant", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])

    # Payments
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("recorded_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("payment_type", sa.Enum("CASH", "WIRE", name="paymenttype"), nullable=False),
        sa.Column("phase", sa.Enum("DEPOSIT", "FINAL", name="paymentphase"), nullable=False),
        sa.Column("reference", sa.String(200), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_payments_order_id", "payments", ["order_id"])

    # Shipments
    op.create_table(
        "shipments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False, unique=True),
        sa.Column(
            "shipping_type",
            sa.Enum("EXPRESS_AIR", "STANDARD_AIR", "MARITIME", name="shippingtype"),
            nullable=True,
        ),
        sa.Column("actual_weight_lbs", sa.Float(), nullable=True),
        sa.Column("actual_cost_usd", sa.Float(), nullable=True),
        sa.Column("markup_usd", sa.Float(), nullable=True),
        sa.Column("customs_estimate", sa.Float(), nullable=True),
        sa.Column("customs_actual", sa.Float(), nullable=True),
        sa.Column("tracking_number", sa.String(200), nullable=True),
        sa.Column("shipped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("arrived_miami_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("arrived_cuba_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Price Checks
    op.create_table(
        "price_checks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_item_id", sa.Integer(), sa.ForeignKey("order_items.id"), nullable=False),
        sa.Column("checked_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("original_price", sa.Float(), nullable=False),
        sa.Column("current_price", sa.Float(), nullable=False),
        sa.Column("price_changed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("client_notified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("client_confirmed", sa.Boolean(), nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_price_checks_order_item_id", "price_checks", ["order_item_id"])


def downgrade() -> None:
    op.drop_table("price_checks")
    op.drop_table("shipments")
    op.drop_table("payments")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS orderstatus")
    op.execute("DROP TYPE IF EXISTS paymenttype")
    op.execute("DROP TYPE IF EXISTS paymentphase")
    op.execute("DROP TYPE IF EXISTS shippingtype")
