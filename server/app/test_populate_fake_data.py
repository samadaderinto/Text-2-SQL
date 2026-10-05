from io import StringIO
import pytest
from django.core.management import call_command

from app.models import Cart, CartItem, Customer, Order, Product, Query, Store, User


@pytest.mark.django_db
def test_populate_fake_data_creates_models():
    out = StringIO()
    call_command(
        "populate_fake_data",
        products=25,
        customers=20,
        orders=15,
        queries=10,
        email="test_owner@audql.test",
        password="TestPassword123!",
        no_es=True,
        stdout=out,
    )

    output = out.getvalue()
    assert "Fake data generation complete!" in output

    user = User.objects.get(email="test_owner@audql.test")
    assert user.is_superuser is True
    assert user.check_password("TestPassword123!")

    store = Store.objects.get(user=user)
    assert store is not None

    products = Product.objects.filter(store=store)
    assert products.count() == 25
    for p in products:
        assert p.available >= 0
        assert p.price > 0
        assert p.rating >= 0
        assert p.category in dict(Product.CATEGORIES_CHOICE)

    customers = Customer.objects.filter(user=user)
    assert customers.count() == 20
    emails = [c.email for c in customers]
    assert len(emails) == len(set(emails))  # Unique emails

    orders = Order.objects.filter(user=user)
    assert orders.count() == 15
    order_ids = [o.id for o in orders]
    assert len(order_ids) == len(set(order_ids))  # Unique IDs
    for o in orders:
        assert o.status in ["paid", "pending", "cancelled"]
        assert o.total >= 0
        assert o.subtotal >= 0
        assert o.cart.ordered is True

    cart_items = CartItem.objects.filter(cart__user=user)
    assert cart_items.count() >= 15
    for item in cart_items:
        assert item.quantity >= 1
        assert item.product in products

    queries = Query.objects.filter(user=user)
    assert queries.count() == 10
    for q in queries:
        assert q.action in ["SELECT", "UPDATE", "DELETE", "INSERT"]


@pytest.mark.django_db
def test_populate_fake_data_idempotent_repopulation():
    out = StringIO()
    # First run
    call_command(
        "populate_fake_data",
        products=5,
        customers=5,
        orders=5,
        queries=5,
        email="idempotent@audql.test",
        no_es=True,
        stdout=out,
    )

    # Second run without flush should append safely
    call_command(
        "populate_fake_data",
        products=5,
        customers=5,
        orders=5,
        queries=5,
        email="idempotent@audql.test",
        no_es=True,
        stdout=out,
    )

    user = User.objects.get(email="idempotent@audql.test")
    assert Product.objects.filter(store__user=user).count() == 10
    assert Customer.objects.filter(user=user).count() == 10
    assert Order.objects.filter(user=user).count() == 10


@pytest.mark.django_db
def test_seed_demo_delegates_to_large():
    out = StringIO()
    call_command("seed_demo", large=True, no_flush=True, no_es=True, stdout=out)
    output = out.getvalue()
    assert "Fake data generation complete!" in output
    assert Product.objects.count() >= 500
    assert Customer.objects.count() >= 500
    assert Order.objects.count() >= 1000


@pytest.mark.django_db
def test_production_safety_guard_blocks_accidental_runs():
    from unittest.mock import patch
    from django.core.management.base import CommandError

    with patch("django.conf.settings.DEPLOY_ENV", "production"):
        with pytest.raises(CommandError, match="SAFETY BLOCK"):
            call_command("seed_demo")

        with pytest.raises(CommandError, match="SAFETY BLOCK"):
            call_command("populate_fake_data")
