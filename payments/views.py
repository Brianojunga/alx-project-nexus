from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from orders.models import Order
from .models import Payment
from .services.paystack import PaystackService
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from .tasks import send_payment_confirmation_email
# Create your views here.

class PaymentViewSet(viewsets.ViewSet):

    def create(self, request, vendor_slug=None, order_id=None):
        order = get_object_or_404(
            Order,
            id=order_id,
            vendor__slug=vendor_slug,
            status="pending",
        )

        paystack = PaystackService()
        response, reference = paystack.initialize(order)

        if response and response.get('status') == True:
            return Response(
                {
                    "reference": reference, 
                    "checkout_url": response['data']['authorization_url']
                })

        return Response(
            {"error" : 'Failed to initialize payment'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
class Verify(APIView):
    
    @transaction.atomic()
    def get(self, request, reference):
        payment = get_object_or_404(Payment, reference=reference)

        paystack = PaystackService()
        verification = paystack.verify(payment.reference)
       
        if verification and verification.get('status') == True:
            payment.status = "success"
            payment.save()

            order = payment.order
            order.status = "paid"
            order.save()
            #send confirmation email
            send_payment_confirmation_email.delay(
                payment.order.user.email, payment.reference, payment.amount)

            return Response(
                {"message": "Payment verified successfully."},
                status=status.HTTP_200_OK
            )
        
        payment.status = "failed"
        payment.save()

        return Response(
            {"error": "Payment verification failed."},
            status=status.HTTP_400_BAD_REQUEST
        )
