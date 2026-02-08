from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from accounts.models import Vendor
from .models import Category, Product


class CategoryModelTests(TestCase):
    def setUp(self):
        self.vendor = Vendor.objects.create(
            company_name='TestVendor', address='123 Street',
            phone_number='1234567890', email='vendor@test.com'
        )

    def test_category_creation(self):
        #Test creating a category
        category = Category.objects.create(
            name='Electronics',
            vendor=self.vendor
        )
        self.assertEqual(category.name, 'Electronics')
        self.assertEqual(category.vendor, self.vendor)

    def test_category_unique_per_vendor(self):
        #Test that category names must be unique per vendor
        Category.objects.create(name='Electronics', vendor=self.vendor)
        # Creating same category for same vendor should fail
        with self.assertRaises(Exception):
            Category.objects.create(name='Electronics', vendor=self.vendor)

    def test_category_same_name_different_vendors(self):
        #Test that same category name can exist for different vendors.
        vendor2 = Vendor.objects.create(
            company_name='Vendor2', address='456 St',
            phone_number='0987654321', email='vendor2@test.com'
        )
        cat1 = Category.objects.create(name='Electronics', vendor=self.vendor)
        cat2 = Category.objects.create(name='Electronics', vendor=vendor2)
        self.assertNotEqual(cat1.id, cat2.id)
        self.assertEqual(cat1.name, cat2.name)

    def test_category_string_representation(self):
        #Test category __str__ method
        category = Category.objects.create(
            name='Fashion',
            vendor=self.vendor
        )
        self.assertEqual(str(category), 'Fashion')


class ProductModelTests(TestCase):
    def setUp(self):
        self.vendor = Vendor.objects.create(
            company_name='TestVendor', address='123 Street',
            phone_number='1234567890', email='vendor@test.com'
        )
        self.category = Category.objects.create(
            name='Electronics',
            vendor=self.vendor
        )

    def test_product_creation(self):
        #Test creating a product
        product = Product.objects.create(
            name='Laptop',
            description='High-performance laptop',
            price=Decimal('999.99'),
            category=self.category,
            vendor=self.vendor,
            discount=Decimal('10')
        )
        self.assertEqual(product.name, 'Laptop')
        self.assertEqual(product.price, Decimal('999.99'))
        self.assertEqual(product.discount, Decimal('10'))
        self.assertEqual(product.category, self.category)

    def test_product_default_values(self):
        #Test product default values
        product = Product.objects.create(
            name='Mouse',
            description='Wireless mouse',
            price=Decimal('25.00'),
            category=self.category,
            vendor=self.vendor
        )
        self.assertEqual(product.quantity, 1)
        self.assertEqual(product.discount, Decimal('0'))
        self.assertIsNotNone(product.created_at)
        self.assertIsNotNone(product.updated_at)

    def test_product_with_discount(self):
        #Test product with discount
        product = Product.objects.create(
            name='Keyboard',
            description='Mechanical keyboard',
            price=Decimal('150.00'),
            category=self.category,
            vendor=self.vendor,
            discount=Decimal('25')
        )
        self.assertEqual(product.discount, Decimal('25'))

    def test_product_null_discount(self):
        #Test product with null discount defaults to 0
        product = Product.objects.create(
            name='Monitor',
            description='4K Monitor',
            price=Decimal('500.00'),
            category=self.category,
            vendor=self.vendor,
            discount=None
        )
        self.assertIsNone(product.discount)

    def test_product_string_representation(self):
        #Test product __str__ method
        product = Product.objects.create(
            name='Headphones',
            description='Noise-cancelling headphones',
            price=Decimal('299.99'),
            category=self.category,
            vendor=self.vendor
        )
        self.assertEqual(str(product), 'Headphones')

    def test_product_large_quantity(self):
        #Test product with large quantity
        product = Product.objects.create(
            name='USB Cable',
            description='USB-C cable',
            price=Decimal('10.00'),
            category=self.category,
            vendor=self.vendor,
            quantity=1000
        )
        self.assertEqual(product.quantity, 1000)

    def test_multiple_products_same_category(self):
        #Test multiple products in same category
        product1 = Product.objects.create(
            name='Product 1',
            description='Desc 1',
            price=Decimal('100.00'),
            category=self.category,
            vendor=self.vendor
        )
        product2 = Product.objects.create(
            name='Product 2',
            description='Desc 2',
            price=Decimal('200.00'),
            category=self.category,
            vendor=self.vendor
        )
        self.assertEqual(self.category.products.count(), 2)
