from django.db import models

# Create your models here.

class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(choices=GENDER_STATUS, max_length=7)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    phone1 = PhoneNumberField(region="US")
    password = models.CharField(max_length=90)
    phone2 = PhoneNumberField(region="US", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name",
                       "gender", "phone1", "password"]

    objects = UserManager()
