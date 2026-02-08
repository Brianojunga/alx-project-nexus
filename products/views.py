from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from django.shortcuts import get_object_or_404
from accounts.models import Vendor, Membership
from accounts.permissions import IsVendorAdminOrAgent
from services.caching import caching, clear_vendor_cache


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsVendorAdminOrAgent]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Category.objects.none()
        
        return Category.objects.filter(
            vendor__slug=self.kwargs['vendor_slug']
        )
    
    def list(self, request, *args, **kwargs):
        return caching(self, request, "category", *args, **kwargs)
    
    def perform_create(self, serializer):
        if getattr(self, 'swagger_fake_view', False):
            return serializer.save()
        
        vendor = get_object_or_404(Vendor, slug=self.kwargs.get('vendor_slug'))
        serializer.save(vendor=vendor)
        # Clear cache after creation
        clear_vendor_cache(vendor.slug, "category")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if getattr(self, 'swagger_fake_view', False):
            return context
        
        slug = self.kwargs.get('vendor_slug')
        if not slug:
            return context
        
        context['vendor'] = get_object_or_404(Vendor, slug=slug)
        return context
    

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsVendorAdminOrAgent]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Product.objects.none()
        
        vendor_slug = self.kwargs.get('vendor_slug')
        queryset = Product.objects.filter(vendor__slug=vendor_slug)
        
        # Optional filtering by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset.select_related('category', 'vendor')
    
    def list(self, request, *args, **kwargs):
        return caching(self, request, "product", *args, **kwargs)
    
    def perform_create(self, serializer):
        vendor = get_object_or_404(Vendor, slug=self.kwargs['vendor_slug'])
        serializer.save(vendor=vendor)
        # Clear cache after creation
        clear_vendor_cache(vendor.slug, "product")


    def get_serializer_context(self):
        context = super().get_serializer_context()
        if getattr(self, 'swagger_fake_view', False):
            return context
        
        slug = self.kwargs.get('vendor_slug')
        if not slug:
            return context
        
        context['vendor'] = get_object_or_404(Vendor, slug=slug)
        return context