from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone



from utils.mixins import DatesMixin

from phonenumber_field.modelfields import PhoneNumberField
from nanoid import generate


# Create your models here.


def generate_order_id():
    return generate(size=15)


class UserManager(BaseUserManager):
    def create_user(self, email=None, password=None, **extra_fields):
        """
        Create and save a user with the given email and password.
        """

        if not email:
            raise ValueError("Email Address Is Needed")
        if not password:
            raise ValueError("Password Must Be Provided")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

    def create_staffuser(self, email=None, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("staffuser must have is_staff=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=90)
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password"]

    objects = UserManager()

    class Meta:
        db_table = "user"
        ordering = ["created"]


class Store(DatesMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True
    )
    username = models.CharField(max_length=17, unique=True)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=100)
    bio = models.TextField()
    phone = PhoneNumberField(null=True, blank=True)
    currency = models.CharField(max_length=89, default="USD")

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self._generate_unique_username()
        super().save(*args, **kwargs)

    def _generate_unique_username(self, size=15):
        username = generate(size=size)
        while Store.objects.filter(username=username).exists():
            username = generate(size)
        return username

    class Meta:
        db_table = "store"
        ordering = ["created"]


class Product(DatesMixin):
    CATEGORIES_CHOICE = (
        ("fishing", "fishing"),
        ("sports", "sports"),
        ("electronics", "electronics"),
        ("phones", "phones"),
        ("games", "games"),
        ("tablets", "tablets"),
        ("outwear", "outwear"),
        ("pets", "pets"),
        ("toys", "toys"),
        ("computing", "computing"),
        ("lingerie", "lingerie"),
        ("books", "books"),
        ("beverages", "beverages"),
    )

    store = models.ForeignKey("Store", on_delete=models.CASCADE)
    title = models.CharField(max_length=225, blank=False, null=False)
    description = models.TextField(null=False, blank=False)
    price = models.DecimalField(
        max_digits=15, decimal_places=2, blank=False, null=False
    )
    available = models.IntegerField(
        null=False, blank=False, validators=[MinValueValidator(0)]
    )
    category = models.CharField(max_length=150)
    currency = models.CharField(max_length=89)
    rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    sales = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    def set_availability(self, quantity_bought: int):
        if quantity_bought < 0:
            raise ValueError("Quantity bought cannot be negative.")
        if quantity_bought > self.available:
            raise ValueError("Quantity bought exceeds available stock.")
        self.available -= quantity_bought

    def save(self, *args, **kwargs):
        self.currency = self.store.currency
        super().save(*args, **kwargs)

    class Meta:
        db_table = "product"
        ordering = ["created"]


class Cart(DatesMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    class Meta:
        db_table = "cart"
        ordering = ["created"]


class CartItem(DatesMixin):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)], default=1)

    class Meta:
        db_table = "cartitem"
        ordering = ["created"]


class Order(DatesMixin):
    ORDER_STATUS_CHOICE = (
        ("pending", "pending"),
        ("cancelled", "cancelled"),
        ("paid", "paid"),
    )

    id = models.CharField(
        max_length=15, default=generate_order_id, unique=True, primary_key=True
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(choices=ORDER_STATUS_CHOICE, max_length=15)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self._generate_unique()
        super().save(*args, **kwargs)

    def _generate_unique(self, size=15):
        id = generate(size)
        while Order.objects.filter(id=id).exists():
            id = generate(size=size)
        return id

    class Meta:
        db_table = "order"
        ordering = ["created"]


class Customer(DatesMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=225)
    last_name = models.CharField(max_length=225)
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField()
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = "customer"
        ordering = ["created"]


class Notification(DatesMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    push_notification = models.BooleanField(default=True)

    class Meta:
        db_table = "notification"
        ordering = ["created"]


class NotificationDevice(DatesMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_devices",
    )
    token = models.CharField(max_length=500, unique=True)
    platform = models.CharField(max_length=40, default="web")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_device"
        ordering = ["created"]


class Query(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.CharField(max_length=225)
    action = models.CharField(max_length=20)
    
    class Meta:
        db_table = "query"


class QueueJob(models.Model):
    class Kind(models.TextChoices):
        SEARCH_INDEX = "search.index", "Search index"
        SEARCH_DELETE = "search.delete", "Search delete"
        QUERY_GENERATE = "query.generate", "Generate query"
        QUERY_AUDIO = "query.audio", "Transcribe audio query"
        EMAIL_ACTIVATION = "email.activation", "Activation email"
        EMAIL_PASSWORD_RESET = "email.password_reset", "Password reset email"
        NOTIFICATION_SEND = "notification.send", "Send notification"
        ORDERS_EXPORT = "orders.export", "Export orders"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="queue_jobs",
    )
    kind = models.CharField(max_length=40, choices=Kind.choices)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.QUEUED, db_index=True
    )
    payload = models.JSONField(default=dict)
    result = models.JSONField(
        null=True, blank=True, encoder=DjangoJSONEncoder
    )
    error = models.CharField(max_length=500, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    available_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "queue_job"
        ordering = ["created_at"]
