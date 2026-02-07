from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from .models import Vendor, Membership, CustomUserManager

User = get_user_model()


class CustomUserModelTests(TestCase):
    def test_create_user(self):
        #Test creating a regular user.
        user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'user@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_email_raises_error(self):
        #Test that creating user without email raises ValueError
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpass123')

    def test_create_superuser(self):
        #Test creating a superuser
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser_without_staff_flag_raises_error(self):
        #Test that superuser requires is_staff=True
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_staff=False
            )

    def test_user_email_uniqueness(self):
        #Test that email field is unique
        User.objects.create_user(email='user@example.com', password='pass')
        with self.assertRaises(Exception):
            User.objects.create_user(email='user@example.com', password='pass')

    def test_user_string_representation(self):
        #Test user __str__ method returns email
        user = User.objects.create_user(email='user@example.com', password='pass')
        self.assertEqual(str(user), 'user@example.com')


class VendorModelTests(TestCase):
    def test_vendor_creation(self):
        #Test creating a vendor
        vendor = Vendor.objects.create(
            company_name='Acme Corp',
            address='123 Business St',
            phone_number='1234567890',
            email='vendor@acme.com'
        )
        self.assertEqual(vendor.company_name, 'Acme Corp')
        self.assertEqual(vendor.address, '123 Business St')
        self.assertEqual(vendor.phone_number, '1234567890')
        self.assertEqual(vendor.email, 'vendor@acme.com')

    def test_vendor_slug_auto_generation(self):
        #Test that slug is automatically generated from company_name
        vendor = Vendor.objects.create(
            company_name='Test Company',
            address='123 St',
            phone_number='1234567890',
            email='test@company.com'
        )
        self.assertEqual(vendor.slug, 'test-company')

    def test_vendor_slug_uniqueness(self):
        #Test that slug field is unique
        Vendor.objects.create(
            company_name='Acme Corp',
            address='123 St',
            phone_number='1234567890',
            email='vendor1@acme.com'
        )
        with self.assertRaises(Exception):
            Vendor.objects.create(
                company_name='Acme Corp',
                address='456 St',
                phone_number='0987654321',
                email='vendor2@acme.com'
            )

    def test_vendor_default_values(self):
        #Test default values for vendor fields
        vendor = Vendor.objects.create(
            company_name='Test Vendor',
            address='123 St',
            phone_number='1234567890',
            email='test@vendor.com'
        )
        self.assertFalse(vendor.approved)
        self.assertTrue(vendor.is_active)
        self.assertIsNotNone(vendor.created_at)


class MembershipModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='pass')
        self.vendor = Vendor.objects.create(
            company_name='Test Vendor',
            address='123 St',
            phone_number='1234567890',
            email='vendor@test.com'
        )

    def test_membership_creation(self):
        #Test creating a membership
        membership = Membership.objects.create(
            user=self.user,
            vendor=self.vendor,
            role='Vendor_admin'
        )
        self.assertEqual(membership.user, self.user)
        self.assertEqual(membership.vendor, self.vendor)
        self.assertEqual(membership.role, 'Vendor_admin')

    def test_membership_default_role(self):
        #Test that default role is 'User'
        membership = Membership.objects.create(
            user=self.user,
            vendor=self.vendor
        )
        self.assertEqual(membership.role, 'user')

    def test_membership_role_choices(self):
        #Test all role choices are valid
        roles = ['Platform_admin', 'Platform_agent', 'Vendor_admin', 'Vendor_agent', 'User']
        for idx, role in enumerate(roles):
            user = User.objects.create_user(email=f'user{idx}@example.com', password='pass')
            membership = Membership.objects.create(
                user=user,
                vendor=self.vendor,
                role=role
            )
            self.assertEqual(membership.role, role)

    def test_membership_unique_together(self):
        #Test that user-vendor combination must be unique
        Membership.objects.create(
            user=self.user,
            vendor=self.vendor,
            role='Vendor_admin'
        )
        with self.assertRaises(Exception):
            Membership.objects.create(
                user=self.user,
                vendor=self.vendor,
                role='Vendor_agent'
            )
