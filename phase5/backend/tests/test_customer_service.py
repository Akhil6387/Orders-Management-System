"""
Unit Tests – CustomerService
Tests business logic for customer CRUD operations.
"""
import pytest

from app.services.customer_service import CustomerService
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.core.exceptions import NotFoundError, DuplicateError, ValidationError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _svc(db):
    return CustomerService(db)


def _create(db, *, full_name="Test User", email="test@example.com", phone="+15005550100"):
    return _svc(db).create_customer(
        CustomerCreate(full_name=full_name, email=email, phone_number=phone)
    )


# ---------------------------------------------------------------------------
# create_customer
# ---------------------------------------------------------------------------

class TestCreateCustomer:
    def test_creates_with_correct_fields(self, db_session):
        svc = _svc(db_session)
        customer = svc.create_customer(
            CustomerCreate(
                full_name="  Jane Doe  ",
                email="JANE@Example.COM",
                phone_number="+1234567890",
            )
        )
        assert customer.id is not None
        assert customer.full_name == "Jane Doe"      # stripped
        assert customer.email == "jane@example.com"  # lowercased
        assert customer.phone_number == "+1234567890"

    def test_email_normalised_to_lowercase(self, db_session):
        customer = _create(db_session, email="UPPER@DOMAIN.COM")
        assert customer.email == "upper@domain.com"

    def test_raises_on_duplicate_email(self, db_session):
        _create(db_session, email="dup@example.com")
        with pytest.raises(DuplicateError) as exc_info:
            _create(db_session, email="dup@example.com", full_name="Someone Else")
        assert "dup@example.com" in str(exc_info.value).lower()

    def test_raises_on_duplicate_email_case_insensitive(self, db_session):
        _create(db_session, email="dup2@example.com")
        with pytest.raises(DuplicateError):
            _create(db_session, email="DUP2@example.com", full_name="Other")

    def test_phone_is_optional(self, db_session):
        svc = _svc(db_session)
        customer = svc.create_customer(
            CustomerCreate(full_name="No Phone", email="nophone@example.com")
        )
        assert customer.phone_number is None


# ---------------------------------------------------------------------------
# get_customer
# ---------------------------------------------------------------------------

class TestGetCustomer:
    def test_returns_existing_customer(self, db_session, persisted_customer):
        svc = _svc(db_session)
        result = svc.get_customer(persisted_customer.id)
        assert result.id == persisted_customer.id
        assert result.email == persisted_customer.email

    def test_raises_not_found_for_missing_id(self, db_session):
        with pytest.raises(NotFoundError):
            _svc(db_session).get_customer(99999)


# ---------------------------------------------------------------------------
# get_customers
# ---------------------------------------------------------------------------

class TestGetCustomers:
    def test_empty_list_when_none_exist(self, db_session):
        customers, total = _svc(db_session).get_customers()
        assert customers == []
        assert total == 0

    def test_returns_all_with_count(self, db_session):
        _create(db_session, email="a@x.com")
        _create(db_session, email="b@x.com")
        customers, total = _svc(db_session).get_customers()
        assert total == 2
        assert len(customers) == 2

    def test_pagination(self, db_session):
        for i in range(6):
            _create(db_session, email=f"page{i}@x.com")
        page1, total = _svc(db_session).get_customers(page=1, page_size=4)
        assert total == 6
        assert len(page1) == 4

    def test_search_by_name(self, db_session):
        _create(db_session, full_name="Alice Wonder", email="alice@x.com")
        _create(db_session, full_name="Bob Builder", email="bob@x.com")
        results, total = _svc(db_session).get_customers(search="Alice")
        assert total == 1
        assert results[0].full_name == "Alice Wonder"

    def test_search_by_email(self, db_session):
        _create(db_session, email="find.me@x.com")
        _create(db_session, email="other@x.com")
        results, total = _svc(db_session).get_customers(search="find.me")
        assert total == 1

    def test_search_case_insensitive(self, db_session):
        _create(db_session, full_name="CamelCased", email="camel@x.com")
        results, _ = _svc(db_session).get_customers(search="camelcased")
        assert len(results) == 1


# ---------------------------------------------------------------------------
# update_customer
# ---------------------------------------------------------------------------

class TestUpdateCustomer:
    def test_updates_name(self, db_session, persisted_customer):
        updated = _svc(db_session).update_customer(
            persisted_customer.id, CustomerUpdate(full_name="New Name")
        )
        assert updated.full_name == "New Name"

    def test_updates_email_normalised(self, db_session, persisted_customer):
        updated = _svc(db_session).update_customer(
            persisted_customer.id, CustomerUpdate(email="NEWEMAIL@X.COM")
        )
        assert updated.email == "newemail@x.com"

    def test_updates_phone(self, db_session, persisted_customer):
        updated = _svc(db_session).update_customer(
            persisted_customer.id, CustomerUpdate(phone_number="+19998887777")
        )
        assert updated.phone_number == "+19998887777"

    def test_raises_not_found_for_missing_customer(self, db_session):
        with pytest.raises(NotFoundError):
            _svc(db_session).update_customer(99999, CustomerUpdate(full_name="x"))

    def test_raises_duplicate_when_email_taken(self, db_session, persisted_customer):
        other = _create(db_session, email="taken@x.com", full_name="Other")
        with pytest.raises(DuplicateError):
            _svc(db_session).update_customer(
                persisted_customer.id, CustomerUpdate(email="taken@x.com")
            )

    def test_same_email_update_does_not_raise(self, db_session, persisted_customer):
        """Updating other fields while keeping same email should succeed."""
        updated = _svc(db_session).update_customer(
            persisted_customer.id,
            CustomerUpdate(email=persisted_customer.email, full_name="Renamed"),
        )
        assert updated.email == persisted_customer.email
        assert updated.full_name == "Renamed"


# ---------------------------------------------------------------------------
# delete_customer
# ---------------------------------------------------------------------------

class TestDeleteCustomer:
    def test_deletes_customer_without_orders(self, db_session, persisted_customer):
        result = _svc(db_session).delete_customer(persisted_customer.id)
        assert result is True
        with pytest.raises(NotFoundError):
            _svc(db_session).get_customer(persisted_customer.id)

    def test_raises_not_found_for_missing_customer(self, db_session):
        with pytest.raises(NotFoundError):
            _svc(db_session).delete_customer(99999)

    def test_raises_validation_error_when_customer_has_orders(
        self, db_session, persisted_order, persisted_customer
    ):
        with pytest.raises(ValidationError) as exc_info:
            _svc(db_session).delete_customer(persisted_customer.id)
        assert "order" in str(exc_info.value).lower()
