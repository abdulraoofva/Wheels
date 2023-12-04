from django.contrib import admin
from .models import Usertable,CarOwner,CarListing

# Register your models here.
admin.site.register(Usertable)
admin.site.register(CarOwner)
admin.site.register(CarListing)