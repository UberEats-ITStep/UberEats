from rest_framework import serializers
from orders.models import Order
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    client_email = serializers.CharField(source='client.email', read_only=True)
    client_username = serializers.CharField(source='client.username', read_only=True)
    client_avatar = serializers.CharField(source='client.profile.avatar', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'client', 'client_email', 'client_username', 'client_avatar',
            'restaurant', 'order', 'rating', 'comment', 'created_at', 'updated_at',
        ]
        read_only_fields = ['client']

    def validate(self, attrs):
        if self.instance:
            return attrs

        order = attrs.get('order')
        restaurant = attrs.get('restaurant')
        user = self.context['request'].user

        if order.client != user:
            raise serializers.ValidationError({"order": "You can only review your own orders."})

        if order.status != Order.STATUS_COMPLETED:
            raise serializers.ValidationError({"order": "You can only review completed orders."})

        if order.restaurant != restaurant:
            raise serializers.ValidationError({"restaurant": "The reviewed restaurant must match the order's restaurant."})

        if Review.objects.filter(order=order).exists():
            raise serializers.ValidationError({"order": "You have already reviewed this order."})

        return attrs

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)