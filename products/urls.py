# products/urls.py
from django.urls import path
from .views import CategoryViewSet, ProductViewSet

# Manual nested URL patterns
category_list = CategoryViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

category_detail = CategoryViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

product_list = ProductViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

product_detail = ProductViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    # Category endpoints
    path('vendors/<slug:vendor_slug>/categories/', category_list, name='vendor-category-list'),
    path('vendors/<slug:vendor_slug>/categories/<int:pk>/', category_detail, name='vendor-category-detail'),
    
    # Product endpoints
    path('vendors/<slug:vendor_slug>/products/', product_list, name='vendor-product-list'),
    path('vendors/<slug:vendor_slug>/products/<int:pk>/', product_detail, name='vendor-product-detail'),
]