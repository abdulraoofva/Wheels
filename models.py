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
    car_owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.ImageField(upload_to='car_images/')

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"
    
class CarImage(models.Model):
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='car_images/')

    def __str__(self):
        return f"Image for {self.car}"
class Booking(models.Model):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    car_owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE)
    user = models.ForeignKey(Usertable, on_delete=models.CASCADE)
    car_listing = models.ForeignKey(CarListing, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    start_date = models.DateField()
    end_date = models.DateField()
    special_request = models.TextField()

    # Personal Details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15)

    # License Details
    license_number = models.CharField(max_length=20)
    license_pdf = models.FileField(upload_to='license_pdfs/')

    # Aadhaar Details
    aadhaar_number = models.CharField(max_length=20)
    aadhaar_pdf = models.FileField(upload_to='aadhaar_pdfs/')

    # New Location Field
    location = models.CharField(max_length=255, default='') # You can adjust the field type accordingly

    def __str__(self):
        return f"Booking for {self.car_listing} by {self.user.email}"
    


class CarAccessory(models.Model):
    name = models.CharField(max_length=100)
    accessory_id = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compatibility = models.CharField(max_length=100)
    quantity_available = models.PositiveIntegerField()
    description = models.TextField()
    installation_requirements = models.TextField()
    manufacturer = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    dimensions_weight = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='accessory_thumbnails/')

    def __str__(self):
        return self.name

class AccessoryImage(models.Model):
    accessory = models.ForeignKey(CarAccessory, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='accessory_images/')

    def __str__(self):
        return f"Image for {self.accessory.name}"
    
    # models.py

from django.db import models

class Driver(models.Model):
    driver_name = models.CharField(max_length=100)
    email = models.EmailField()
    contact_number = models.CharField(max_length=15)
    driver_license = models.FileField(upload_to='driver_licenses/')
    conduct_certificate = models.FileField(upload_to='conduct_certificates/')
    address = models.TextField()
    location = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='driver_photos/', blank=True, null=True)

    def __str__(self):
        return self.driver_name
    

    from django.db import models
from django.contrib.auth.models import User
from .models import CarAccessory

from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class CartItem(models.Model):
    user = models.ForeignKey(Usertable, on_delete=models.CASCADE)
    product = models.ForeignKey('CarAccessory', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s cart item: {self.product.name}"

    def save(self, *args, **kwargs):
        # Calculate subtotal before saving
        self.subtotal = self.product.price * self.quantity
        super().save(*args, **kwargs)

from django.db import models
from .models import CarAccessory, Usertable

class Wishlist(models.Model):
    user = models.ForeignKey(Usertable, on_delete=models.CASCADE)
    product = models.ForeignKey('CarAccessory', on_delete=models.CASCADE)

    def __str__(self):
        return f"Wishlist for {self.user.email}"
    


from django.db import models
from django.contrib.auth.models import User

class Checkout(models.Model):
    user = models.ForeignKey(Usertable, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Checkout for {self.user.email}"

class CheckoutItem(models.Model):
    checkout = models.ForeignKey(Checkout, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('CarAccessory', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.checkout}"




