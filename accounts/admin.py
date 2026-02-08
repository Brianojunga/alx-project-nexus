from django.contrib import admin
from .models import CustomUser, Vendor, Membership

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Vendor)
admin.site.register(Membership)