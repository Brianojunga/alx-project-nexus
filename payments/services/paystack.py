import uuid
import requests
from django.conf import settings
from payments.models import Payment
import os

class PaystackService:
    def __init__(self):
        self.reference = str(uuid.uuid4())
        self.base_url = 'https://api.paystack.co'
        self.headers = {
            "Authorization": f"Bearer  {os.getenv("PAYSTACK_SECRET_KEY")}",
            "Content-Type": "application/json"
        }

    def initialize(self, order):
        subaccount = order.vendor.paystack_account
        url = f"{self.base_url}/transaction/initialize" 

        payload = {
            "email": order.user.email if order.user else "guest@platform.com",
            "amount": int(order.total_amount * 100),
            "reference" : self.reference,
            "currency": "KES",
            "callback_url" : f"http://127.0.0.1:8000/api/payments/verify/{self.reference}/",
            "subaccount": subaccount.subaccount_code
        }

        try:
            res = requests.post(url, headers=self.headers, json=payload)
            res.raise_for_status()
            Payment.objects.create(
                order=order,
                reference=self.reference,
                amount=order.total,
                status="pending",
            )
            return res.json(), self.reference
        except requests.exceptions.RequestException as e:
            print(f"Paystack Error: {e}")
            return None
        
 
    def verify(self, reference):
        url = f"{self.base_url}/transaction/verify/{reference}",
        try:
            res = requests.get(url, headers=self.headers)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            print(f"Paystack Verification Error: {e}")
            return None