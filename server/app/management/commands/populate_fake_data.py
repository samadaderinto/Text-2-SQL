import os
import random
from decimal import Decimal
from datetime import timedelta

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from nanoid import generate

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


# Categorized product templates (base names and typical price ranges in USD)
PRODUCT_CATALOG = {
    "electronics": {
        "items": [
            "Noise-Canceling Wireless Headphones",
            "4K Ultra HD Monitor 27-inch",
            "Bluetooth Portable Speaker",
            "Smart Home Security Camera",
            "True Wireless Earbuds with ANC",
            "USB-C Multiport Docking Station",
            "Wireless Fast Charging Pad",
            "Smart LED Color Desk Lamp",
            "Mini Portable Projector 1080p",
            "Digital Audio Interface 2-Channel",
        ],
        "min_price": 24.99,
        "max_price": 499.99,
    },
    "computing": {
        "items": [
            "RGB Mechanical Gaming Keyboard",
            "Ergonomic Vertical Optical Mouse",
            "External NVMe SSD 1TB USB 3.2",
            "Dual-Band Wi-Fi 6 Router",
            "Laptop Aluminum Riser Stand",
            "Ultra-Wide Curved Gaming Monitor",
            "HD Webcam with Privacy Shutter",
            "Braided USB-C Cable 100W 2m",
            "Active DisplayPort to HDMI Adapter",
            "Memory Foam Ergonomic Wrist Rest",
        ],
        "min_price": 19.50,
        "max_price": 799.00,
    },
    "phones": {
        "items": [
            "3-Axis Handheld Smartphone Gimbal",
            "Shockproof Magnetic Phone Case",
            "Tempered Glass Screen Protector 3-Pack",
            "Fast Wireless Car Mount Charger",
            "Magnetic Portable Power Bank 10000mAh",
            "Foldable Desktop Phone Stand",
            "Clip-On Macro and Wide Angle Lens",
            "Bluetooth Remote Shutter Button",
            "Waterproof Phone Pouch Case",
            "Braided Lightning to USB-C Cable",
        ],
        "min_price": 9.99,
        "max_price": 249.00,
    },
    "sports": {
        "items": [
            "Trail Running Shoes All-Terrain",
            "High-Density Non-Slip Yoga Mat",
            "Adjustable Quick-Select Dumbbell",
            "Insulated Stainless Gym Shaker 32oz",
            "Breathable Compression Knee Sleeve",
            "Speed Jump Rope with Ball Bearings",
            "Resistance Workout Bands 5-Piece",
            "Deep Tissue Muscle Massage Gun",
            "Reflective Running Waist Pack",
            "Electrolyte Hydration Flask",
        ],
        "min_price": 14.50,
        "max_price": 299.00,
    },
    "outwear": {
        "items": [
            "Waterproof Breathable Rain Jacket",
            "Packable Down Puffer Coat",
            "Thermal Fleece Half-Zip Pullover",
            "Windproof Softshell Trekking Jacket",
            "Merino Wool Baselayer Crew Top",
            "Insulated Winter Ski Gloves",
            "Lightweight Hooded Windbreaker",
            "Thermal Water-Resistant Hiking Pants",
            "Polarized Alpine Sunglasses",
            "Merino Wool Thermal Beanie",
        ],
        "min_price": 35.00,
        "max_price": 389.00,
    },
    "books": {
        "items": [
            "Mastering High-Performance SQL",
            "Designing Data-Intensive Applications",
            "The Pragmatic Software Architect",
            "Microservices Patterns & Best Practices",
            "Cloud-Native Distributed Systems",
            "Modern Machine Learning with Python",
            "Database Internals: Storage Engines",
            "Site Reliability Engineering Handbook",
            "Clean Architecture in Production",
            "Practical Text-to-SQL Pipelines",
        ],
        "min_price": 18.00,
        "max_price": 79.99,
    },
    "beverages": {
        "items": [
            "Single-Origin Ethiopian Whole Bean Coffee 1kg",
            "Artisan Ceremonial Grade Matcha 100g",
            "Organic Loose-Leaf Jasmine Green Tea",
            "Airtight Cold Brew Pitcher 1.5L",
            "Single-Batch Colombian Dark Roast",
            "Craft Cascara Coffee Cherry Tea",
            "Earl Grey Supreme Black Tea Tin",
            "Double-Wall Vacuum Insulated Tumbler",
            "Organic Chamomile Herbal Infusion",
            "Artisan Hot Chocolate Blend 500g",
        ],
        "min_price": 7.50,
        "max_price": 65.00,
    },
    "games": {
        "items": [
            "Wireless Low-Latency Game Controller",
            "Surround Sound Noise-Isolating Gaming Headset",
            "Custom Double-Shot PBT Keycap Set",
            "Precision RGB Gaming Mouse Pad XL",
            "Ergonomic Lumbar Support Gaming Cushion",
            "Arcade Fight Stick with Sanwa Buttons",
            "Retro Handheld Gaming Console 64GB",
            "Detachable Noise-Canceling Boom Mic",
            "Dual Controller Charging Dock",
            "Anti-Slip Controller Grip Tape Set",
        ],
        "min_price": 14.99,
        "max_price": 219.00,
    },
    "tablets": {
        "items": [
            "Active Stylus Pen with Palm Rejection",
            "Magnetic Folio Smart Cover Case",
            "Matte Paper-Feel Screen Protector 2-Pack",
            "Ultra-Slim Bluetooth Keyboard with Trackpad",
            "Multi-Angle Aluminum Tablet Desk Arm",
            "Protective Shockproof Kids Tablet Case",
            "Padded Neoprene Tablet Sleeve 11-inch",
            "USB-C Tablet Hub with 4K HDMI Output",
            "Capacitive Touchscreen Drawing Glove",
            "Fast Tablet Wall Charger 45W GaN",
        ],
        "min_price": 12.00,
        "max_price": 189.00,
    },
    "fishing": {
        "items": [
            "Carbon Fiber Telescopic Fishing Rod",
            "High-Speed Gear Ratio Spinning Reel",
            "Multi-Compartment Waterproof Tackle Box",
            "Braided Superline Fishing Line 300m",
            "Corrosion-Resistant Fishing Pliers",
            "Stainless Steel Fish Lip Gripper",
            "Realistic Crankbait Fishing Lure Kit 10-Pack",
            "Folding Floating Landing Net",
            "Polarized UV400 Fishing Sunglasses",
            "Waterproof Fishing Backpack with Rod Holder",
        ],
        "min_price": 16.50,
        "max_price": 259.00,
    },
    "pets": {
        "items": [
            "Orthopedic Memory Foam Pet Bed",
            "Automatic Quiet Water Fountain 2.5L",
            "Interactive Laser Teaser Toy for Cats",
            "Reflective Breathable Dog Harness",
            "Slow-Feeder Anti-Gulping Food Bowl",
            "Self-Cleaning Slicker Grooming Brush",
            "Durable Natural Rubber Chew Bone",
            "Odor-Free Biodegradable Waste Bags 300-Count",
            "Cozy Fleece Winter Dog Jacket",
            "Multilevel Sturdy Cat Scratching Post",
        ],
        "min_price": 8.99,
        "max_price": 149.00,
    },
    "toys": {
        "items": [
            "STEM Programmable Robotics Kit",
            "Magnetic Geometric Tiles 100-Piece",
            "High-Speed 4WD RC Off-Road Buggy",
            "Wooden Educational Montessori Puzzle",
            "Mini Foldable Drone with HD Camera",
            "Classic Die-Cast Metal Vehicle Set",
            "Kids Digital Camera with Thermal Printer",
            "Kinetic Play Sand Sensory Kit",
            "Glow-in-the-Dark Constellation Planetarium",
            "Solar-Powered Rover Building Kit",
        ],
        "min_price": 15.00,
        "max_price": 179.99,
    },
    "lingerie": {
        "items": [
            "Seamless Wirefree Everyday Bralette",
            "Mulberry Silk Breathable Pajama Set",
            "Soft Modal Stretch Boxer Briefs 3-Pack",
            "Lace-Trimmed Satin Sleep Camisole",
            "Breathable Organic Cotton Lounge Shorts",
            "Lightweight Cooling Chemise Nightdress",
            "Ribbed Seamless Loungewear Bralette",
            "Ultra-Soft Robe with Satin Tie",
            "Thermal Modal Sleep Tee",
            "No-Show Seamless Hipster Underwear 5-Pack",
        ],
        "min_price": 18.00,
        "max_price": 160.00,
    },
}

PRODUCT_ADJECTIVES = [
    "Pro",
    "Ultra",
    "Max",
    "Elite",
    "Compact",
    "Ergonomic",
    "Wireless",
    "Heavy-Duty",
    "Artisan",
    "Premium",
    "Smart",
    "Classic",
    "Eco-Friendly",
    "Portable",
    "Advanced",
    "Precision",
    "Modular",
    "Custom",
    "Heritage",
    "Performance",
]

FIRST_NAMES = [
    "Amara", "Noah", "Maya", "Liam", "Sophia", "Ethan", "Olivia", "Lucas",
    "Aria", "Mateo", "Emma", "Aiden", "Zoe", "James", "Elena", "Jackson",
    "Chloe", "Daniel", "Mila", "Alexander", "Fatima", "David", "Layla",
    "Gabriel", "Isabella", "Benjamin", "Sara", "Elijah", "Hannah", "Oliver",
    "Grace", "Samuel", "Priya", "Henry", "Ava", "Marcus", "Nora", "Leo",
    "Lina", "Julian", "Camila", "Jack", "Leila", "Owen", "Stella", "Caleb",
    "Mia", "Nathan", "Harper", "Sebastian", "Clara", "Wyatt", "Kora", "Isaac",
]

LAST_NAMES = [
    "Okafor", "Stone", "Chen", "Brooks", "Patel", "Miller", "Reed", "Rossi",
    "Tanaka", "Silva", "Kim", "Williams", "Mueller", "Novak", "Fischer",
    "Dubois", "Santos", "Larsen", "Kowalski", "Yamamoto", "Nakamura", "Morales",
    "Johansson", "Popov", "Al-Mansoor", "Zhao", "Gomez", "Taylor", "Anderson",
    "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Martinez",
    "Robinson", "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen",
]

EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "outlook.com", "icloud.com", "proton.me",
    "mail.com", "techflow.io", "audql.test", "enterprise.org", "store.co",
]

US_AREA_CODES = [
    "201", "206", "212", "213", "303", "312", "415", "503", "617",
    "702", "718", "818", "917", "925", "949",
]

SAMPLE_QUERIES = [
    ("show all paid orders", "SELECT"),
    ("find customers with inactive accounts", "SELECT"),
    ("list top 10 best-selling electronics", "SELECT"),
    ("calculate total revenue for paid orders", "SELECT"),
    ("find out of stock products in sports category", "SELECT"),
    ("show orders with total greater than 150 dollars", "SELECT"),
    ("list all products with rating above 4.5", "SELECT"),
    ("count total orders grouped by status", "SELECT"),
    ("find customers created in the last 90 days", "SELECT"),
    ("show products with low stock less than 10 units", "SELECT"),
    ("find all pending orders awaiting fulfillment", "SELECT"),
    ("calculate average product price by category", "SELECT"),
    ("show recent customer signups with gmail addresses", "SELECT"),
    ("list top 5 highest total value orders", "SELECT"),
    ("find products in computing category ordered by price", "SELECT"),
    ("show orders cancelled this year", "SELECT"),
    ("find customers with phone numbers in 415 area code", "SELECT"),
    ("count total products available in inventory", "SELECT"),
    ("calculate average rating for all books", "SELECT"),
    ("show monthly sales revenue for current year", "SELECT"),
    ("update stock for low inventory items", "UPDATE"),
    ("mark pending orders older than 30 days as cancelled", "UPDATE"),
    ("update customer active status for verified emails", "UPDATE"),
    ("apply 10 percent discount to winter outwear products", "UPDATE"),
    ("reset ratings for unreviewed product items", "UPDATE"),
    ("delete cancelled cart drafts older than 60 days", "DELETE"),
    ("remove inactive guest customer accounts", "DELETE"),
    ("purge expired notification tokens", "DELETE"),
    ("insert promotional seasonal customer discount", "INSERT"),
    ("add new flagship noise-canceling headphones to store", "INSERT"),
]


class Command(BaseCommand):
    help = (
        "Populate the database with a large volume of realistic demo data "
        "(products across all categories, customers, carts, cart items, orders with diverse statuses, "
        "and queries) for testing Text-to-SQL, search, filtering, and performance."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--products",
            type=int,
            default=500,
            help="Number of products to generate across all categories (default: 500).",
        )
        parser.add_argument(
            "--customers",
            type=int,
            default=500,
            help="Number of customers to generate (default: 500).",
        )
        parser.add_argument(
            "--orders",
            type=int,
            default=1000,
            help="Number of orders to generate with carts and items (default: 1000).",
        )
        parser.add_argument(
            "--queries",
            type=int,
            default=100,
            help="Number of natural language query log records to generate (default: 100).",
        )
        parser.add_argument(
            "--email",
            type=str,
            default=None,
            help="Email address of the store owner user (default: ADMIN_EMAIL or owner@audql.local).",
        )
        parser.add_argument(
            "--password",
            type=str,
            default=None,
            help="Password for the store owner user (default: ADMIN_PASSWORD or DemoPass123!).",
        )
        parser.add_argument(
            "--store-name",
            type=str,
            default="EchoCart Flagship Store",
            help="Name of the demo store (default: EchoCart Flagship Store).",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Flush the existing database before generating fake data.",
        )
        parser.add_argument(
            "--no-es",
            action="store_true",
            help="Skip Elasticsearch index creation and document indexing.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Batch size for bulk_create operations (default: 500).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force execution even if running in production.",
        )

    def handle(self, *args, **options):
        if str(getattr(settings, "DEPLOY_ENV", "")).lower() in ("production", "prod"):
            if not options.get("force"):
                raise CommandError(
                    "SAFETY BLOCK: Refusing to populate fake data in production (DEPLOY_ENV='production'). "
                    "This command is strictly intended for local development and testing environments."
                )

        num_products = options["products"]
        num_customers = options["customers"]
        num_orders = options["orders"]
        num_queries = options["queries"]
        batch_size = options["batch_size"]
        flush = options["flush"]
        skip_es = options["no_es"]

        if flush:
            self.stdout.write("Flushing existing database records...")
            call_command("flush", interactive=False, verbosity=0)

        # Resolve primary user credentials
        email = (
            options["email"]
            or os.environ.get("ADMIN_EMAIL")
            or "owner@audql.local"
        ).lower()
        password = (
            options["password"]
            or os.environ.get("ADMIN_PASSWORD")
            or "DemoPass123!"
        )

        with transaction.atomic():
            user = self.get_or_create_user(email, password)
            store = self.get_or_create_store(user, options["store_name"])
            Notification.objects.get_or_create(
                user=user,
                defaults={"email_notification": True, "push_notification": True},
            )

            self.stdout.write(f"Owner user: {user.email} (Store: {store.name})")

            # 1. Generate Products
            self.stdout.write(f"Generating {num_products} products across 13 categories...")
            products = self.generate_products(store, num_products, batch_size)
            self.stdout.write(self.style.SUCCESS(f"✓ Created {len(products)} products."))

            # 2. Generate Customers
            self.stdout.write(f"Generating {num_customers} customers...")
            customers = self.generate_customers(user, num_customers, batch_size)
            self.stdout.write(self.style.SUCCESS(f"✓ Created {len(customers)} customers."))

            # 3. Generate Orders, Carts, and CartItems
            self.stdout.write(f"Generating {num_orders} orders with associated carts and items...")
            orders_count, items_count = self.generate_orders(
                user, products, num_orders, batch_size
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created {orders_count} orders containing {items_count} cart items."
                )
            )

            # 4. Generate Natural Language Queries
            self.stdout.write(f"Generating {num_queries} query history entries...")
            queries = self.generate_queries(user, num_queries, batch_size)
            self.stdout.write(self.style.SUCCESS(f"✓ Created {len(queries)} query logs."))

        # 5. Optional Elasticsearch indexing
        if not skip_es:
            self.index_in_elasticsearch()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("Fake data generation complete!"))
        self.stdout.write(f"  • Store Owner: {user.email}")
        self.stdout.write(f"  • Password:    {password}")
        self.stdout.write(f"  • Products:    {len(products):,}")
        self.stdout.write(f"  • Customers:   {len(customers):,}")
        self.stdout.write(f"  • Orders:      {orders_count:,}")
        self.stdout.write(f"  • Queries:     {len(queries):,}")
        self.stdout.write("=" * 60 + "\n")

    def get_or_create_user(self, email, password):
        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create_superuser(
                email=email,
                password=password,
                first_name="Admin",
                last_name="Owner",
            )
        else:
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
        return user

    def get_or_create_store(self, user, store_name):
        store, _ = Store.objects.get_or_create(
            user=user,
            defaults={
                "name": store_name,
                "email": user.email,
                "bio": "Premium modern commerce hub for verified high-volume queries and analysis.",
                "phone": "+14155550100",
                "currency": "USD",
            },
        )
        return store

    def generate_products(self, store, count, batch_size):
        categories = list(PRODUCT_CATALOG.keys())
        now = timezone.now()
        product_instances = []

        for i in range(count):
            category = categories[i % len(categories)]
            catalog = PRODUCT_CATALOG[category]
            base_item = catalog["items"][i % len(catalog["items"])]
            adjective = PRODUCT_ADJECTIVES[(i * 7 + 3) % len(PRODUCT_ADJECTIVES)]
            title = f"{adjective} {base_item}"
            if i >= len(catalog["items"]) * len(PRODUCT_ADJECTIVES):
                title = f"{title} Edition #{i + 1}"

            # Price with realistic cents (.99, .50, .00, .95)
            price_float = random.uniform(catalog["min_price"], catalog["max_price"])
            price_cents = random.choice([0.99, 0.50, 0.00, 0.95, 0.49])
            price = Decimal(f"{int(price_float)}.{int(price_cents * 100):02d}")

            # Availability: 5% out of stock, 10% low stock (1-9), 85% normal stock
            stock_roll = random.random()
            if stock_roll < 0.05:
                available = 0
            elif stock_roll < 0.15:
                available = random.randint(1, 9)
            else:
                available = random.randint(10, 450)

            # Rating: skewed between 3.50 and 5.00
            rating = Decimal(f"{random.uniform(3.0, 5.0):.2f}")
            sales = random.randint(0, 3200)

            # Description
            description = (
                f"Premium quality {base_item.lower()} featuring high-grade engineering, "
                f"exceptional durability, and verified ratings. Designed for high performance."
            )

            product = Product(
                store=store,
                title=title,
                description=description,
                price=price,
                available=available,
                category=category,
                currency=store.currency,
                rating=rating,
                sales=sales,
            )
            # Spread historical timestamps over the past 365 days
            days_ago = random.randint(1, 365)
            created_dt = now - timedelta(days=days_ago, minutes=random.randint(0, 1440))
            product.created = created_dt
            product.updated = created_dt
            product_instances.append(product)

        created_products = Product.objects.bulk_create(
            product_instances, batch_size=batch_size
        )
        # Fetch with IDs if SQLite bulk_create didn't attach PKs
        if not created_products or not getattr(created_products[0], "id", None):
            created_products = list(
                Product.objects.filter(store=store).order_by("-id")[:count]
            )
        return created_products

    def generate_customers(self, user, count, batch_size):
        now = timezone.now()
        customer_instances = []
        used_emails = set(
            Customer.objects.values_list("email", flat=True)
        )

        for i in range(count):
            first_name = FIRST_NAMES[(i * 3 + 1) % len(FIRST_NAMES)]
            last_name = LAST_NAMES[(i * 5 + 2) % len(LAST_NAMES)]
            domain = EMAIL_DOMAINS[i % len(EMAIL_DOMAINS)]

            # Ensure unique email
            email_candidate = f"{first_name.lower()}.{last_name.lower()}.{i + 1}@{domain}"
            suffix = 1
            while email_candidate in used_emails:
                email_candidate = f"{first_name.lower()}.{last_name.lower()}.{i + 1}.{suffix}@{domain}"
                suffix += 1
            used_emails.add(email_candidate)

            # Valid E.164 phone number with US area code
            area = US_AREA_CODES[i % len(US_AREA_CODES)]
            phone_num = f"+1{area}555{i % 9000 + 1000:04d}"

            # Active status: ~85% active, ~15% inactive
            is_active = (i % 7) != 0

            days_ago = random.randint(1, 365)
            created_dt = now - timedelta(days=days_ago, minutes=random.randint(0, 1440))

            customer = Customer(
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=email_candidate,
                phone_number=phone_num,
                is_active=is_active,
            )
            customer.created = created_dt
            customer.updated = created_dt
            customer_instances.append(customer)

        created_customers = Customer.objects.bulk_create(
            customer_instances, batch_size=batch_size
        )
        return created_customers

    def generate_orders(self, user, products, count, batch_size):
        if not products:
            return 0, 0

        now = timezone.now()
        statuses = ["paid"] * 70 + ["pending"] * 20 + ["cancelled"] * 10

        # Step 1: Bulk create Carts
        cart_instances = []
        for i in range(count):
            days_ago = random.randint(1, 365)
            created_dt = now - timedelta(days=days_ago, minutes=random.randint(0, 1440))
            cart = Cart(user=user, ordered=True)
            cart.created = created_dt
            cart.updated = created_dt
            cart_instances.append(cart)

        created_carts = Cart.objects.bulk_create(cart_instances, batch_size=batch_size)
        if not created_carts or not getattr(created_carts[0], "id", None):
            created_carts = list(
                Cart.objects.filter(user=user, ordered=True).order_by("-id")[:count]
            )
            created_carts.reverse()

        # Step 2: Prepare CartItems and Orders
        order_instances = []
        cart_item_instances = []

        existing_order_ids = set(Order.objects.values_list("id", flat=True))

        for i, cart in enumerate(created_carts):
            # Select 1 to 4 distinct products
            item_count = random.randint(1, 4)
            chosen_products = random.sample(
                products, min(item_count, len(products))
            )

            subtotal = Decimal("0.00")
            for product in chosen_products:
                qty = random.randint(1, 4)
                item = CartItem(
                    cart=cart,
                    product=product,
                    quantity=qty,
                )
                item.created = cart.created
                item.updated = cart.updated
                cart_item_instances.append(item)
                subtotal += product.price * qty

            total = subtotal
            status = statuses[i % len(statuses)]

            # Generate unique 15-character order ID
            order_id = generate(size=15)
            while order_id in existing_order_ids:
                order_id = generate(size=15)
            existing_order_ids.add(order_id)

            order = Order(
                id=order_id,
                user=user,
                status=status,
                cart=cart,
                subtotal=subtotal,
                total=total,
            )
            order.created = cart.created
            order.updated = cart.updated
            order_instances.append(order)

        # Bulk create items and orders
        CartItem.objects.bulk_create(cart_item_instances, batch_size=batch_size)
        Order.objects.bulk_create(order_instances, batch_size=batch_size)

        return len(order_instances), len(cart_item_instances)

    def generate_queries(self, user, count, batch_size):
        query_instances = []
        for i in range(count):
            template_query, action = SAMPLE_QUERIES[i % len(SAMPLE_QUERIES)]
            if i >= len(SAMPLE_QUERIES):
                text = f"{template_query} (run #{i + 1})"
            else:
                text = template_query

            query_instances.append(
                Query(
                    user=user,
                    query=text,
                    action=action,
                )
            )

        created_queries = Query.objects.bulk_create(
            query_instances, batch_size=batch_size
        )
        return created_queries

    def index_in_elasticsearch(self):
        try:
            from app.search_index import (
                SEARCH_DEFINITIONS,
                bulk_index_instances,
                ensure_search_indices,
                get_elasticsearch_client,
            )

            client = get_elasticsearch_client()
            if not client.ping():
                self.stdout.write(
                    self.style.WARNING(
                        "Elasticsearch server ping failed. Skipping search indexing."
                    )
                )
                return

            self.stdout.write("Syncing search indices with new demo data...")
            ensure_search_indices(client)
            counts = []
            for resource, definition in SEARCH_DEFINITIONS.items():
                queryset = definition["model"].objects.select_related(
                    "store" if resource == "products" else None
                ).iterator(chunk_size=500)
                _, indexed = bulk_index_instances(client, queryset)
                counts.append(f"{resource}: {indexed}")

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Elasticsearch indices updated ({', '.join(counts)})."
                )
            )
        except Exception as exc:
            self.stdout.write(
                self.style.WARNING(
                    f"Elasticsearch indexing skipped (not available or error: {exc})."
                )
            )
