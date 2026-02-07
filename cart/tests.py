from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
import cart.signals  
from accounts.models import Vendor
from products.models import Category, Product
from .models import Cart, CartItem


class CartModelTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(email='user@example.com', password='pass')
		self.vendor = Vendor.objects.create(
			company_name='Acme Corp', address='123 Lane', phone_number='1234567890', email='v@acme.com'
		)
		self.category = Category.objects.create(name='Default', vendor=self.vendor)
		self.product1 = Product.objects.create(
			name='Product 1', description='P1', price=Decimal('10.00'), category=self.category, vendor=self.vendor, discount=Decimal('0')
		)
		self.product2 = Product.objects.create(
			name='Product 2', description='P2', price=Decimal('20.00'), category=self.category, vendor=self.vendor, discount=Decimal('50')
		)
		self.cart = Cart.objects.create(user=self.user, vendor=self.vendor, session_key='abc')

	def test_cartitem_total_calculation(self):
		item = CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
		self.assertEqual(item.total, Decimal('20.00'))

		item2 = CartItem.objects.create(cart=self.cart, product=self.product2, quantity=3)
		self.assertEqual(item2.total, Decimal('30.00'))

	def test_compute_total_and_signals_update_cart_total(self):
		# create items (signals should update cart.total)
		CartItem.objects.create(cart=self.cart, product=self.product1, quantity=1)
		CartItem.objects.create(cart=self.cart, product=self.product2, quantity=2)
		
		self.cart.refresh_from_db()
		self.assertEqual(self.cart.total, Decimal('30.00'))

		# delete one item and ensure total updates
		item = self.cart.items.filter(product=self.product2).first()
		item.delete()
		self.cart.refresh_from_db()
		self.assertEqual(self.cart.total, Decimal('10.00'))

