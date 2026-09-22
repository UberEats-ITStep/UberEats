from rest_framework import serializers

class CreateIntentRequestSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)

class CreateIntentResponseSerializer(serializers.Serializer):
    client_secret = serializers.CharField()
