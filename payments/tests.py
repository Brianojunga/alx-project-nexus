from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Vendor
from products.models import Category, Product
from orders.models import Order
from .models import Payment, VendorSubAccount

User = get_user_model()


class PaymentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='pass')
        self.vendor = Vendor.objects.create(
            company_name='TestVendor', address='123 Street',
            phone_number='1234567890', email='vendor@test.com'
        )
        self.category = Category.objects.create(name='Test Category', vendor=self.vendor)
        self.product = Product.objects.create(
            name='Test Product', description='Test', price=Decimal('50.00'),
            category=self.category, vendor=self.vendor
        )
        self.order = Order.objects.create(
            user=self.user, vendor=self.vendor, status='pending',
            subtotal=Decimal('100.00'), tax=Decimal('10.00'), total=Decimal('110.00')
        )

    def test_payment_creation(self):
        #Test creating a payment
        payment = Payment.objects.create(
            order=self.order,
            reference='PAY-12345',
            amount=Decimal('110.00'),
            status='pending',
            channel='paystack'
        )
        self.assertEqual(payment.reference, 'PAY-12345')
        self.assertEqual(payment.amount, Decimal('110.00'))
        self.assertEqual(payment.status, 'pending')
        self.assertEqual(payment.order, self.order)

    def test_payment_status_choices(self):
        #Test all payment status choices
        statuses = ['pending', 'success', 'failed']
        for idx, status in enumerate(statuses):
            # Create separate user for each order to avoid unique constraint violation
            user = User.objects.create_user(email=f'user{idx}@example.com', password='pass')
            order = Order.objects.create(
                user=user, vendor=self.vendor, status='pending',
                subtotal=Decimal('100.00'), tax=Decimal('10.00'), 
                total=Decimal('110.00')
            )
            payment = Payment.objects.create(
                order=order,
                reference=f'PAY-{idx}',
                amount=Decimal('110.00'),
                status=status
            )
            self.assertEqual(payment.status, status)

    def test_payment_reference_uniqueness(self):
        #Test that payment reference must be unique
        Payment.objects.create(
            order=self.order,
            reference='UNIQUE-REF',
            amount=Decimal('110.00'),
            status='pending'
        )
        with self.assertRaises(Exception):
            Payment.objects.create(
                order=self.order,
                reference='UNIQUE-REF',
                amount=Decimal('110.00'),
                status='pending'
            )

    def test_payment_default_values(self):
        #Test payment default values
        payment = Payment.objects.create(
            order=self.order,
            reference='DEFAULT-TEST',
            amount=Decimal('110.00')
        )
        self.assertEqual(payment.status, 'pending')
        self.assertIsNotNone(payment.created_at)


class VendorSubAccountModelTests(TestCase):
    def setUp(self):
        self.vendor = Vendor.objects.create(
            company_name='TestVendor', address='123 Street',
            phone_number='1234567890', email='vendor@test.com'
        )

    def test_subaccount_creation(self):
        #Test creating a vendor subaccount
        subaccount = VendorSubAccount.objects.create(
            vendor=self.vendor,
            subaccount_code='SUB-12345',
            percentage_charge=Decimal('98.50')
        )
        self.assertEqual(subaccount.vendor, self.vendor)
        self.assertEqual(subaccount.subaccount_code, 'SUB-12345')
        self.assertEqual(subaccount.percentage_charge, Decimal('98.50'))

    def test_subaccount_default_percentage(self):
        #Test default percentage charge value
        subaccount = VendorSubAccount.objects.create(
            vendor=self.vendor,
            subaccount_code='SUB-DEFAULT'
        )
        self.assertEqual(subaccount.percentage_charge, Decimal('98.50'))

    def test_subaccount_code_uniqueness(self):
        #Test that subaccount_code is unique
        VendorSubAccount.objects.create(
            vendor=self.vendor,
            subaccount_code='UNIQUE-CODE'
        )
        vendor2 = Vendor.objects.create(
            company_name='Vendor2', address='456 St',
            phone_number='0987654321', email='vendor2@test.com'
        )
        with self.assertRaises(Exception):
            VendorSubAccount.objects.create(
                vendor=vendor2,
                subaccount_code='UNIQUE-CODE'
            )

    def test_vendor_oneone_subaccount(self):
        #Test that vendor has OneToOne relationship with subaccount
        subaccount = VendorSubAccount.objects.create(
            vendor=self.vendor,
            subaccount_code='SUB-ONONE'
        )
        # Creating another subaccount for same vendor should fail
        with self.assertRaises(Exception):
            VendorSubAccount.objects.create(
                vendor=self.vendor,
                subaccount_code='SUB-ONONE-2'
            )
