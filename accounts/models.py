from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.text import slugify

# Create your models here.
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
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = "email"  
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Vendor(models.Model):
    company_name = models.CharField(max_length=100, blank=False, null=False)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=False, null=False)
    slug = models.SlugField(unique=True)
    approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.company_name)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Membership(models.Model):
    ROLE_CHOICES = (
        ("Platform_admin", "platform Admin"),
        ("Platform_agent", "platform Agent"),
        ("Vendor_admin", "vendor Admin"),
        ("Vendor_agent", "vendor Agent"),
        ("User", "user")
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='memberships')
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.CASCADE)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="user")

    class Meta:
        unique_together = ("user", "vendor")

