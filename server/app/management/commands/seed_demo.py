from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import (
    Cart,
    CartItem,
    Customer,
    Notification,
    Order,
    Product,
    Query,
    Store,
    User,
)


class Command(BaseCommand):
    help = "Flush the local database and seed it with demo data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-flush",
            action="store_true",
            help="Seed demo data without flushing existing rows first.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["no_flush"]:
            call_command("flush", interactive=False, verbosity=0)

        password = "DemoPass123!"
        users = [
            self.create_user(
                email="owner@audql.test",
                password=password,
                first_name="Amara",
                last_name="Okafor",
                is_staff=True,
                is_superuser=True,
            ),
            self.create_user(
                email="manager@audql.test",
                password=password,
                first_name="Noah",
                last_name="Stone",
            ),
            self.create_user(
                email="analyst@audql.test",
                password=password,
                first_name="Maya",
                last_name="Chen",
            ),
        ]

        stores = [
            self.create_store(
                user=users[0],
                username="amara-market",
                name="Amara Market",
                bio="Everyday electronics, books, and accessories for busy teams.",
                phone="+14155550100",
                currency="USD",
            ),
            self.create_store(
                user=users[1],
                username="northline",
                name="Northline Outfitters",
                bio="Outdoor gear, sports goods, and useful travel basics.",
                phone="+14155550101",
                currency="USD",
            ),
            self.create_store(
                user=users[2],
                username="chen-supply",
                name="Chen Supply Co.",
                bio="Office, computing, and smart-home products with quick delivery.",
                phone="+14155550102",
                currency="USD",
            ),
        ]

        products = [
            self.create_product(stores[0], "Noise-Canceling Headphones", "Bluetooth headphones with soft ear pads and long battery life.", "129.99", 42, "electronics", "4.70", 118),
            self.create_product(stores[0], "Portable USB-C Hub", "Seven-port hub for laptops, tablets, and compact workstations.", "49.95", 65, "computing", "4.45", 86),
            self.create_product(stores[0], "SQL Pocket Guide", "Compact reference book for analysts learning practical SQL.", "24.50", 120, "books", "4.80", 203),
            self.create_product(stores[1], "Trail Running Shoes", "Lightweight shoes with grippy soles for weekend trails.", "89.00", 31, "sports", "4.35", 54),
            self.create_product(stores[1], "Insulated Rain Jacket", "Packable outwear with taped seams and breathable lining.", "139.00", 18, "outwear", "4.60", 72),
            self.create_product(stores[1], "Stainless Water Bottle", "Double-wall bottle that keeps drinks cold through long days.", "22.00", 88, "beverages", "4.25", 147),
            self.create_product(stores[2], "Mechanical Keyboard", "Low-profile keyboard with quiet tactile switches.", "99.95", 27, "computing", "4.75", 91),
            self.create_product(stores[2], "Smart Desk Lamp", "Adjustable lamp with warm, cool, and focus lighting modes.", "64.00", 34, "electronics", "4.40", 63),
            self.create_product(stores[2], "Tablet Stand", "Foldable aluminum stand for tablets and small laptops.", "28.75", 76, "tablets", "4.15", 134),
        ]

        for user_index, user in enumerate(users):
            Notification.objects.create(
                user=user,
                email_notification=True,
                sms_notification=user_index == 1,
            )
            self.create_customers(user, user_index)
            self.create_queries(user)

        self.create_order(users[0], [products[0], products[2]], [1, 2], "paid")
        self.create_order(users[0], [products[1]], [3], "pending")
        self.create_order(users[1], [products[3], products[5]], [2, 4], "paid")
        self.create_order(users[1], [products[4]], [1], "cancelled")
        self.create_order(users[2], [products[6], products[8]], [1, 2], "pending")
        self.create_order(users[2], [products[7]], [2], "paid")

        Cart.objects.create(user=users[0], ordered=False)
        open_cart = Cart.objects.create(user=users[1], ordered=False)
        CartItem.objects.create(cart=open_cart, product=products[4], quantity=1)
        CartItem.objects.create(cart=open_cart, product=products[5], quantity=2)

        self.stdout.write(self.style.SUCCESS("Database flushed and seeded with demo data."))
        self.stdout.write(f"Demo password for all users: {password}")
        self.stdout.write("Primary login: owner@audql.test")

    def create_user(self, **data):
        password = data.pop("password")
        user = User.objects.create_user(password=password, **data)
        user.is_active = True
        user.save(update_fields=["is_active"])
        return user

    def create_store(self, user, **data):
        return Store.objects.create(user=user, email=user.email, **data)

    def create_product(self, store, title, description, price, available, category, rating, sales):
        return Product.objects.create(
            store=store,
            title=title,
            description=description,
            price=Decimal(price),
            available=available,
            category=category,
            currency=store.currency,
            rating=Decimal(rating),
            sales=sales,
        )

    def create_customers(self, user, offset):
        names = [
            ("Grace", "Miller", "+14155550200"),
            ("Ethan", "Brooks", "+14155550201"),
            ("Lina", "Patel", "+14155550202"),
            ("Samuel", "Reed", "+14155550203"),
        ]
        for index, (first_name, last_name, phone) in enumerate(names, start=1):
            Customer.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=f"{first_name.lower()}.{last_name.lower()}.{offset}@example.test",
                phone_number=phone,
                is_active=index % 2 == 0,
            )

    def create_queries(self, user):
        queries = [
            ("show all paid orders", "SELECT"),
            ("find customers with inactive accounts", "SELECT"),
            ("update low stock products", "UPDATE"),
            ("delete cancelled cart drafts", "DELETE"),
        ]
        for query, action in queries:
            Query.objects.create(user=user, query=query, action=action)

    def create_order(self, user, products, quantities, status):
        cart = Cart.objects.create(user=user, ordered=True)
        subtotal = Decimal("0.00")
        for product, quantity in zip(products, quantities):
            CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            subtotal += product.price * quantity

        total = subtotal
        return Order.objects.create(
            user=user,
            cart=cart,
            status=status,
            subtotal=subtotal,
            total=total,
        )
