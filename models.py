from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.hashers import make_password

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class Usertable(AbstractUser):
    # Custom fields for your user model
    username = models.CharField(max_length=20, blank=True, null=True, unique=True)
    role = models.CharField(max_length=25, default="normal_user")
    email = models.EmailField(primary_key=True, unique=True)  # Email as unique USERNAME_FIELD
    dob = models.DateField(default='2000-01-01')
    phone = models.CharField(max_length=15, blank=True, null=True)

    # Custom User Manager
    objects = CustomUserManager()

    # Additional fields and methods for your custom user model if needed

    def __str__(self):
        return self.email

    
from django.db import models
from django.contrib.auth.hashers import make_password

class CarOwner(models.Model):
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True, primary_key=True)
    document = models.FileField(upload_to='car_owner_documents/')
    address = models.TextField()
    location = models.CharField(max_length=100)
    venue_name = models.CharField(max_length=100)
    proposal_status = models.CharField(max_length=10, default='Pending')
    password = models.CharField(max_length=128, null=True, blank=True)
    password_generated = models.BooleanField(default=False)  # Flag to track if password was generated

    def set_password(self, raw_password):
        # Set the hashed password for the CarOwner
        self.password = make_password(raw_password)
        self.password_generated = True

    def __str__(self):
        return self.venue_name


class CarListing(models.Model):
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.ImageField(upload_to='car_images/')

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"