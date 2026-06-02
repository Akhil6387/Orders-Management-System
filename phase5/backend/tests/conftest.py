"""
Test Configuration and Fixtures
Full fixture suite for unit tests (SQLite) and integration tests (PostgreSQL via env).
"""
import os
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.base import Base
from app.api.dependencies import get_db
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus

# ---------------------------------------------------------------------------
# Database engine selection
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "sqlite:///:memory:"
)

_connect_args = {}
_pool_kwargs: dict = {}

if TEST_DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}
    _pool_kwargs = {"poolclass": StaticPool}

engine = create_engine(TEST_DATABASE_URL, connect_args=_connect_args, **_pool_kwargs)

# Enable FK enforcement for SQLite (mirrors PostgreSQL behaviour)
if TEST_DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------------------------
# Core fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def db_session():
    """Fresh database for every test function."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient wired to the per-test DB session."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Raw data fixtures (dict payloads – mirror API request bodies)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_product_data():
    return {
        "product_name": "Widget Pro",
        "sku": "WGT-001",
        "price": 29.99,
        "quantity_in_stock": 100,
    }


@pytest.fixture
def sample_customer_data():
    return {
        "full_name": "Alice Smith",
        "email": "alice@example.com",
        "phone_number": "+14155550100",
    }


@pytest.fixture
def another_product_data():
    return {
        "product_name": "Gadget Basic",
        "sku": "GDG-001",
        "price": 9.99,
        "quantity_in_stock": 50,
    }


@pytest.fixture
def another_customer_data():
    return {
        "full_name": "Bob Jones",
        "email": "bob@example.com",
        "phone_number": "+14155550200",
    }


# ---------------------------------------------------------------------------
# ORM-level fixtures (persist objects directly, bypass HTTP layer)
# ---------------------------------------------------------------------------

@pytest.fixture
def persisted_product(db_session, sample_product_data):
    """A Product row already committed to the test DB."""
    p = Product(
        product_name=sample_product_data["product_name"],
        sku=sample_product_data["sku"].upper(),
        price=Decimal(str(sample_product_data["price"])),
        quantity_in_stock=sample_product_data["quantity_in_stock"],
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture
def persisted_customer(db_session, sample_customer_data):
    """A Customer row already committed to the test DB."""
    c = Customer(
        full_name=sample_customer_data["full_name"],
        email=sample_customer_data["email"].lower(),
        phone_number=sample_customer_data["phone_number"],
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


@pytest.fixture
def persisted_order(db_session, persisted_product, persisted_customer):
    """A pending Order with one item, already committed."""
    order = Order(
        customer_id=persisted_customer.id,
        total_amount=Decimal("29.99"),
        status=OrderStatus.PENDING,
    )
    db_session.add(order)
    db_session.flush()

    item = OrderItem(
        order_id=order.id,
        product_id=persisted_product.id,
        quantity=1,
        unit_price=persisted_product.price,
    )
    db_session.add(item)

    # Deduct stock to mirror service behaviour
    persisted_product.quantity_in_stock -= 1
    db_session.commit()
    db_session.refresh(order)
    return order


# ---------------------------------------------------------------------------
# Helper / factory aliases (keep existing tests compatible)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_product(sample_product_data):
    """Alias kept for backward compatibility."""
    return sample_product_data


@pytest.fixture
def sample_customer(sample_customer_data):
    """Alias kept for backward compatibility."""
    return sample_customer_data
