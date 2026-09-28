import json
import tempfile
from pathlib import Path

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from kink import di
from unittest.mock import Mock, patch

from utils.algorithms import TokenGenerator, auth_token
from .models import (
    Cart,
    Customer,
    Notification,
    Order,
    Product,
    Store,
    User,
    generate_order_id,
)
from .services import SearchService
from .views import parse_non_negative_int, parse_positive_int


class ParsePositiveIntTests(TestCase):
    def test_returns_integer_for_valid_input(self):
        self.assertEqual(parse_positive_int("12", 1, "limit"), 12)
        self.assertEqual(parse_positive_int(None, 15, "limit"), 15)

    def test_rejects_zero_and_non_integer_input(self):
        from rest_framework.exceptions import ValidationError

        for value in ("0", "invalid"):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    parse_positive_int(value, 1, "limit")

    def test_non_negative_parser_accepts_zero_and_rejects_negative_input(self):
        from rest_framework.exceptions import ValidationError

        self.assertEqual(parse_non_negative_int("0", 0, "offset"), 0)
        with self.assertRaises(ValidationError):
            parse_non_negative_int("-1", 0, "offset")

    def test_test_database_uses_sqlite(self):
        from django.db import connection

        self.assertEqual(connection.vendor, "sqlite")


class ProductModelTests(TestCase):
    def test_product_currency_comes_from_its_store(self):
        user = User.objects.create_user(email="owner@example.com", password="ValidPass1!")
        store = Store.objects.create(
            user=user,
            email=user.email,
            name="Owner Store",
            bio="",
            currency="GBP",
        )

        product = Product.objects.create(
            store=store,
            title="Notebook",
            description="A lined notebook",
            price="4.50",
            available=10,
            category="books",
            currency="USD",
        )

        self.assertEqual(product.currency, "GBP")

    def test_stock_update_rejects_negative_and_overlarge_quantities(self):
        user = User.objects.create_user(email="stock@example.com", password="ValidPass1!")
        store = Store.objects.create(
            user=user, name="Stock Store", bio="", currency="USD"
        )
        product = Product.objects.create(
            store=store,
            title="Notebook",
            description="A lined notebook",
            price="4.50",
            available=10,
            category="books",
            currency="USD",
        )

        product.set_availability(3)
        self.assertEqual(product.available, 7)

        for quantity in (-1, 8):
            with self.subTest(quantity=quantity):
                with self.assertRaises(ValueError):
                    product.set_availability(quantity)
        self.assertEqual(product.available, 7)

    def test_order_id_generator_returns_unique_length_ids(self):
        first_id = generate_order_id()
        second_id = generate_order_id()

        self.assertEqual(len(first_id), 15)
        self.assertNotEqual(first_id, second_id)


class UtilityFunctionTests(TestCase):
    def test_token_generator_invalidates_token_when_activation_changes(self):
        user = User.objects.create_user(email="owner@example.com", password="ValidPass1!")
        generator = TokenGenerator()
        token = generator.make_token(user)

        self.assertTrue(generator.check_token(user, token))
        user.is_active = True
        user.save(update_fields=["is_active"])
        self.assertFalse(generator.check_token(user, token))

    def test_auth_token_returns_access_and_refresh_tokens(self):
        user = User.objects.create_user(email="owner@example.com", password="ValidPass1!")

        tokens = auth_token(user)

        self.assertEqual(set(tokens), {"access", "refresh"})
        self.assertTrue(tokens["access"])
        self.assertTrue(tokens["refresh"])


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AuthenticationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_signup_creates_account_and_login_requires_activation(self):
        signup_response = self.client.post(
            "/auth/signup/",
            {"email": "new-store@example.com", "password": "ValidPass1!"},
            format="json",
        )

        self.assertEqual(signup_response.status_code, 201)
        user = User.objects.get(email="new-store@example.com")
        self.assertFalse(user.is_active)
        self.assertTrue(Store.objects.filter(user=user).exists())
        self.assertTrue(Notification.objects.filter(user=user).exists())

        invalid_login_response = self.client.post(
            "/auth/login/",
            {"email": user.email, "password": "IncorrectPass1!"},
            format="json",
        )
        self.assertEqual(invalid_login_response.status_code, 400)

        inactive_login_response = self.client.post(
            "/auth/login/",
            {"email": user.email, "password": "ValidPass1!"},
            format="json",
        )
        self.assertEqual(inactive_login_response.status_code, 403)

        user.is_active = True
        user.save(update_fields=["is_active"])
        login_response = self.client.post(
            "/auth/login/",
            {"email": user.email, "password": "ValidPass1!"},
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access", login_response.data["token"])
        self.assertIn("refresh", login_response.data["token"])
        self.assertEqual(login_response.data["data"]["email"], user.email)

    def test_signup_rejects_duplicate_email(self):
        User.objects.create_user(email="taken@example.com", password="ValidPass1!")

        response = self.client.post(
            "/auth/signup/",
            {"email": "taken@example.com", "password": "ValidPass1!"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_signup_rejects_weak_password(self):
        response = self.client.post(
            "/auth/signup/",
            {"email": "weak@example.com", "password": "short"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(email="weak@example.com").exists())

    def test_activation_endpoint_activates_account(self):
        user = User.objects.create_user(
            email="pending@example.com", password="ValidPass1!"
        )
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = TokenGenerator().make_token(user)

        response = self.client.get(f"/auth/activate/{uidb64}/{token}/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "http://localhost:4174/auth/signin")
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    @override_settings(FRONTEND_URL="https://shop.example.test")
    def test_activation_redirect_uses_configured_frontend_url(self):
        user = User.objects.create_user(
            email="configured@example.com", password="ValidPass1!"
        )
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = TokenGenerator().make_token(user)

        response = self.client.get(f"/auth/activate/{uidb64}/{token}/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "https://shop.example.test/auth/signin")

    def test_activation_rejects_invalid_identifier_without_exposing_exception(self):
        malformed_encoding_response = self.client.get(
            "/auth/activate/%%%/not-a-token/"
        )
        malformed_id_response = self.client.get(
            f"/auth/activate/{urlsafe_base64_encode(force_bytes('not-an-id'))}/not-a-token/"
        )

        for response in (malformed_encoding_response, malformed_id_response):
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data, {"uidb64": "Invalid user identifier."})

    def test_logout_blacklists_refresh_token(self):
        user = User.objects.create_user(
            email="logout@example.com",
            password="ValidPass1!",
            is_active=True,
        )
        self.client.force_authenticate(user=user)
        refresh_token = auth_token(user)["refresh"]

        logout_response = self.client.post(
            "/auth/logout/", {"refresh": refresh_token}, format="json"
        )

        self.assertEqual(logout_response.status_code, 205)
        self.assertEqual(logout_response.content, b"")
        refresh_response = self.client.post(
            "/auth/refresh-token/", {"refresh": refresh_token}, format="json"
        )
        self.assertEqual(refresh_response.status_code, 400)


class ProductApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            email="owner@example.com", password="ValidPass1!"
        )
        self.store = Store.objects.create(
            user=self.owner,
            email=self.owner.email,
            name="Owner Store",
            bio="",
            currency="USD",
        )
        self.product = Product.objects.create(
            store=self.store,
            title="Blue Notebook",
            description="A lined notebook",
            price="4.50",
            available=10,
            category="books",
            currency="USD",
        )

    def test_search_returns_only_the_authenticated_users_products(self):
        other_user = User.objects.create_user(
            email="other@example.com", password="ValidPass1!"
        )
        other_store = Store.objects.create(
            user=other_user,
            email=other_user.email,
            name="Other Store",
            bio="",
        )
        Product.objects.create(
            store=other_store,
            title="Blue Pen",
            description="A blue pen",
            price="2.00",
            available=5,
            category="books",
            currency="USD",
        )
        self.client.force_authenticate(user=self.owner)

        with patch.object(
            SearchService,
            "search_records",
            return_value=([str(self.product.pk)], 1),
        ):
            response = self.client.get("/product/search/", {"query": "Blue"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["products"][0]["id"], self.product.id)

    def test_search_rejects_non_positive_page_size(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.get("/product/search/", {"limit": "0"})

        self.assertEqual(response.status_code, 400)

    def test_product_create_update_and_delete_endpoints(self):
        self.client.force_authenticate(user=self.owner)

        create_response = self.client.post(
            "/product/create/",
            {
                "title": "Green Pen",
                "description": "A green pen",
                "price": "2.50",
                "available": "4",
                "category": "books",
                "currency": "USD",
            },
            format="multipart",
        )

        self.assertEqual(create_response.status_code, 201, create_response.data)
        created_product = Product.objects.get(title="Green Pen")
        self.assertEqual(created_product.store, self.store)
        self.assertEqual(created_product.currency, self.store.currency)

        update_response = self.client.put(
            "/product/update/",
            {"id": created_product.id, "title": "Green Marker"},
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        created_product.refresh_from_db()
        self.assertEqual(created_product.title, "Green Marker")

        delete_response = self.client.delete(f"/product/delete/{created_product.id}/")
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Product.objects.filter(pk=created_product.id).exists())

    def test_protected_product_endpoint_rejects_anonymous_user(self):
        response = self.client.get("/product/search/")

        self.assertEqual(response.status_code, 401)


class CustomerApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            email="owner@example.com", password="ValidPass1!"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com", password="ValidPass1!"
        )
        self.client.force_authenticate(user=self.owner)

    def test_customer_create_search_and_update_endpoints(self):
        customer_data = {
            "first_name": "Alex",
            "last_name": "Morgan",
            "email": "alex@example.com",
            "phone_number": "+14155552671",
        }

        create_response = self.client.post(
            "/customers/create/", customer_data, format="multipart"
        )
        self.assertEqual(create_response.status_code, 201, create_response.data)
        customer = Customer.objects.get(email=customer_data["email"])
        self.assertEqual(customer.user, self.owner)

        with patch.object(
            SearchService,
            "search_records",
            return_value=([str(customer.pk)], 1),
        ):
            search_response = self.client.get(
                "/customers/search/", {"query": "Alex"}
            )
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(search_response.data["count"], 1)
        self.assertEqual(search_response.data["customers"][0]["id"], customer.id)

        update_response = self.client.put(
            "/customers/update/",
            {
                **customer_data,
                "first_name": "Alexandra",
            },
            format="json",
        )
        self.assertEqual(update_response.status_code, 201, update_response.data)
        customer.refresh_from_db()
        self.assertEqual(customer.first_name, "Alexandra")

    def test_customer_search_is_scoped_to_the_authenticated_user(self):
        Customer.objects.create(
            user=self.other_user,
            first_name="Alex",
            last_name="Other",
            email="other-alex@example.com",
            phone_number="+14155552672",
        )

        with patch.object(SearchService, "search_records", return_value=([], 0)):
            response = self.client.get("/customers/search/", {"query": "Alex"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)


class OrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="ValidPass1!",
            first_name="Order Owner",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com", password="ValidPass1!"
        )
        self.cart = Cart.objects.create(user=self.owner)
        self.order = Order.objects.create(
            user=self.owner,
            cart=self.cart,
            status="pending",
            subtotal="12.50",
            total="12.50",
        )
        self.client.force_authenticate(user=self.owner)

    def test_order_create_update_search_download_and_delete_endpoints(self):
        create_cart = Cart.objects.create(user=self.owner)
        create_response = self.client.post(
            "/orders/create/",
            {
                "cart": create_cart.pk,
                "status": "pending",
                "subtotal": "7.25",
                "total": "7.25",
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201, create_response.data)
        created_order = Order.objects.get(cart=create_cart)
        self.assertEqual(created_order.user, self.owner)

        update_response = self.client.put(
            "/orders/update/",
            {"id": self.order.id, "status": "paid"},
            format="json",
        )
        self.assertEqual(update_response.status_code, 201, update_response.data)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "paid")

        with patch.object(
            SearchService,
            "search_records",
            return_value=([str(self.order.pk)], 1),
        ) as search_records:
            search_response = self.client.get(
                "/orders/search/", {"status": "paid", "limit": 10}
            )
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(search_response.data["count"], 1)
        self.assertEqual(search_response.data["orders"][0]["id"], self.order.id)
        self.assertEqual(
            search_records.call_args.kwargs["filters"],
            {"status": "paid"},
        )

        download_response = self.client.get(f"/orders/download/{self.order.id}/")
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(download_response["Content-Type"], "text/csv")
        self.assertIn(self.order.id, download_response.content.decode())

        all_orders_response = self.client.get("/orders/download/")
        self.assertEqual(all_orders_response.status_code, 200)
        self.assertIn("Order ID", all_orders_response.content.decode())

        delete_response = self.client.delete(f"/orders/delete/{created_order.id}/")
        self.assertEqual(delete_response.status_code, 205)
        self.assertFalse(Order.objects.filter(pk=created_order.id).exists())

    def test_order_csv_escapes_formula_cells(self):
        self.owner.first_name = "=HYPERLINK(\"https://example.test\")"
        self.owner.save(update_fields=["first_name"])

        response = self.client.get(f"/orders/download/{self.order.id}/")
        csv_data = response.content.decode()

        self.assertIn("'=HYPERLINK", csv_data)
        self.assertNotIn(',"=HYPERLINK', csv_data)

    def test_order_csv_escapes_formula_order_identifiers(self):
        order = Order.objects.create(
            id="=1+1",
            user=self.owner,
            cart=self.cart,
            status="pending",
            subtotal="12.50",
            total="12.50",
        )

        response = self.client.get(f"/orders/download/{order.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("'=1+1", response.content.decode())

    def test_order_creation_rejects_another_users_cart(self):
        other_cart = Cart.objects.create(user=self.other_user)

        response = self.client.post(
            "/orders/create/",
            {
                "cart": other_cart.pk,
                "status": "pending",
                "subtotal": "1.00",
                "total": "1.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_order_search_rejects_negative_offset(self):
        response = self.client.get("/orders/search/", {"offset": -1})

        self.assertEqual(response.status_code, 400)


class SettingsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="owner@example.com",
            password="ValidPass1!",
            first_name="Owner",
        )
        self.store = Store.objects.create(
            user=self.user,
            email=self.user.email,
            name="Owner Store",
            bio="Current bio",
        )
        self.notification = Notification.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_store_and_notification_settings_can_be_read_and_updated(self):
        store_response = self.client.get("/settings/store/get/")
        self.assertEqual(store_response.status_code, 200)
        self.assertEqual(store_response.data["name"], "Owner Store")

        store_update_response = self.client.put(
            "/settings/store/update/",
            {"name": "Updated Store", "bio": "Updated bio"},
            format="json",
        )
        self.assertEqual(store_update_response.status_code, 201)
        self.store.refresh_from_db()
        self.assertEqual(self.store.name, "Updated Store")

        notification_response = self.client.get("/settings/notifications/get/")
        self.assertEqual(notification_response.status_code, 200)
        self.assertTrue(notification_response.data["email_notification"])

        notification_update_response = self.client.put(
            "/settings/notifications/update/",
            {"email_notification": False, "sms_notification": True},
            format="json",
        )
        self.assertEqual(notification_update_response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertFalse(self.notification.email_notification)
        self.assertTrue(self.notification.sms_notification)

    def test_admin_settings_can_be_read_and_updated(self):
        get_response = self.client.get("/settings/admin/get/")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.data["email"], self.user.email)

        update_response = self.client.put(
            "/settings/admin/update/",
            {"first_name": "Updated"},
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_admin_password_update_hashes_password_and_validates_strength(self):
        response = self.client.put(
            "/settings/admin/update/",
            {"password": "AnotherStrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("AnotherStrongPass123!"))
        self.assertNotEqual(self.user.password, "AnotherStrongPass123!")

        weak_response = self.client.put(
            "/settings/admin/update/", {"password": "short"}, format="json"
        )
        self.assertEqual(weak_response.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("AnotherStrongPass123!"))


class AuthEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="owner@example.com",
            password="ValidPass1!",
            is_active=True,
        )

    def test_refresh_endpoint_returns_a_new_access_token(self):
        response = self.client.post(
            "/auth/refresh-token/",
            {"refresh": auth_token(self.user)["refresh"]},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["access"])
        self.assertTrue(response.data["refresh"])

    def test_reset_password_request_and_reset_update_password(self):
        with self.settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"):
            request_response = self.client.post(
                "/auth/reset-password/request/",
                {"email": self.user.email},
                format="json",
            )
        self.assertEqual(request_response.status_code, 200)

        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        from django.contrib.auth.tokens import PasswordResetTokenGenerator

        reset_token = PasswordResetTokenGenerator().make_token(self.user)
        reset_response = self.client.post(
            "/auth/reset-password/reset/",
            {
                "uidb64": uidb64,
                "token": reset_token,
                "new_password": "NewStrongPass1!",
            },
            format="json",
        )

        self.assertEqual(reset_response.status_code, 205)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPass1!"))

    def test_reset_password_request_does_not_disclose_unknown_accounts(self):
        from django.core import mail

        with self.settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"):
            known_response = self.client.post(
                "/auth/reset-password/request/",
                {"email": self.user.email},
                format="json",
            )
            unknown_response = self.client.post(
                "/auth/reset-password/request/",
                {"email": "missing@example.com"},
                format="json",
            )

        self.assertEqual(known_response.status_code, 200)
        self.assertEqual(unknown_response.status_code, 200)
        self.assertEqual(known_response.data, unknown_response.data)
        self.assertEqual(len(mail.outbox), 1)

    def test_reset_password_rejects_weak_password_and_malformed_identifier(self):
        weak_response = self.client.post(
            "/auth/reset-password/reset/",
            {
                "uidb64": urlsafe_base64_encode(force_bytes(self.user.pk)),
                "token": "unused",
                "new_password": "short",
            },
            format="json",
        )
        self.assertEqual(weak_response.status_code, 400)

        malformed_uid_response = self.client.post(
            "/auth/reset-password/reset/",
            {
                "uidb64": "%%%not-base64",
                "token": "unused",
                "new_password": "AnotherStrongPass123!",
            },
            format="json",
        )
        self.assertEqual(malformed_uid_response.status_code, 401)

        unknown_uid_response = self.client.post(
            "/auth/reset-password/reset/",
            {
                "uidb64": urlsafe_base64_encode(force_bytes("999999")),
                "token": "unused",
                "new_password": "AnotherStrongPass123!",
            },
            format="json",
        )
        self.assertEqual(unknown_uid_response.status_code, 401)

    def test_invalid_refresh_token_is_rejected(self):
        response = self.client.post(
            "/auth/refresh-token/", {"refresh": "invalid-token"}, format="json"
        )

        self.assertEqual(response.status_code, 400)


class QueryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="owner@example.com", password="ValidPass1!"
        )

    def test_generate_query_endpoint_executes_normalized_plan(self):
        self.client.force_authenticate(user=self.user)
        service = di[SearchService]
        service_response = {
            "status": "success",
            "message": "Found 0 products.",
            "results": [],
        }

        with patch.object(
            service, "generate_query_response", return_value=service_response
        ):
            response = self.client.post(
                "/query/generate/", {"prompt": "list products"}, format="json"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, service_response)

    def test_generate_query_rejects_invalid_plan(self):
        self.client.force_authenticate(user=self.user)
        service = di[SearchService]

        with patch.object(
            service,
            "generate_query_response",
            side_effect=ValueError("Unsupported query resource."),
        ):
            response = self.client.post(
                "/query/generate/", {"prompt": "list products"}, format="json"
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["status"], "error")

    def test_generate_query_requires_authentication(self):
        response = self.client.post(
            "/query/generate/", {"prompt": "list products"}, format="json"
        )

        self.assertEqual(response.status_code, 401)

    def test_search_endpoints_validate_and_forward_search_terms(self):
        self.client.force_authenticate(user=self.user)
        service = di[SearchService]
        with patch.object(
            service, "elastic_search", return_value='{"status":"success","data":[]}'
        ) as elastic_search:
            get_response = self.client.get("/query/search/", {"query": "notebook"})
            post_response = self.client.post(
                "/query/search/", {"search": "pencil"}, format="json"
            )

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(
            [call.args[0] for call in elastic_search.call_args_list],
            ["notebook", "pencil"],
        )

        missing_query = self.client.get("/query/search/")
        self.assertEqual(missing_query.status_code, 400)

    def test_generated_sql_mutation_confirmation_endpoints_remain_disabled(self):
        self.client.force_authenticate(user=self.user)

        update_response = self.client.put(
            "/query/upload/update/", {"query": "UPDATE product SET title='x'"}, format="json"
        )
        delete_response = self.client.delete("/query/upload/delete/")
        create_response = self.client.post(
            "/query/upload/create/", {"query": "INSERT INTO product"}, format="json"
        )

        for response in (update_response, delete_response, create_response):
            with self.subTest(status=response.status_code):
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.data["status"], "error")

    def test_audio_upload_uses_and_cleans_storage_backend_file(self):
        self.client.force_authenticate(user=self.user)
        service = di[SearchService]
        response_payload = {"transcript": "list products", "results": []}
        with tempfile.TemporaryDirectory() as media_root:
            with self.settings(MEDIA_ROOT=media_root):
                uploaded_audio = {}

                def read_audio(user, audio_file):
                    uploaded_audio["bytes"] = audio_file.read()
                    return response_payload

                with patch.object(
                    service,
                    "generate_query_response_from_audio",
                    side_effect=read_audio,
                ):
                    response = self.client.post(
                        "/query/upload/",
                        {
                            "file": SimpleUploadedFile(
                                "recording.webm",
                                b"test audio bytes",
                                content_type="audio/webm",
                            )
                        },
                        format="multipart",
                    )

                self.assertEqual(response.status_code, 200, response.data)
                self.assertEqual(response.data, response_payload)
                self.assertEqual(uploaded_audio["bytes"], b"test audio bytes")
                self.assertEqual(
                    [path for path in Path(media_root).rglob("*") if path.is_file()],
                    [],
                )

    def test_audio_upload_cleans_file_when_processing_fails(self):
        self.client.force_authenticate(user=self.user)
        service = di[SearchService]
        with tempfile.TemporaryDirectory() as media_root:
            with self.settings(MEDIA_ROOT=media_root):
                with patch.object(
                    service,
                    "generate_query_response_from_audio",
                    side_effect=ValueError("unreadable audio"),
                ):
                    response = self.client.post(
                        "/query/upload/",
                        {
                            "file": SimpleUploadedFile(
                                "recording.webm",
                                b"test audio bytes",
                                content_type="audio/webm",
                            )
                        },
                        format="multipart",
                    )

                self.assertEqual(response.status_code, 500)
                self.assertEqual(
                    [path for path in Path(media_root).rglob("*") if path.is_file()],
                    [],
                )


class SearchServiceUnitTests(TestCase):
    def setUp(self):
        self.service = SearchService()

    def test_normalize_query_plan_removes_unsafe_fields_and_bounds_limit(self):
        plan = self.service.normalize_query_plan(
            json.dumps(
                {
                    "resource": "Products",
                    "intent": "search",
                    "search": "  pencil  ",
                    "filters": {"category": "books", "password": "secret"},
                    "sort": "password",
                    "limit": 500,
                }
            )
        )

        self.assertEqual(plan["resource"], "products")
        self.assertEqual(plan["search"], "pencil")
        self.assertEqual(plan["filters"], {"category": "books"})
        self.assertEqual(plan["sort"], "-created")
        self.assertEqual(plan["limit"], 100)

    def test_normalize_query_plan_rejects_unknown_resources_and_intents(self):
        for plan in (
            {"resource": "users", "intent": "list"},
            {"resource": "products", "intent": "delete"},
        ):
            with self.subTest(plan=plan):
                with self.assertRaises(ValueError):
                    self.service.normalize_query_plan(json.dumps(plan))

    def test_normalize_query_plan_rejects_malformed_object_and_filter_values(self):
        for content in (
            json.dumps(["products"]),
            json.dumps({"resource": "products", "filters": ["title"]}),
            json.dumps({"resource": "products", "filters": {"title": ["not", "scalar"]}}),
        ):
            with self.subTest(content=content):
                with self.assertRaises(ValueError):
                    self.service.normalize_query_plan(content)

    def test_normalize_query_plan_rejects_malformed_sort_and_uses_safe_default(self):
        plan = self.service.normalize_query_plan(
            json.dumps({"resource": "products", "sort": "---created"})
        )

        self.assertEqual(plan["sort"], "-created")

    @override_settings(OPENAI_API_KEY=None)
    def test_query_service_reports_missing_openai_configuration(self):
        service = SearchService()

        with self.assertRaisesRegex(ValueError, "not configured"):
            service.build_query_plan("list products")
        self.assertIsNone(service.audio_to_text(None))

    def test_search_records_queries_elasticsearch_with_owner_filter_and_paging(self):
        client = Mock()
        client.indices.exists.return_value = True
        client.search.return_value = {
            "hits": {
                "hits": [{"_id": "123"}],
                "total": {"value": 1},
            }
        }
        with patch("app.services.get_elasticsearch_client", return_value=client):
            ids, total = self.service.search_records(
                "products",
                type("UserIdentity", (), {"pk": 42})(),
                query="notebook",
                offset=10,
                limit=5,
            )

        self.assertEqual((ids, total), (["123"], 1))
        request = client.search.call_args.kwargs
        self.assertEqual(request["index"], "audql-products")
        self.assertEqual(request["from_"], 10)
        self.assertEqual(request["size"], 5)
        self.assertEqual(
            request["query"]["bool"]["filter"],
            [{"term": {"owner_id": "42"}}],
        )

    def test_elastic_search_returns_only_user_owned_documents(self):
        client = Mock()
        client.indices.exists.return_value = True
        client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_index": "audql-products",
                        "_source": {"entity_id": "1", "owner_id": "42"},
                    }
                ]
            }
        }
        with patch("app.services.get_elasticsearch_client", return_value=client):
            result = self.service.elastic_search(
                "notebook",
                type("UserIdentity", (), {"pk": 42})(),
            )

        self.assertEqual(result["data"][0]["resource"], "products")
        self.assertEqual(
            client.search.call_args.kwargs["query"]["bool"]["filter"],
            [{"term": {"owner_id": "42"}}],
        )

    def test_execute_query_plan_only_returns_the_current_users_records(self):
        own_store = Store.objects.create(
            user=User.objects.create_user(
                email="owner@example.com", password="ValidPass1!"
            ),
            name="Owner",
            bio="",
        )
        other_store = Store.objects.create(
            user=User.objects.create_user(
                email="other@example.com", password="ValidPass1!"
            ),
            name="Other",
            bio="",
        )
        own_product = Product.objects.create(
            store=own_store,
            title="Blue pencil",
            description="Writing tool",
            price="1.00",
            available=4,
            category="books",
            currency="USD",
        )
        Product.objects.create(
            store=other_store,
            title="Blue pencil",
            description="Other owner's item",
            price="1.00",
            available=4,
            category="books",
            currency="USD",
        )
        plan = {
            "resource": "products",
            "intent": "search",
            "search": "Blue",
            "filters": {},
            "sort": "-created",
            "limit": 10,
        }

        result = self.service.execute_query_plan(own_store.user, plan)

        self.assertEqual(result["total_count"], 1)
        self.assertEqual(result["results"][0]["id"], own_product.id)

    def test_parse_openai_response(self):
        parsed = self.service.parse_openai_response(
            json.dumps(
                {
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "message": {"content": "SELECT * FROM products"},
                        }
                    ]
                }
            )
        )
        self.assertEqual(parsed, "SELECT * FROM products")

    def test_sql_generated_mutations_are_disabled(self):
        self.assertEqual(
            json.loads(self.service.confirm_and_execute_create(None))["status"],
            "error",
        )
        self.assertEqual(
            json.loads(self.service.confirm_and_execute_update(None, {}))["status"],
            "error",
        )
        self.assertEqual(
            json.loads(self.service.confirm_and_execute_delete(None))["status"],
            "error",
        )
