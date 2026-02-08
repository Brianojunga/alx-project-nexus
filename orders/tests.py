from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.models import Q
from uuid import uuid4

from accounts.models import Vendor
from products.models import Category, Product
from .models import Order, OrderItem

User = get_user_model()


class OrderModelTests(TestCase):
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

    def test_order_creation(self):
        #Test creating an order with user
        order = Order.objects.create(
            user=self.user, vendor=self.vendor, status='pending',
            subtotal=Decimal('100.00'), tax=Decimal('10.00'), total=Decimal('110.00')
        )
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total, Decimal('110.00'))
        self.assertIsNotNone(order.id)

    def test_order_with_session_key(self):
        #Test creating an order with session_key for guest users
        order = Order.objects.create(
            session_key='guest-session-123', vendor=self.vendor, status='pending',
            subtotal=Decimal('50.00'), tax=Decimal('5.00'), total=Decimal('55.00')
        )
        self.assertEqual(order.session_key, 'guest-session-123')
        self.assertIsNone(order.user)
        self.assertEqual(order.status, 'pending')

    def test_order_status_choices(self):
        #Test that all status choices are valid
        statuses = ['pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled']
        for idx, status in enumerate(statuses):
            # Create separate user for each order to avoid unique constraint violation
            user = User.objects.create_user(email=f'statususer{idx}@example.com', password='pass')
            order = Order.objects.create(
                user=user, vendor=self.vendor, status=status,
                subtotal=Decimal('100.00'), tax=Decimal('10.00'), total=Decimal('110.00')
            )
            self.assertEqual(order.status, status)

    def test_unique_pending_order_per_user_vendor(self):
        #Test that only one pending order per user-vendor combination is allowed
        Order.objects.create(
            user=self.user, vendor=self.vendor, status='pending',
            subtotal=Decimal('100.00'), tax=Decimal('10.00'), total=Decimal('110.00')
        )
        # Creating another pending order with same user and vendor should fail
        with self.assertRaises(Exception):
            Order.objects.create(
                user=self.user, vendor=self.vendor, status='pending',
                subtotal=Decimal('50.00'), tax=Decimal('5.00'), total=Decimal('55.00')
            )


class OrderItemModelTests(TestCase):
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

    def test_orderitem_creation(self):
        #Test creating an order item
        item = OrderItem.objects.create(
            order=self.order, product=self.product, quantity=2,
            price=Decimal('50.00')
        )
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.order, self.order)
        self.assertEqual(item.product, self.product)

    def test_orderitem_total_calculation(self):
        #Test that total is automatically calculated on save
        item = OrderItem.objects.create(
            order=self.order, product=self.product, quantity=3,
            price=Decimal('50.00')
        )
        # total should be product.price * quantity
        expected_total = Decimal('50.00') * 3
        self.assertEqual(item.total, expected_total)

    def test_orderitem_string_representation(self):
        #Test orderitem __str__ method.
        item = OrderItem.objects.create(
            order=self.order, product=self.product, quantity=2,
            price=Decimal('50.00')
        )
        self.assertIn('Test Product', str(item))
        self.assertIn('2', str(item))

    def test_orderitem_deletion_on_product_protect(self):
        #Test that OrderItem references have PROTECT constraint on Product
        OrderItem.objects.create(
            order=self.order, product=self.product, quantity=1,
            price=Decimal('50.00')
        )
        #Deleting the product should raise ProtectedError
        with self.assertRaises(Exception):
            self.product.delete()
