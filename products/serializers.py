from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'vendor']
        read_only_fields = ['id', 'vendor']
    
    def validate_name(self, value):
        vendor = self.context.get('vendor')
        if not vendor:
            return value
        
        # Exclude current instance during update
        queryset = Category.objects.filter(name=value, vendor=vendor)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Category with this name already exists for this vendor"
            )
        
        return value  # ← Added return statement


class ProductSerializer(serializers.ModelSerializer):
    # Use PrimaryKeyRelatedField for write operations, nested for reads
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True
    )
    category_detail = CategorySerializer(source='category', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'category', 'category_detail',
            'vendor', 'discount', 'quantity', 'photo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'vendor', 'created_at', 'updated_at']

    def validate_category(self, value):
        """Validate that category belongs to the vendor"""
        vendor = self.context.get('vendor')
        if not vendor:
            raise serializers.ValidationError('Vendor context is required')
        
        if value.vendor != vendor:
            raise serializers.ValidationError(
                'Category does not belong to this vendor.'
            )
        return value

    def validate_price(self, value):
        """Validate price is positive"""
        if value < 0:
            raise serializers.ValidationError('Price must be a positive value.')
        return value

    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value < 0:
            raise serializers.ValidationError('Quantity must be a positive value.')
        return value
    
    def validate_discount(self, value):
        """Validate discount is between 0 and 100"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError('Discount must be between 0 and 100.')
        return value